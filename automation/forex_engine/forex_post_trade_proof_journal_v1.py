"""Score post-trade proof readiness before repeatability scoring."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "AIOS_FOREX_POST_TRADE_PROOF_JOURNAL_V1"
MODE = "READ_ONLY_METADATA_ONLY_POST_TRADE_PROOF_JOURNAL"

POST_TRADE_PROOF_JOURNAL_READY = "POST_TRADE_PROOF_JOURNAL_READY"
BLOCKED_BY_POST_TRADE_REVIEW = "BLOCKED_BY_POST_TRADE_REVIEW"
BLOCKED_BY_RECEIPT_PROOF = "BLOCKED_BY_RECEIPT_PROOF"
BLOCKED_BY_PNL_RECORD = "BLOCKED_BY_PNL_RECORD"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_BANKING_FOCUS = "BLOCKED_BY_BANKING_FOCUS"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_PROFIT_REPEATABILITY_EVIDENCE_V1"

REQUIRED_RECEIPT_FIELDS = ("ready_for_post_trade_review", "receipt_sanitized", "demo_order_executed")
REQUIRED_POST_TRADE_FIELDS = (
    "post_trade_review_required",
    "post_trade_review_completed",
    "daily_pnl_recorded",
    "realized_pnl_present",
    "realized_pnl_is_demo",
    "spread_slippage_recorded",
    "risk_review_recorded",
    "owner_review_required",
    "no_second_trade_without_review",
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


def evaluate_forex_post_trade_proof_journal_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = _mapping(payload)
    sensitive_blockers = _sensitive_data_blockers(source)
    if sensitive_blockers:
        return _build(
            status=BLOCKED_BY_SENSITIVE_DATA,
            proof_data_present=False,
            proof_data_sanitized=False,
            receipt_proof_summary={},
            post_trade_review_summary={},
            journal_entry={},
            blockers=tuple(sensitive_blockers),
            next_best_packet=NEXT_BEST_PACKET,
        )

    banking_blockers = _banking_focus_blockers(source)
    if banking_blockers:
        return _build(
            status=BLOCKED_BY_BANKING_FOCUS,
            proof_data_present=False,
            proof_data_sanitized=False,
            receipt_proof_summary={},
            post_trade_review_summary={},
            journal_entry={},
            blockers=tuple(banking_blockers),
            next_best_packet=NEXT_BEST_PACKET,
        )

    if not source:
        return _build(
            status=INCOMPLETE_INPUTS,
            proof_data_present=False,
            proof_data_sanitized=False,
            receipt_proof_summary={},
            post_trade_review_summary={},
            journal_entry={},
            blockers=("payload_missing",),
            next_best_packet=NEXT_BEST_PACKET,
        )

    receipt_proof = _mapping(source.get("receipt_proof"))
    post_trade_review = _mapping(source.get("post_trade_review"))
    if not receipt_proof:
        return _build(
            status=BLOCKED_BY_RECEIPT_PROOF,
            proof_data_present=False,
            proof_data_sanitized=False,
            receipt_proof_summary={},
            post_trade_review_summary={},
            journal_entry={},
            blockers=("receipt_proof_missing",),
            next_best_packet=NEXT_BEST_PACKET,
        )

    missing_receipt_fields = [field for field in REQUIRED_RECEIPT_FIELDS if field not in receipt_proof]
    if missing_receipt_fields:
        return _build(
            status=BLOCKED_BY_RECEIPT_PROOF,
            proof_data_present=False,
            proof_data_sanitized=False,
            receipt_proof_summary={
                "missing_fields": tuple(missing_receipt_fields),
            },
            post_trade_review_summary={},
            journal_entry={},
            blockers=tuple(f"missing_{field}" for field in missing_receipt_fields),
            next_best_packet=NEXT_BEST_PACKET,
        )

    if not post_trade_review:
        return _build(
            status=BLOCKED_BY_POST_TRADE_REVIEW,
            proof_data_present=bool(receipt_proof.get("receipt_sanitized")),
            proof_data_sanitized=bool(receipt_proof.get("receipt_sanitized")),
            receipt_proof_summary=_receipt_summary(receipt_proof),
            post_trade_review_summary={},
            journal_entry={},
            blockers=("post_trade_review_missing",),
            next_best_packet=NEXT_BEST_PACKET,
        )

    missing_review_fields = [
        field for field in REQUIRED_POST_TRADE_FIELDS if field not in post_trade_review
    ]
    if missing_review_fields:
        return _build(
            status=BLOCKED_BY_POST_TRADE_REVIEW,
            proof_data_present=True,
            proof_data_sanitized=bool(receipt_proof.get("receipt_sanitized")),
            receipt_proof_summary=_receipt_summary(receipt_proof),
            post_trade_review_summary={
                "missing_fields": tuple(missing_review_fields),
            },
            journal_entry={},
            blockers=tuple(f"missing_{field}" for field in missing_review_fields),
            next_best_packet=NEXT_BEST_PACKET,
        )

    receipt_summary = _receipt_summary(receipt_proof)
    review_summary = _post_trade_review_summary(post_trade_review)

    if not receipt_summary["ready_for_post_trade_review"]:
        return _build(
            status=BLOCKED_BY_RECEIPT_PROOF,
            proof_data_present=True,
            proof_data_sanitized=False,
            receipt_proof_summary=receipt_summary,
            post_trade_review_summary=review_summary,
            journal_entry={},
            blockers=("receipt_not_ready_for_post_trade_review",),
            next_best_packet=NEXT_BEST_PACKET,
        )

    if not receipt_summary["demo_order_executed"]:
        return _build(
            status=BLOCKED_BY_RECEIPT_PROOF,
            proof_data_present=True,
            proof_data_sanitized=False,
            receipt_proof_summary=receipt_summary,
            post_trade_review_summary=review_summary,
            journal_entry={},
            blockers=("demo_order_executed_false",),
            next_best_packet=NEXT_BEST_PACKET,
        )

    if not review_summary["realized_pnl_present"]:
        return _build(
            status=BLOCKED_BY_PNL_RECORD,
            proof_data_present=True,
            proof_data_sanitized=receipt_summary["receipt_sanitized"],
            receipt_proof_summary=receipt_summary,
            post_trade_review_summary=review_summary,
            journal_entry={},
            blockers=("realized_pnl_present_false",),
            next_best_packet=NEXT_BEST_PACKET,
        )

    review_blockers = [
        key
        for key, value in review_summary.items()
        if key in REQUIRED_POST_TRADE_FIELDS and not value
    ]
    if review_blockers:
        return _build(
            status=BLOCKED_BY_POST_TRADE_REVIEW,
            proof_data_present=True,
            proof_data_sanitized=receipt_summary["receipt_sanitized"],
            receipt_proof_summary=receipt_summary,
            post_trade_review_summary=review_summary,
            journal_entry={},
            blockers=tuple(review_blockers),
            next_best_packet=NEXT_BEST_PACKET,
        )

    journal_entry = {
        "demo_trade_reviewed": True,
        "realized_pnl_present": review_summary["realized_pnl_present"],
        "realized_pnl_is_demo": review_summary["realized_pnl_is_demo"],
        "proof_ready_for_repeatability_scoring": True,
        "no_live_trade_authorized": True,
    }
    return _build(
        status=POST_TRADE_PROOF_JOURNAL_READY,
        proof_data_present=True,
        proof_data_sanitized=receipt_summary["receipt_sanitized"],
        receipt_proof_summary=receipt_summary,
        post_trade_review_summary=review_summary,
        journal_entry=journal_entry,
        blockers=(),
        next_best_packet=NEXT_BEST_PACKET,
    )


def _build(
    *,
    status: str,
    proof_data_present: bool,
    proof_data_sanitized: bool,
    receipt_proof_summary: Mapping[str, Any],
    post_trade_review_summary: Mapping[str, Any],
    journal_entry: Mapping[str, Any],
    blockers: Sequence[str],
    next_best_packet: str,
) -> dict[str, Any]:
    ready = status == POST_TRADE_PROOF_JOURNAL_READY
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
        "receipt_proof_summary": dict(receipt_proof_summary),
        "post_trade_review_summary": dict(post_trade_review_summary),
        "journal_entry": dict(journal_entry),
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
    if status == POST_TRADE_PROOF_JOURNAL_READY:
        return "Route journal_entry into profit repeatability scoring."
    if status == BLOCKED_BY_RECEIPT_PROOF:
        return "Provide a valid routed receipt proof with ready_for_post_trade_review true."
    if status == BLOCKED_BY_PNL_RECORD:
        return "Capture realized PnL and rerun."
    if status == BLOCKED_BY_POST_TRADE_REVIEW:
        return "Complete all post-trade review fields and rerun."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys/values and rerun."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove banking/transfer keys unless explicitly false safety fields."
    if status == INCOMPLETE_INPUTS:
        return "Provide receipt_proof and post_trade_review payload."
    return "Provide complete post-trade proof metadata."


def _receipt_summary(receipt_proof: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ready_for_post_trade_review": _bool(receipt_proof.get("ready_for_post_trade_review")),
        "receipt_sanitized": _bool(receipt_proof.get("receipt_sanitized")),
        "demo_order_executed": _bool(receipt_proof.get("demo_order_executed")),
    }


def _post_trade_review_summary(review: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "post_trade_review_required": _bool(review.get("post_trade_review_required")),
        "post_trade_review_completed": _bool(review.get("post_trade_review_completed")),
        "daily_pnl_recorded": _bool(review.get("daily_pnl_recorded")),
        "realized_pnl_present": _bool(review.get("realized_pnl_present")),
        "realized_pnl_is_demo": _bool(review.get("realized_pnl_is_demo")),
        "spread_slippage_recorded": _bool(review.get("spread_slippage_recorded")),
        "risk_review_recorded": _bool(review.get("risk_review_recorded")),
        "owner_review_required": _bool(review.get("owner_review_required")),
        "no_second_trade_without_review": _bool(review.get("no_second_trade_without_review")),
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


def _unique(values: Sequence[str]) -> list[str]:
    return sorted(set(values))
