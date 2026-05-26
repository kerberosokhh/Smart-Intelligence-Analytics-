from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.core.llm import get_llm

PROMPT_PATH = Path(__file__).parent / "prompts" / "chart.txt"


class ChartSpec(BaseModel):
    type: Literal["bar", "line", "pie", "scatter", "table"]
    title: str | None = None
    xField: str | None = None
    yField: str | None | list[str] = None
    seriesField: str | None = None
    data: list[dict[str, Any]] = Field(default_factory=list)


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8").strip()


def generate_chart_spec(
    question: str,
    sql: str | None,
    rows: list[dict[str, Any]],
) -> ChartSpec:
    from app.services.viz_service import normalize_chart_spec

    if not rows:
        return ChartSpec(type="table", title="查询结果", data=[])

    llm = get_llm(streaming=False)
    structured = llm.with_structured_output(ChartSpec)
    prompt = f"""{_load_prompt()}

User question: {question}
SQL: {sql or "N/A"}
Rows JSON: {rows[:20]}
"""
    try:
        spec = structured.invoke(prompt)
        if isinstance(spec, ChartSpec):
            return normalize_chart_spec(spec, rows)
        return normalize_chart_spec(ChartSpec.model_validate(spec), rows)
    except Exception:
        return normalize_chart_spec(
            ChartSpec(type="table", title="查询结果", data=rows),
            rows,
        )
