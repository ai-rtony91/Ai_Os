"""Evaluate whether demo proof is sufficient for owner live micro exception review."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "AIOS_FOREX_PROOF_TO_LIVE_MICRO_GATE_V1"
MODE = "READ_ONLY_METADATA_ONLY_LIVE_MICRO_GATE"

READY_FOR_OWNER_LIVE_MICRO_EXCEPTION_REVIEW = (
    "READY_FOR_OWNER_LIVE_MICRO_EXCEPTION_REVIEW"
)
CONTINUE_DEMO_PROOF_CAPTURE = "CONTINUE_DEMO_PROOF_CAPTURE"
BLOCKED_BY_DEMO_RECEIPT_REQUIRED = "BLOCKED_BY_DEMO_RECEIPT_REQUIRED"
BLOCKED_BY_POST_TRADE_REVIEW = "BLOCKED_BY_POST_TRADE_REVIEW"
BLOCKED_BY_REPEATABILITY = "BLOCKED_BY_REPEATABILITY"
BLOCKED_BY_RISK_GATES = "BLOCKED_BY_RISK_GATES"
BLOCKED_BY_OWNER_APPROVAL = "BLOCKED_BY_OWNER_APPROVAL"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_BANKING_FOCUS = "BLOCKED_BY_BANKING_FOCUS"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = (
    "AIOS_FOREX_LIVE_MICRO_EXCEPTION_REVIEW_AFTER_DEMO_PROFIT_EVIDENCE_V1"
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


def evaluate_forex_proof_to_live_micro_gate_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = _mapping(payload)
    sensitive_blockers = _sensitive_data_blockers(source)
    if sensitive_blockers:
        return _build(
            status=BLOCKED_BY_SENSITIVE_DATA,
            proof_data_present=False,
            proof_data_sanitized=False,
            demo_receipt_review={},
            repeatability_evidence={},
            risk={},
            owner={},
            blockers=tuple(sensitive_blockers),
            live_micro_review_packet={},
            next_best_packet=NEXT_BEST_PACKET,
        )

    banking_blockers = _banking_focus_blockers(source)
    if banking_blockers:
        return _build(
            status=BLOCKED_BY_BANKING_FOCUS,
            proof_data_present=False,
            proof_data_sanitized=False,
            demo_receipt_review={},
            repeatability_evidence={},
            risk={},
            owner={},
            blockers=tuple(banking_blockers),
            live_micro_review_packet={},
            next_best_packet=NEXT_BEST_PACKET,
        )

    demo_receipt_review = _mapping(source.get("demo_receipt_review"))
    repeatability_evidence = _mapping(source.get("repeatability_evidence"))
    risk = _mapping(source.get("risk"))
    owner = _mapping(source.get("owner"))

    if not demo_receipt_review:
        return _build(
            status=BLOCKED_BY_DEMO_RECEIPT_REQUIRED,
            proof_data_present=False,
            proof_data_sanitized=False,
            demo_receipt_review={},
            repeatability_evidence=repeatability_evidence,
            risk=risk,
            owner=owner,
            blockers=("demo_receipt_review_missing",),
            live_micro_review_packet={},
            next_best_packet=NEXT_BEST_PACKET,
        )

    if not _bool(demo_receipt_review.get("demo_receipt_ready")):
        return _build(
            status=BLOCKED_BY_DEMO_RECEIPT_REQUIRED,
            proof_data_present=True,
            proof_data_sanitized=True,
            demo_receipt_review=_demo_receipt_summary(demo_receipt_review),
            repeatability_evidence=repeatability_evidence,
            risk=risk,
            owner=owner,
            blockers=("demo_receipt_ready_false",),
            live_micro_review_packet={},
            next_best_packet=NEXT_BEST_PACKET,
        )

    if not _bool(demo_receipt_review.get("post_trade_review_ready")):
        return _build(
            status=BLOCKED_BY_POST_TRADE_REVIEW,
            proof_data_present=True,
            proof_data_sanitized=True,
            demo_receipt_review=_demo_receipt_summary(demo_receipt_review),
            repeatability_evidence=repeatability_evidence,
            risk=risk,
            owner=owner,
            blockers=("post_trade_review_ready_false",),
            live_micro_review_packet={},
            next_best_packet=NEXT_BEST_PACKET,
        )

    if _int(demo_receipt_review.get("demo_order_count")) < 1:
        return _build(
            status=BLOCKED_BY_DEMO_RECEIPT_REQUIRED,
            proof_data_present=True,
            proof_data_sanitized=True,
            demo_receipt_review=_demo_receipt_summary(demo_receipt_review),
            repeatability_evidence=repeatability_evidence,
            risk=risk,
            owner=owner,
            blockers=("demo_order_count_must_be_at_least_one",),
            live_micro_review_packet={},
            next_best_packet=NEXT_BEST_PACKET,
        )

    if not repeatability_evidence:
        return _build(
            status=BLOCKED_BY_REPEATABILITY,
            proof_data_present=True,
            proof_data_sanitized=True,
            demo_receipt_review=_demo_receipt_summary(demo_receipt_review),
            repeatability_evidence={},
            risk=risk,
            owner=owner,
            blockers=("repeatability_evidence_missing",),
            live_micro_review_packet={},
            next_best_packet=NEXT_BEST_PACKET,
        )

    repeatability_summary = _repeatability_summary(repeatability_evidence)
    if repeatability_summary["repeatability_score"] < 70:
        return _build(
            status=CONTINUE_DEMO_PROOF_CAPTURE,
            proof_data_present=True,
            proof_data_sanitized=True,
            demo_receipt_review=_demo_receipt_summary(demo_receipt_review),
            repeatability_evidence=repeatability_summary,
            risk=risk,
            owner=owner,
            blockers=("repeatability_score_below_70",),
            live_micro_review_packet={},
            next_best_packet=NEXT_BEST_PACKET,
        )

    missing_repeatability = [
        key
        for key, value in repeatability_summary.items()
        if key in ("expectancy_positive", "drawdown_within_limit", "profit_factor_meets_threshold")
        and value is not True
    ]
    if missing_repeatability:
        return _build(
            status=BLOCKED_BY_REPEATABILITY,
            proof_data_present=True,
            proof_data_sanitized=True,
            demo_receipt_review=_demo_receipt_summary(demo_receipt_review),
            repeatability_evidence=repeatability_summary,
            risk=risk,
            owner=owner,
            blockers=tuple(missing_repeatability),
            live_micro_review_packet={},
            next_best_packet=NEXT_BEST_PACKET,
        )

    if not risk:
        return _build(
            status=BLOCKED_BY_RISK_GATES,
            proof_data_present=True,
            proof_data_sanitized=True,
            demo_receipt_review=_demo_receipt_summary(demo_receipt_review),
            repeatability_evidence=repeatability_summary,
            risk=risk,
            owner=owner,
            blockers=("risk_payload_missing",),
            live_micro_review_packet={},
            next_best_packet=NEXT_BEST_PACKET,
        )

    risk_summary = _risk_summary(risk)
    if not risk_summary["risk_gate_ok"]:
        return _build(
            status=BLOCKED_BY_RISK_GATES,
            proof_data_present=True,
            proof_data_sanitized=True,
            demo_receipt_review=_demo_receipt_summary(demo_receipt_review),
            repeatability_evidence=repeatability_summary,
            risk=risk_summary,
            owner=owner,
            blockers=tuple(risk_summary["blockers"]),
            live_micro_review_packet={},
            next_best_packet=NEXT_BEST_PACKET,
        )

    owner_summary = _owner_summary(owner)
    if not owner_summary["live_micro_owner_review_required"]:
        return _build(
            status=BLOCKED_BY_OWNER_APPROVAL,
            proof_data_present=True,
            proof_data_sanitized=True,
            demo_receipt_review=_demo_receipt_summary(demo_receipt_review),
            repeatability_evidence=repeatability_summary,
            risk=risk_summary,
            owner=owner_summary,
            blockers=("live_micro_owner_review_required_false",),
            live_micro_review_packet={},
            next_best_packet=NEXT_BEST_PACKET,
        )
    if owner_summary["live_execution_authorized"] or owner_summary["live_trade_executed"]:
        return _build(
            status=BLOCKED_BY_OWNER_APPROVAL,
            proof_data_present=True,
            proof_data_sanitized=True,
            demo_receipt_review=_demo_receipt_summary(demo_receipt_review),
            repeatability_evidence=repeatability_summary,
            risk=risk_summary,
            owner=owner_summary,
            blockers=("live_execution_authorized_or_live_trade_executed",),
            live_micro_review_packet={},
            next_best_packet=NEXT_BEST_PACKET,
        )

    return _build(
        status=READY_FOR_OWNER_LIVE_MICRO_EXCEPTION_REVIEW,
        proof_data_present=True,
        proof_data_sanitized=True,
        demo_receipt_review=_demo_receipt_summary(demo_receipt_review),
        repeatability_evidence=repeatability_summary,
        risk=risk_summary,
        owner=owner_summary,
        blockers=(),
        live_micro_review_packet={
            "review_only": True,
            "live_execution_authorized": False,
            "owner_review_required": True,
            "proof_sources": [
                "demo_receipt_review",
                "post_trade_review",
                "repeatability_evidence",
                "risk",
                "owner",
            ],
            "next_best_packet": NEXT_BEST_PACKET,
        },
        next_best_packet=NEXT_BEST_PACKET,
    )


def _repeatability_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "repeatability_score": _int(data.get("repeatability_score")),
        "expectancy_positive": _bool(data.get("expectancy_positive")),
        "drawdown_within_limit": _bool(data.get("drawdown_within_limit")),
        "profit_factor_meets_threshold": _bool(data.get("profit_factor_meets_threshold")),
    }


def _risk_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    max_risk_per_trade_pct = _decimal(data.get("max_risk_per_trade_pct"))
    max_daily_loss_pct = _decimal(data.get("max_daily_loss_pct"))
    kill_switch_ready = _bool(data.get("kill_switch_ready"))
    daily_loss_stop_ready = _bool(data.get("daily_loss_stop_ready"))

    blockers: list[str] = []
    if max_risk_per_trade_pct > 0.01:
        blockers.append("max_risk_per_trade_pct_above_limit")
    if max_daily_loss_pct > 0.03:
        blockers.append("max_daily_loss_pct_above_limit")
    if not kill_switch_ready:
        blockers.append("kill_switch_ready_false")
    if not daily_loss_stop_ready:
        blockers.append("daily_loss_stop_ready_false")

    return {
        "max_risk_per_trade_pct": max_risk_per_trade_pct,
        "max_daily_loss_pct": max_daily_loss_pct,
        "kill_switch_ready": kill_switch_ready,
        "daily_loss_stop_ready": daily_loss_stop_ready,
        "risk_gate_ok": not blockers,
        "blockers": blockers,
    }


def _owner_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "live_micro_owner_review_required": _bool(data.get("live_micro_owner_review_required")),
        "live_execution_authorized": _bool(data.get("live_execution_authorized")),
        "live_trade_executed": _bool(data.get("live_trade_executed")),
    }


def _demo_receipt_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "demo_receipt_ready": _bool(data.get("demo_receipt_ready")),
        "post_trade_review_ready": _bool(data.get("post_trade_review_ready")),
        "demo_order_count": _int(data.get("demo_order_count")),
    }


def _build(
    *,
    status: str,
    proof_data_present: bool,
    proof_data_sanitized: bool,
    demo_receipt_review: Mapping[str, Any],
    repeatability_evidence: Mapping[str, Any],
    risk: Mapping[str, Any],
    owner: Mapping[str, Any],
    blockers: Sequence[str],
    live_micro_review_packet: Mapping[str, Any],
    next_best_packet: str,
) -> dict[str, Any]:
    ready = status == READY_FOR_OWNER_LIVE_MICRO_EXCEPTION_REVIEW
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
        "ready_for_live_micro_review": ready,
        "demo_receipt_review": dict(demo_receipt_review),
        "repeatability_evidence": dict(repeatability_evidence),
        "risk": dict(risk),
        "owner": dict(owner),
        "proof_sources": [
            "demo_receipt_review",
            "post_trade_review",
            "repeatability_evidence",
            "risk",
            "owner",
        ],
        "live_micro_review_packet": dict(live_micro_review_packet),
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
            "ready_for_live_micro_review": ready,
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
    if status == READY_FOR_OWNER_LIVE_MICRO_EXCEPTION_REVIEW:
        return "Open the owner live micro exception review packet."
    if status == CONTINUE_DEMO_PROOF_CAPTURE:
        return "Continue demo proof capture and rerun once repeatability evidence improves."
    if status == BLOCKED_BY_DEMO_RECEIPT_REQUIRED:
        return "Produce valid demo_receipt_review payload."
    if status == BLOCKED_BY_POST_TRADE_REVIEW:
        return "Complete post-trade review proof readiness."
    if status == BLOCKED_BY_REPEATABILITY:
        return "Improve repeatability score and expectancy/drawdown/profit-factor gates."
    if status == BLOCKED_BY_RISK_GATES:
        return "Resolve risk gate blockers."
    if status == BLOCKED_BY_OWNER_APPROVAL:
        return "Ensure owner review required true and live authorization false."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys and values."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove banking/withdrawal/transfer focus keys."
    if status == INCOMPLETE_INPUTS:
        return "Provide the required four payload sections."
    return "Re-run with complete gate inputs."


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


def _decimal(value: Any) -> float:
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


def _unique(values: Sequence[str]) -> list[str]:
    return sorted(set(values))
