from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.db.models import SysMessage, SysSessionSummary


def load_session_messages(
    db: Session,
    session_id: str,
    *,
    limit: int = 10,
) -> list[SysMessage]:
    get_session(db, session_id)
    stmt = (
        select(SysMessage)
        .where(SysMessage.session_id == session_id)
        .order_by(SysMessage.created_at.desc())
        .limit(limit * 2)
    )
    rows = list(db.scalars(stmt).all())
    rows.reverse()
    return rows


def save_message(
    db: Session,
    *,
    session_id: str,
    role: str,
    content: str,
    sql: str | None = None,
    result: list[dict[str, Any]] | None = None,
    chart_spec: dict[str, Any] | None = None,
) -> SysMessage:
    get_session(db, session_id)
    message = SysMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role=role,
        content=content,
        sql_query=sql,
        query_result_json=json.dumps(result, ensure_ascii=False) if result is not None else None,
        chart_spec_json=json.dumps(chart_spec, ensure_ascii=False) if chart_spec is not None else None,
        created_at=datetime.utcnow(),
    )
    db.add(message)
    db.flush()
    return message


def build_chat_history(messages: list[SysMessage]) -> list[BaseMessage]:
    history: list[BaseMessage] = []
    for msg in messages:
        if msg.role == "user":
            history.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            history.append(AIMessage(content=msg.content))
    return history


def save_session_summary(db: Session, session_id: str, summary: str) -> None:
    row = db.get(SysSessionSummary, session_id)
    if row is None:
        row = SysSessionSummary(session_id=session_id, summary=summary)
        db.add(row)
    else:
        row.summary = summary
        row.updated_at = datetime.utcnow()
    db.flush()
