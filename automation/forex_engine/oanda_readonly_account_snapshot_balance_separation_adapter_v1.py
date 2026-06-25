from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.broker_balance_bucket_equity_separation_v1 import (
    BROKER_BALANCE_BUCKET_EQUITY_SEPARATION_READY,
    evaluate_broker_balance_bucket_equity_separation_v1,
)


PACKET_ID = (
    "AIOS-FOREX-OANDA-READONLY-ACCOUNT-SNAPSHOT-BALANCE-SEPARATION-"
    "ADAPTER-V1"
)
ADAPTER_VERSION = "v1"

OANDA_READONLY_ACCOUNT_SNAPSHOT_BALANCE_SEPARATION_READY = (
    "OANDA_READONLY_ACCOUNT_SNAPSHOT_BALANCE_SEPARATION_READY"
)
BLOCKED_MISSING_READONLY_CAPTURE_RESULT = (
    "BLOCKED_MISSING_READONLY_CAPTURE_RESULT"
)
BLOCKED_MISSING_ACCOUNT_SNAPSHOT = "BLOCKED_MISSING_ACCOUNT_SNAPSHOT"
BLOCKED_BALANCE_SEPARATION_INPUTS = "BLOCKED_BALANCE_SEPARATION_INPUTS"
REJECTED_UNSAFE_CAPTURE_AUTHORITY = "REJECTED_UNSAFE_CAPTURE_AUTHORITY"

EXECUTION_AUTHORITY_FIELDS = (
    "network_allowed",
    "network_call_allowed",
    "broker_call_allowed",
    "broker_network_call_allowed",
    "broker_api_call_allowed",
    "broker_write_allowed",
    "credential_access_allowed",
    "credential_read_allowed",
    "account_id_read_allowed",
    "dotenv_read_allowed",
    "env_read_allowed",
    "order_placement_allowed",
    "order_close_allowed",
    "order_mutation_allowed",
    "trade_mutation_allowed",
    "position_mutation_allowed",
    "live_endpoint_allowed",
    "live_trading_allowed",
    "live_allocation_allowed",
    "raw_broker_payload_persistence_allowed",
    "file_persistence_allowed",
    "write_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
    "live_funding_allowed",
)

SAFETY_PROOF_FIELDS = (
    "network_call_performed",
    "broker_network_call_performed",
    "broker_api_call_performed",
    "broker_call_performed",
    "broker_write_performed",
    "credential_read_performed",
    "account_id_read_performed",
    "dotenv_read",
    "env_read",
    "order_placement_performed",
    "order_close_performed",
    "order_mutation_performed",
    "trade_mutation_performed",
    "position_mutation_performed",
    "orders_endpoint_called",
    "live_endpoint_used",
    "raw_broker_payload_persisted",
    "file_persistence_performed",
    "write_performed",
    "scheduler_started",
    "daemon_started",
    "webhook_called",
    "live_funding_performed",
    "vault_read_performed",
    "credential_value_printed",
    "account_id_value_printed",
    "vault_value_persisted_to_repo",
    "profit_claimed",
)

UNSAFE_TRUE_FIELDS = EXECUTION_AUTHORITY_FIELDS + SAFETY_PROOF_FIELDS

SENSITIVE_VALUE_KEYS = {
    "access_token",
    "token",
    "authorization",
    "password",
    "secret",
    "secret_value",
    "credential_value",
    "api_key",
    "runtime_access_token",
    "runtime_account_id",
    "account_id",
    "accountid",
}

ACCOUNT_FIELD_ALIASES = {
    "balance": ("balance",),
    "NAV": ("NAV", "nav", "netAssetValue"),
    "unrealizedPL": ("unrealizedPL", "unrealized_pl", "unrealizedPl"),
    "pl": ("pl", "realizedPL", "realized_pl", "profitLoss"),
    "marginUsed": ("marginUsed", "margin_used"),
    "marginAvailable": ("marginAvailable", "margin_available"),
    "openTradeCount": ("openTradeCount", "open_trade_count"),
    "openPositionCount": ("openPositionCount", "open_position_count"),
    "pendingOrderCount": ("pendingOrderCount", "pending_order_count"),
}


def evaluate_oanda_readonly_account_snapshot_balance_separation_adapter_v1(
    read_only_capture_result: dict[str, Any] | Mapping[str, Any] | None,
    bucket_risk_policy: dict[str, Any] | Mapping[str, Any] | None,
) -> dict[str, Any]:
    capture = _mapping(read_only_capture_result)
    policy = _mapping(bucket_risk_policy)
    source = _extract_account_snapshot(capture)

    if not capture:
        return _adapter_decision(
            status=BLOCKED_MISSING_READONLY_CAPTURE_RESULT,
            blockers=["read_only_capture_result_required"],
            normalized_account_snapshot={},
            balance_separation_decision=None,
            source_capture_summary=_source_capture_summary(capture, source),
        )

    unsafe_blockers = _unsafe_input_blockers(capture, "read_only_capture_result")
    unsafe_blockers.extend(_unsafe_input_blockers(policy, "bucket_risk_policy"))
    if unsafe_blockers:
        return _adapter_decision(
            status=REJECTED_UNSAFE_CAPTURE_AUTHORITY,
            blockers=_unique(unsafe_blockers),
            normalized_account_snapshot={},
            balance_separation_decision=None,
            source_capture_summary=_source_capture_summary(capture, source),
        )

    if not source["account_snapshot"]:
        return _adapter_decision(
            status=BLOCKED_MISSING_ACCOUNT_SNAPSHOT,
            blockers=["sanitized_account_snapshot_required"],
            normalized_account_snapshot={},
            balance_separation_decision=None,
            source_capture_summary=_source_capture_summary(capture, source),
        )

    normalized_snapshot = _normalize_account_snapshot(
        source["account_snapshot"],
        source["pl_evidence"],
    )
    separation_decision = evaluate_broker_balance_bucket_equity_separation_v1(
        account_snapshot=normalized_snapshot,
        bucket_risk_policy=policy,
    )
    separation_status = _text(separation_decision.get("status"))
    if separation_status == BROKER_BALANCE_BUCKET_EQUITY_SEPARATION_READY:
        return _adapter_decision(
            status=OANDA_READONLY_ACCOUNT_SNAPSHOT_BALANCE_SEPARATION_READY,
            blockers=[],
            normalized_account_snapshot=normalized_snapshot,
            balance_separation_decision=separation_decision,
            source_capture_summary=_source_capture_summary(capture, source),
        )

    blockers = [f"balance_separation_status_{separation_status}"]
    blockers.extend(_string_items(separation_decision.get("blockers")))
    return _adapter_decision(
        status=BLOCKED_BALANCE_SEPARATION_INPUTS,
        blockers=_unique(blockers),
        normalized_account_snapshot=normalized_snapshot,
        balance_separation_decision=separation_decision,
        source_capture_summary=_source_capture_summary(capture, source),
    )


def _adapter_decision(
    *,
    status: str,
    blockers: Sequence[str],
    normalized_account_snapshot: Mapping[str, Any],
    balance_separation_decision: Mapping[str, Any] | None,
    source_capture_summary: Mapping[str, Any],
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "packet_id": PACKET_ID,
        "adapter_version": ADAPTER_VERSION,
        "status": status,
        "blockers": list(blockers),
        "warnings": _warnings(status),
        "normalized_account_snapshot": dict(normalized_account_snapshot),
        "balance_separation_decision": dict(balance_separation_decision)
        if isinstance(balance_separation_decision, Mapping)
        else None,
        "source_capture_summary": dict(source_capture_summary),
        "safety_proof": _safety_proof(),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }
    result.update(_safety_proof())
    return result


def _extract_account_snapshot(capture: Mapping[str, Any]) -> dict[str, Any]:
    top_pl_evidence = _mapping(capture.get("pl_evidence"))
    decision = _mapping(capture.get("decision"))
    decision_pl_evidence = _mapping(decision.get("pl_evidence"))

    candidates = (
        (
            "pl_evidence.account_summary_snapshot",
            top_pl_evidence.get("account_summary_snapshot"),
            top_pl_evidence,
        ),
        (
            "decision.pl_evidence.account_summary_snapshot",
            decision_pl_evidence.get("account_summary_snapshot"),
            decision_pl_evidence,
        ),
        (
            "account_summary_snapshot",
            capture.get("account_summary_snapshot"),
            top_pl_evidence or decision_pl_evidence,
        ),
        (
            "account_snapshot",
            capture.get("account_snapshot"),
            top_pl_evidence or decision_pl_evidence,
        ),
    )
    for source_path, account_snapshot, pl_evidence in candidates:
        snapshot = _mapping(account_snapshot)
        if snapshot:
            return {
                "source_path": source_path,
                "account_snapshot": snapshot,
                "pl_evidence": _mapping(pl_evidence),
            }
    return {"source_path": None, "account_snapshot": {}, "pl_evidence": {}}


def _normalize_account_snapshot(
    account_snapshot: Mapping[str, Any],
    pl_evidence: Mapping[str, Any],
) -> dict[str, Any]:
    normalized = {
        target: _first_present(account_snapshot, *aliases)
        for target, aliases in ACCOUNT_FIELD_ALIASES.items()
    }
    if not _has_any_key(account_snapshot, *ACCOUNT_FIELD_ALIASES["openTradeCount"]):
        normalized["openTradeCount"] = _evidence_count(
            pl_evidence.get("open_trade_evidence")
        )
    if not _has_any_key(account_snapshot, *ACCOUNT_FIELD_ALIASES["openPositionCount"]):
        normalized["openPositionCount"] = _evidence_count(
            pl_evidence.get("open_position_evidence")
        )
    if not _has_any_key(account_snapshot, *ACCOUNT_FIELD_ALIASES["pendingOrderCount"]):
        normalized["pendingOrderCount"] = 0
    return normalized


def _source_capture_summary(
    capture: Mapping[str, Any],
    source: Mapping[str, Any],
) -> dict[str, Any]:
    decision = _mapping(capture.get("decision"))
    pl_evidence = _mapping(source.get("pl_evidence"))
    return {
        "capture_status": _first_present(capture, "script_status", "status")
        or _first_present(decision, "script_status", "status"),
        "pl_capture_classification": _first_present(
            capture,
            "pl_capture_classification",
        )
        or _first_present(decision, "pl_capture_classification"),
        "account_snapshot_source": source.get("source_path"),
        "open_trade_evidence_count": _evidence_count(
            pl_evidence.get("open_trade_evidence")
        ),
        "open_position_evidence_count": _evidence_count(
            pl_evidence.get("open_position_evidence")
        ),
        "sanitized_only": True,
        "account_id_required": False,
        "raw_payload_persisted": False,
        "adapter_only_not_bucket_updater": True,
    }


def _unsafe_input_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            for raw_key, value in node.items():
                key = str(raw_key)
                key_normalized = key.strip()
                if key_normalized in UNSAFE_TRUE_FIELDS and _truthy_unsafe(value):
                    blockers.append(f"unsafe_{label}_{key_normalized}_true")
                if (
                    key_normalized in SENSITIVE_VALUE_KEYS
                    and _sensitive_value_present(value)
                ):
                    blockers.append(f"unsafe_{label}_{key_normalized}_present")
                visit(value)
        elif isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
            for child in node:
                visit(child)

    visit(payload)
    return _unique(blockers)


def _warnings(status: str) -> list[str]:
    warnings = [
        "adapter_only_not_bucket_updater",
        "sanitized_capture_input_only",
        "no_oanda_call_performed_by_adapter",
        "no_broker_network_call_performed_by_adapter",
        "no_vault_env_or_credential_read_by_adapter",
        "no_order_or_trade_mutation_performed_by_adapter",
        "raw_broker_payload_not_persisted",
        "broker_balance_not_automatic_aios_bucket",
        "nav_equity_separated_from_broker_balance",
        "unrealized_pl_not_withdrawable_or_compoundable",
        "configured_bucket_controls_risk",
        "live_allocation_false",
    ]
    if status == OANDA_READONLY_ACCOUNT_SNAPSHOT_BALANCE_SEPARATION_READY:
        warnings.append("balance_separation_decision_ready_for_owner_review")
    return warnings


def _next_safe_action(status: str) -> str:
    return {
        OANDA_READONLY_ACCOUNT_SNAPSHOT_BALANCE_SEPARATION_READY: (
            "owner_review_balance_separation_decision_no_order"
        ),
        BLOCKED_MISSING_READONLY_CAPTURE_RESULT: (
            "provide_sanitized_read_only_capture_result"
        ),
        BLOCKED_MISSING_ACCOUNT_SNAPSHOT: (
            "provide_sanitized_account_summary_snapshot"
        ),
        BLOCKED_BALANCE_SEPARATION_INPUTS: (
            "review_balance_separation_blockers_before_any_next_trade"
        ),
        REJECTED_UNSAFE_CAPTURE_AUTHORITY: (
            "remove_unsafe_authority_or_sensitive_runtime_fields"
        ),
    }.get(status, "stop_and_review_adapter_inputs")


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _safety_proof() -> dict[str, bool]:
    return {field: False for field in SAFETY_PROOF_FIELDS}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _first_present(mapping: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping:
            return mapping.get(key)
    return None


def _has_any_key(mapping: Mapping[str, Any], *keys: str) -> bool:
    return any(key in mapping for key in keys)


def _evidence_count(value: Any) -> int:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return len(value)
    return 0


def _truthy_unsafe(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "allowed", "performed"}
    return False


def _sensitive_value_present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _string_items(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [str(item) for item in value]
    return []


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return value.strip() if isinstance(value, str) else str(value).strip()


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = _text(value)
        if text and text not in seen:
            seen.add(text)
            output.append(text)
    return output
