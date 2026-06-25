"""Local-only trade latency baseline reporter for AI_OS Forex evidence.

The reporter evaluates caller-provided timestamps only. It never uses current
time, network, broker endpoints, credentials, files, schedulers, or order APIs.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any


PACKET_ID = "AIOS-FOREX-TRADE-LATENCY-BASELINE-REPORTER-LOCAL-APPLY-V1"
MODE = "LOCAL_ONLY_TRADE_LATENCY_BASELINE"

LATENCY_READY_FOR_REVIEW = "LATENCY_READY_FOR_REVIEW"
BLOCK_LATENCY_MISSING_TIMESTAMPS = "BLOCK_LATENCY_MISSING_TIMESTAMPS"
BLOCK_LATENCY_SLOW_SEGMENT = "BLOCK_LATENCY_SLOW_SEGMENT"
BLOCK_LATENCY_INVALID_EVIDENCE = "BLOCK_LATENCY_INVALID_EVIDENCE"

TIMESTAMP_FIELDS: tuple[str, ...] = (
    "quote_received_utc",
    "signal_generated_utc",
    "preview_started_utc",
    "preview_completed_utc",
    "risk_gate_started_utc",
    "risk_gate_completed_utc",
    "owner_approval_utc",
    "order_submit_started_utc",
    "order_filled_utc",
    "monitor_started_utc",
    "pl_classified_utc",
    "audit_written_utc",
)

TRADE_CONTEXT_FIELDS: tuple[str, ...] = (
    "instrument",
    "direction",
    "strategy_name",
    "candidate_id",
    "order_fill_transaction_id",
    "pl_capture_classification",
    "profit_claimed",
)

SEGMENT_DEFINITIONS: tuple[tuple[str, str, str], ...] = (
    ("quote_to_signal_ms", "quote_received_utc", "signal_generated_utc"),
    ("signal_to_preview_ms", "signal_generated_utc", "preview_started_utc"),
    ("preview_duration_ms", "preview_started_utc", "preview_completed_utc"),
    ("preview_to_risk_gate_ms", "preview_completed_utc", "risk_gate_started_utc"),
    ("risk_gate_duration_ms", "risk_gate_started_utc", "risk_gate_completed_utc"),
    ("risk_gate_to_approval_ms", "risk_gate_completed_utc", "owner_approval_utc"),
    ("approval_to_submit_ms", "owner_approval_utc", "order_submit_started_utc"),
    ("submit_to_fill_ms", "order_submit_started_utc", "order_filled_utc"),
    ("fill_to_monitor_ms", "order_filled_utc", "monitor_started_utc"),
    (
        "monitor_to_pl_classification_ms",
        "monitor_started_utc",
        "pl_classified_utc",
    ),
    (
        "pl_classification_to_audit_ms",
        "pl_classified_utc",
        "audit_written_utc",
    ),
)

DEFAULT_LIMITS_MS: dict[str, float] = {
    "quote_to_signal_max_ms": 5000,
    "signal_to_preview_max_ms": 5000,
    "preview_duration_max_ms": 5000,
    "risk_gate_duration_max_ms": 5000,
    "approval_to_submit_max_ms": 30000,
    "submit_to_fill_max_ms": 5000,
    "fill_to_monitor_max_ms": 30000,
    "monitor_to_pl_classification_max_ms": 30000,
    "pl_classification_to_audit_max_ms": 30000,
    "total_trade_cycle_max_ms": 120000,
}

SEGMENT_LIMIT_KEYS: dict[str, str] = {
    "quote_to_signal_ms": "quote_to_signal_max_ms",
    "signal_to_preview_ms": "signal_to_preview_max_ms",
    "preview_duration_ms": "preview_duration_max_ms",
    "risk_gate_duration_ms": "risk_gate_duration_max_ms",
    "approval_to_submit_ms": "approval_to_submit_max_ms",
    "submit_to_fill_ms": "submit_to_fill_max_ms",
    "fill_to_monitor_ms": "fill_to_monitor_max_ms",
    "monitor_to_pl_classification_ms": "monitor_to_pl_classification_max_ms",
    "pl_classification_to_audit_ms": "pl_classification_to_audit_max_ms",
    "total_trade_cycle_ms": "total_trade_cycle_max_ms",
}


def evaluate_trade_latency_baseline(
    evidence: dict | None = None, limits: dict | None = None
) -> dict:
    """Evaluate local trade timing evidence for owner review readiness."""

    try:
        active_limits = _merge_limits(limits)
        if not isinstance(evidence, Mapping):
            return _result(
                allowed=False,
                decision=BLOCK_LATENCY_INVALID_EVIDENCE,
                blocked_reasons=["evidence must be a mapping"],
                missing_timestamps=list(TIMESTAMP_FIELDS),
                invalid_timestamps=[],
                latency_segments_ms={},
                slow_segments=[],
                fastest_segment=None,
                slowest_segment=None,
                total_trade_cycle_ms=None,
                latency_ready_for_review=False,
                summary="Latency review blocked because evidence is missing or malformed.",
            )

        missing_context = _missing_fields(evidence.get("trade_context"), TRADE_CONTEXT_FIELDS)
        if missing_context:
            return _result(
                allowed=False,
                decision=BLOCK_LATENCY_INVALID_EVIDENCE,
                blocked_reasons=[
                    "trade_context is missing required fields: "
                    + ", ".join(missing_context)
                ],
                missing_timestamps=[],
                invalid_timestamps=[],
                latency_segments_ms={},
                slow_segments=[],
                fastest_segment=None,
                slowest_segment=None,
                total_trade_cycle_ms=None,
                latency_ready_for_review=False,
                summary="Latency review blocked because trade context is incomplete.",
            )

        timestamps = evidence.get("timestamps")
        missing_timestamps = _missing_fields(timestamps, TIMESTAMP_FIELDS)
        if missing_timestamps:
            return _result(
                allowed=False,
                decision=BLOCK_LATENCY_MISSING_TIMESTAMPS,
                blocked_reasons=[
                    "timestamps are missing required fields: "
                    + ", ".join(missing_timestamps)
                ],
                missing_timestamps=missing_timestamps,
                invalid_timestamps=[],
                latency_segments_ms={},
                slow_segments=[],
                fastest_segment=None,
                slowest_segment=None,
                total_trade_cycle_ms=None,
                latency_ready_for_review=False,
                summary="Latency review blocked because required timestamps are missing.",
            )

        parsed_timestamps, invalid_timestamps = _parse_timestamps(timestamps)
        if invalid_timestamps:
            return _result(
                allowed=False,
                decision=BLOCK_LATENCY_INVALID_EVIDENCE,
                blocked_reasons=[
                    "timestamps are malformed or not ISO-8601 strings: "
                    + ", ".join(invalid_timestamps)
                ],
                missing_timestamps=[],
                invalid_timestamps=invalid_timestamps,
                latency_segments_ms={},
                slow_segments=[],
                fastest_segment=None,
                slowest_segment=None,
                total_trade_cycle_ms=None,
                latency_ready_for_review=False,
                summary="Latency review blocked because timestamps are invalid.",
            )

        chronological_errors = _chronological_errors(parsed_timestamps)
        if chronological_errors:
            return _result(
                allowed=False,
                decision=BLOCK_LATENCY_INVALID_EVIDENCE,
                blocked_reasons=[
                    "timestamps are out of chronological order: "
                    + ", ".join(chronological_errors)
                ],
                missing_timestamps=[],
                invalid_timestamps=chronological_errors,
                latency_segments_ms={},
                slow_segments=[],
                fastest_segment=None,
                slowest_segment=None,
                total_trade_cycle_ms=None,
                latency_ready_for_review=False,
                summary="Latency review blocked because timestamps are out of order.",
            )

        latency_segments_ms = _latency_segments(parsed_timestamps)
        total_trade_cycle_ms = latency_segments_ms["total_trade_cycle_ms"]
        slow_segments = _slow_segments(latency_segments_ms, active_limits)
        fastest_segment = _fastest_segment(latency_segments_ms)
        slowest_segment = _slowest_segment(latency_segments_ms)

        if slow_segments:
            return _result(
                allowed=False,
                decision=BLOCK_LATENCY_SLOW_SEGMENT,
                blocked_reasons=[
                    "one or more latency segments exceeded the configured limit"
                ],
                missing_timestamps=[],
                invalid_timestamps=[],
                latency_segments_ms=latency_segments_ms,
                slow_segments=slow_segments,
                fastest_segment=fastest_segment,
                slowest_segment=slowest_segment,
                total_trade_cycle_ms=total_trade_cycle_ms,
                latency_ready_for_review=False,
                summary="Latency review blocked because at least one timing segment is slow.",
            )

        return _result(
            allowed=True,
            decision=LATENCY_READY_FOR_REVIEW,
            blocked_reasons=[],
            missing_timestamps=[],
            invalid_timestamps=[],
            latency_segments_ms=latency_segments_ms,
            slow_segments=[],
            fastest_segment=fastest_segment,
            slowest_segment=slowest_segment,
            total_trade_cycle_ms=total_trade_cycle_ms,
            latency_ready_for_review=True,
            summary=(
                "Latency evidence is complete, ordered, and within configured "
                "limits. This is local review readiness only and does not "
                "approve or place a trade."
            ),
        )
    except Exception as exc:  # pragma: no cover - defensive boundary
        return _result(
            allowed=False,
            decision=BLOCK_LATENCY_INVALID_EVIDENCE,
            blocked_reasons=[f"malformed latency evidence blocked safely: {exc}"],
            missing_timestamps=[],
            invalid_timestamps=["unhandled_validation_error"],
            latency_segments_ms={},
            slow_segments=[],
            fastest_segment=None,
            slowest_segment=None,
            total_trade_cycle_ms=None,
            latency_ready_for_review=False,
            summary="Latency review blocked because evidence could not be evaluated safely.",
        )


def _missing_fields(section: Any, required_fields: tuple[str, ...]) -> list[str]:
    if not isinstance(section, Mapping):
        return list(required_fields)
    return [
        field
        for field in required_fields
        if field not in section or _is_empty(section[field])
    ]


def _is_empty(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _merge_limits(limits: dict | None) -> dict[str, float]:
    active = dict(DEFAULT_LIMITS_MS)
    if isinstance(limits, Mapping):
        for key, default_value in DEFAULT_LIMITS_MS.items():
            parsed = _to_finite_float(limits.get(key, default_value))
            if parsed is not None:
                active[key] = parsed
    return active


def _to_finite_float(value: Any) -> float | None:
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
    if parsed != parsed or parsed in (float("inf"), float("-inf")):
        return None
    return parsed


def _parse_timestamps(timestamps: Mapping[str, Any]) -> tuple[dict[str, datetime], list[str]]:
    parsed: dict[str, datetime] = {}
    invalid: list[str] = []
    for field in TIMESTAMP_FIELDS:
        value = timestamps.get(field)
        timestamp = _parse_iso_timestamp(value)
        if timestamp is None:
            invalid.append(field)
        else:
            parsed[field] = timestamp
    return parsed, invalid


def _parse_iso_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _chronological_errors(parsed_timestamps: Mapping[str, datetime]) -> list[str]:
    errors: list[str] = []
    for previous_field, next_field in zip(TIMESTAMP_FIELDS, TIMESTAMP_FIELDS[1:]):
        if parsed_timestamps[next_field] < parsed_timestamps[previous_field]:
            errors.append(f"{next_field}_before_{previous_field}")
    return errors


def _latency_segments(parsed_timestamps: Mapping[str, datetime]) -> dict[str, float]:
    segments: dict[str, float] = {}
    for segment_name, start_field, end_field in SEGMENT_DEFINITIONS:
        segments[segment_name] = _delta_ms(
            parsed_timestamps[start_field],
            parsed_timestamps[end_field],
        )
    segments["total_trade_cycle_ms"] = _delta_ms(
        parsed_timestamps["quote_received_utc"],
        parsed_timestamps["audit_written_utc"],
    )
    return segments


def _delta_ms(start: datetime, end: datetime) -> float:
    return (end - start).total_seconds() * 1000


def _slow_segments(
    latency_segments_ms: Mapping[str, float], limits: Mapping[str, float]
) -> list[dict[str, float | str]]:
    slow: list[dict[str, float | str]] = []
    for segment_name, value in latency_segments_ms.items():
        limit_key = SEGMENT_LIMIT_KEYS.get(segment_name)
        if not limit_key:
            continue
        limit = limits[limit_key]
        if value > limit:
            slow.append(
                {
                    "segment": segment_name,
                    "ms": value,
                    "limit_ms": limit,
                }
            )
    return slow


def _fastest_segment(latency_segments_ms: Mapping[str, float]) -> dict[str, float | str] | None:
    atomic_segments = {
        name: value
        for name, value in latency_segments_ms.items()
        if name != "total_trade_cycle_ms"
    }
    if not atomic_segments:
        return None
    name = min(atomic_segments, key=atomic_segments.get)
    return {"segment": name, "ms": atomic_segments[name]}


def _slowest_segment(latency_segments_ms: Mapping[str, float]) -> dict[str, float | str] | None:
    atomic_segments = {
        name: value
        for name, value in latency_segments_ms.items()
        if name != "total_trade_cycle_ms"
    }
    if not atomic_segments:
        return None
    name = max(atomic_segments, key=atomic_segments.get)
    return {"segment": name, "ms": atomic_segments[name]}


def _operator_benefit() -> str:
    return (
        "Anthony/operator benefit: shows where time is being lost; reduces "
        "guessing after a trade loss; gives one plain continue/stop answer for "
        "timing evidence; protects Anthony from approving another trade when "
        "timing evidence is missing; helps separate bad timing from bad strategy."
    )


def _next_safe_action(decision: str) -> str:
    if decision == LATENCY_READY_FOR_REVIEW:
        return (
            "Review the complete timing evidence with Anthony before any separate "
            "trade approval discussion."
        )
    if decision == BLOCK_LATENCY_MISSING_TIMESTAMPS:
        return "Capture every required timestamp before considering another trade review."
    if decision == BLOCK_LATENCY_SLOW_SEGMENT:
        return "Investigate the slow latency segment before considering another trade review."
    return "Fix the malformed local latency evidence before considering another trade review."


def _safety() -> dict[str, bool]:
    return {
        "local_only": True,
        "broker_calls_allowed": False,
        "credential_access_allowed": False,
        "order_placement_allowed": False,
        "order_close_allowed": False,
        "live_endpoint_allowed": False,
        "repo_mutation_outside_allowed_files": False,
        "uses_current_time": False,
    }


def _result(
    *,
    allowed: bool,
    decision: str,
    blocked_reasons: list[str],
    missing_timestamps: list[str],
    invalid_timestamps: list[str],
    latency_segments_ms: dict[str, float],
    slow_segments: list[dict[str, float | str]],
    fastest_segment: dict[str, float | str] | None,
    slowest_segment: dict[str, float | str] | None,
    total_trade_cycle_ms: float | None,
    latency_ready_for_review: bool,
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
        "missing_timestamps": missing_timestamps,
        "invalid_timestamps": invalid_timestamps,
        "latency_segments_ms": latency_segments_ms,
        "slow_segments": slow_segments,
        "fastest_segment": fastest_segment,
        "slowest_segment": slowest_segment,
        "total_trade_cycle_ms": total_trade_cycle_ms,
        "latency_ready_for_review": latency_ready_for_review,
        "safety": _safety(),
        "summary": summary,
    }
