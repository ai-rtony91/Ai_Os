"""Deterministic paper execution quality metrics."""

from __future__ import annotations


def build_execution_quality_metrics(
    execution_records: list[dict[str, object]] | None = None,
    rejected_order_count: int = 0,
    risk_block_count: int = 0,
) -> dict[str, object]:
    records = execution_records or []
    paper_slippages = [float(record.get("paper_slippage", 0.0)) for record in records]
    average_paper_slippage = _safe_divide(sum(paper_slippages), len(paper_slippages))
    fill_latencies = [int(record.get("fill_latency_ms", 0)) for record in records]

    return {
        "paper_slippage": paper_slippages,
        "expected_fill_price": _last_value(records, "expected_fill_price", 0.0),
        "actual_paper_fill_price": _last_value(records, "actual_paper_fill_price", 0.0),
        "spread_estimate": _last_value(records, "spread_estimate", 0.0),
        "fill_latency_ms": _last_value(records, "fill_latency_ms", 0),
        "rejected_order_count": rejected_order_count,
        "risk_block_count": risk_block_count,
        "average_paper_slippage": average_paper_slippage,
        "execution_quality_score": _execution_quality_score(
            average_paper_slippage,
            rejected_order_count,
            risk_block_count,
            fill_latencies,
        ),
    }


def _safe_divide(numerator: float, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _last_value(
    records: list[dict[str, object]],
    key: str,
    default: float | int,
) -> object:
    if not records:
        return default
    return records[-1].get(key, default)


def _execution_quality_score(
    average_paper_slippage: float,
    rejected_order_count: int,
    risk_block_count: int,
    fill_latencies: list[int],
) -> float:
    latency_penalty = _safe_divide(sum(fill_latencies), len(fill_latencies)) / 1000.0
    score = 100.0
    score -= abs(average_paper_slippage)
    score -= rejected_order_count * 5.0
    score -= risk_block_count * 1.0
    score -= latency_penalty
    return max(0.0, min(100.0, score))
