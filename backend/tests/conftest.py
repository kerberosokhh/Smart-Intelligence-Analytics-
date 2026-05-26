from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.agents.nl2sql_agent import clear_agent_cache
from app.config import get_settings
from app.core.llm import get_llm
from app.db.sqlite import reset_engine, run_migrations


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("SQLITE_PATH", str(db_path))
    get_settings.cache_clear()
    get_llm.cache_clear()
    clear_agent_cache()
    reset_engine()

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client

    reset_engine()
    get_settings.cache_clear()
    get_llm.cache_clear()
    clear_agent_cache()


@pytest.fixture
def migrated_db(tmp_path, monkeypatch):
    db_path = tmp_path / "unit.db"
    monkeypatch.setenv("SQLITE_PATH", str(db_path))
    get_settings.cache_clear()
    reset_engine()
    run_migrations()
    yield db_path
    reset_engine()
    get_settings.cache_clear()
