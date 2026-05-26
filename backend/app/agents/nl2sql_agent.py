from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import sqlite3
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage

from app.config import Settings, get_settings
from app.core.llm import get_llm
from app.db.sqlite import (
    execute_readonly_query,
    get_biz_table_names,
    resolve_db_path,
    rows_from_query_result,
    validate_select_only,
)

PROMPT_PATH = Path(__file__).parent / "prompts" / "nl2sql.txt"


@dataclass
class NL2SQLResult:
    answer: str
    sql: str | None
    rows: list[dict[str, Any]]
    messages: list[BaseMessage]


def _load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8").strip()


def build_sql_tools(db_path: Path, llm: Any, *, settings: Settings | None = None):
    settings = settings or get_settings()
    allowed_tables = set(get_biz_table_names(settings))

    @tool
    def sql_db_list_tables() -> str:
        """Input is an empty string, output is a comma-separated list of tables in the database."""
        con = sqlite3.connect(db_path)
        try:
            cur = con.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [
                r[0]
                for r in cur.fetchall()
                if r[0].startswith("biz_") and r[0] in allowed_tables
            ]
            return ", ".join(tables)
        finally:
            con.close()

    @tool
    def sql_db_schema(table_names: str) -> str:
        """Input is comma-separated table names; output is schema and sample rows."""
        con = sqlite3.connect(db_path)
        try:
            cur = con.cursor()
            parts: list[str] = []
            for name in table_names.split(","):
                t = name.strip()
                if t not in allowed_tables:
                    parts.append(f"Error: table {t!r} not found in schema whitelist")
                    continue
                cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?;", (t,))
                row = cur.fetchone()
                if row:
                    parts.append(row[0])
                    quoted = '"' + t.replace('"', '""') + '"'
                    cur.execute(f"SELECT * FROM {quoted} LIMIT 3;")
                    rows = cur.fetchall()
                    if rows:
                        cols = [d[0] for d in cur.description]
                        sample = "\n".join("\t".join(str(c) for c in r) for r in rows)
                        parts.append(
                            f"/*\n3 rows from {t}:\n" + "\t".join(cols) + "\n" + sample + "\n*/"
                        )
            return "\n\n".join(parts)
        finally:
            con.close()

    @tool
    def sql_db_query(query: str) -> str:
        """Execute a SQL query; return stringified rows or error message."""
        try:
            validate_select_only(query)
            rows = execute_readonly_query(query, settings=settings)
            return str([tuple(row.values()) for row in rows])
        except Exception as exc:
            return f"Error: {exc}"

    @tool
    def sql_db_query_checker(query: str) -> str:
        """Double-check SQL before execution; return corrected or original query."""
        prompt = f"""{query}
Double check the sqlite query above for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins

If there are mistakes, rewrite the query. If none, reproduce the original query.
Output the final SQL query only.

SQL Query:"""
        resp = llm.invoke(prompt)
        content = resp.content if hasattr(resp, "content") else str(resp)
        return str(content).strip()

    return [sql_db_list_tables, sql_db_schema, sql_db_query, sql_db_query_checker]


@lru_cache
def _get_agent():
    settings = get_settings()
    llm = get_llm(streaming=False)
    db_path = resolve_db_path(settings)
    tools = build_sql_tools(db_path, llm, settings=settings)
    return create_agent(llm, tools, system_prompt=_load_system_prompt())


def _extract_sql_and_rows(messages: list[BaseMessage]) -> tuple[str | None, list[dict[str, Any]]]:
    sql: str | None = None
    rows: list[dict[str, Any]] = []
    pending_sql: str | None = None

    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                args = tc.get("args") if isinstance(tc, dict) else getattr(tc, "args", None)
                if name == "sql_db_query" and isinstance(args, dict):
                    pending_sql = args.get("query")
        if isinstance(msg, ToolMessage):
            if msg.name == "sql_db_query" and pending_sql:
                sql = pending_sql
                rows = rows_from_query_result(str(msg.content), sql)
                pending_sql = None
    return sql, rows


def run_nl2sql(
    question: str,
    chat_history: list[BaseMessage] | None = None,
) -> NL2SQLResult:
    agent = _get_agent()
    history = list(chat_history or [])
    payload = {"messages": [*history, HumanMessage(content=question)]}
    result = agent.invoke(payload)
    messages: list[BaseMessage] = result["messages"]
    sql, rows = _extract_sql_and_rows(messages)

    answer = ""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
            answer = str(msg.content)
            break

    return NL2SQLResult(answer=answer, sql=sql, rows=rows, messages=messages)


def clear_agent_cache() -> None:
    _get_agent.cache_clear()
