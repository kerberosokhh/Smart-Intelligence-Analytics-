import pytest

from app.config import get_settings
from app.core.llm import get_llm
from app.db.sqlite import execute_readonly_query, validate_select_only


def test_validate_select_only_rejects_dml() -> None:
    with pytest.raises(ValueError, match="仅允许 SELECT"):
        validate_select_only("DELETE FROM biz_orders")


def test_readonly_query_on_demo_data(client) -> None:
    rows = execute_readonly_query(
        "SELECT category, SUM(amount) AS total FROM biz_orders GROUP BY category ORDER BY total DESC"
    )
    assert len(rows) >= 4
    assert "category" in rows[0]
    assert "total" in rows[0]


@pytest.mark.integration
def test_nl2sql_agent_integration(client) -> None:
    settings = get_settings()
    if not settings.deepseek_api_key:
        pytest.skip("DEEPSEEK_API_KEY 未配置")

    from app.agents.nl2sql_agent import run_nl2sql

    result = run_nl2sql("各品类的销售总额是多少？按总额降序。")
    assert result.answer
    assert result.sql
    assert "SELECT" in result.sql.upper()
    assert len(result.rows) >= 1
