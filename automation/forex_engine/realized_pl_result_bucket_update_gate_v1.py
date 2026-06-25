from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal, InvalidOperation
from typing import Any


PACKET_ID = "AIOS-FOREX-REALIZED-PL-RESULT-BUCKET-UPDATE-GATE-V1"
GATE_VERSION = "v1"
DEFAULT_TRADE_ID = "328"

OWNER_RUN_CLOSED_BY_TAKE_PROFIT = "OWNER_RUN_CLOSED_BY_TAKE_PROFIT"
OWNER_RUN_CLOSED_BY_STOP_LOSS = "OWNER_RUN_CLOSED_BY_STOP_LOSS"
OWNER_RUN_CLOSED_REALIZED_PROFIT_OTHER = (
    "OWNER_RUN_CLOSED_REALIZED_PROFIT_OTHER"
)
OWNER_RUN_CLOSED_REALIZED_LOSS_OTHER = "OWNER_RUN_CLOSED_REALIZED_LOSS_OTHER"
OWNER_RUN_CLOSED_BREAKEVEN_OTHER = "OWNER_RUN_CLOSED_BREAKEVEN_OTHER"
OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT = (
    "OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT"
)
OWNER_RUN_TRADE_NOT_FOUND = "OWNER_RUN_TRADE_NOT_FOUND"
OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID = "OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID"

BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT = (
    "BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT"
)
BUCKET_UPDATE_ELIGIBLE_REALIZED_LOSS = "BUCKET_UPDATE_ELIGIBLE_REALIZED_LOSS"
BUCKET_UPDATE_ELIGIBLE_BREAKEVEN = "BUCKET_UPDATE_ELIGIBLE_BREAKEVEN"
BUCKET_UPDATE_BLOCKED_STILL_OPEN = "BUCKET_UPDATE_BLOCKED_STILL_OPEN"
BUCKET_UPDATE_BLOCKED_TRADE_NOT_FOUND = "BUCKET_UPDATE_BLOCKED_TRADE_NOT_FOUND"
BUCKET_UPDATE_BLOCKED_UNSAFE_OR_INVALID = (
    "BUCKET_UPDATE_BLOCKED_UNSAFE_OR_INVALID"
)
BUCKET_UPDATE_BLOCKED_NO_REALIZED_PL = "BUCKET_UPDATE_BLOCKED_NO_REALIZED_PL"
BUCKET_UPDATE_BLOCKED_ALREADY_APPLIED = (
    "BUCKET_UPDATE_BLOCKED_ALREADY_APPLIED"
)

CLOSED_PROFIT_STATUSES = {
    OWNER_RUN_CLOSED_BY_TAKE_PROFIT,
    OWNER_RUN_CLOSED_REALIZED_PROFIT_OTHER,
}
CLOSED_LOSS_STATUSES = {
    OWNER_RUN_CLOSED_BY_STOP_LOSS,
    OWNER_RUN_CLOSED_REALIZED_LOSS_OTHER,
}
CLOSED_BREAKEVEN_STATUSES = {OWNER_RUN_CLOSED_BREAKEVEN_OTHER}
CLOSED_OWNER_STATUSES = (
    CLOSED_PROFIT_STATUSES | CLOSED_LOSS_STATUSES | CLOSED_BREAKEVEN_STATUSES
)

UPSTREAM_REQUIRED_TRUE_FIELDS = (
    "no_new_order_authorized",
    "no_bucket_update_performed",
    "no_live_funding_authorized",
)

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

UNSAFE_TRUE_FIELDS = EXECUTION_AUTHORITY_FIELDS + SAFETY_PROOF_FIELDS + (
    "bucket_update_authorized",
    "bucket_update_performed",
    "bucket_mutation_performed",
    "result_bucket_update_performed",
    "next_trade_authorized",
    "live_funding_authorized",
)

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

APPLIED_TRADE_COLLECTION_KEYS = {
    "applied_trade_ids",
    "applied_result_trade_ids",
    "applied_realized_pl_trade_ids",
    "applied_bucket_update_trade_ids",
    "bucket_update_applied_trade_ids",
    "result_bucket_applied_trade_ids",
}
APPLIED_RESULT_COLLECTION_KEYS = {
    "applied_results",
    "applied_bucket_updates",
    "bucket_updates_applied",
    "result_bucket_updates_applied",
}
APPLIED_BOOLEAN_KEYS = {
    "already_applied",
    "bucket_update_applied",
    "result_bucket_update_applied",
    "realized_pl_applied",
}


def evaluate_realized_pl_result_bucket_update_gate_v1(
    owner_run_exercise_decision: dict[str, Any],
    bucket_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    decision = _mapping(owner_run_exercise_decision)
    bucket = _mapping(bucket_state)
    blockers: list[str] = []
    warnings: list[str] = []

    if not isinstance(owner_run_exercise_decision, Mapping):
        blockers.append("owner_run_exercise_decision_must_be_mapping")
    if bucket_state is not None and not isinstance(bucket_state, Mapping):
        blockers.append("bucket_state_must_be_mapping_when_provided")

    owner_status = _owner_status(decision)
    trade_id = _trade_id(decision)
    realized = _realized_pl(decision)

    if decision:
        blockers.extend(_unsafe_input_blockers(decision, "owner_run_exercise_decision"))
    if bucket:
        blockers.extend(_unsafe_input_blockers(bucket, "bucket_state"))

    blockers.extend(_upstream_safety_blockers(decision))

    if owner_status not in _supported_owner_statuses():
        blockers.append("owner_run_exercise_status_not_supported")

    if _explicit_closed_false(decision) and owner_status in CLOSED_OWNER_STATUSES:
        blockers.append("closed_owner_status_conflicts_with_is_closed_false")

    if blockers:
        return _result(
            gate_status=BUCKET_UPDATE_BLOCKED_UNSAFE_OR_INVALID,
            blockers=blockers,
            warnings=warnings,
            trade_id=trade_id,
            realized_pl=realized,
        )

    if _trade_already_applied(bucket, trade_id):
        return _result(
            gate_status=BUCKET_UPDATE_BLOCKED_ALREADY_APPLIED,
            blockers=[f"trade_{trade_id}_bucket_update_already_applied"],
            warnings=["idempotency_guard_blocked_reapply"],
            trade_id=trade_id,
            realized_pl=realized,
        )

    if owner_status == OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT:
        return _result(
            gate_status=BUCKET_UPDATE_BLOCKED_STILL_OPEN,
            blockers=["owner_run_trade_still_open_no_realized_result"],
            warnings=warnings,
            trade_id=trade_id,
            realized_pl=realized,
        )

    if owner_status == OWNER_RUN_TRADE_NOT_FOUND:
        return _result(
            gate_status=BUCKET_UPDATE_BLOCKED_TRADE_NOT_FOUND,
            blockers=[f"owner_run_trade_{trade_id}_not_found"],
            warnings=warnings,
            trade_id=trade_id,
            realized_pl=realized,
        )

    if owner_status == OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID:
        return _result(
            gate_status=BUCKET_UPDATE_BLOCKED_UNSAFE_OR_INVALID,
            blockers=["upstream_owner_run_blocked_unsafe_or_invalid"],
            warnings=warnings,
            trade_id=trade_id,
            realized_pl=realized,
        )

    if owner_status in CLOSED_OWNER_STATUSES and realized is None:
        return _result(
            gate_status=BUCKET_UPDATE_BLOCKED_NO_REALIZED_PL,
            blockers=["closed_owner_run_result_requires_numeric_realized_pl"],
            warnings=warnings,
            trade_id=trade_id,
            realized_pl=None,
        )

    if owner_status in CLOSED_PROFIT_STATUSES:
        if realized is not None and realized > 0:
            return _result(
                gate_status=BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT,
                blockers=[],
                warnings=warnings,
                trade_id=trade_id,
                realized_pl=realized,
            )
        return _result(
            gate_status=BUCKET_UPDATE_BLOCKED_UNSAFE_OR_INVALID,
            blockers=["closed_profit_owner_status_requires_positive_realized_pl"],
            warnings=warnings,
            trade_id=trade_id,
            realized_pl=realized,
        )

    if owner_status in CLOSED_LOSS_STATUSES:
        if realized is not None and realized < 0:
            return _result(
                gate_status=BUCKET_UPDATE_ELIGIBLE_REALIZED_LOSS,
                blockers=[],
                warnings=warnings,
                trade_id=trade_id,
                realized_pl=realized,
            )
        return _result(
            gate_status=BUCKET_UPDATE_BLOCKED_UNSAFE_OR_INVALID,
            blockers=["closed_loss_owner_status_requires_negative_realized_pl"],
            warnings=warnings,
            trade_id=trade_id,
            realized_pl=realized,
        )

    if owner_status in CLOSED_BREAKEVEN_STATUSES:
        if realized is not None and realized == 0:
            return _result(
                gate_status=BUCKET_UPDATE_ELIGIBLE_BREAKEVEN,
                blockers=[],
                warnings=warnings,
                trade_id=trade_id,
                realized_pl=realized,
            )
        return _result(
            gate_status=BUCKET_UPDATE_BLOCKED_UNSAFE_OR_INVALID,
            blockers=["closed_breakeven_owner_status_requires_zero_realized_pl"],
            warnings=warnings,
            trade_id=trade_id,
            realized_pl=realized,
        )

    return _result(
        gate_status=BUCKET_UPDATE_BLOCKED_UNSAFE_OR_INVALID,
        blockers=["owner_run_status_could_not_be_resolved_to_gate_decision"],
        warnings=warnings,
        trade_id=trade_id,
        realized_pl=realized,
    )


def realized_pl_result_bucket_update_gate_template_v1() -> dict[str, Any]:
    return {
        "owner_run_exercise_decision": {
            "exercise_status": "OWNER_RUN_CLOSED_BY_TAKE_PROFIT",
            "trade_anchor": {"trade_id": DEFAULT_TRADE_ID},
            "realized_pl": "0.0012",
            "no_new_order_authorized": True,
            "no_bucket_update_performed": True,
            "no_live_funding_authorized": True,
            "safety_proof": _safety_proof(),
            "execution_authority": _execution_authority(),
        },
        "bucket_state": {
            "bucket_currency": "USD",
            "applied_trade_ids": [],
            "template_only_not_mutated_by_gate": True,
        },
        "runtime_input_rule": {
            "sanitized_owner_run_decision_only": True,
            "bucket_state_read_only": True,
            "broker_or_oanda_call_supported": False,
            "bucket_mutation_supported": False,
            "next_trade_authorization_supported": False,
            "live_funding_supported": False,
        },
    }


def realized_pl_result_bucket_update_gate_samples_v1() -> (
    dict[str, dict[str, Any]]
):
    return {
        "profit": {
            "owner_run_exercise_decision": _owner_decision(
                OWNER_RUN_CLOSED_BY_TAKE_PROFIT,
                "0.0012",
            ),
            "bucket_state": {"bucket_currency": "USD", "applied_trade_ids": []},
        },
        "loss": {
            "owner_run_exercise_decision": _owner_decision(
                OWNER_RUN_CLOSED_BY_STOP_LOSS,
                "-0.0010",
            ),
            "bucket_state": {"bucket_currency": "USD", "applied_trade_ids": []},
        },
        "breakeven": {
            "owner_run_exercise_decision": _owner_decision(
                OWNER_RUN_CLOSED_BREAKEVEN_OTHER,
                "0.0000",
            ),
            "bucket_state": {"bucket_currency": "USD", "applied_trade_ids": []},
        },
        "still-open": {
            "owner_run_exercise_decision": _owner_decision(
                OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT,
                None,
            ),
            "bucket_state": {"bucket_currency": "USD", "applied_trade_ids": []},
        },
        "trade-not-found": {
            "owner_run_exercise_decision": _owner_decision(
                OWNER_RUN_TRADE_NOT_FOUND,
                None,
            ),
            "bucket_state": {"bucket_currency": "USD", "applied_trade_ids": []},
        },
        "unsafe": {
            "owner_run_exercise_decision": _owner_decision(
                OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID,
                None,
                blockers=["upstream_owner_run_blocked_unsafe_or_invalid"],
            ),
            "bucket_state": {"bucket_currency": "USD", "applied_trade_ids": []},
        },
        "already-applied": {
            "owner_run_exercise_decision": _owner_decision(
                OWNER_RUN_CLOSED_BY_TAKE_PROFIT,
                "0.0012",
            ),
            "bucket_state": {"bucket_currency": "USD", "applied_trade_ids": ["328"]},
        },
    }


def _result(
    *,
    gate_status: str,
    blockers: Sequence[str],
    warnings: Sequence[str],
    trade_id: str,
    realized_pl: Decimal | None,
) -> dict[str, Any]:
    eligible = gate_status in {
        BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT,
        BUCKET_UPDATE_ELIGIBLE_REALIZED_LOSS,
        BUCKET_UPDATE_ELIGIBLE_BREAKEVEN,
    }
    safety = _safety_proof()
    result: dict[str, Any] = {
        "packet_id": PACKET_ID,
        "gate_version": GATE_VERSION,
        "gate_status": gate_status,
        "blockers": _unique(blockers),
        "warnings": _unique(_warnings(gate_status) + list(warnings)),
        "trade_id": trade_id,
        "realized_pl": _decimal_text_or_none(realized_pl),
        "proposed_bucket_delta": _proposed_bucket_delta(
            gate_status,
            trade_id,
            realized_pl,
        ),
        "bucket_update_authorized": eligible,
        "bucket_update_performed": False,
        "next_trade_authorized": False,
        "live_funding_authorized": False,
        "safety_proof": safety,
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(gate_status, trade_id),
    }
    result.update(safety)
    return result


def _proposed_bucket_delta(
    gate_status: str,
    trade_id: str,
    realized_pl: Decimal | None,
) -> dict[str, Any]:
    eligible = gate_status in {
        BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT,
        BUCKET_UPDATE_ELIGIBLE_REALIZED_LOSS,
        BUCKET_UPDATE_ELIGIBLE_BREAKEVEN,
    }
    delta = realized_pl if eligible and realized_pl is not None else Decimal("0")
    return {
        "eligible_for_later_bucket_update": eligible,
        "trade_id": trade_id,
        "source_field": "realized_pl" if eligible else None,
        "bucket_delta": _decimal_text(delta),
        "bucket_delta_applied_here": False,
        "bucket_mutation_performed_here": False,
    }


def _owner_decision(
    status: str,
    realized_pl: str | None,
    *,
    blockers: Sequence[str] | None = None,
) -> dict[str, Any]:
    decision: dict[str, Any] = {
        "packet_id": "AIOS-FOREX-OANDA-OWNER-RUN-CLOSED-RESULT-ADAPTER-EXERCISE-V1",
        "exercise_status": status,
        "trade_anchor": {"trade_id": DEFAULT_TRADE_ID},
        "realized_pl": realized_pl,
        "blockers": list(blockers or []),
        "no_new_order_authorized": True,
        "no_bucket_update_performed": True,
        "no_live_funding_authorized": True,
        "safety_proof": _safety_proof(),
        "execution_authority": _execution_authority(),
    }
    if status in CLOSED_OWNER_STATUSES:
        decision["classifier_decision"] = {"is_closed": True}
    return decision


def _owner_status(decision: Mapping[str, Any]) -> str:
    for path in (
        ("exercise_status",),
        ("owner_run_status",),
        ("status",),
        ("decision", "exercise_status"),
        ("adapter_decision", "exercise_status"),
    ):
        text = _text(_nested_value(decision, path))
        if text:
            return text
    return ""


def _trade_id(decision: Mapping[str, Any]) -> str:
    for path in (
        ("trade_id",),
        ("trade_anchor", "trade_id"),
        ("classifier_decision", "trade_id"),
        ("adapter_decision", "trade_id"),
        ("adapter_decision", "classifier_decision", "trade_id"),
    ):
        text = _text(_nested_value(decision, path))
        if text:
            return text
    return DEFAULT_TRADE_ID


def _realized_pl(decision: Mapping[str, Any]) -> Decimal | None:
    for path in (
        ("realized_pl",),
        ("realizedPL",),
        ("classifier_decision", "realized_pl"),
        ("classifier_decision", "realizedPL"),
        ("adapter_decision", "realized_pl"),
        ("adapter_decision", "classifier_decision", "realized_pl"),
        ("adapter_decision", "classifier_decision", "realizedPL"),
    ):
        if _path_exists(decision, path):
            parsed = _decimal_or_none(_nested_value(decision, path))
            if parsed is not None:
                return parsed
    return None


def _upstream_safety_blockers(decision: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for field in UPSTREAM_REQUIRED_TRUE_FIELDS:
        if decision.get(field) is not True:
            blockers.append(f"upstream_{field}_must_be_true")
    return blockers


def _explicit_closed_false(decision: Mapping[str, Any]) -> bool:
    for path in (
        ("is_closed",),
        ("classifier_decision", "is_closed"),
        ("adapter_decision", "classifier_decision", "is_closed"),
    ):
        if _path_exists(decision, path) and _nested_value(decision, path) is False:
            return True
    return False


def _trade_already_applied(bucket_state: Mapping[str, Any], trade_id: str) -> bool:
    if not bucket_state:
        return False

    trade_text = _text(trade_id)
    for key in APPLIED_TRADE_COLLECTION_KEYS:
        if _contains_trade_id(bucket_state.get(key), trade_text):
            return True
    for key in APPLIED_RESULT_COLLECTION_KEYS:
        if _contains_applied_trade(bucket_state.get(key), trade_text):
            return True
    return _applied_node(bucket_state, trade_text)


def _applied_node(node: Any, trade_id: str) -> bool:
    if isinstance(node, Mapping):
        normalized_keys = {_normalized_key(key): value for key, value in node.items()}
        node_trade_id = _text(
            normalized_keys.get("trade_id")
            or normalized_keys.get("tradeid")
            or normalized_keys.get("id")
        )
        mentions_trade = node_trade_id == trade_id or any(
            trade_id in _normalized_key(key) for key in node
        )
        if mentions_trade and any(
            _truthy_unsafe(normalized_keys.get(key))
            for key in APPLIED_BOOLEAN_KEYS
        ):
            return True
        for key, value in node.items():
            normalized = _normalized_key(key)
            if normalized in APPLIED_TRADE_COLLECTION_KEYS:
                if _contains_trade_id(value, trade_id):
                    return True
            if "applied" in normalized and _contains_applied_trade(value, trade_id):
                return True
            if _applied_node(value, trade_id):
                return True
    elif isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
        return any(_applied_node(item, trade_id) for item in node)
    return False


def _contains_applied_trade(value: Any, trade_id: str) -> bool:
    if _contains_trade_id(value, trade_id):
        return True
    if isinstance(value, Mapping):
        return _applied_node(value, trade_id)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(_contains_applied_trade(item, trade_id) for item in value)
    return False


def _contains_trade_id(value: Any, trade_id: str) -> bool:
    if isinstance(value, str):
        return value.strip() == trade_id
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value) == trade_id
    if isinstance(value, Mapping):
        for key in ("trade_id", "tradeID", "id"):
            if _text(value.get(key)) == trade_id:
                return True
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(_contains_trade_id(item, trade_id) for item in value)
    return False


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


def _supported_owner_statuses() -> set[str]:
    return {
        OWNER_RUN_CLOSED_BY_TAKE_PROFIT,
        OWNER_RUN_CLOSED_BY_STOP_LOSS,
        OWNER_RUN_CLOSED_REALIZED_PROFIT_OTHER,
        OWNER_RUN_CLOSED_REALIZED_LOSS_OTHER,
        OWNER_RUN_CLOSED_BREAKEVEN_OTHER,
        OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT,
        OWNER_RUN_TRADE_NOT_FOUND,
        OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID,
    }


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _safety_proof() -> dict[str, bool]:
    return {field: False for field in SAFETY_PROOF_FIELDS}


def _warnings(gate_status: str) -> list[str]:
    warnings = [
        "gate_only_decision_not_bucket_mutation",
        "proposed_bucket_delta_only",
        "no_oanda_call_performed",
        "no_broker_call_performed",
        "no_order_or_position_mutation_performed",
        "no_credentials_or_account_ids_read",
        "no_runtime_state_written",
        "no_next_trade_authorized",
        "no_live_funding_authorized",
    ]
    if gate_status in {
        BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT,
        BUCKET_UPDATE_ELIGIBLE_REALIZED_LOSS,
        BUCKET_UPDATE_ELIGIBLE_BREAKEVEN,
    }:
        warnings.append(
            "bucket_update_authorized_means_later_apply_eligibility_only"
        )
    return warnings


def _next_safe_action(gate_status: str, trade_id: str) -> str:
    if gate_status in {
        BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT,
        BUCKET_UPDATE_ELIGIBLE_REALIZED_LOSS,
        BUCKET_UPDATE_ELIGIBLE_BREAKEVEN,
    }:
        return "send_decision_to_later_bucket_update_apply_lane_no_mutation_here"
    if gate_status == BUCKET_UPDATE_BLOCKED_STILL_OPEN:
        return "continue_owner_run_read_only_monitoring_no_bucket_update_no_new_trade"
    if gate_status == BUCKET_UPDATE_BLOCKED_TRADE_NOT_FOUND:
        return f"provide_sanitized_closed_trade_or_transaction_evidence_for_trade_{trade_id}"
    if gate_status == BUCKET_UPDATE_BLOCKED_NO_REALIZED_PL:
        return "provide_closed_result_with_numeric_realized_pl_before_bucket_gate"
    if gate_status == BUCKET_UPDATE_BLOCKED_ALREADY_APPLIED:
        return f"do_not_reapply_bucket_delta_for_trade_{trade_id}"
    return "repair_upstream_owner_run_decision_before_bucket_gate"


def _nested_value(mapping: Mapping[str, Any], path: Sequence[str]) -> Any:
    node: Any = mapping
    for key in path:
        if not isinstance(node, Mapping) or key not in node:
            return None
        node = node[key]
    return node


def _path_exists(mapping: Mapping[str, Any], path: Sequence[str]) -> bool:
    node: Any = mapping
    for key in path:
        if not isinstance(node, Mapping) or key not in node:
            return False
        node = node[key]
    return True


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _decimal_or_none(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None
    if not parsed.is_finite():
        return None
    return parsed


def _decimal_text_or_none(value: Decimal | None) -> str | None:
    return _decimal_text(value) if value is not None else None


def _decimal_text(value: Decimal) -> str:
    return format(value, "f")


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
            "applied",
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
