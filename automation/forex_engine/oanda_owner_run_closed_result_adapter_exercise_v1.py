from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.oanda_readonly_closed_result_tpsl_classifier_adapter_v1 import (
    evaluate_oanda_readonly_closed_result_tpsl_classifier_adapter_v1,
)


PACKET_ID = "AIOS-FOREX-OANDA-OWNER-RUN-CLOSED-RESULT-ADAPTER-EXERCISE-V1"
EXERCISE_VERSION = "v1"

ADAPTED_STILL_OPEN_NO_REALIZED_RESULT = "ADAPTED_STILL_OPEN_NO_REALIZED_RESULT"
ADAPTED_CLOSED_BY_TAKE_PROFIT = "ADAPTED_CLOSED_BY_TAKE_PROFIT"
ADAPTED_CLOSED_BY_STOP_LOSS = "ADAPTED_CLOSED_BY_STOP_LOSS"
ADAPTED_CLOSED_REALIZED_PROFIT_OTHER = "ADAPTED_CLOSED_REALIZED_PROFIT_OTHER"
ADAPTED_CLOSED_REALIZED_LOSS_OTHER = "ADAPTED_CLOSED_REALIZED_LOSS_OTHER"
ADAPTED_CLOSED_BREAKEVEN_OTHER = "ADAPTED_CLOSED_BREAKEVEN_OTHER"
ADAPTED_TRADE_NOT_FOUND = "ADAPTED_TRADE_NOT_FOUND"
ADAPTED_BLOCKED_UNSAFE_EVIDENCE = "ADAPTED_BLOCKED_UNSAFE_EVIDENCE"
ADAPTED_BLOCKED_INVALID_EVIDENCE = "ADAPTED_BLOCKED_INVALID_EVIDENCE"

OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT = "OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT"
OWNER_RUN_CLOSED_BY_TAKE_PROFIT = "OWNER_RUN_CLOSED_BY_TAKE_PROFIT"
OWNER_RUN_CLOSED_BY_STOP_LOSS = "OWNER_RUN_CLOSED_BY_STOP_LOSS"
OWNER_RUN_CLOSED_REALIZED_PROFIT_OTHER = "OWNER_RUN_CLOSED_REALIZED_PROFIT_OTHER"
OWNER_RUN_CLOSED_REALIZED_LOSS_OTHER = "OWNER_RUN_CLOSED_REALIZED_LOSS_OTHER"
OWNER_RUN_CLOSED_BREAKEVEN_OTHER = "OWNER_RUN_CLOSED_BREAKEVEN_OTHER"
OWNER_RUN_TRADE_NOT_FOUND = "OWNER_RUN_TRADE_NOT_FOUND"
OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID = "OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID"

DEFAULT_TRADE_ANCHOR: dict[str, str] = {
    "trade_id": "328",
    "instrument": "EUR_USD",
    "entry_open_price": "1.13689",
    "take_profit_order_id": "329",
    "stop_loss_order_id": "330",
    "expected_units": "1",
}

ADAPTER_STATUS_TO_EXERCISE_STATUS = {
    ADAPTED_STILL_OPEN_NO_REALIZED_RESULT: OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT,
    ADAPTED_CLOSED_BY_TAKE_PROFIT: OWNER_RUN_CLOSED_BY_TAKE_PROFIT,
    ADAPTED_CLOSED_BY_STOP_LOSS: OWNER_RUN_CLOSED_BY_STOP_LOSS,
    ADAPTED_CLOSED_REALIZED_PROFIT_OTHER: OWNER_RUN_CLOSED_REALIZED_PROFIT_OTHER,
    ADAPTED_CLOSED_REALIZED_LOSS_OTHER: OWNER_RUN_CLOSED_REALIZED_LOSS_OTHER,
    ADAPTED_CLOSED_BREAKEVEN_OTHER: OWNER_RUN_CLOSED_BREAKEVEN_OTHER,
    ADAPTED_TRADE_NOT_FOUND: OWNER_RUN_TRADE_NOT_FOUND,
    ADAPTED_BLOCKED_UNSAFE_EVIDENCE: OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID,
    ADAPTED_BLOCKED_INVALID_EVIDENCE: OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID,
}

CLOSED_ADAPTER_STATUSES = {
    ADAPTED_CLOSED_BY_TAKE_PROFIT,
    ADAPTED_CLOSED_BY_STOP_LOSS,
    ADAPTED_CLOSED_REALIZED_PROFIT_OTHER,
    ADAPTED_CLOSED_REALIZED_LOSS_OTHER,
    ADAPTED_CLOSED_BREAKEVEN_OTHER,
}

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
    "vault_read_allowed",
    "windows_vault_read_allowed",
    "dotenv_read_allowed",
    "env_read_allowed",
    "order_placement_allowed",
    "order_close_allowed",
    "order_mutation_allowed",
    "trade_mutation_allowed",
    "position_mutation_allowed",
    "live_endpoint_allowed",
    "live_trading_allowed",
    "live_order_allowed",
    "raw_broker_payload_persistence_allowed",
    "file_persistence_allowed",
    "write_allowed",
    "bucket_update_allowed",
    "bucket_mutation_allowed",
    "result_bucket_update_allowed",
    "result_bucket_mutation_allowed",
    "next_order_authorized",
    "next_trade_authorized",
    "next_allocation_authorized",
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
    "vault_read_performed",
    "windows_vault_read_performed",
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
    "bucket_update_performed",
    "bucket_mutation_performed",
    "result_bucket_update_performed",
    "result_bucket_mutation_performed",
    "next_order_authorized",
    "next_trade_authorized",
    "next_allocation_authorized",
    "scheduler_started",
    "daemon_started",
    "webhook_called",
    "live_funding_performed",
)

UNSAFE_TRUE_FIELDS = EXECUTION_AUTHORITY_FIELDS + SAFETY_PROOF_FIELDS
SENSITIVE_KEY_TERMS = (
    "token",
    "authorization",
    "account_id",
    "runtime_account_id",
    "credential",
    "secret",
    "password",
    "api_key",
    "apikey",
)
RAW_PAYLOAD_KEY_TERMS = ("raw_payload", "rawpayload", "raw_broker_payload")
REQUEST_HEADER_KEY_TERMS = ("headers", "request_headers", "requestheaders")
ENDPOINT_URL_KEY_TERMS = ("url", "endpoint_url", "endpointurl")
ACTION_KEY_TERMS = (
    "network",
    "broker",
    "credential",
    "vault",
    "dotenv",
    "env",
    "order",
    "trade",
    "position",
    "live",
    "write",
    "bucket",
    "scheduler",
    "daemon",
    "webhook",
    "funding",
    "next_order",
    "next_trade",
    "next_allocation",
)
ACTION_STATE_TERMS = (
    "allowed",
    "performed",
    "started",
    "called",
    "authorized",
    "enabled",
    "used",
    "read",
    "mutated",
    "placed",
    "closed",
)


def evaluate_oanda_owner_run_closed_result_adapter_exercise_v1(
    owner_run_capture_json: dict[str, Any] | Mapping[str, Any] | None,
    trade_anchor: dict[str, Any] | Mapping[str, Any] | None = None,
    exercise_metadata: dict[str, Any] | Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    anchor = _normalize_anchor(trade_anchor)
    metadata = _mapping(exercise_metadata)

    if owner_run_capture_json is None or not isinstance(
        owner_run_capture_json,
        Mapping,
    ):
        return blocked_oanda_owner_run_closed_result_adapter_exercise_v1(
            blockers=["owner_run_capture_json_must_be_mapping"],
            warnings=["exercise_rejected_input_before_adapter"],
            trade_anchor=anchor,
            exercise_metadata=metadata,
            adapter_status=ADAPTED_BLOCKED_INVALID_EVIDENCE,
        )

    if exercise_metadata is not None and not isinstance(exercise_metadata, Mapping):
        return blocked_oanda_owner_run_closed_result_adapter_exercise_v1(
            blockers=["exercise_metadata_must_be_mapping_when_provided"],
            warnings=["exercise_rejected_metadata_before_adapter"],
            trade_anchor=anchor,
            exercise_metadata={},
            adapter_status=ADAPTED_BLOCKED_INVALID_EVIDENCE,
        )

    unsafe_blockers = _unsafe_input_blockers(
        owner_run_capture_json,
        "owner_run_capture_json",
    )
    unsafe_blockers.extend(_unsafe_input_blockers(metadata, "exercise_metadata"))
    if unsafe_blockers:
        return blocked_oanda_owner_run_closed_result_adapter_exercise_v1(
            blockers=_unique(unsafe_blockers),
            warnings=[
                "unsafe_owner_run_json_rejected_before_adapter",
                "no_adapter_call_performed",
            ],
            trade_anchor=anchor,
            exercise_metadata=metadata,
            adapter_status=ADAPTED_BLOCKED_UNSAFE_EVIDENCE,
        )

    adapter_decision = evaluate_oanda_readonly_closed_result_tpsl_classifier_adapter_v1(
        owner_run_capture_json,
        anchor,
    )
    return _exercise_decision(
        adapter_decision=adapter_decision,
        adapter_status=_text(adapter_decision.get("adapter_status")),
        blockers=_string_items(adapter_decision.get("blockers")),
        warnings=_string_items(adapter_decision.get("warnings")),
        trade_anchor=anchor,
        exercise_metadata=metadata,
    )


def blocked_oanda_owner_run_closed_result_adapter_exercise_v1(
    *,
    blockers: Sequence[str],
    warnings: Sequence[str] | None = None,
    trade_anchor: dict[str, Any] | Mapping[str, Any] | None = None,
    exercise_metadata: dict[str, Any] | Mapping[str, Any] | None = None,
    adapter_status: str = ADAPTED_BLOCKED_INVALID_EVIDENCE,
) -> dict[str, Any]:
    return _exercise_decision(
        adapter_decision=None,
        adapter_status=adapter_status,
        blockers=blockers,
        warnings=warnings or [],
        trade_anchor=_normalize_anchor(trade_anchor),
        exercise_metadata=_mapping(exercise_metadata),
    )


def default_trade_anchor_v1() -> dict[str, str]:
    return dict(DEFAULT_TRADE_ANCHOR)


def oanda_owner_run_closed_result_adapter_exercise_template_v1() -> dict[str, Any]:
    return {
        "trade_anchor": default_trade_anchor_v1(),
        "exercise_metadata": {
            "packet_id": PACKET_ID,
            "owner_supplied_sanitized_json_only": True,
            "exercise_report_only": True,
        },
        "owner_run_capture_json": _safe_capture(
            {
                "decision": {
                    "pl_evidence": {
                        "open_trade_evidence": [
                            {
                                "trade_id": "328",
                                "instrument": "EUR_USD",
                                "currentUnits": "1",
                                "unrealizedPL": "sanitized_number",
                                "takeProfitOrder": {"id": "329"},
                                "stopLossOrder": {"id": "330"},
                            }
                        ],
                        "realized_pl_values": [],
                        "realized_pl_total": "0",
                    }
                },
                "transaction_match": {"transactions": []},
            }
        ),
        "template_only": True,
        "owner_run_exercise_only_not_broker_caller": True,
        "owner_run_exercise_only_not_oanda_caller": True,
        "owner_run_exercise_only_not_order_closer": True,
        "owner_run_exercise_only_not_bucket_updater": True,
        "owner_run_exercise_only_not_next_trade_authorizer": True,
        "owner_run_exercise_only_not_scheduler_or_daemon": True,
        "runtime_input_rule": {
            "owner_supplied_sanitized_local_json_supported": True,
            "oanda_capture_execution_supported": False,
            "vault_read_supported": False,
            "dotenv_read_supported": False,
            "environment_read_supported": False,
            "raw_input_persistence_supported": False,
        },
    }


def oanda_owner_run_closed_result_adapter_exercise_default_samples_v1() -> (
    dict[str, dict[str, Any]]
):
    return {
        "still-open": _safe_capture(
            {
                "decision": {
                    "status": "OWNER_RUN_SANITIZED_READ_ONLY_CAPTURE",
                    "pl_evidence": {
                        "open_trade_evidence": [
                            {
                                "trade_id": "328",
                                "instrument": "EUR_USD",
                                "currentUnits": "1",
                                "unrealizedPL": "0.0008",
                                "takeProfitOrder": {"id": "329"},
                                "stopLossOrder": {"id": "330"},
                            }
                        ],
                        "realized_pl_values": [],
                        "realized_pl_total": "0",
                    },
                },
                "transaction_match": {"transactions": []},
            }
        ),
        "closed-by-tp": _safe_capture(
            {
                "closed_trade_snapshot": {
                    "closed_trades": [
                        {
                            "id": "328",
                            "instrument": "EUR_USD",
                            "state": "CLOSED",
                            "currentUnits": "0",
                            "closeTime": "SANITIZED_TIMESTAMP",
                            "realizedPL": "0.0012",
                            "takeProfitOrder": {"id": "329"},
                        }
                    ]
                },
                "transaction_match": {
                    "transactions": [
                        {
                            "id": "329",
                            "type": "ORDER_FILL",
                            "orderID": "329",
                            "reason": "TAKE_PROFIT_ORDER",
                            "tradesClosed": [
                                {"tradeID": "328", "realizedPL": "0.0012"}
                            ],
                        }
                    ]
                },
            }
        ),
        "closed-by-sl": _safe_capture(
            {
                "trade_evidence": {
                    "tradeID": "328",
                    "instrument": "EUR_USD",
                    "state": "CLOSED",
                    "currentUnits": "0",
                    "closeTime": "SANITIZED_TIMESTAMP",
                    "realizedPL": "-0.0010",
                    "stopLossOrder": {"id": "330"},
                },
                "transactions": [
                    {
                        "id": "330",
                        "type": "ORDER_FILL",
                        "orderID": "330",
                        "reason": "STOP_LOSS_ORDER",
                        "tradesClosed": [
                            {"tradeID": "328", "realizedPL": "-0.0010"}
                        ],
                    }
                ],
            }
        ),
        "closed-other-profit": _safe_capture(
            {
                "closed_trade_snapshot": {
                    "closed_trades": [
                        {
                            "tradeID": "328",
                            "instrument": "EUR_USD",
                            "state": "CLOSED",
                            "currentUnits": "0",
                            "closeTime": "SANITIZED_TIMESTAMP",
                            "realizedPL": "0.0006",
                        }
                    ]
                },
                "transactions": [
                    {
                        "id": "410",
                        "type": "ORDER_FILL",
                        "reason": "CLIENT_ORDER",
                        "tradesClosed": [
                            {"tradeID": "328", "realizedPL": "0.0006"}
                        ],
                    }
                ],
            }
        ),
        "closed-other-loss": _safe_capture(
            {
                "closed_trade_snapshot": {
                    "closed_trades": [
                        {
                            "tradeID": "328",
                            "instrument": "EUR_USD",
                            "state": "CLOSED",
                            "currentUnits": "0",
                            "closeTime": "SANITIZED_TIMESTAMP",
                            "realizedPL": "-0.0006",
                        }
                    ]
                },
            }
        ),
        "breakeven": _safe_capture(
            {
                "closed_trade_snapshot": {
                    "closed_trades": [
                        {
                            "tradeID": "328",
                            "instrument": "EUR_USD",
                            "state": "CLOSED",
                            "currentUnits": "0",
                            "closeTime": "SANITIZED_TIMESTAMP",
                            "realizedPL": "0.0000",
                        }
                    ]
                },
            }
        ),
        "trade-not-found": _safe_capture(
            {
                "open_trade_snapshot": {"open_trades": []},
                "closed_trade_snapshot": {"closed_trades": []},
                "transaction_match": {"transactions": []},
                "pl_evidence": {
                    "open_trade_evidence": [],
                    "realized_pl_values": [],
                    "realized_pl_total": None,
                },
            }
        ),
        "unsafe": {
            "execution_authority": {
                **_execution_authority(),
                "order_placement_allowed": True,
            },
            "safety_proof": _safety_proof(),
            "pl_evidence": {
                "open_trade_evidence": [],
                "realized_pl_values": [],
            },
        },
    }


def _exercise_decision(
    *,
    adapter_decision: Mapping[str, Any] | None,
    adapter_status: str,
    blockers: Sequence[str],
    warnings: Sequence[str],
    trade_anchor: Mapping[str, str],
    exercise_metadata: Mapping[str, Any],
) -> dict[str, Any]:
    adapter_mapping = _mapping(adapter_decision)
    classifier_mapping = _mapping(adapter_mapping.get("classifier_decision"))
    classifier_status = _text(adapter_mapping.get("classifier_status")) or None
    exercise_status = ADAPTER_STATUS_TO_EXERCISE_STATUS.get(
        adapter_status,
        OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID,
    )
    mapped_blockers = list(blockers)
    mapped_warnings = list(warnings)
    if adapter_status not in ADAPTER_STATUS_TO_EXERCISE_STATUS:
        mapped_blockers.append(f"unsupported_adapter_status_{adapter_status}")
        mapped_warnings.append("exercise_blocked_unsupported_adapter_status")

    profit_claimed = bool(
        adapter_status in CLOSED_ADAPTER_STATUSES
        and classifier_mapping.get("is_closed") is True
        and adapter_mapping.get("profit_claimed") is True
    )
    result: dict[str, Any] = {
        "packet_id": PACKET_ID,
        "exercise_version": EXERCISE_VERSION,
        "exercise_status": exercise_status,
        "blockers": _unique(mapped_blockers),
        "warnings": _unique(_warnings(exercise_status) + mapped_warnings),
        "trade_anchor": dict(trade_anchor),
        "exercise_metadata": dict(exercise_metadata),
        "adapter_decision": dict(adapter_mapping) if adapter_mapping else None,
        "adapter_status": adapter_status,
        "classifier_status": classifier_status,
        "profit_claimed": profit_claimed,
        "realized_pl": _optional_text(classifier_mapping.get("realized_pl")),
        "unrealized_pl": _optional_text(classifier_mapping.get("unrealized_pl")),
        "matched_take_profit_order_id": _optional_text(
            classifier_mapping.get("matched_take_profit_order_id")
        ),
        "matched_stop_loss_order_id": _optional_text(
            classifier_mapping.get("matched_stop_loss_order_id")
        ),
        "no_new_order_authorized": True,
        "no_next_trade_authorized": True,
        "no_bucket_update_performed": True,
        "no_live_funding_authorized": True,
        "safety_proof": _safety_proof(),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(exercise_status),
    }
    result.update(_safety_proof())
    return result


def _unsafe_input_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            for raw_key, value in node.items():
                key = _normalized_key(raw_key)
                if key in UNSAFE_TRUE_FIELDS and _truthy_unsafe(value):
                    blockers.append(f"unsafe_{label}_{key}_true")
                if _action_flag_key(key) and _truthy_unsafe(value):
                    blockers.append(f"unsafe_{label}_{key}_true")
                if _sensitive_key(key) and _sensitive_value_present(value):
                    blockers.append(f"unsafe_{label}_{key}_present")
                if _endpoint_url_key(key) and _present(value):
                    blockers.append(f"unsafe_{label}_{key}_present")
                if _request_header_key(key) and _present(value):
                    blockers.append(f"unsafe_{label}_{key}_present")
                if _raw_payload_key(key) and _present(value):
                    blockers.append(f"unsafe_{label}_{key}_present")
                visit(value)
        elif isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
            for child in node:
                visit(child)

    visit(payload)
    return _unique(blockers)


def _normalize_anchor(anchor: Mapping[str, Any] | None) -> dict[str, str]:
    source = _mapping(anchor)
    normalized = dict(DEFAULT_TRADE_ANCHOR)
    for key in DEFAULT_TRADE_ANCHOR:
        value = _text(source.get(key))
        if value:
            normalized[key] = value
    return normalized


def _safe_capture(payload: Mapping[str, Any]) -> dict[str, Any]:
    capture = dict(payload)
    capture["execution_authority"] = _execution_authority()
    capture["safety_proof"] = _safety_proof()
    capture.update(_safety_proof())
    return capture


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _safety_proof() -> dict[str, bool]:
    return {field: False for field in SAFETY_PROOF_FIELDS}


def _warnings(exercise_status: str) -> list[str]:
    warnings = [
        "owner_run_exercise_only_not_broker_caller",
        "owner_run_exercise_only_not_oanda_caller",
        "owner_run_exercise_only_not_order_closer",
        "owner_run_exercise_only_not_order_mutator",
        "owner_run_exercise_only_not_bucket_updater",
        "owner_run_exercise_only_not_next_trade_authorizer",
        "owner_run_exercise_only_not_scheduler_or_daemon",
        "owner_supplied_sanitized_json_only",
        "no_oanda_capture_run_performed_by_exercise",
        "no_vault_env_or_credential_read_by_exercise",
        "no_raw_owner_input_persistence",
        "open_unrealized_pl_is_not_profit_claim",
    ]
    if exercise_status == OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID:
        warnings.append("exercise_blocked_before_or_after_adapter")
    if exercise_status.startswith("OWNER_RUN_CLOSED"):
        warnings.append("closed_result_requires_owner_review_before_bucket_or_next_trade")
    return warnings


def _next_safe_action(exercise_status: str) -> str:
    if exercise_status == OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT:
        return "continue_owner_run_read_only_monitoring_no_order_no_bucket_update"
    if exercise_status in {
        OWNER_RUN_CLOSED_BY_TAKE_PROFIT,
        OWNER_RUN_CLOSED_BY_STOP_LOSS,
        OWNER_RUN_CLOSED_REALIZED_PROFIT_OTHER,
        OWNER_RUN_CLOSED_REALIZED_LOSS_OTHER,
        OWNER_RUN_CLOSED_BREAKEVEN_OTHER,
    }:
        return "owner_review_exercise_report_before_bucket_gate_or_next_trade_gate"
    if exercise_status == OWNER_RUN_TRADE_NOT_FOUND:
        return "provide_sanitized_owner_run_closed_trade_or_transaction_evidence_for_trade_328"
    return "remove_unsafe_fields_or_repair_sanitized_owner_run_json_before_retry"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_items(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [str(item) for item in value]
    return []


def _optional_text(value: Any) -> str | None:
    text = _text(value)
    return text if text else None


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return value.strip() if isinstance(value, str) else str(value).strip()


def _normalized_key(value: Any) -> str:
    return str(value).strip().replace("-", "_").replace(" ", "_").lower()


def _action_flag_key(key: str) -> bool:
    if key.startswith("no_") or "_not_" in key or key.endswith("_not_supported"):
        return False
    return any(term in key for term in ACTION_KEY_TERMS) and any(
        term in key for term in ACTION_STATE_TERMS
    )


def _sensitive_key(key: str) -> bool:
    return any(term in key for term in SENSITIVE_KEY_TERMS)


def _endpoint_url_key(key: str) -> bool:
    return key in ENDPOINT_URL_KEY_TERMS or key.endswith("_url")


def _request_header_key(key: str) -> bool:
    return key in REQUEST_HEADER_KEY_TERMS


def _raw_payload_key(key: str) -> bool:
    return any(term in key for term in RAW_PAYLOAD_KEY_TERMS)


def _truthy_unsafe(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {
            "true",
            "yes",
            "1",
            "allowed",
            "performed",
            "enabled",
            "started",
            "called",
            "authorized",
            "used",
            "read",
            "mutated",
            "placed",
            "closed",
        }
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value == 1
    return False


def _sensitive_value_present(value: Any) -> bool:
    if value in (None, False):
        return False
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return False
        upper = text.upper()
        return "REDACTED" not in upper and "SANITIZED" not in upper
    return True


def _present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return bool(value)
    if isinstance(value, Mapping):
        return bool(value)
    return True


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = _text(value)
        if text and text not in seen:
            seen.add(text)
            output.append(text)
    return output
