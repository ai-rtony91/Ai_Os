"""Compute repeatability score for demo profit evidence."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "AIOS_FOREX_PROFIT_REPEATABILITY_EVIDENCE_V1"
MODE = "READ_ONLY_METADATA_ONLY_PROFIT_REPEATABILITY_EVIDENCE"

REPEATABILITY_EVIDENCE_READY_FOR_REVIEW = "REPEATABILITY_EVIDENCE_READY_FOR_REVIEW"
CONTINUE_DEMO_PROOF_CAPTURE = "CONTINUE_DEMO_PROOF_CAPTURE"
BLOCKED_BY_INSUFFICIENT_SAMPLE = "BLOCKED_BY_INSUFFICIENT_SAMPLE"
BLOCKED_BY_NEGATIVE_EXPECTANCY = "BLOCKED_BY_NEGATIVE_EXPECTANCY"
BLOCKED_BY_DRAWDOWN = "BLOCKED_BY_DRAWDOWN"
BLOCKED_BY_UNREALISTIC_RETURN_CLAIM = "BLOCKED_BY_UNREALISTIC_RETURN_CLAIM"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_BANKING_FOCUS = "BLOCKED_BY_BANKING_FOCUS"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_PROOF_TO_LIVE_MICRO_GATE_V1"

REQUIRED_FIELDS = (
    "sample_count",
    "min_sample_count",
    "expectancy_positive",
    "profit_factor",
    "min_profit_factor",
    "max_drawdown_pct",
    "max_allowed_drawdown_pct",
    "walk_forward_gate_cleared",
    "out_of_sample_passed",
    "daily_review_count",
    "weekly_review_count",
    "monthly_review_count",
    "yearly_review_ready",
    "guaranteed_profit_claimed",
    "fixed_return_promised",
)

HARD_FALSE_FIELDS = (
    "live_trade_executed",
    "live_execution_authorized",
    "demo_trade_executed_by_this_module",
    "broker_api_called",
    "credential_read",
    "credential_stored",
    "api_key_stored",
    "master_password_used",
    "vault_password_used",
    "money_moved",
    "bank_access_used",
    "scheduler_created",
    "daemon_created",
    "webhook_created",
    "dashboard_runtime_created",
    "banking_work_built",
    "withdrawal_work_built",
    "transfer_work_built",
)

SENSITIVE_KEY_PARTS = (
    "api_key",
    "token_value",
    "password",
    "master_password",
    "vault_password",
    "account_number",
    "routing_number",
    "card_number",
    "debit_card_number",
    "cvv",
    "account_id",
    "oanda_account_id",
    "bearer",
    "broker_token",
    "access_token",
    "private_key",
)

SENSITIVE_VALUE_MARKERS = (
    "sk-",
    "bearer",
    "api key",
    "token value",
    "broker token",
    "access token",
    "private key",
    "password",
    "secret",
    "-----begin",
)

BANKING_KEY_PARTS = (
    "bank",
    "banking",
    "withdraw",
    "withdrawal",
    "transfer",
    "debit",
    "card",
    "rail",
    "ach",
    "wire",
    "sweep",
    "bucket_purge",
    "money_movement",
    "deposit",
)

BANKING_ALLOWED_FALSE_FIELDS = frozenset(
    {
        "money_moved",
        "money_movement_allowed",
        "bank_access_used",
        "banking_work_built",
        "withdrawal_work_built",
        "transfer_work_built",
    }
)


def evaluate_forex_profit_repeatability_evidence_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = _mapping(payload)
    sensitive_blockers = _sensitive_data_blockers(source)
    if sensitive_blockers:
        return _build(
            status=BLOCKED_BY_SENSITIVE_DATA,
            proof_data_present=False,
            proof_data_sanitized=False,
            evidence_summary={},
            blockers=tuple(sensitive_blockers),
            next_best_packet=NEXT_BEST_PACKET,
        )

    banking_blockers = _banking_focus_blockers(source)
    if banking_blockers:
        return _build(
            status=BLOCKED_BY_BANKING_FOCUS,
            proof_data_present=False,
            proof_data_sanitized=False,
            evidence_summary={},
            blockers=tuple(banking_blockers),
            next_best_packet=NEXT_BEST_PACKET,
        )

    evidence = _mapping(source.get("evidence"))
    if not evidence:
        return _build(
            status=INCOMPLETE_INPUTS,
            proof_data_present=False,
            proof_data_sanitized=False,
            evidence_summary={},
            blockers=("evidence_missing",),
            next_best_packet=NEXT_BEST_PACKET,
        )

    missing_fields = [field for field in REQUIRED_FIELDS if field not in evidence]
    if missing_fields:
        return _build(
            status=INCOMPLETE_INPUTS,
            proof_data_present=False,
            proof_data_sanitized=False,
            evidence_summary={"missing_fields": tuple(missing_fields)},
            blockers=tuple(f"missing_{field}" for field in missing_fields),
            next_best_packet=NEXT_BEST_PACKET,
        )

    summary = _evidence_summary(evidence)
    if summary["sample_count"] <= 0:
        return _build(
            status=BLOCKED_BY_INSUFFICIENT_SAMPLE,
            proof_data_present=False,
            proof_data_sanitized=True,
            evidence_summary=summary,
            blockers=("sample_count_zero",),
            next_best_packet=NEXT_BEST_PACKET,
        )

    if summary["sample_count"] < summary["min_sample_count"]:
        return _build(
            status=CONTINUE_DEMO_PROOF_CAPTURE,
            proof_data_present=True,
            proof_data_sanitized=True,
            evidence_summary=summary,
            blockers=("sample_count_below_minimum",),
            next_best_packet=NEXT_BEST_PACKET,
        )

    if summary["guaranteed_profit_claimed"] or summary["fixed_return_promised"]:
        return _build(
            status=BLOCKED_BY_UNREALISTIC_RETURN_CLAIM,
            proof_data_present=True,
            proof_data_sanitized=True,
            evidence_summary=summary,
            blockers=("unrealistic_return_claim",),
            next_best_packet=NEXT_BEST_PACKET,
        )

    if not summary["expectancy_positive"]:
        return _build(
            status=BLOCKED_BY_NEGATIVE_EXPECTANCY,
            proof_data_present=True,
            proof_data_sanitized=True,
            evidence_summary=summary,
            blockers=("expectancy_positive_false",),
            next_best_packet=NEXT_BEST_PACKET,
        )

    if not summary["walk_forward_gate_cleared"] or not summary["out_of_sample_passed"]:
        return _build(
            status=CONTINUE_DEMO_PROOF_CAPTURE,
            proof_data_present=True,
            proof_data_sanitized=True,
            evidence_summary=summary,
            blockers=("walk_forward_or_out_of_sample_false",),
            next_best_packet=NEXT_BEST_PACKET,
        )

    if summary["max_drawdown_pct"] > summary["max_allowed_drawdown_pct"]:
        return _build(
            status=BLOCKED_BY_DRAWDOWN,
            proof_data_present=True,
            proof_data_sanitized=True,
            evidence_summary=summary,
            blockers=("max_drawdown_exceeds_limit",),
            next_best_packet=NEXT_BEST_PACKET,
        )

    if summary["repeatability_score"] < 70:
        return _build(
            status=CONTINUE_DEMO_PROOF_CAPTURE,
            proof_data_present=True,
            proof_data_sanitized=True,
            evidence_summary=summary,
            blockers=("repeatability_score_below_70",),
            next_best_packet=NEXT_BEST_PACKET,
        )

    return _build(
        status=REPEATABILITY_EVIDENCE_READY_FOR_REVIEW,
        proof_data_present=True,
        proof_data_sanitized=True,
        evidence_summary=summary,
        blockers=(),
        next_best_packet=NEXT_BEST_PACKET,
    )


def _build(
    *,
    status: str,
    proof_data_present: bool,
    proof_data_sanitized: bool,
    evidence_summary: Mapping[str, Any],
    blockers: Sequence[str],
    next_best_packet: str,
) -> dict[str, Any]:
    ready = status == REPEATABILITY_EVIDENCE_READY_FOR_REVIEW
    repeatability_score = int(evidence_summary.get("repeatability_score", 0))
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "ready": ready,
        "owner_decision_required": True,
        "read_only": True,
        "metadata_only": True,
        "proof_data_present": bool(proof_data_present),
        "proof_data_sanitized": bool(proof_data_sanitized),
        "repeatability_score": repeatability_score,
        "daily_ready": bool(evidence_summary.get("daily_ready", False)),
        "weekly_ready": bool(evidence_summary.get("weekly_ready", False)),
        "monthly_ready": bool(evidence_summary.get("monthly_ready", False)),
        "yearly_ready": bool(evidence_summary.get("yearly_ready", False)),
        "ready_for_live_micro_review": ready and repeatability_score >= 70,
        "evidence_summary": dict(evidence_summary),
        "blockers": list(blockers),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": _safe_manual_next_action(status),
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "status": status,
            "ready": ready,
            "proof_data_present": bool(proof_data_present),
            "proof_data_sanitized": bool(proof_data_sanitized),
            "repeatability_score": repeatability_score,
            "ready_for_live_micro_review": ready and repeatability_score >= 70,
            "blockers": list(blockers),
            "next_best_packet": next_best_packet,
        },
        "safety": {
            "read_only": True,
            "metadata_only": True,
            "owner_decision_required": True,
            **{field: False for field in HARD_FALSE_FIELDS},
        },
        **{field: False for field in HARD_FALSE_FIELDS},
    }


def _safe_manual_next_action(status: str) -> str:
    if status == REPEATABILITY_EVIDENCE_READY_FOR_REVIEW:
        return "Route evidence into the live micro review gate."
    if status == CONTINUE_DEMO_PROOF_CAPTURE:
        return "Collect more qualifying evidence and rerun."
    if status == BLOCKED_BY_INSUFFICIENT_SAMPLE:
        return "Increase sample_count to at least minimum."
    if status == BLOCKED_BY_NEGATIVE_EXPECTANCY:
        return "Improve expectancy before continuing."
    if status == BLOCKED_BY_DRAWDOWN:
        return "Reduce drawdown to within policy."
    if status == BLOCKED_BY_UNREALISTIC_RETURN_CLAIM:
        return "Remove guaranteed or fixed-return claims."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys/values and rerun."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove banking and transfer keys unless explicitly false safety fields."
    return "Provide complete evidence payload."


def _evidence_summary(evidence: Mapping[str, Any]) -> dict[str, Any]:
    sample_count = _number(evidence.get("sample_count"))
    min_sample_count = max(_number(evidence.get("min_sample_count")), 1)
    expectancy_positive = _bool(evidence.get("expectancy_positive"))
    walk_forward_gate_cleared = _bool(evidence.get("walk_forward_gate_cleared"))
    out_of_sample_passed = _bool(evidence.get("out_of_sample_passed"))
    guaranteed_profit_claimed = _bool(evidence.get("guaranteed_profit_claimed"))
    fixed_return_promised = _bool(evidence.get("fixed_return_promised"))

    profit_factor = _number(evidence.get("profit_factor"))
    min_profit_factor = _number(evidence.get("min_profit_factor"))
    max_drawdown_pct = _number(evidence.get("max_drawdown_pct"))
    max_allowed_drawdown_pct = _number(evidence.get("max_allowed_drawdown_pct"))
    daily_review_count = _int(evidence.get("daily_review_count"))
    weekly_review_count = _int(evidence.get("weekly_review_count"))
    monthly_review_count = _int(evidence.get("monthly_review_count"))
    yearly_review_ready = _bool(evidence.get("yearly_review_ready"))

    profit_factor_meets_threshold = profit_factor >= min_profit_factor if min_profit_factor > 0 else False

    score = 0
    score += min(sample_count / min_sample_count, 1.0) * 30
    if expectancy_positive:
        score += 25
    if walk_forward_gate_cleared and out_of_sample_passed:
        score += 15
    if profit_factor_meets_threshold:
        score += 15
    if max_drawdown_pct <= max_allowed_drawdown_pct:
        score += 10
    if (
        daily_review_count >= 1
        and weekly_review_count >= 1
        and monthly_review_count >= 1
        and yearly_review_ready
    ):
        score += 20
    repeatability_score = int(min(max(round(score), 0), 100))

    return {
        "sample_count": sample_count,
        "min_sample_count": min_sample_count,
        "expectancy_positive": expectancy_positive,
        "profit_factor": profit_factor,
        "min_profit_factor": min_profit_factor,
        "max_drawdown_pct": max_drawdown_pct,
        "max_allowed_drawdown_pct": max_allowed_drawdown_pct,
        "walk_forward_gate_cleared": walk_forward_gate_cleared,
        "out_of_sample_passed": out_of_sample_passed,
        "daily_review_count": daily_review_count,
        "weekly_review_count": weekly_review_count,
        "monthly_review_count": monthly_review_count,
        "yearly_review_ready": yearly_review_ready,
        "guaranteed_profit_claimed": guaranteed_profit_claimed,
        "fixed_return_promised": fixed_return_promised,
        "repeatability_score": repeatability_score,
        "drawdown_within_limit": max_drawdown_pct <= max_allowed_drawdown_pct,
        "profit_factor_meets_threshold": profit_factor_meets_threshold,
        "daily_ready": daily_review_count >= 1,
        "weekly_ready": weekly_review_count >= 1,
        "monthly_ready": monthly_review_count >= 1,
        "yearly_ready": yearly_review_ready,
    }


def _sensitive_data_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key_text = str(raw_key)
            key_path = f"{path}.{raw_key}"
            if _sensitive_key_blocked(key_text):
                blockers.append(f"{key_path}:sensitive_key")
                continue
            blockers.extend(_sensitive_data_blockers(child, key_path))
        return tuple(_unique(blockers))

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_sensitive_data_blockers(child, f"{path}[{index}]"))
        return tuple(_unique(blockers))

    if isinstance(value, str) and _has_secret_value(value):
        blockers.append(f"{path}:secret_like_value")
    elif isinstance(value, int) and not isinstance(value, bool) and _has_long_digit_run(
        str(value)
    ):
        blockers.append(f"{path}:long_digit_run")
    return tuple(_unique(blockers))


def _banking_focus_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key_text = str(raw_key).lower().replace("-", "_")
            key_path = f"{path}.{raw_key}"
            if key_text in BANKING_ALLOWED_FALSE_FIELDS and child is False:
                continue
            if any(part in key_text for part in BANKING_KEY_PARTS):
                blockers.append(f"{key_path}:banking_focus")
                continue
            blockers.extend(_banking_focus_blockers(child, key_path))
        return tuple(_unique(blockers))

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_banking_focus_blockers(child, f"{path}[{index}]"))
        return tuple(_unique(blockers))
    return tuple(_unique(blockers))


def _sensitive_key_blocked(key_text: str) -> bool:
    normalized = str(key_text).lower().replace("-", "_")
    if normalized.endswith("_redacted"):
        return False
    return any(part in normalized for part in SENSITIVE_KEY_PARTS)


def _has_secret_value(value: str) -> bool:
    lowered = value.strip().lower()
    return any(marker in lowered for marker in SENSITIVE_VALUE_MARKERS) or _has_long_digit_run(
        lowered
    )


def _has_long_digit_run(text: str, minimum: int = 8) -> bool:
    run = 0
    for char in text:
        if char.isdigit():
            run += 1
            if run >= minimum:
                return True
        else:
            run = 0
    return False


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _number(value: Any) -> float:
    if isinstance(value, bool) or value is None:
        return 0.0
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def _int(value: Any) -> int:
    if isinstance(value, bool) or value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return 0
    return 0


def _unique(values: Sequence[str]) -> list[str]:
    return sorted(set(values))
