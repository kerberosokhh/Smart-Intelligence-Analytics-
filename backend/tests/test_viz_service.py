from app.agents.chart_agent import ChartSpec
from app.services.viz_service import normalize_chart_spec


def test_viz_fallback_to_table_when_fields_missing() -> None:
    rows = [{"a": 1}, {"a": 2}]
    spec = ChartSpec(type="bar", xField="missing", yField="also_missing", data=rows)
    normalized = normalize_chart_spec(spec, rows)
    assert normalized.type == "table"
    assert normalized.data == rows


def test_viz_keeps_valid_bar_chart() -> None:
    rows = [{"category": "A", "total": 10}, {"category": "B", "total": 20}]
    spec = ChartSpec(type="bar", xField="category", yField="total", data=rows)
    normalized = normalize_chart_spec(spec, rows)
    assert normalized.type == "bar"
    assert normalized.xField == "category"
