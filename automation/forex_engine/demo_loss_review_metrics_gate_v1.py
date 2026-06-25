"""Local-only loss-review metrics gate for AI_OS Forex demo evidence.

This module is intentionally pure and dependency-light. It evaluates caller-
provided evidence only; it never calls brokers, credentials, files, network
endpoints, schedulers, or order APIs.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any


PACKET_ID = "AIOS-FOREX-DEMO-LOSS-REVIEW-METRICS-GATE-LOCAL-APPLY-V1"
MODE = "LOCAL_APPLY"

REVIEW_READY_FOR_OWNER_APPROVAL = "REVIEW_READY_FOR_OWNER_APPROVAL"
BLOCK_NEXT_DEMO_ORDER_MISSING_METRICS = "BLOCK_NEXT_DEMO_ORDER_MISSING_METRICS"
BLOCK_NEXT_DEMO_ORDER_WEAK_LINEAGE = "BLOCK_NEXT_DEMO_ORDER_WEAK_LINEAGE"
BLOCK_NEXT_DEMO_ORDER_WEAK_RISK_GEOMETRY = "BLOCK_NEXT_DEMO_ORDER_WEAK_RISK_GEOMETRY"
BLOCK_NEXT_DEMO_ORDER_WEAK_SIGNAL = "BLOCK_NEXT_DEMO_ORDER_WEAK_SIGNAL"
BLOCK_NEXT_DEMO_ORDER_WEAK_MARKET_REGIME = (
    "BLOCK_NEXT_DEMO_ORDER_WEAK_MARKET_REGIME"
)
BLOCK_NEXT_DEMO_ORDER_LATENCY_NOT_MEASURED = (
    "BLOCK_NEXT_DEMO_ORDER_LATENCY_NOT_MEASURED"
)


DEFAULT_LIMITS: dict[str, float] = {
    "minimum_paper_sample_size": 30,
    "minimum_expectancy": 0.0,
    "minimum_profit_factor": 1.2,
    "maximum_drawdown": 500.0,
    "minimum_signal_confidence": 0.0,
    "maximum_quote_age_ms": 5000,
    "maximum_broker_round_trip_ms": 5000,
    "maximum_polling_interval_ms": 30000,
    "minimum_r_multiple": 1.0,
}

REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "trade_result": (
        "trade_id",
        "close_reason",
        "realized_pl_total",
        "pl_capture_classification",
        "open_trade_count",
        "open_position_count",
        "pending_order_count",
        "profit_claimed",
    ),
    "entry_metrics": (
        "signal_time_utc",
        "order_submit_time_utc",
        "fill_time_utc",
        "instrument",
        "direction",
        "entry_price",
        "bid",
        "ask",
        "mid",
        "quote_age_ms",
        "candle_timestamp_utc",
    ),
    "signal_metrics": (
        "strategy_name",
        "strategy_version",
        "candidate_id",
        "candidate_rank",
        "signal_confidence",
        "signal_threshold",
        "signal_passed",
        "reason_code",
    ),
    "market_regime_metrics": (
        "regime_label",
        "trend_state",
        "atr",
        "volatility_bucket",
        "session",
        "news_filter_passed",
    ),
    "spread_slippage_metrics": (
        "spread_at_signal",
        "spread_at_preview",
        "spread_at_submit",
        "spread_at_fill",
        "expected_price",
        "fill_price",
        "slippage",
        "cost_model_expected",
        "actual_cost",
    ),
    "risk_geometry_metrics": (
        "stop_distance",
        "take_profit_distance",
        "r_multiple",
        "units",
        "risk_amount",
        "risk_percent",
        "reward_amount",
        "max_spread_gate_passed",
        "max_data_age_gate_passed",
        "kill_switch_passed",
        "daily_loss_gate_passed",
        "cooldown_after_loss_passed",
        "duplicate_setup_gate_passed",
    ),
    "timing_latency_metrics": (
        "signal_to_preview_ms",
        "preview_to_risk_gate_ms",
        "risk_gate_to_approval_ms",
        "approval_to_submit_ms",
        "submit_to_fill_ms",
        "fill_to_monitor_ms",
        "monitor_to_pl_classification_ms",
        "polling_interval_ms",
        "broker_round_trip_ms",
    ),
    "paper_to_demo_lineage_metrics": (
        "paper_sample_size",
        "minimum_sample_size",
        "expectancy",
        "profit_factor",
        "max_drawdown",
        "win_rate",
        "walk_forward_passed",
        "market_regime_coverage_passed",
        "freshness_passed",
        "proof_bundle_passed",
        "promotion_verdict",
    ),
}

NUMERIC_FIELDS: dict[str, tuple[str, ...]] = {
    "trade_result": (
        "realized_pl_total",
        "open_trade_count",
        "open_position_count",
        "pending_order_count",
    ),
    "entry_metrics": ("entry_price", "bid", "ask", "mid", "quote_age_ms"),
    "signal_metrics": (
        "candidate_rank",
        "signal_confidence",
        "signal_threshold",
    ),
    "market_regime_metrics": ("atr",),
    "spread_slippage_metrics": (
        "spread_at_signal",
        "spread_at_preview",
        "spread_at_submit",
        "spread_at_fill",
        "expected_price",
        "fill_price",
        "slippage",
        "cost_model_expected",
        "actual_cost",
    ),
    "risk_geometry_metrics": (
        "stop_distance",
        "take_profit_distance",
        "r_multiple",
        "units",
        "risk_amount",
        "risk_percent",
        "reward_amount",
    ),
    "timing_latency_metrics": REQUIRED_FIELDS["timing_latency_metrics"],
    "paper_to_demo_lineage_metrics": (
        "paper_sample_size",
        "minimum_sample_size",
        "expectancy",
        "profit_factor",
        "max_drawdown",
        "win_rate",
    ),
}

BOOLEAN_FIELDS: dict[str, tuple[str, ...]] = {
    "trade_result": ("profit_claimed",),
    "signal_metrics": ("signal_passed",),
    "market_regime_metrics": ("news_filter_passed",),
    "risk_geometry_metrics": (
        "max_spread_gate_passed",
        "max_data_age_gate_passed",
        "kill_switch_passed",
        "daily_loss_gate_passed",
        "cooldown_after_loss_passed",
        "duplicate_setup_gate_passed",
    ),
    "paper_to_demo_lineage_metrics": (
        "walk_forward_passed",
        "market_regime_coverage_passed",
        "freshness_passed",
        "proof_bundle_passed",
    ),
}

LATENCY_FIELDS = REQUIRED_FIELDS["timing_latency_metrics"]


def evaluate_demo_loss_review_metrics_gate(
    evidence: dict | None = None, limits: dict | None = None
) -> dict:
    """Evaluate whether loss-review evidence is ready for owner approval.

    The return value is a deterministic dictionary. Malformed input is treated
    as missing evidence and never propagates an exception to the caller.
    """

    try:
        active_limits = _merge_limits(limits)
        if not isinstance(evidence, Mapping):
            return _result(
                allowed=False,
                decision=BLOCK_NEXT_DEMO_ORDER_MISSING_METRICS,
                blocked_reasons=[
                    "evidence must be a mapping with required loss-review sections"
                ],
                missing_metrics={
                    section: list(fields)
                    for section, fields in REQUIRED_FIELDS.items()
                },
                metrics_status=_missing_metrics_status(),
                gate_status=_gate_status(metrics_complete=False),
                latency_segments_ms={},
                summary="Next demo order blocked because loss-review evidence is missing.",
            )

        missing_metrics, metrics_status = _find_missing_metrics(evidence)
        if missing_metrics:
            return _result(
                allowed=False,
                decision=BLOCK_NEXT_DEMO_ORDER_MISSING_METRICS,
                blocked_reasons=["required loss-review metrics are missing"],
                missing_metrics=missing_metrics,
                metrics_status=metrics_status,
                gate_status=_gate_status(metrics_complete=False),
                latency_segments_ms={},
                summary="Next demo order blocked because required metrics are absent.",
            )

        invalid_metrics = _find_invalid_metrics(evidence)
        if invalid_metrics:
            status_with_invalids = {
                **metrics_status,
                "invalid_metrics": invalid_metrics,
            }
            return _result(
                allowed=False,
                decision=BLOCK_NEXT_DEMO_ORDER_MISSING_METRICS,
                blocked_reasons=["required metrics are present but malformed"],
                missing_metrics=invalid_metrics,
                metrics_status=status_with_invalids,
                gate_status=_gate_status(metrics_complete=False),
                latency_segments_ms=_latency_segments(evidence),
                summary="Next demo order blocked because required metrics are malformed.",
            )

        blocked_reasons: list[str] = []
        blocked_decisions: list[str] = []
        gate_status = _gate_status(metrics_complete=True)

        def block(decision: str, gate_key: str, reason: str) -> None:
            gate_status[gate_key] = False
            blocked_decisions.append(decision)
            blocked_reasons.append(f"{decision}: {reason}")

        trade = evidence["trade_result"]
        entry = evidence["entry_metrics"]
        signal = evidence["signal_metrics"]
        market = evidence["market_regime_metrics"]
        risk = evidence["risk_geometry_metrics"]
        timing = evidence["timing_latency_metrics"]
        lineage = evidence["paper_to_demo_lineage_metrics"]

        if (
            _number(trade["open_trade_count"]) > 0
            or _number(trade["open_position_count"]) > 0
            or _number(trade["pending_order_count"]) > 0
        ):
            block(
                BLOCK_NEXT_DEMO_ORDER_WEAK_RISK_GEOMETRY,
                "risk_geometry_passed",
                "trade result is not flat: open trades, positions, or pending orders remain",
            )

        if _boolean(trade["profit_claimed"]) and _number(trade["realized_pl_total"]) <= 0:
            block(
                BLOCK_NEXT_DEMO_ORDER_WEAK_LINEAGE,
                "lineage_passed",
                "profit was claimed while realized P/L was not positive",
            )

        required_sample_size = max(
            _number(active_limits["minimum_paper_sample_size"]),
            _number(lineage["minimum_sample_size"]),
        )
        if _number(lineage["paper_sample_size"]) < required_sample_size:
            block(
                BLOCK_NEXT_DEMO_ORDER_WEAK_LINEAGE,
                "lineage_passed",
                "paper sample size is below the required minimum",
            )

        if _number(lineage["expectancy"]) <= _number(active_limits["minimum_expectancy"]):
            block(
                BLOCK_NEXT_DEMO_ORDER_WEAK_LINEAGE,
                "lineage_passed",
                "expectancy is not above the minimum threshold",
            )

        if _number(lineage["profit_factor"]) < _number(
            active_limits["minimum_profit_factor"]
        ):
            block(
                BLOCK_NEXT_DEMO_ORDER_WEAK_LINEAGE,
                "lineage_passed",
                "profit factor is below the minimum threshold",
            )

        if _number(lineage["max_drawdown"]) > _number(active_limits["maximum_drawdown"]):
            block(
                BLOCK_NEXT_DEMO_ORDER_WEAK_LINEAGE,
                "lineage_passed",
                "maximum drawdown exceeds the allowed threshold",
            )

        for flag in (
            "walk_forward_passed",
            "market_regime_coverage_passed",
            "freshness_passed",
            "proof_bundle_passed",
        ):
            if not _boolean(lineage[flag]):
                block(
                    BLOCK_NEXT_DEMO_ORDER_WEAK_LINEAGE,
                    "lineage_passed",
                    f"{flag} is false",
                )

        if _promotion_verdict_blocks(lineage["promotion_verdict"]):
            block(
                BLOCK_NEXT_DEMO_ORDER_WEAK_LINEAGE,
                "lineage_passed",
                "promotion verdict is not owner-review ready",
            )

        if not _boolean(signal["signal_passed"]):
            block(
                BLOCK_NEXT_DEMO_ORDER_WEAK_SIGNAL,
                "signal_passed",
                "signal_passed is false",
            )

        if _number(signal["signal_confidence"]) < _number(
            active_limits["minimum_signal_confidence"]
        ):
            block(
                BLOCK_NEXT_DEMO_ORDER_WEAK_SIGNAL,
                "signal_passed",
                "signal confidence is below the minimum threshold",
            )

        if not _boolean(market["news_filter_passed"]):
            block(
                BLOCK_NEXT_DEMO_ORDER_WEAK_MARKET_REGIME,
                "market_regime_passed",
                "news filter did not pass",
            )

        for flag in (
            "max_spread_gate_passed",
            "max_data_age_gate_passed",
            "kill_switch_passed",
            "daily_loss_gate_passed",
            "cooldown_after_loss_passed",
            "duplicate_setup_gate_passed",
        ):
            if not _boolean(risk[flag]):
                block(
                    BLOCK_NEXT_DEMO_ORDER_WEAK_RISK_GEOMETRY,
                    "risk_geometry_passed",
                    f"{flag} is false",
                )

        if _number(risk["r_multiple"]) < _number(active_limits["minimum_r_multiple"]):
            block(
                BLOCK_NEXT_DEMO_ORDER_WEAK_RISK_GEOMETRY,
                "risk_geometry_passed",
                "R multiple is below the minimum threshold",
            )

        if _number(entry["quote_age_ms"]) > _number(
            active_limits["maximum_quote_age_ms"]
        ):
            block(
                BLOCK_NEXT_DEMO_ORDER_LATENCY_NOT_MEASURED,
                "latency_measured",
                "quote age exceeds the maximum allowed latency",
            )

        if _number(timing["broker_round_trip_ms"]) > _number(
            active_limits["maximum_broker_round_trip_ms"]
        ):
            block(
                BLOCK_NEXT_DEMO_ORDER_LATENCY_NOT_MEASURED,
                "latency_measured",
                "broker round trip exceeds the maximum allowed latency",
            )

        if _number(timing["polling_interval_ms"]) > _number(
            active_limits["maximum_polling_interval_ms"]
        ):
            block(
                BLOCK_NEXT_DEMO_ORDER_LATENCY_NOT_MEASURED,
                "latency_measured",
                "monitor polling interval exceeds the maximum allowed latency",
            )

        if blocked_decisions:
            decision = blocked_decisions[0]
            return _result(
                allowed=False,
                decision=decision,
                blocked_reasons=blocked_reasons,
                missing_metrics={},
                metrics_status=metrics_status,
                gate_status=gate_status,
                latency_segments_ms=_latency_segments(evidence),
                summary=(
                    "Next demo order blocked. Loss-review evidence is present, "
                    "but one or more approval gates failed."
                ),
            )

        return _result(
            allowed=True,
            decision=REVIEW_READY_FOR_OWNER_APPROVAL,
            blocked_reasons=[],
            missing_metrics={},
            metrics_status=metrics_status,
            gate_status=gate_status,
            latency_segments_ms=_latency_segments(evidence),
            summary=(
                "Loss-review evidence is complete and all local gates passed. "
                "This is owner-review readiness only and does not place or "
                "authorize a demo order by itself."
            ),
        )
    except Exception as exc:  # pragma: no cover - defensive final boundary
        return _result(
            allowed=False,
            decision=BLOCK_NEXT_DEMO_ORDER_MISSING_METRICS,
            blocked_reasons=[f"malformed evidence blocked safely: {exc}"],
            missing_metrics={"malformed_input": ["unhandled validation error"]},
            metrics_status=_missing_metrics_status(),
            gate_status=_gate_status(metrics_complete=False),
            latency_segments_ms={},
            summary="Next demo order blocked because evidence could not be evaluated safely.",
        )


def _merge_limits(limits: dict | None) -> dict[str, float]:
    active = dict(DEFAULT_LIMITS)
    if isinstance(limits, Mapping):
        for key in DEFAULT_LIMITS:
            if key in limits:
                parsed = _try_number(limits[key])
                if parsed is not None:
                    active[key] = parsed
    return active


def _find_missing_metrics(evidence: Mapping[str, Any]) -> tuple[dict, dict]:
    missing_metrics: dict[str, list[str]] = {}
    metrics_status: dict[str, dict[str, Any]] = {}

    for section, fields in REQUIRED_FIELDS.items():
        section_value = evidence.get(section)
        if not isinstance(section_value, Mapping):
            missing_metrics[section] = list(fields)
            metrics_status[section] = {
                "present": False,
                "missing_count": len(fields),
                "missing_fields": list(fields),
            }
            continue

        missing_fields = [
            field
            for field in fields
            if field not in section_value or _is_empty(section_value[field])
        ]
        if missing_fields:
            missing_metrics[section] = missing_fields
        metrics_status[section] = {
            "present": not missing_fields,
            "missing_count": len(missing_fields),
            "missing_fields": missing_fields,
        }

    return missing_metrics, metrics_status


def _find_invalid_metrics(evidence: Mapping[str, Any]) -> dict[str, list[str]]:
    invalid_metrics: dict[str, list[str]] = {}

    for section, fields in NUMERIC_FIELDS.items():
        section_value = evidence[section]
        for field in fields:
            if _try_number(section_value[field]) is None:
                invalid_metrics.setdefault(section, []).append(field)

    for section, fields in BOOLEAN_FIELDS.items():
        section_value = evidence[section]
        for field in fields:
            if _try_boolean(section_value[field]) is None:
                invalid_metrics.setdefault(section, []).append(field)

    return invalid_metrics


def _is_empty(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _try_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        parsed = float(value)
    elif isinstance(value, str):
        try:
            parsed = float(value.strip())
        except ValueError:
            return None
    else:
        return None
    return parsed if math.isfinite(parsed) else None


def _number(value: Any) -> float:
    parsed = _try_number(value)
    if parsed is None:
        raise ValueError(f"expected finite number, received {value!r}")
    return parsed


def _try_boolean(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "y", "1", "pass", "passed"}:
            return True
        if normalized in {"false", "no", "n", "0", "fail", "failed"}:
            return False
    if isinstance(value, int) and value in {0, 1}:
        return bool(value)
    return None


def _boolean(value: Any) -> bool:
    parsed = _try_boolean(value)
    if parsed is None:
        raise ValueError(f"expected boolean, received {value!r}")
    return parsed


def _promotion_verdict_blocks(value: Any) -> bool:
    text = str(value).strip().upper()
    if text in {
        "REVIEW_READY_FOR_OWNER_APPROVAL",
        "PROMOTION_GATE_PASS",
        "READY_FOR_OWNER_REVIEW",
        "PASS",
        "PASSED",
        "APPROVED_FOR_REVIEW",
    }:
        return False
    blocked_markers = ("REJECT", "BLOCK", "INSUFFICIENT", "MORE_EVIDENCE", "FAIL")
    return any(marker in text for marker in blocked_markers) or not text


def _missing_metrics_status() -> dict[str, dict[str, Any]]:
    return {
        section: {
            "present": False,
            "missing_count": len(fields),
            "missing_fields": list(fields),
        }
        for section, fields in REQUIRED_FIELDS.items()
    }


def _gate_status(metrics_complete: bool) -> dict[str, bool]:
    return {
        "metrics_complete": metrics_complete,
        "lineage_passed": metrics_complete,
        "risk_geometry_passed": metrics_complete,
        "signal_passed": metrics_complete,
        "market_regime_passed": metrics_complete,
        "latency_measured": metrics_complete,
    }


def _latency_segments(evidence: Mapping[str, Any]) -> dict[str, float]:
    timing = evidence.get("timing_latency_metrics")
    if not isinstance(timing, Mapping):
        return {}
    segments: dict[str, float] = {}
    for field in LATENCY_FIELDS:
        parsed = _try_number(timing.get(field))
        if parsed is not None:
            segments[field] = parsed
    return segments


def _safety() -> dict[str, bool]:
    return {
        "local_only": True,
        "broker_calls_allowed": False,
        "credential_access_allowed": False,
        "order_placement_allowed": False,
        "order_close_allowed": False,
        "live_endpoint_allowed": False,
        "repo_mutation_outside_allowed_files": False,
    }


def _operator_benefit() -> str:
    return (
        "Anthony/operator benefit: prevents another blind demo trade; forces "
        "proof before approval; shows what is missing; protects time and "
        "capital; separates safety failure from edge failure; makes next-order "
        "approval a yes/no review instead of guesswork."
    )


def _next_safe_action(decision: str) -> str:
    if decision == REVIEW_READY_FOR_OWNER_APPROVAL:
        return (
            "Owner may review the complete evidence bundle; this gate still does "
            "not place, approve, or submit an order."
        )
    if decision == BLOCK_NEXT_DEMO_ORDER_MISSING_METRICS:
        return "Capture every required loss-review metric before considering another demo order."
    if decision == BLOCK_NEXT_DEMO_ORDER_WEAK_LINEAGE:
        return "Rebuild paper-to-demo lineage evidence before considering another demo order."
    if decision == BLOCK_NEXT_DEMO_ORDER_WEAK_SIGNAL:
        return "Improve and revalidate signal evidence before considering another demo order."
    if decision == BLOCK_NEXT_DEMO_ORDER_WEAK_MARKET_REGIME:
        return "Revalidate market regime and news-filter evidence before considering another demo order."
    if decision == BLOCK_NEXT_DEMO_ORDER_WEAK_RISK_GEOMETRY:
        return "Repair risk geometry and safety gate evidence before considering another demo order."
    if decision == BLOCK_NEXT_DEMO_ORDER_LATENCY_NOT_MEASURED:
        return "Measure and reduce quote, broker, and monitor latency before considering another demo order."
    return "Continue read-only review before considering another demo order."


def _result(
    *,
    allowed: bool,
    decision: str,
    blocked_reasons: list[str],
    missing_metrics: dict,
    metrics_status: dict,
    gate_status: dict,
    latency_segments_ms: dict,
    summary: str,
) -> dict:
    return {
        "packet_id": PACKET_ID,
        "mode": MODE,
        "allowed": allowed,
        "decision": decision,
        "blocked_reasons": blocked_reasons,
        "operator_benefit": _operator_benefit(),
        "next_safe_action": _next_safe_action(decision),
        "metrics_status": metrics_status,
        "gate_status": gate_status,
        "safety": _safety(),
        "missing_metrics": missing_metrics,
        "latency_segments_ms": latency_segments_ms,
        "summary": summary,
    }
