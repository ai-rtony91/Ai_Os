"""Classify metadata readiness for the Forex proof-data intake stage."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "AIOS_FOREX_PROOF_DATA_INTAKE_V1"
MODE = "READ_ONLY_METADATA_ONLY_PROOF_DATA_INTAKE"

PROOF_DATA_READY_FOR_ROUTING = "PROOF_DATA_READY_FOR_ROUTING"
PROOF_DATA_WAITING_FOR_DEMO_RECEIPT = "PROOF_DATA_WAITING_FOR_DEMO_RECEIPT"
BLOCKED_BY_UNSANITIZED_PROOF_DATA = "BLOCKED_BY_UNSANITIZED_PROOF_DATA"
BLOCKED_BY_FAKE_PROOF_CLAIM = "BLOCKED_BY_FAKE_PROOF_CLAIM"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_BANKING_FOCUS = "BLOCKED_BY_BANKING_FOCUS"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_DEMO_RECEIPT_PROOF_ROUTER_V1"

ALLOWED_SOURCE_TYPES = frozenset(
    {
        "OWNER_APPROVED_DEMO_READINESS",
        "OANDA_DEMO_RECEIPT",
        "SANITIZED_RUNTIME_RECEIPT",
    }
)

REQUIRED_SOURCE_FIELDS = (
    "source_type",
    "upstream_packet_id",
    "receipt_present",
    "demo_order_executed",
    "live_trade_executed",
    "money_moved",
    "receipt_sanitized",
    "raw_broker_payload_present",
    "account_id_redacted",
    "order_id_redacted",
    "credential_values_redacted",
    "profit_claimed",
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


def evaluate_forex_proof_data_intake_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = _mapping(payload)
    sensitive_blockers = _sensitive_data_blockers(source)
    if sensitive_blockers:
        return _build(
            status=BLOCKED_BY_SENSITIVE_DATA,
            proof_data_present=False,
            proof_data_sanitized=False,
            proof_source_summary={},
            blockers=tuple(sensitive_blockers),
            next_best_packet=NEXT_BEST_PACKET,
        )

    banking_blockers = _banking_focus_blockers(source)
    if banking_blockers:
        return _build(
            status=BLOCKED_BY_BANKING_FOCUS,
            proof_data_present=False,
            proof_data_sanitized=False,
            proof_source_summary={},
            blockers=tuple(banking_blockers),
            next_best_packet=NEXT_BEST_PACKET,
        )

    proof_source = _mapping(source.get("proof_source"))
    if not proof_source:
        return _build(
            status=INCOMPLETE_INPUTS,
            proof_data_present=False,
            proof_data_sanitized=False,
            proof_source_summary={},
            blockers=("proof_source_missing",),
            next_best_packet=NEXT_BEST_PACKET,
        )

    missing_fields = [field for field in REQUIRED_SOURCE_FIELDS if field not in proof_source]
    if missing_fields:
        return _build(
            status=INCOMPLETE_INPUTS,
            proof_data_present=False,
            proof_data_sanitized=False,
            proof_source_summary={"missing_fields": tuple(missing_fields)},
            blockers=tuple(f"missing_{field}" for field in missing_fields),
            next_best_packet=NEXT_BEST_PACKET,
        )

    status = _intake_status(proof_source)
    summary = _proof_source_summary(proof_source)
    return _build(
        status=status,
        proof_data_present=summary["receipt_present"],
        proof_data_sanitized=summary["receipt_sanitized"],
        proof_source_summary=summary,
        blockers=_status_blockers(status, summary),
        next_best_packet=NEXT_BEST_PACKET,
    )


def _intake_status(source: Mapping[str, Any]) -> str:
    source_type = _text(source.get("source_type"))
    receipt_present = _bool(source.get("receipt_present"))
    receipt_sanitized = _bool(source.get("receipt_sanitized"))
    demo_order_executed = _bool(source.get("demo_order_executed"))
    profit_claimed = _bool(source.get("profit_claimed"))
    live_trade_executed = _bool(source.get("live_trade_executed"))
    money_moved = _bool(source.get("money_moved"))
    raw_broker_payload_present = _bool(source.get("raw_broker_payload_present"))
    account_id_redacted = _bool(source.get("account_id_redacted"))
    order_id_redacted = _bool(source.get("order_id_redacted"))
    credential_values_redacted = _bool(source.get("credential_values_redacted"))

    if source_type not in ALLOWED_SOURCE_TYPES:
        return BLOCKED_BY_UNSANITIZED_PROOF_DATA
    if live_trade_executed or money_moved or raw_broker_payload_present:
        return BLOCKED_BY_UNSANITIZED_PROOF_DATA
    if not demo_order_executed:
        return BLOCKED_BY_UNSANITIZED_PROOF_DATA
    if not account_id_redacted or not order_id_redacted or not credential_values_redacted:
        return BLOCKED_BY_UNSANITIZED_PROOF_DATA
    if source_type == "OWNER_APPROVED_DEMO_READINESS" and not receipt_present:
        return PROOF_DATA_WAITING_FOR_DEMO_RECEIPT
    if profit_claimed and not receipt_present:
        return BLOCKED_BY_FAKE_PROOF_CLAIM
    if not receipt_present:
        return BLOCKED_BY_UNSANITIZED_PROOF_DATA
    if not receipt_sanitized:
        return BLOCKED_BY_UNSANITIZED_PROOF_DATA
    return PROOF_DATA_READY_FOR_ROUTING


def _status_blockers(status: str, summary: Mapping[str, Any]) -> tuple[str, ...]:
    if status == PROOF_DATA_READY_FOR_ROUTING:
        return ()
    if status == PROOF_DATA_WAITING_FOR_DEMO_RECEIPT:
        return ("receipt_not_present_yet",)
    if status == BLOCKED_BY_FAKE_PROOF_CLAIM:
        return ("profit_claimed_without_receipt",)
    if status == BLOCKED_BY_UNSANITIZED_PROOF_DATA:
        return ("demo_receipt_unsanitized_or_boundary_violation",)
    if status == INCOMPLETE_INPUTS:
        return ("incomplete_inputs",)
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return ("sensitive_data_detected",)
    if status == BLOCKED_BY_BANKING_FOCUS:
        return ("banking_focus_detected",)
    return ("proof_data_not_acceptable",)


def _build(
    *,
    status: str,
    proof_data_present: bool,
    proof_data_sanitized: bool,
    proof_source_summary: Mapping[str, Any],
    blockers: Sequence[str],
    next_best_packet: str,
) -> dict[str, Any]:
    ready = status == PROOF_DATA_READY_FOR_ROUTING
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
        "proof_source_summary": dict(proof_source_summary),
        "blockers": list(blockers),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": _safe_manual_next_action(status),
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "status": status,
            "ready": ready,
            "owner_decision_required": True,
            "proof_data_present": bool(proof_data_present),
            "proof_data_sanitized": bool(proof_data_sanitized),
            "proof_source_summary": dict(proof_source_summary),
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
    if status == PROOF_DATA_READY_FOR_ROUTING:
        return "Route proof_source into the demo receipt proof router."
    if status == PROOF_DATA_WAITING_FOR_DEMO_RECEIPT:
        return "Collect a real OANDA demo receipt before routing."
    if status == BLOCKED_BY_FAKE_PROOF_CLAIM:
        return "Remove claimed proof values until a real receipt exists."
    if status in {BLOCKED_BY_UNSANITIZED_PROOF_DATA, INCOMPLETE_INPUTS}:
        return "Re-run with complete redacted proof_source metadata."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove banking/transfer keys unless they are explicitly false safety fields."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys and values."
    return "Correct proof_source fields and rerun."


def _proof_source_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_type": _text(source.get("source_type")),
        "upstream_packet_id": _text(source.get("upstream_packet_id")),
        "receipt_present": _bool(source.get("receipt_present")),
        "demo_order_executed": _bool(source.get("demo_order_executed")),
        "live_trade_executed": _bool(source.get("live_trade_executed")),
        "money_moved": _bool(source.get("money_moved")),
        "receipt_sanitized": _bool(source.get("receipt_sanitized")),
        "raw_broker_payload_present": _bool(source.get("raw_broker_payload_present")),
        "account_id_redacted": _bool(source.get("account_id_redacted")),
        "order_id_redacted": _bool(source.get("order_id_redacted")),
        "credential_values_redacted": _bool(source.get("credential_values_redacted")),
        "profit_claimed": _bool(source.get("profit_claimed")),
    }


def _sensitive_data_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key_text = str(raw_key)
            child_path = f"{path}.{raw_key}"
            if _sensitive_key_blocked(key_text):
                blockers.append(f"{child_path}:sensitive_key")
                continue
            blockers.extend(_sensitive_data_blockers(child, child_path))
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
            child_path = f"{path}.{raw_key}"
            if key_text in BANKING_ALLOWED_FALSE_FIELDS and child is False:
                continue
            if any(part in key_text for part in BANKING_KEY_PARTS):
                blockers.append(f"{child_path}:banking_focus")
                continue
            blockers.extend(_banking_focus_blockers(child, child_path))
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


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _unique(values: Sequence[str]) -> list[str]:
    return sorted(set(values))
