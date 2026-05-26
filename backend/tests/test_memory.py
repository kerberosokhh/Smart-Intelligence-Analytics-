from app.core.memory import build_chat_history, load_session_messages, save_message
from app.db.sqlite import db_session
from app.core.session import create_session
from langchain_core.messages import AIMessage, HumanMessage


def test_memory_load_save_and_history(migrated_db) -> None:
    with db_session() as db:
        session = create_session(db, title="记忆测试")
        save_message(db, session_id=session.id, role="user", content="第一轮问题")
        save_message(db, session_id=session.id, role="assistant", content="第一轮回答")
        save_message(db, session_id=session.id, role="user", content="第二轮问题")

        rows = load_session_messages(db, session.id, limit=10)
        assert len(rows) == 3
        history = build_chat_history(rows)
        assert len(history) == 3
        assert isinstance(history[0], HumanMessage)
        assert isinstance(history[1], AIMessage)
        assert history[2].content == "第二轮问题"
