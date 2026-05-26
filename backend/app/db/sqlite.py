from __future__ import annotations

import ast
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings, get_settings
from app.db.models import Base

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
FORBIDDEN_SQL = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|ATTACH|DETACH|REPLACE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)


def resolve_db_path(settings: Settings | None = None) -> Path:
    settings = settings or get_settings()
    path = Path(settings.sqlite_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_database_url(settings: Settings | None = None) -> str:
    db_path = resolve_db_path(settings)
    return f"sqlite:///{db_path.as_posix()}"


_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_engine(settings: Settings | None = None) -> Engine:
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_engine(
            get_database_url(settings),
            connect_args={"check_same_thread": False},
        )
        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    get_engine()
    assert _SessionLocal is not None
    return _SessionLocal


@contextmanager
def db_session() -> Iterator[Session]:
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def reset_engine() -> None:
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None


def run_migrations(settings: Settings | None = None) -> None:
    db_path = resolve_db_path(settings)
    con = sqlite3.connect(db_path)
    try:
        con.execute(
            "CREATE TABLE IF NOT EXISTS _migrations (name TEXT PRIMARY KEY, applied_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
        )
        applied = {
            row[0]
            for row in con.execute("SELECT name FROM _migrations").fetchall()
        }
        for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if sql_file.name in applied:
                continue
            con.executescript(sql_file.read_text(encoding="utf-8"))
            con.execute("INSERT INTO _migrations (name) VALUES (?)", (sql_file.name,))
            con.commit()
    finally:
        con.close()
    get_engine(settings)
    Base.metadata.create_all(get_engine(settings))


def validate_select_only(sql: str) -> None:
    normalized = sql.strip()
    if not normalized:
        raise ValueError("SQL 不能为空")
    upper = normalized.upper()
    if not upper.startswith("SELECT"):
        raise ValueError("仅允许 SELECT 查询")
    if FORBIDDEN_SQL.search(normalized):
        raise ValueError("检测到不允许的 SQL 关键字")


def execute_readonly_query(
    sql: str,
    *,
    settings: Settings | None = None,
) -> list[dict[str, Any]]:
    settings = settings or get_settings()
    validate_select_only(sql)

    db_path = resolve_db_path(settings)
    con = sqlite3.connect(db_path, timeout=settings.sql_timeout_seconds)
    con.row_factory = sqlite3.Row
    try:
        con.execute(f"PRAGMA query_only = ON")
        cur = con.cursor()
        cur.execute(sql)
        rows = [dict(row) for row in cur.fetchmany(settings.max_query_rows + 1)]
        if len(rows) > settings.max_query_rows:
            raise ValueError(f"查询结果超过 {settings.max_query_rows} 行上限")
        return rows
    finally:
        con.close()


def parse_tool_query_result(content: str) -> list[dict[str, Any]] | None:
    """将 Agent sql_db_query 返回的字符串解析为 dict 列表。"""
    content = content.strip()
    if not content or content.startswith("Error:"):
        return None
    try:
        raw = ast.literal_eval(content)
    except (SyntaxError, ValueError):
        return None
    if not isinstance(raw, list) or not raw:
        return []
    if isinstance(raw[0], tuple):
        return [{"value": item} for item in raw]
    return [{"value": raw}]


def rows_from_query_result(content: str, sql: str | None = None) -> list[dict[str, Any]]:
    """优先重新执行 SQL 获取带列名的结果；失败则解析 tool 返回字符串。"""
    if sql:
        try:
            return execute_readonly_query(sql)
        except Exception:
            pass
    parsed = parse_tool_query_result(content)
    return parsed if parsed is not None else []


def get_business_schema(settings: Settings | None = None) -> dict[str, Any]:
    engine = get_engine(settings)
    inspector = inspect(engine)
    tables: dict[str, Any] = {}
    for table in sorted(inspector.get_table_names()):
        if not table.startswith("biz_"):
            continue
        columns = [
            {
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
                "primary_key": col.get("primary_key", False),
            }
            for col in inspector.get_columns(table)
        ]
        tables[table] = {"columns": columns}
    return {"tables": tables}


def get_biz_table_names(settings: Settings | None = None) -> list[str]:
    return list(get_business_schema(settings)["tables"].keys())
