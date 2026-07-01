"""Sanitized evidence contract for a live micro attempt receipt."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "AIOS_FOREX_LIVE_RECEIPT_EVIDENCE_INTAKE_CONTRACT_V1"
MODE = "READ_ONLY_METADATA_ONLY_LIVE_RECEIPT_EVIDENCE_CONTRACT"

LIVE_RECEIPT_EVIDENCE_CONTRACT_READY = "LIVE_RECEIPT_EVIDENCE_CONTRACT_READY"
LIVE_RECEIPT_EVIDENCE_COMPLETE = "LIVE_RECEIPT_EVIDENCE_COMPLETE"
BLOCKED_BY_MISSING_BROKER_RECEIPT = "BLOCKED_BY_MISSING_BROKER_RECEIPT"
BLOCKED_BY_MISSING_EXIT_RECEIPT = "BLOCKED_BY_MISSING_EXIT_RECEIPT"
BLOCKED_BY_MISSING_REALIZED_PNL = "BLOCKED_BY_MISSING_REALIZED_PNL"
BLOCKED_BY_MISSING_COST_RECONCILIATION = "BLOCKED_BY_MISSING_COST_RECONCILIATION"
BLOCKED_BY_MISSING_POST_TRADE_REVIEW = "BLOCKED_BY_MISSING_POST_TRADE_REVIEW"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_RAW_PAYLOAD = "BLOCKED_BY_RAW_PAYLOAD"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

REQUIRED_EVIDENCE_FIELDS = (
    "attempt_id_redacted",
    "broker_receipt_present",
    "entry_timestamp_utc",
    "instrument",
    "side",
    "units_or_size_redacted",
    "entry_price_present",
    "stop_loss_present",
    "take_profit_or_exit_plan_present",
    "exit_receipt_present",
    "exit_timestamp_utc",
    "exit_price_present",
    "realized_pnl_present",
    "realized_pnl_value",
    "pnl_currency",
    "spread_cost_recorded",
    "fee_cost_recorded",
    "slippage_recorded",
    "net_pnl_after_costs",
    "post_trade_review_complete",
    "rule_followed_classified",
    "mistake_classified",
    "repeat_attempt_allowed",
    "account_id_absent",
    "order_id_absent_or_redacted",
    "transaction_id_absent_or_redacted",
    "credentials_absent",
    "raw_payload_absent",
    "screenshot_private_data_absent",
)

REDACTION_TRUE_FIELDS = (
    "attempt_id_redacted",
    "units_or_size_redacted",
    "account_id_absent",
    "order_id_absent_or_redacted",
    "transaction_id_absent_or_redacted",
    "credentials_absent",
    "raw_payload_absent",
    "screenshot_private_data_absent",
)

FORBIDDEN_FIELDS = (
    "account_id",
    "api_key",
    "token",
    "password",
    "secret",
    "credential",
    "raw_payload",
    "raw_broker_payload",
    "order_id",
    "transaction_id",
    "bank_account",
)

HARD_FALSE_FIELDS = (
    "live_trade_executed_by_this_module",
    "demo_trade_executed_by_this_module",
    "broker_api_called_by_this_module",
    "credential_read",
    "credential_stored",
    "account_id_read",
    "account_id_stored",
    "order_placed",
    "order_closed",
    "money_moved",
    "bank_access_used",
    "withdrawal_initiated",
    "scheduler_created",
    "daemon_created",
    "webhook_created",
    "profit_guaranteed",
)

SENSITIVE_VALUE_MARKERS = (
    "sk-",
    "bearer",
    "api key",
    "token",
    "password",
    "secret",
    "private key",
    "raw broker payload",
)


def evaluate_forex_live_receipt_evidence_intake_contract_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = _mapping(payload)
    raw_blockers = _raw_payload_blockers(source)
    if raw_blockers:
        return _build(status=BLOCKED_BY_RAW_PAYLOAD, blockers=raw_blockers, evidence={})

    sensitive_blockers = _sensitive_data_blockers(source)
    if sensitive_blockers:
        return _build(
            status=BLOCKED_BY_SENSITIVE_DATA,
            blockers=sensitive_blockers,
            evidence={},
        )

    if not source:
        return _build(status=INCOMPLETE_INPUTS, blockers=("payload_missing",), evidence={})

    if source.get("contract_only") is True:
        contract_blockers = _contract_only_blockers(source)
        return _build(
            status=(
                LIVE_RECEIPT_EVIDENCE_CONTRACT_READY
                if not contract_blockers
                else BLOCKED_BY_SENSITIVE_DATA
            ),
            blockers=contract_blockers,
            evidence=source,
        )

    missing_fields = [field for field in REQUIRED_EVIDENCE_FIELDS if field not in source]
    if missing_fields:
        return _build(
            status=INCOMPLETE_INPUTS,
            blockers=tuple(f"{field}_missing" for field in missing_fields),
            evidence=source,
        )

    redaction_blockers = _redaction_blockers(source)
    if redaction_blockers:
        return _build(
            status=BLOCKED_BY_SENSITIVE_DATA,
            blockers=redaction_blockers,
            evidence=source,
        )

    if source.get("broker_receipt_present") is not True:
        return _build(
            status=BLOCKED_BY_MISSING_BROKER_RECEIPT,
            blockers=("broker_receipt_present_must_be_true",),
            evidence=source,
        )

    if source.get("exit_receipt_present") is not True:
        return _build(
            status=BLOCKED_BY_MISSING_EXIT_RECEIPT,
            blockers=("exit_receipt_present_must_be_true",),
            evidence=source,
        )

    pnl_blockers = _realized_pnl_blockers(source)
    if pnl_blockers:
        return _build(
            status=BLOCKED_BY_MISSING_REALIZED_PNL,
            blockers=pnl_blockers,
            evidence=source,
        )

    cost_blockers = _cost_blockers(source)
    if cost_blockers:
        return _build(
            status=BLOCKED_BY_MISSING_COST_RECONCILIATION,
            blockers=cost_blockers,
            evidence=source,
        )

    review_blockers = _post_trade_review_blockers(source)
    if review_blockers:
        return _build(
            status=BLOCKED_BY_MISSING_POST_TRADE_REVIEW,
            blockers=review_blockers,
            evidence=source,
        )

    return _build(status=LIVE_RECEIPT_EVIDENCE_COMPLETE, blockers=(), evidence=source)


def _build(
    *,
    status: str,
    blockers: Sequence[str],
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    hard_false = {field: False for field in HARD_FALSE_FIELDS}
    ready = status in {
        LIVE_RECEIPT_EVIDENCE_CONTRACT_READY,
        LIVE_RECEIPT_EVIDENCE_COMPLETE,
    }
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "ready": ready,
        "required_fields": list(REQUIRED_EVIDENCE_FIELDS),
        "forbidden_fields": list(FORBIDDEN_FIELDS),
        "redaction_rules": {
            "identifiers": "absent_or_redacted",
            "credentials": "absent",
            "raw_payloads": "absent",
            "screenshots": "private_data_absent",
            "repeat_attempt_allowed": False,
        },
        "acceptance_statuses": [
            LIVE_RECEIPT_EVIDENCE_CONTRACT_READY,
            LIVE_RECEIPT_EVIDENCE_COMPLETE,
        ],
        "rejection_statuses": [
            BLOCKED_BY_MISSING_BROKER_RECEIPT,
            BLOCKED_BY_MISSING_EXIT_RECEIPT,
            BLOCKED_BY_MISSING_REALIZED_PNL,
            BLOCKED_BY_MISSING_COST_RECONCILIATION,
            BLOCKED_BY_MISSING_POST_TRADE_REVIEW,
            BLOCKED_BY_SENSITIVE_DATA,
            BLOCKED_BY_RAW_PAYLOAD,
            INCOMPLETE_INPUTS,
        ],
        "exact_blockers": list(blockers),
        "evidence_summary": _safe_evidence_summary(evidence),
        "safety": {
            "read_only": True,
            "metadata_only": True,
            "evidence_contract_only": status == LIVE_RECEIPT_EVIDENCE_CONTRACT_READY,
            **hard_false,
        },
        "hard_false_fields": dict(hard_false),
        **hard_false,
    }


def _contract_only_blockers(source: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if source.get("contract_acknowledged") is not True:
        blockers.append("contract_acknowledged_must_be_true")
    if source.get("sanitized_evidence_only") is not True:
        blockers.append("sanitized_evidence_only_must_be_true")
    if source.get("repeat_attempt_allowed") is not False:
        blockers.append("repeat_attempt_allowed_must_be_false")
    for field in REDACTION_TRUE_FIELDS[2:]:
        if source.get(field) is not True:
            blockers.append(f"{field}_must_be_true")
    return tuple(_unique(blockers))


def _redaction_blockers(source: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in REDACTION_TRUE_FIELDS:
        if source.get(field) is not True:
            blockers.append(f"{field}_must_be_true")
    if source.get("repeat_attempt_allowed") is not False:
        blockers.append("repeat_attempt_allowed_must_be_false")
    return tuple(_unique(blockers))


def _realized_pnl_blockers(source: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if source.get("realized_pnl_present") is not True:
        blockers.append("realized_pnl_present_must_be_true")
    if source.get("realized_pnl_value") is None:
        blockers.append("realized_pnl_value_missing")
    if not source.get("pnl_currency"):
        blockers.append("pnl_currency_missing")
    return tuple(_unique(blockers))


def _cost_blockers(source: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in (
        "spread_cost_recorded",
        "fee_cost_recorded",
        "slippage_recorded",
    ):
        if source.get(field) is not True:
            blockers.append(f"{field}_must_be_true")
    if source.get("net_pnl_after_costs") is None:
        blockers.append("net_pnl_after_costs_missing")
    return tuple(_unique(blockers))


def _post_trade_review_blockers(source: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in (
        "post_trade_review_complete",
        "rule_followed_classified",
        "mistake_classified",
    ):
        if source.get(field) is not True:
            blockers.append(f"{field}_must_be_true")
    if source.get("repeat_attempt_allowed") is not False:
        blockers.append("repeat_attempt_allowed_must_be_false")
    return tuple(_unique(blockers))


def _safe_evidence_summary(evidence: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker_receipt_present": evidence.get("broker_receipt_present") is True,
        "exit_receipt_present": evidence.get("exit_receipt_present") is True,
        "realized_pnl_present": evidence.get("realized_pnl_present") is True,
        "cost_reconciliation_present": all(
            evidence.get(field) is True
            for field in (
                "spread_cost_recorded",
                "fee_cost_recorded",
                "slippage_recorded",
            )
        )
        and evidence.get("net_pnl_after_costs") is not None,
        "post_trade_review_complete": evidence.get("post_trade_review_complete") is True,
        "sensitive_data_absent": all(
            evidence.get(field) is True
            for field in (
                "account_id_absent",
                "order_id_absent_or_redacted",
                "transaction_id_absent_or_redacted",
                "credentials_absent",
                "raw_payload_absent",
                "screenshot_private_data_absent",
            )
        ),
    }


def _raw_payload_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            normalized = _normalized_key(raw_key)
            key_path = f"{path}.{raw_key}"
            if normalized in {"raw_payload", "raw_broker_payload"}:
                blockers.append(f"{key_path}:raw_payload_forbidden")
                continue
            blockers.extend(_raw_payload_blockers(child, key_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_raw_payload_blockers(child, f"{path}[{index}]"))
    return tuple(_unique(blockers))


def _sensitive_data_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key_path = f"{path}.{raw_key}"
            if _sensitive_key_blocked(raw_key):
                blockers.append(f"{key_path}:sensitive_key")
                continue
            blockers.extend(_sensitive_data_blockers(child, key_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_sensitive_data_blockers(child, f"{path}[{index}]"))
    elif isinstance(value, str) and _has_sensitive_value(value):
        blockers.append(f"{path}:sensitive_value")
    return tuple(_unique(blockers))


def _sensitive_key_blocked(key: Any) -> bool:
    normalized = _normalized_key(key)
    if normalized.startswith("no_"):
        return False
    if normalized.endswith("_absent") or normalized.endswith("_absent_or_redacted"):
        return False
    if normalized.endswith("_redacted"):
        return False
    return normalized in FORBIDDEN_FIELDS or any(
        normalized == field for field in FORBIDDEN_FIELDS
    )


def _has_sensitive_value(value: str) -> bool:
    lowered = value.strip().lower()
    return any(marker in lowered for marker in SENSITIVE_VALUE_MARKERS)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _normalized_key(value: Any) -> str:
    return str(value).lower().replace("-", "_").replace(" ", "_")


def _unique(values: Sequence[str]) -> list[str]:
    return sorted(set(values))
