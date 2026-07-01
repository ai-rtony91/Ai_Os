"""Route sanitized OANDA demo receipt metadata into post-trade proof processing."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "AIOS_FOREX_DEMO_RECEIPT_PROOF_ROUTER_V1"
MODE = "READ_ONLY_METADATA_ONLY_DEMO_RECEIPT_PROOF_ROUTER"

DEMO_RECEIPT_PROOF_ROUTED = "DEMO_RECEIPT_PROOF_ROUTED"
PROOF_DATA_WAITING_FOR_DEMO_RECEIPT = "PROOF_DATA_WAITING_FOR_DEMO_RECEIPT"
BLOCKED_BY_RECEIPT_MISSING = "BLOCKED_BY_RECEIPT_MISSING"
BLOCKED_BY_RECEIPT_UNSANITIZED = "BLOCKED_BY_RECEIPT_UNSANITIZED"
BLOCKED_BY_ORDER_COUNT = "BLOCKED_BY_ORDER_COUNT"
BLOCKED_BY_OANDA_DEMO_BOUNDARY = "BLOCKED_BY_OANDA_DEMO_BOUNDARY"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_BANKING_FOCUS = "BLOCKED_BY_BANKING_FOCUS"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_POST_TRADE_PROOF_JOURNAL_V1"

ALLOWED_DEMO_MODES = frozenset({"DEMO", "PRACTICE", "OANDA_DEMO"})
REQUIRED_RECEIPT_FIELDS = (
    "receipt_present",
    "broker_name",
    "mode",
    "demo_order_executed",
    "live_trade_executed",
    "money_moved",
    "order_count",
    "instrument",
    "side",
    "units",
    "order_id_redacted",
    "account_id_redacted",
    "credential_values_redacted",
    "stop_loss_present",
    "take_profit_present",
    "execution_timestamp_present",
    "receipt_sanitized",
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


def evaluate_forex_demo_receipt_proof_router_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = _mapping(payload)
    sensitive_blockers = _sensitive_data_blockers(source)
    if sensitive_blockers:
        return _build(
            status=BLOCKED_BY_SENSITIVE_DATA,
            proof_data_present=False,
            proof_data_sanitized=False,
            receipt_summary={},
            routed_proof_packet={},
            blockers=tuple(sensitive_blockers),
            next_best_packet=NEXT_BEST_PACKET,
        )

    banking_blockers = _banking_focus_blockers(source)
    if banking_blockers:
        return _build(
            status=BLOCKED_BY_BANKING_FOCUS,
            proof_data_present=False,
            proof_data_sanitized=False,
            receipt_summary={},
            routed_proof_packet={},
            blockers=tuple(banking_blockers),
            next_best_packet=NEXT_BEST_PACKET,
        )

    receipt = _mapping(source.get("receipt"))
    if not receipt:
        return _build(
            status=INCOMPLETE_INPUTS,
            proof_data_present=False,
            proof_data_sanitized=False,
            receipt_summary={},
            routed_proof_packet={},
            blockers=("receipt_payload_missing",),
            next_best_packet=NEXT_BEST_PACKET,
        )

    missing_fields = [field for field in REQUIRED_RECEIPT_FIELDS if field not in receipt]
    if missing_fields:
        return _build(
            status=INCOMPLETE_INPUTS,
            proof_data_present=False,
            proof_data_sanitized=False,
            receipt_summary={
                "missing_fields": tuple(missing_fields),
            },
            routed_proof_packet={},
            blockers=tuple(f"missing_{field}" for field in missing_fields),
            next_best_packet=NEXT_BEST_PACKET,
        )

    status = _receipt_status(receipt)
    summary = _receipt_summary(receipt)
    routed = {}
    blockers = _status_blockers(status)

    if status == DEMO_RECEIPT_PROOF_ROUTED:
        routed = {
            "instrument": _text(receipt.get("instrument")),
            "side": _text(receipt.get("side")),
            "units": receipt.get("units"),
            "demo_order_executed": True,
            "order_count": _int(receipt.get("order_count")),
            "stop_loss_present": _bool(receipt.get("stop_loss_present")),
            "take_profit_present": _bool(receipt.get("take_profit_present")),
            "receipt_sanitized": True,
            "ready_for_post_trade_review": True,
        }

    return _build(
        status=status,
        proof_data_present=summary["receipt_present"],
        proof_data_sanitized=summary["receipt_sanitized"],
        receipt_summary=summary,
        routed_proof_packet=routed,
        blockers=tuple(blockers),
        next_best_packet=NEXT_BEST_PACKET,
    )


def _receipt_status(receipt: Mapping[str, Any]) -> str:
    if not _bool(receipt.get("receipt_present")):
        return PROOF_DATA_WAITING_FOR_DEMO_RECEIPT
    if not _bool(receipt.get("receipt_sanitized")):
        return BLOCKED_BY_RECEIPT_UNSANITIZED
    if not _bool(receipt.get("demo_order_executed")):
        return BLOCKED_BY_RECEIPT_UNSANITIZED
    if _bool(receipt.get("live_trade_executed")):
        return BLOCKED_BY_RECEIPT_UNSANITIZED
    if _bool(receipt.get("money_moved")):
        return BLOCKED_BY_RECEIPT_UNSANITIZED
    if not _bool(receipt.get("order_id_redacted")):
        return BLOCKED_BY_RECEIPT_UNSANITIZED
    if not _bool(receipt.get("account_id_redacted")):
        return BLOCKED_BY_RECEIPT_UNSANITIZED
    if not _bool(receipt.get("credential_values_redacted")):
        return BLOCKED_BY_RECEIPT_UNSANITIZED
    if _text(receipt.get("broker_name")) != "OANDA":
        return BLOCKED_BY_OANDA_DEMO_BOUNDARY
    if _text(receipt.get("mode")) not in ALLOWED_DEMO_MODES:
        return BLOCKED_BY_OANDA_DEMO_BOUNDARY
    if _int(receipt.get("order_count")) != 1:
        return BLOCKED_BY_ORDER_COUNT
    if not _bool(receipt.get("stop_loss_present")):
        return BLOCKED_BY_RECEIPT_UNSANITIZED
    if not _bool(receipt.get("take_profit_present")):
        return BLOCKED_BY_RECEIPT_UNSANITIZED
    if not _bool(receipt.get("execution_timestamp_present")):
        return BLOCKED_BY_RECEIPT_UNSANITIZED
    return DEMO_RECEIPT_PROOF_ROUTED


def _status_blockers(status: str) -> tuple[str, ...]:
    if status == DEMO_RECEIPT_PROOF_ROUTED:
        return ()
    if status == PROOF_DATA_WAITING_FOR_DEMO_RECEIPT:
        return ("receipt_not_present",)
    if status == BLOCKED_BY_RECEIPT_MISSING:
        return ("receipt_payload_missing",)
    if status == BLOCKED_BY_RECEIPT_UNSANITIZED:
        return ("receipt_not_sanitized_or_not_demo_only",)
    if status == BLOCKED_BY_ORDER_COUNT:
        return ("order_count_must_be_one",)
    if status == BLOCKED_BY_OANDA_DEMO_BOUNDARY:
        return ("broker_or_mode_not_oanda_demo",)
    if status == INCOMPLETE_INPUTS:
        return ("incomplete_inputs",)
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return ("sensitive_data_detected",)
    if status == BLOCKED_BY_BANKING_FOCUS:
        return ("banking_focus_detected",)
    return ("receipt_router_blocked",)


def _build(
    *,
    status: str,
    proof_data_present: bool,
    proof_data_sanitized: bool,
    receipt_summary: Mapping[str, Any],
    routed_proof_packet: Mapping[str, Any],
    blockers: Sequence[str],
    next_best_packet: str,
) -> dict[str, Any]:
    ready = status == DEMO_RECEIPT_PROOF_ROUTED
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
        "receipt_summary": dict(receipt_summary),
        "routed_proof_packet": dict(routed_proof_packet),
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
            "receipt_summary": dict(receipt_summary),
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
    if status == DEMO_RECEIPT_PROOF_ROUTED:
        return "Route the sanitized receipt packet to post-trade proof journal."
    if status == PROOF_DATA_WAITING_FOR_DEMO_RECEIPT:
        return "Collect a sanitized OANDA demo receipt first."
    if status == BLOCKED_BY_RECEIPT_UNSANITIZED:
        return "Only redacted and sanitized demo receipts are accepted."
    if status == BLOCKED_BY_ORDER_COUNT:
        return "Use exactly one OANDA demo order for this intake."
    if status == BLOCKED_BY_OANDA_DEMO_BOUNDARY:
        return "Use OANDA broker and demo/practice mode."
    if status == BLOCKED_BY_RECEIPT_MISSING:
        return "Provide the receipt payload."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys and secret-like values."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove banking/transfer-related keys unless explicitly false safety fields."
    if status == INCOMPLETE_INPUTS:
        return "Provide complete receipt metadata for all required fields."
    return "Provide complete, sanitized demo receipt metadata."


def _receipt_summary(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "receipt_present": _bool(receipt.get("receipt_present")),
        "broker_name": _text(receipt.get("broker_name")),
        "mode": _text(receipt.get("mode")),
        "demo_order_executed": _bool(receipt.get("demo_order_executed")),
        "live_trade_executed": _bool(receipt.get("live_trade_executed")),
        "money_moved": _bool(receipt.get("money_moved")),
        "order_count": _int(receipt.get("order_count")),
        "instrument": _text(receipt.get("instrument")),
        "side": _text(receipt.get("side")),
        "units": _number(receipt.get("units")),
        "order_id_redacted": _bool(receipt.get("order_id_redacted")),
        "account_id_redacted": _bool(receipt.get("account_id_redacted")),
        "credential_values_redacted": _bool(receipt.get("credential_values_redacted")),
        "stop_loss_present": _bool(receipt.get("stop_loss_present")),
        "take_profit_present": _bool(receipt.get("take_profit_present")),
        "execution_timestamp_present": _bool(
            receipt.get("execution_timestamp_present")
        ),
        "receipt_sanitized": _bool(receipt.get("receipt_sanitized")),
        "route_to_post_trade_review": _bool(receipt.get("receipt_present")),
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


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _number(value: Any) -> int | float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int | float):
        return value
    if isinstance(value, str):
        try:
            text = value.strip()
            if "." in text:
                return float(text)
            return int(text)
        except ValueError:
            return None
    return None


def _unique(values: Sequence[str]) -> list[str]:
    return sorted(set(values))
