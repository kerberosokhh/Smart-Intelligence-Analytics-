from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.schema import router as schema_router
from app.api.sessions import router as sessions_router
from app.config import get_settings
from app.db.sqlite import run_migrations


@asynccontextmanager
async def lifespan(_app: FastAPI):
    run_migrations()
    yield


settings = get_settings()

app = FastAPI(
    title="Smart Intelligence Analytics API",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions_router)
app.include_router(chat_router)
app.include_router(schema_router)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "smart-intelligence-analytics"}
