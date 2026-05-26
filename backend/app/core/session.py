from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import SysMessage, SysSession


def _now() -> datetime:
    return datetime.utcnow()


def list_sessions(db: Session) -> list[SysSession]:
    stmt = select(SysSession).order_by(SysSession.updated_at.desc())
    return list(db.scalars(stmt).all())


def create_session(db: Session, *, title: str = "新对话") -> SysSession:
    session = SysSession(
        id=str(uuid.uuid4()),
        title=title,
        created_at=_now(),
        updated_at=_now(),
    )
    db.add(session)
    db.flush()
    return session


def get_session(db: Session, session_id: str) -> SysSession:
    session = db.get(SysSession, session_id)
    if session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="会话不存在")
    return session


def update_session_title(db: Session, session_id: str, title: str) -> SysSession:
    session = get_session(db, session_id)
    session.title = title
    session.updated_at = _now()
    db.flush()
    return session


def delete_session(db: Session, session_id: str) -> None:
    session = get_session(db, session_id)
    db.delete(session)


def list_messages(db: Session, session_id: str) -> list[SysMessage]:
    get_session(db, session_id)
    stmt = (
        select(SysMessage)
        .where(SysMessage.session_id == session_id)
        .order_by(SysMessage.created_at.asc())
    )
    return list(db.scalars(stmt).all())


def count_user_messages(db: Session, session_id: str) -> int:
    stmt = select(SysMessage).where(
        SysMessage.session_id == session_id,
        SysMessage.role == "user",
    )
    return len(list(db.scalars(stmt).all()))
