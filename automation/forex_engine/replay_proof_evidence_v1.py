"""Deterministic replay proof evidence adapter for AIOS Forex.

This module evaluates caller-provided replay summary dictionaries only. It does
not run replay engines, read broker files, read credentials, call network
services, or create trading authority.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


REPLAY_PROOF_EVIDENCE_VERSION = "replay_proof_evidence_v1"

REPLAY_PROOF_READY = "REPLAY_PROOF_READY"
REPLAY_PROOF_BLOCKED = "REPLAY_PROOF_BLOCKED"
REPLAY_PROOF_INCOMPLETE = "REPLAY_PROOF_INCOMPLETE"

PROTECTED_PERMISSION_FLAGS = {
    "broker_execution_allowed": False,
    "live_trading_allowed": False,
    "order_submission_allowed": False,
    "credential_access_allowed": False,
    "account_access_allowed": False,
    "dashboard_execution_authority": False,
    "owner_approval_created": False,
}

REQUIRED_REPLAY_FIELDS = (
    "replay_id",
    "run_count",
    "event_count",
    "mismatch_count",
    "deterministic_replay",
    "sanitized",
    "evidence_age_days",
    "max_evidence_age_days",
)

SECRET_OR_ACCOUNT_FIELD_FRAGMENTS = (
    "api_key",
    "access_token",
    "refresh_token",
    "authorization",
    "bearer",
    "password",
    "secret",
    "credential",
    "account_id",
    "accountid",
    "account_number",
    "account_reference",
    "broker_order_id",
    "raw_order_id",
    "raw_transaction_id",
    "raw_payload",
    "order_payload",
)

UNSAFE_TRUE_FIELDS = (
    "broker_execution_allowed",
    "live_trading_allowed",
    "order_submission_allowed",
    "credential_access_allowed",
    "account_access_allowed",
    "dashboard_execution_authority",
    "owner_approval_created",
    "execution_allowed",
    "trade_allowed",
    "broker_access_allowed",
    "money_movement_allowed",
    "vacation_mode_execution_allowed",
)


def build_sample_replay_summary() -> dict[str, Any]:
    return {
        "replay_id": "replay-proof-sample-001",
        "run_count": 3,
        "event_count": 144,
        "mismatch_count": 0,
        "deterministic_replay": True,
        "sanitized": True,
        "evidence_age_days": 1,
        "max_evidence_age_days": 7,
    }


def evaluate_replay_proof_evidence(
    replay_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate a deterministic replay summary for review-only evidence."""

    if replay_summary is None:
        return _result(
            status=REPLAY_PROOF_INCOMPLETE,
            blockers=["replay summary is required"],
            missing_fields=list(REQUIRED_REPLAY_FIELDS),
            metrics={},
            next_safe_action="Provide a sanitized deterministic replay summary.",
        )

    if not isinstance(replay_summary, Mapping):
        return _result(
            status=REPLAY_PROOF_INCOMPLETE,
            blockers=["replay summary must be a dictionary"],
            missing_fields=list(REQUIRED_REPLAY_FIELDS),
            metrics={},
            next_safe_action="Provide replay proof evidence as a dictionary.",
        )

    summary = dict(replay_summary)
    safety_blockers = _unsafe_fragments(summary, "replay_summary")
    missing_fields = _missing_fields(summary, REQUIRED_REPLAY_FIELDS)
    if missing_fields:
        return _result(
            status=REPLAY_PROOF_INCOMPLETE,
            blockers=safety_blockers + [f"missing field: {name}" for name in missing_fields],
            missing_fields=missing_fields,
            metrics={},
            next_safe_action="Provide all required replay proof fields and rerun locally.",
        )

    run_count = _decimal(summary.get("run_count"))
    event_count = _decimal(summary.get("event_count"))
    mismatch_count = _decimal(summary.get("mismatch_count"))
    evidence_age = _decimal(summary.get("evidence_age_days"))
    max_age = _decimal(summary.get("max_evidence_age_days"))

    numeric_errors = [
        name
        for name, value in (
            ("run_count", run_count),
            ("event_count", event_count),
            ("mismatch_count", mismatch_count),
            ("evidence_age_days", evidence_age),
            ("max_evidence_age_days", max_age),
        )
        if value is None
    ]
    if numeric_errors:
        return _result(
            status=REPLAY_PROOF_INCOMPLETE,
            blockers=safety_blockers + [f"field must be numeric: {name}" for name in numeric_errors],
            missing_fields=[],
            metrics={},
            next_safe_action="Repair numeric replay proof fields and rerun locally.",
        )

    blockers = list(safety_blockers)
    if not _text(summary.get("replay_id")):
        blockers.append("replay_id must be non-empty")
    if run_count <= 0:
        blockers.append("run_count must be positive")
    if event_count <= 0:
        blockers.append("event_count must be positive")
    if mismatch_count < 0:
        blockers.append("mismatch_count cannot be negative")
    if mismatch_count > 0:
        blockers.append("replay mismatches are present")
    if summary.get("deterministic_replay") is not True:
        blockers.append("replay is not marked deterministic")
    if summary.get("sanitized") is not True:
        blockers.append("replay summary is not marked sanitized")
    if max_age < 0:
        blockers.append("max_evidence_age_days cannot be negative")
    if evidence_age < 0:
        blockers.append("evidence_age_days cannot be negative")
    if max_age >= 0 and evidence_age > max_age:
        blockers.append("replay evidence is stale")

    metrics = {
        "replay_id": _text(summary.get("replay_id")),
        "run_count": int(run_count),
        "event_count": int(event_count),
        "mismatch_count": int(mismatch_count),
        "deterministic_replay": summary.get("deterministic_replay") is True,
        "sanitized": summary.get("sanitized") is True,
        "freshness": {
            "evidence_age_days": _float(evidence_age),
            "max_evidence_age_days": _float(max_age),
            "fresh": max_age >= 0 and evidence_age <= max_age,
        },
    }
    status = REPLAY_PROOF_BLOCKED if blockers else REPLAY_PROOF_READY
    next_safe_action = (
        "Continue to walk-forward/OOS evidence; replay proof creates no trading approval."
        if status == REPLAY_PROOF_READY
        else "Repair replay proof blockers before relying on this evidence."
    )
    return _result(
        status=status,
        blockers=_dedupe(blockers),
        missing_fields=[],
        metrics=metrics,
        next_safe_action=next_safe_action,
    )


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return dict(result)


def result_to_operator_text(result: Mapping[str, Any]) -> str:
    status = str(result.get("replay_proof_status", result.get("status", REPLAY_PROOF_INCOMPLETE)))
    if status == REPLAY_PROOF_READY:
        metrics = result.get("metrics") or {}
        return (
            "Replay proof evidence is ready for review only. "
            f"Replay {metrics.get('replay_id')} has {metrics.get('event_count')} events "
            "and No trading approval was created."
        )
    blockers = result.get("blockers") or ["replay proof evidence incomplete"]
    return "Replay proof evidence blocked: " + "; ".join(str(item) for item in blockers)


def _result(
    *,
    status: str,
    blockers: list[str],
    missing_fields: list[str],
    metrics: Mapping[str, Any],
    next_safe_action: str,
) -> dict[str, Any]:
    return {
        "engine_version": REPLAY_PROOF_EVIDENCE_VERSION,
        "status": status,
        "replay_proof_status": status,
        "metrics": dict(metrics),
        "blockers": list(blockers),
        "missing_fields": list(missing_fields),
        "next_safe_action": next_safe_action,
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


def _missing_fields(payload: Mapping[str, Any], required: tuple[str, ...]) -> list[str]:
    return [name for name in required if name not in payload]


def _unsafe_fragments(value: Any, prefix: str) -> list[str]:
    fragments: list[str] = []
    _scan_payload(value, prefix, fragments)
    return fragments


def _scan_payload(value: Any, path: str, fragments: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            lowered = key_text.lower()
            if lowered in UNSAFE_TRUE_FIELDS:
                if _truthy(item):
                    fragments.append(f"{path}.{key_text} is unsafe true")
                continue
            if any(fragment in lowered for fragment in SECRET_OR_ACCOUNT_FIELD_FRAGMENTS):
                fragments.append(f"{path}.{key_text} contains secret-like or account-like data")
            _scan_payload(item, f"{path}.{key_text}", fragments)
    elif isinstance(value, (list, tuple, set)):
        for index, item in enumerate(value):
            _scan_payload(item, f"{path}[{index}]", fragments)
    elif isinstance(value, str):
        lowered = value.lower()
        if any(fragment in lowered for fragment in SECRET_OR_ACCOUNT_FIELD_FRAGMENTS):
            fragments.append(f"{path} contains secret-like or account-like text")


def _decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError):
        return None


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return False


def _text(value: Any) -> str:
    if value is None:
        return ""
    return value.strip() if isinstance(value, str) else str(value).strip()


def _float(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.000001")))


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


__all__ = [
    "PROTECTED_PERMISSION_FLAGS",
    "REPLAY_PROOF_BLOCKED",
    "REPLAY_PROOF_EVIDENCE_VERSION",
    "REPLAY_PROOF_INCOMPLETE",
    "REPLAY_PROOF_READY",
    "build_sample_replay_summary",
    "evaluate_replay_proof_evidence",
    "result_to_jsonable_dict",
    "result_to_operator_text",
]
