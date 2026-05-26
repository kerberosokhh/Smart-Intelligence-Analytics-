"""NL2SQL 组件接口探测测试 — 基于 ChatDeepSeek + create_agent + SQL 工具。

验证 LangChain 1.x 官方 SQL Agent 模式与 DeepSeek 的实际入参/出参结构。
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from langchain.agents import create_agent
from langchain.tools import tool

from app.config import get_settings
from app.core.llm import get_llm

# ---------------------------------------------------------------------------
# 最小 Demo 库（与 Phase3 biz_orders 结构对齐的简化版）
# ---------------------------------------------------------------------------

DEMO_DDL = """
CREATE TABLE biz_orders (
    id INTEGER PRIMARY KEY,
    order_date TEXT NOT NULL,
    region TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL
);
"""

DEMO_ROWS = [
    ("2024-01-05", "华东", "电子产品", 1200.0),
    ("2024-01-12", "华北", "服装", 350.0),
    ("2024-02-03", "华东", "服装", 890.0),
    ("2024-02-18", "华南", "电子产品", 2100.0),
    ("2024-03-01", "华东", "电子产品", 980.0),
    ("2024-03-15", "华北", "食品", 420.0),
]


def _init_demo_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    try:
        con.executescript("DROP TABLE IF EXISTS biz_orders;")
        con.executescript(DEMO_DDL)
        con.executemany(
            "INSERT INTO biz_orders (order_date, region, category, amount) VALUES (?, ?, ?, ?);",
            DEMO_ROWS,
        )
        con.commit()
    finally:
        con.close()


def _build_sql_tools(db_path: Path, llm: Any) -> list:
    """按 LangChain sql-agent 教程封装 4 个 SQL 工具。"""

    @tool
    def sql_db_list_tables() -> str:
        """Input is an empty string, output is a comma-separated list of tables in the database."""
        con = sqlite3.connect(db_path)
        try:
            cur = con.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [r[0] for r in cur.fetchall() if not r[0].startswith("sqlite_")]
            return ", ".join(tables)
        finally:
            con.close()

    @tool
    def sql_db_schema(table_names: str) -> str:
        """Input is comma-separated table names; output is schema and sample rows."""
        con = sqlite3.connect(db_path)
        try:
            cur = con.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            valid = {r[0] for r in cur.fetchall() if not r[0].startswith("sqlite_")}
            parts: list[str] = []
            for name in table_names.split(","):
                t = name.strip()
                if t not in valid:
                    parts.append(f"Error: table {t!r} not found")
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
                        parts.append(f"/*\n3 rows from {t}:\n" + "\t".join(cols) + "\n" + sample + "\n*/")
            return "\n\n".join(parts)
        finally:
            con.close()

    @tool
    def sql_db_query(query: str) -> str:
        """Execute a SQL query; return stringified rows or error message."""
        q = query.strip().upper()
        if not q.startswith("SELECT"):
            return "Error: only SELECT queries are allowed"
        con = sqlite3.connect(db_path)
        try:
            cur = con.cursor()
            cur.execute(query)
            return str(cur.fetchall())
        except Exception as exc:
            return f"Error: {exc}"
        finally:
            con.close()

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


NL2SQL_SYSTEM_PROMPT = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct sqlite query to run,
then look at the results and return the answer. Limit queries to at most 5 results
unless the user specifies otherwise.

You MUST double check your query before executing it using sql_db_query_checker.
If you get an error while executing, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.).

To start you should ALWAYS look at the tables in the database.
Then query the schema of the most relevant tables.
""".strip()


def _message_to_dict(msg: Any) -> dict[str, Any]:
    """将 LangChain Message 序列化为可断言的结构。"""
    base: dict[str, Any] = {
        "type": type(msg).__name__,
        "content": getattr(msg, "content", None),
    }
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        base["tool_calls"] = [
            {
                "name": tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None),
                "args": tc.get("args") if isinstance(tc, dict) else getattr(tc, "args", None),
                "id": tc.get("id") if isinstance(tc, dict) else getattr(tc, "id", None),
            }
            for tc in msg.tool_calls
        ]
    if hasattr(msg, "name"):
        base["name"] = msg.name
    return base


@pytest.fixture
def demo_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "nl2sql_demo.db"
    _init_demo_db(db_path)
    return db_path


@pytest.fixture(autouse=True)
def clear_caches():
    get_settings.cache_clear()
    get_llm.cache_clear()
    yield
    get_settings.cache_clear()
    get_llm.cache_clear()


def test_nl2sql_agent_interface(demo_db: Path) -> None:
    """探测 create_agent + SQL 工具与 DeepSeek 的实际接口。"""
    settings = get_settings()
    if not settings.deepseek_api_key:
        pytest.skip("DEEPSEEK_API_KEY 未配置")

    llm = get_llm(streaming=False)
    tools = _build_sql_tools(demo_db, llm)

    # --- create_agent 入参 ---
    agent = create_agent(
        llm,
        tools,
        system_prompt=NL2SQL_SYSTEM_PROMPT,
    )

    assert hasattr(agent, "invoke")
    assert hasattr(agent, "stream")
    print(f"\n[接口] agent 类型: {type(agent).__name__}")

    # --- invoke 入参格式 ---
    question = "华东地区各品类的销售总额是多少？按总额降序排列。"
    invoke_input = {"messages": [{"role": "user", "content": question}]}
    print(f"\n[接口] invoke 入参: {json.dumps(invoke_input, ensure_ascii=False, indent=2)}")

    result = agent.invoke(invoke_input)

    # --- invoke 出参结构 ---
    assert "messages" in result
    messages = result["messages"]
    assert isinstance(messages, list) and len(messages) >= 2

    serialized = [_message_to_dict(m) for m in messages]
    print(f"\n[接口] invoke 出参 messages 共 {len(serialized)} 条:")
    for i, m in enumerate(serialized):
        line = json.dumps(m, ensure_ascii=True, default=str)[:500]
        print(f"  [{i}] {line}")

    last = messages[-1]
    final_content = last.content if hasattr(last, "content") else str(last)
    assert final_content
    print(f"\n[接口] 最终回答: {final_content[:300]}")

    # 应至少触发一次 SQL 相关 tool call
    tool_names = {
        tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
        for msg in messages
        if hasattr(msg, "tool_calls") and msg.tool_calls
        for tc in msg.tool_calls
    }
    print(f"\n[接口] 触发的工具: {sorted(tool_names)}")
    assert "sql_db_list_tables" in tool_names or "sql_db_query" in tool_names


def test_nl2sql_agent_stream_interface(demo_db: Path) -> None:
    """探测 agent.stream 的 stream_mode 与逐步输出结构。"""
    settings = get_settings()
    if not settings.deepseek_api_key:
        pytest.skip("DEEPSEEK_API_KEY 未配置")

    llm = get_llm(streaming=False)
    tools = _build_sql_tools(demo_db, llm)
    agent = create_agent(llm, tools, system_prompt=NL2SQL_SYSTEM_PROMPT)

    question = "哪个地区的订单总金额最高？"
    stream_input = {"messages": [{"role": "user", "content": question}]}

    steps: list[dict[str, Any]] = []
    for step in agent.stream(stream_input, stream_mode="values"):
        assert "messages" in step
        last_msg = step["messages"][-1]
        steps.append(_message_to_dict(last_msg))

    print(f"\n[接口] stream(stream_mode='values') 共 {len(steps)} 步")
    for i, s in enumerate(steps):
        print(f"  step[{i}] type={s['type']} name={s.get('name')} tools={s.get('tool_calls')}")

    assert len(steps) >= 2
    assert steps[-1]["type"] in ("AIMessage", "AIMessageChunk")
