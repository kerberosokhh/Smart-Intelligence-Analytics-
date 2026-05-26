from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.session import (
    create_session,
    delete_session,
    get_session,
    list_messages,
    list_sessions,
    update_session_title,
)
from app.db.sqlite import db_session
from app.schemas.session import (
    MessageResponse,
    SessionCreate,
    SessionResponse,
    SessionUpdate,
)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


def get_db():
    with db_session() as db:
        yield db


@router.get("", response_model=list[SessionResponse])
def get_sessions(db: Session = Depends(get_db)) -> list[SessionResponse]:
    return [SessionResponse.from_row(s) for s in list_sessions(db)]


@router.post("", response_model=SessionResponse, status_code=201)
def post_session(payload: SessionCreate, db: Session = Depends(get_db)) -> SessionResponse:
    session = create_session(db, title=payload.title)
    return SessionResponse.from_row(session)


@router.patch("/{session_id}", response_model=SessionResponse)
def patch_session(
    session_id: str,
    payload: SessionUpdate,
    db: Session = Depends(get_db),
) -> SessionResponse:
    session = update_session_title(db, session_id, payload.title)
    return SessionResponse.from_row(session)


@router.delete("/{session_id}", status_code=204)
def remove_session(session_id: str, db: Session = Depends(get_db)) -> None:
    delete_session(db, session_id)


@router.get("/{session_id}/messages", response_model=list[MessageResponse])
def get_session_messages(session_id: str, db: Session = Depends(get_db)) -> list[MessageResponse]:
    get_session(db, session_id)
    return [MessageResponse.from_row(m) for m in list_messages(db, session_id)]
