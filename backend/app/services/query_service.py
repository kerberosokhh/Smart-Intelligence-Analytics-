from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

from app.agents.chart_agent import ChartSpec, generate_chart_spec
from app.agents.nl2sql_agent import run_nl2sql
from app.core.memory import build_chat_history, load_session_messages, save_message
from app.core.session import count_user_messages, update_session_title
from app.db.sqlite import db_session


def _chunk_text(text: str, size: int = 8) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size)] if text else []


def _auto_title(message: str) -> str:
    title = message.strip().replace("\n", " ")
    return title[:30] + ("..." if len(title) > 30 else "")


async def stream_query(session_id: str, user_message: str) -> AsyncIterator[dict[str, Any]]:
    with db_session() as db:
        history_rows = load_session_messages(db, session_id, limit=10)
        is_first_user = count_user_messages(db, session_id) == 0
        save_message(db, session_id=session_id, role="user", content=user_message)

    chat_history = build_chat_history(history_rows)

    try:
        nl2sql = run_nl2sql(user_message, chat_history)
    except Exception as exc:
        yield {"type": "error", "content": f"NL2SQL 执行失败: {exc}"}
        return

    if nl2sql.sql:
        yield {"type": "sql", "content": nl2sql.sql}

    if nl2sql.rows:
        yield {"type": "data", "content": nl2sql.rows}

    try:
        chart = generate_chart_spec(user_message, nl2sql.sql, nl2sql.rows)
    except Exception:
        chart = ChartSpec(type="table", title="查询结果", data=nl2sql.rows)

    chart_dict = chart.model_dump()
    yield {"type": "chart", "content": chart_dict}

    answer = nl2sql.answer or "已完成查询，请查看右侧图表与数据。"
    for chunk in _chunk_text(answer):
        yield {"type": "token", "content": chunk}

    assistant_id: str
    with db_session() as db:
        assistant = save_message(
            db,
            session_id=session_id,
            role="assistant",
            content=answer,
            sql=nl2sql.sql,
            result=nl2sql.rows,
            chart_spec=chart_dict,
        )
        if is_first_user:
            update_session_title(db, session_id, _auto_title(user_message))
        assistant_id = assistant.id

    yield {"type": "done", "message_id": assistant_id}
