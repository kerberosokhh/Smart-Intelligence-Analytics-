from datetime import datetime

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    title: str = Field(default="新对话", max_length=200)


class SessionUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class SessionResponse(BaseModel):
    id: str
    title: str
    createdAt: str
    updatedAt: str

    @classmethod
    def from_row(cls, session) -> "SessionResponse":
        return cls(
            id=session.id,
            title=session.title,
            createdAt=_iso(session.created_at),
            updatedAt=_iso(session.updated_at),
        )


class MessageResponse(BaseModel):
    id: str
    sessionId: str
    role: str
    content: str
    sql: str | None = None
    createdAt: str

    @classmethod
    def from_row(cls, message) -> "MessageResponse":
        return cls(
            id=message.id,
            sessionId=message.session_id,
            role=message.role,
            content=message.content,
            sql=message.sql_query,
            createdAt=_iso(message.created_at),
        )


def _iso(value: datetime | str) -> str:
    if isinstance(value, str):
        return value
    return value.isoformat()
