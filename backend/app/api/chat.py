from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.schemas.chat import ChatStreamRequest
from app.services.query_service import stream_query

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/stream")
async def chat_stream(payload: ChatStreamRequest) -> EventSourceResponse:
    async def event_generator():
        async for event in _stream_events(payload.session_id, payload.message):
            yield {
                "event": event["type"],
                "data": json.dumps(event, ensure_ascii=False),
            }

    return EventSourceResponse(event_generator())


async def _stream_events(session_id: str, message: str):
    async for event in stream_query(session_id, message):
        yield event
