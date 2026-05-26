from __future__ import annotations

import json
from unittest.mock import patch

from app.agents.chart_agent import ChartSpec
from app.agents.nl2sql_agent import NL2SQLResult


def test_chat_stream_mocked(client) -> None:
    session_id = client.post("/api/sessions", json={"title": "SSE测试"}).json()["id"]

    mock_nl2sql = NL2SQLResult(
        answer="各品类销售总额已统计完成。",
        sql="SELECT category, SUM(amount) AS total FROM biz_orders GROUP BY category",
        rows=[
            {"category": "电子产品", "total": 1000.0},
            {"category": "服装", "total": 500.0},
        ],
        messages=[],
    )
    mock_chart = ChartSpec(
        type="bar",
        title="各品类销售总额",
        xField="category",
        yField="total",
        data=mock_nl2sql.rows,
    )

    with (
        patch("app.services.query_service.run_nl2sql", return_value=mock_nl2sql),
        patch("app.services.query_service.generate_chart_spec", return_value=mock_chart),
    ):
        with client.stream(
            "POST",
            "/api/chat/stream",
            json={"session_id": session_id, "message": "各品类销售总额是多少？"},
        ) as response:
            assert response.status_code == 200
            events: list[dict] = []
            for line in response.iter_lines():
                if not line or not line.startswith("data:"):
                    continue
                events.append(json.loads(line.removeprefix("data:").strip()))

    types = [e["type"] for e in events]
    assert "sql" in types
    assert "data" in types
    assert "chart" in types
    assert "token" in types
    assert types[-1] == "done"

    messages = client.get(f"/api/sessions/{session_id}/messages").json()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["sql"]

    session = client.get("/api/sessions").json()[0]
    assert session["title"] != "SSE测试"
