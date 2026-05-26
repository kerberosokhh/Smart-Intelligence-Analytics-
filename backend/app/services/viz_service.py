from __future__ import annotations

from typing import Any

from app.agents.chart_agent import ChartSpec


def normalize_chart_spec(spec: ChartSpec, rows: list[dict[str, Any]]) -> ChartSpec:
    data = rows if rows else spec.data
    if not data:
        return ChartSpec(type="table", title=spec.title or "查询结果", data=[])

    keys = set(data[0].keys())
    chart_type = spec.type

    if chart_type != "table":
        x_ok = spec.xField in keys if spec.xField else False
        y_field = spec.yField
        if isinstance(y_field, list):
            y_ok = any(f in keys for f in y_field)
        else:
            y_ok = y_field in keys if y_field else False
        if not x_ok or not y_ok or len(data) < 2:
            chart_type = "table"

    if chart_type == "pie" and len(data) > 12:
        chart_type = "bar"

    return ChartSpec(
        type=chart_type,
        title=spec.title or "查询结果",
        xField=spec.xField if chart_type != "table" else None,
        yField=spec.yField if chart_type != "table" else None,
        seriesField=spec.seriesField if chart_type != "table" else None,
        data=data,
    )
