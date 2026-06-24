from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-BROKER-ADAPTER-ONE-ORDER-FINAL-WIRE-V1"
FINAL_WIRE_VERSION = "v1"

FINAL_WIRE_BLOCKED_MISSING_RUNTIME_EXCEPTION = (
    "FINAL_WIRE_BLOCKED_MISSING_RUNTIME_EXCEPTION"
)
FINAL_WIRE_BLOCKED_RUNTIME_EXCEPTION_NOT_READY = (
    "FINAL_WIRE_BLOCKED_RUNTIME_EXCEPTION_NOT_READY"
)
FINAL_WIRE_BLOCKED_ADAPTER_CONTEXT = "FINAL_WIRE_BLOCKED_ADAPTER_CONTEXT"
FINAL_WIRE_BLOCKED_ORDER_PAYLOAD = "FINAL_WIRE_BLOCKED_ORDER_PAYLOAD"
FINAL_WIRE_BLOCKED_OWNER_APPROVAL = "FINAL_WIRE_BLOCKED_OWNER_APPROVAL"
FINAL_WIRE_READY_FOR_MANUAL_ONE_ORDER_DEMO_RUNTIME_ATTEMPT = (
    "FINAL_WIRE_READY_FOR_MANUAL_ONE_ORDER_DEMO_RUNTIME_ATTEMPT"
)
FINAL_WIRE_REJECTED = "FINAL_WIRE_REJECTED"

RUNTIME_EXCEPTION_READY_STATUS = "EXCEPTION_READY_FOR_MANUAL_RUNTIME_DEMO_ORDER_ATTEMPT"

EXECUTION_AUTHORITY_FIELDS = (
    "execution_allowed",
    "demo_order_allowed",
    "live_order_allowed",
    "broker_write_allowed",
    "autonomous_order_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
)

FORBIDDEN_ORDER_PAYLOAD_KEY_TERMS = (
    "account_id",
    "token",
    "credential",
    "secret",
    "password",
    "authorization",
)

PRE_TRADE_EVIDENCE_REQUIREMENTS = (
    "broker_environment",
    "instrument",
    "direction",
    "order_type",
    "units",
    "stop_loss",
    "take_profit",
    "risk_amount",
    "reward_risk_ratio",
    "spread_snapshot",
    "balance_snapshot",
    "nav_snapshot",
    "margin_snapshot",
    "timestamp_utc",
    "owner_approval_id",
)

POST_TRADE_EVIDENCE_REQUIREMENTS = (
    "order_attempted",
    "order_id_or_sanitized_reference",
    "filled_or_rejected",
    "fill_price_or_rejection_reason",
    "stop_loss_attached",
    "take_profit_attached",
    "realized_pl_when_closed",
    "close_reason",
    "post_balance",
    "post_nav",
    "timestamp_utc",
)


def evaluate_oanda_demo_broker_adapter_one_order_final_wire_v1(
    runtime_exception_result: dict | None = None,
    adapter_runtime_context: dict | None = None,
    sanitized_order_payload: dict | None = None,
    owner_final_wire_approval: dict | None = None,
) -> dict:
    runtime_exception = _mapping(runtime_exception_result)
    if not runtime_exception:
        return _result(
            status=FINAL_WIRE_BLOCKED_MISSING_RUNTIME_EXCEPTION,
            blockers=["missing_runtime_exception_result"],
            warnings=_warnings(FINAL_WIRE_BLOCKED_MISSING_RUNTIME_EXCEPTION),
            runtime_exception=runtime_exception,
            adapter_context=_mapping(adapter_runtime_context),
            order_payload=_mapping(sanitized_order_payload),
            owner_approval=_mapping(owner_final_wire_approval),
        )

    adapter_context = _mapping(adapter_runtime_context)
    order_payload = _mapping(sanitized_order_payload)
    owner_approval = _mapping(owner_final_wire_approval)

    unsafe_blockers = _unsafe_execution_blockers(
        runtime_exception,
        adapter_context,
        order_payload,
        owner_approval,
    )
    runtime_blockers = _runtime_exception_blockers(runtime_exception)
    adapter_blockers = _adapter_context_blockers(adapter_context)
    order_blockers = _order_payload_blockers(order_payload)
    owner_blockers = _owner_approval_blockers(owner_approval)

    blockers = _unique(
        unsafe_blockers
        + runtime_blockers
        + adapter_blockers
        + order_blockers
        + owner_blockers
    )
    status = _status(
        unsafe_blockers=unsafe_blockers,
        runtime_blockers=runtime_blockers,
        adapter_blockers=adapter_blockers,
        order_blockers=order_blockers,
        owner_blockers=owner_blockers,
    )

    return _result(
        status=status,
        blockers=blockers,
        warnings=_warnings(status),
        runtime_exception=runtime_exception,
        adapter_context=adapter_context,
        order_payload=order_payload,
        owner_approval=owner_approval,
    )


def _status(
    *,
    unsafe_blockers: list[str],
    runtime_blockers: list[str],
    adapter_blockers: list[str],
    order_blockers: list[str],
    owner_blockers: list[str],
) -> str:
    if unsafe_blockers:
        return FINAL_WIRE_REJECTED
    if runtime_blockers:
        return FINAL_WIRE_BLOCKED_RUNTIME_EXCEPTION_NOT_READY
    if adapter_blockers:
        return FINAL_WIRE_BLOCKED_ADAPTER_CONTEXT
    if order_blockers:
        return FINAL_WIRE_BLOCKED_ORDER_PAYLOAD
    if owner_blockers:
        return FINAL_WIRE_BLOCKED_OWNER_APPROVAL
    return FINAL_WIRE_READY_FOR_MANUAL_ONE_ORDER_DEMO_RUNTIME_ATTEMPT


def _runtime_exception_blockers(runtime_exception: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if runtime_exception.get("status") != RUNTIME_EXCEPTION_READY_STATUS:
        blockers.append("runtime_exception_status_not_ready")
    if not _bool(runtime_exception.get("allowed_manual_runtime_invocation")):
        blockers.append("runtime_exception_manual_runtime_invocation_not_allowed")

    contract = _runtime_contract(runtime_exception)
    if not contract:
        blockers.append("missing_runtime_exception_one_order_runtime_contract")
    if not _bool(contract.get("one_order_only")):
        blockers.append("runtime_exception_one_order_only_required")
    if _number(contract.get("max_order_attempts"), -1) != 1:
        blockers.append("runtime_exception_max_order_attempts_must_be_one")

    blockers.extend(_authority_blockers(runtime_exception, "runtime_exception_result"))
    return blockers


def _adapter_context_blockers(adapter_context: Mapping[str, Any]) -> list[str]:
    if not adapter_context:
        return ["missing_adapter_runtime_context"]

    required_true = (
        "demo_environment",
        "runtime_only_credentials_present",
        "account_id_runtime_only",
        "token_runtime_only",
        "one_order_only",
        "kill_switch_ready",
        "daily_stop_ready",
        "max_loss_gate_ready",
        "manual_runtime_invocation_required",
    )
    required_false = (
        "live_environment",
        "credential_persistence_detected",
        "account_id_persistence_detected",
        "order_already_attempted",
        "broker_network_call_performed",
        "order_placement_performed",
    )

    blockers: list[str] = []
    if adapter_context.get("broker") != "OANDA_DEMO":
        blockers.append("adapter_context_broker_must_be_oanda_demo")
    if adapter_context.get("environment") != "DEMO":
        blockers.append("adapter_context_environment_must_be_demo")
    for field in required_true:
        if not _bool(adapter_context.get(field)):
            blockers.append(f"adapter_context_{field}_required")
    for field in required_false:
        if _bool(adapter_context.get(field)):
            blockers.append(f"adapter_context_{field}_must_be_false")

    if _number(adapter_context.get("max_order_attempts"), -1) != 1:
        blockers.append("adapter_context_max_order_attempts_must_be_one")
    if _number(adapter_context.get("existing_open_orders"), -1) != 0:
        blockers.append("adapter_context_existing_open_orders_must_be_zero")
    if _number(adapter_context.get("existing_pending_orders"), -1) != 0:
        blockers.append("adapter_context_existing_pending_orders_must_be_zero")

    blockers.extend(_authority_blockers(adapter_context, "adapter_context"))
    return blockers


def _order_payload_blockers(order_payload: Mapping[str, Any]) -> list[str]:
    if not order_payload:
        return ["missing_sanitized_order_payload"]

    blockers: list[str] = []
    if not _text(order_payload.get("instrument")):
        blockers.append("order_payload_instrument_required")
    if order_payload.get("direction") not in {"BUY", "SELL"}:
        blockers.append("order_payload_direction_must_be_buy_or_sell")
    if order_payload.get("order_type") not in {"MARKET", "LIMIT", "STOP"}:
        blockers.append("order_payload_order_type_must_be_market_limit_or_stop")
    if not _positive_number(order_payload.get("units")):
        blockers.append("order_payload_units_must_be_positive")
    if "stop_loss" not in order_payload or order_payload.get("stop_loss") is None:
        blockers.append("order_payload_stop_loss_required")
    if "take_profit" not in order_payload or order_payload.get("take_profit") is None:
        blockers.append("order_payload_take_profit_required")
    if not _positive_number(order_payload.get("risk_amount")):
        blockers.append("order_payload_risk_amount_must_be_positive")
    if _number(order_payload.get("reward_risk_ratio"), 0) < 1.0:
        blockers.append("order_payload_reward_risk_ratio_must_be_at_least_one")
    if not _sanitized_client_order_id(order_payload.get("client_order_id")):
        blockers.append("order_payload_client_order_id_must_be_sanitized")

    forbidden_keys = _forbidden_payload_keys(order_payload)
    for key in forbidden_keys:
        blockers.append(f"order_payload_forbidden_{key}_field")

    blockers.extend(_authority_blockers(order_payload, "order_payload"))
    return blockers


def _owner_approval_blockers(owner_approval: Mapping[str, Any]) -> list[str]:
    if not owner_approval:
        return ["missing_owner_final_wire_approval"]

    required_true = (
        "owner_approved_final_manual_demo_order_attempt",
        "owner_confirmed_demo_only",
        "owner_confirmed_no_live_money",
        "owner_confirmed_one_order_only",
        "owner_confirmed_max_one_attempt",
        "owner_confirmed_stop_loss",
        "owner_confirmed_take_profit",
        "owner_confirmed_loss_possible",
        "owner_confirmed_no_profit_guarantee",
        "owner_confirmed_runtime_credentials_outside_repo",
        "owner_confirmed_manual_invocation_required",
        "owner_confirmed_no_autonomous_execution",
        "owner_confirmed_no_second_order",
    )

    blockers: list[str] = []
    for field in required_true:
        if not _bool(owner_approval.get(field)):
            blockers.append(f"{field}_required")
    blockers.extend(_authority_blockers(owner_approval, "owner_approval"))
    return blockers


def _result(
    *,
    status: str,
    blockers: list[str],
    warnings: list[str],
    runtime_exception: Mapping[str, Any],
    adapter_context: Mapping[str, Any],
    order_payload: Mapping[str, Any],
    owner_approval: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "packet_id": PACKET_ID,
        "final_wire_version": FINAL_WIRE_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "runtime_exception_summary": _runtime_exception_summary(runtime_exception),
        "adapter_runtime_summary": _adapter_runtime_summary(adapter_context),
        "sanitized_order_summary": _sanitized_order_summary(order_payload),
        "owner_approval_summary": _owner_approval_summary(owner_approval),
        "final_wire_request": _final_wire_request(status, order_payload),
        "dry_run_rehearsal": _dry_run_rehearsal(status),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }


def _final_wire_request(status: str, order_payload: Mapping[str, Any]) -> dict[str, Any]:
    ready = status == FINAL_WIRE_READY_FOR_MANUAL_ONE_ORDER_DEMO_RUNTIME_ATTEMPT
    return {
        "status": "READY_FOR_MANUAL_RUNTIME_INVOCATION" if ready else "NOT_READY",
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "one_order_only": True,
        "max_order_attempts": 1,
        "live_trading_allowed": False,
        "autonomous_execution_allowed": False,
        "credential_persistence_allowed": False,
        "account_id_persistence_allowed": False,
        "order_payload": _sanitized_order_payload(order_payload) if ready else None,
        "required_evidence": {
            "pre_trade": list(PRE_TRADE_EVIDENCE_REQUIREMENTS),
            "post_trade": list(POST_TRADE_EVIDENCE_REQUIREMENTS),
        },
        "stop_after_order_attempt": True,
        "no_second_order": True,
    }


def _dry_run_rehearsal(status: str) -> dict[str, Any]:
    ready = status == FINAL_WIRE_READY_FOR_MANUAL_ONE_ORDER_DEMO_RUNTIME_ATTEMPT
    return {
        "ready": ready,
        "status": "DRY_RUN_READY_FOR_MANUAL_RUNTIME_INVOCATION"
        if ready
        else "DRY_RUN_BLOCKED",
        "runtime_execution_flag_required": True,
        "execute_demo_order_flag_status": "BLOCKED_PENDING_FINAL_OWNER_RUNTIME_RUN",
        "broker_network_call_performed": False,
        "order_placement_performed": False,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "rehearsal_steps": [
            "validate_runtime_exception_ready",
            "validate_demo_only_adapter_context",
            "validate_sanitized_order_payload",
            "validate_owner_final_wire_approval",
            "build_final_wire_request",
            "stop_before_broker_call",
        ],
    }


def _runtime_exception_summary(runtime_exception: Mapping[str, Any]) -> dict[str, Any]:
    contract = _runtime_contract(runtime_exception)
    return {
        "status": _text(runtime_exception.get("status"), "MISSING"),
        "allowed_manual_runtime_invocation": _bool(
            runtime_exception.get("allowed_manual_runtime_invocation")
        ),
        "one_order_only": _bool(contract.get("one_order_only")),
        "max_order_attempts": _number(contract.get("max_order_attempts"), 0),
    }


def _adapter_runtime_summary(adapter_context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker": _text(adapter_context.get("broker"), "MISSING"),
        "environment": _text(adapter_context.get("environment"), "MISSING"),
        "demo_environment": _bool(adapter_context.get("demo_environment")),
        "live_environment": _bool(adapter_context.get("live_environment")),
        "runtime_only_credentials_present": _bool(
            adapter_context.get("runtime_only_credentials_present")
        ),
        "credential_persistence_detected": _bool(
            adapter_context.get("credential_persistence_detected")
        ),
        "account_id_persistence_detected": _bool(
            adapter_context.get("account_id_persistence_detected")
        ),
        "account_id_runtime_only": _bool(adapter_context.get("account_id_runtime_only")),
        "token_runtime_only": _bool(adapter_context.get("token_runtime_only")),
        "one_order_only": _bool(adapter_context.get("one_order_only")),
        "max_order_attempts": _number(adapter_context.get("max_order_attempts"), 0),
        "existing_open_orders": _number(adapter_context.get("existing_open_orders"), 0),
        "existing_pending_orders": _number(
            adapter_context.get("existing_pending_orders"), 0
        ),
        "order_already_attempted": _bool(adapter_context.get("order_already_attempted")),
        "kill_switch_ready": _bool(adapter_context.get("kill_switch_ready")),
        "daily_stop_ready": _bool(adapter_context.get("daily_stop_ready")),
        "max_loss_gate_ready": _bool(adapter_context.get("max_loss_gate_ready")),
        "manual_runtime_invocation_required": _bool(
            adapter_context.get("manual_runtime_invocation_required")
        ),
    }


def _sanitized_order_summary(order_payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "instrument": _text(order_payload.get("instrument"), "MISSING"),
        "direction": _text(order_payload.get("direction"), "MISSING"),
        "order_type": _text(order_payload.get("order_type"), "MISSING"),
        "units": _number(order_payload.get("units"), 0),
        "stop_loss_present": "stop_loss" in order_payload
        and order_payload.get("stop_loss") is not None,
        "take_profit_present": "take_profit" in order_payload
        and order_payload.get("take_profit") is not None,
        "risk_amount": _number(order_payload.get("risk_amount"), 0),
        "reward_risk_ratio": _number(order_payload.get("reward_risk_ratio"), 0),
        "client_order_id_present": bool(_text(order_payload.get("client_order_id"))),
        "forbidden_payload_keys_detected": _forbidden_payload_keys(order_payload),
    }


def _owner_approval_summary(owner_approval: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "owner_approved_final_manual_demo_order_attempt": _bool(
            owner_approval.get("owner_approved_final_manual_demo_order_attempt")
        ),
        "owner_confirmed_demo_only": _bool(owner_approval.get("owner_confirmed_demo_only")),
        "owner_confirmed_no_live_money": _bool(
            owner_approval.get("owner_confirmed_no_live_money")
        ),
        "owner_confirmed_one_order_only": _bool(
            owner_approval.get("owner_confirmed_one_order_only")
        ),
        "owner_confirmed_max_one_attempt": _bool(
            owner_approval.get("owner_confirmed_max_one_attempt")
        ),
        "owner_confirmed_stop_loss": _bool(owner_approval.get("owner_confirmed_stop_loss")),
        "owner_confirmed_take_profit": _bool(
            owner_approval.get("owner_confirmed_take_profit")
        ),
        "owner_confirmed_loss_possible": _bool(
            owner_approval.get("owner_confirmed_loss_possible")
        ),
        "owner_confirmed_no_profit_guarantee": _bool(
            owner_approval.get("owner_confirmed_no_profit_guarantee")
        ),
        "owner_confirmed_runtime_credentials_outside_repo": _bool(
            owner_approval.get("owner_confirmed_runtime_credentials_outside_repo")
        ),
        "owner_confirmed_manual_invocation_required": _bool(
            owner_approval.get("owner_confirmed_manual_invocation_required")
        ),
        "owner_confirmed_no_autonomous_execution": _bool(
            owner_approval.get("owner_confirmed_no_autonomous_execution")
        ),
        "owner_confirmed_no_second_order": _bool(
            owner_approval.get("owner_confirmed_no_second_order")
        ),
    }


def _sanitized_order_payload(order_payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "instrument": order_payload.get("instrument"),
        "direction": order_payload.get("direction"),
        "order_type": order_payload.get("order_type"),
        "units": order_payload.get("units"),
        "stop_loss": order_payload.get("stop_loss"),
        "take_profit": order_payload.get("take_profit"),
        "risk_amount": order_payload.get("risk_amount"),
        "reward_risk_ratio": order_payload.get("reward_risk_ratio"),
        "client_order_id": order_payload.get("client_order_id"),
    }


def _runtime_contract(runtime_exception: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(runtime_exception.get("one_order_runtime_contract"))


def _unsafe_execution_blockers(*payloads: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for index, payload in enumerate(payloads):
        blockers.extend(_authority_blockers(payload, f"payload_{index}"))
    return blockers


def _authority_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []
    authority = _mapping(payload.get("execution_authority"))
    for field in EXECUTION_AUTHORITY_FIELDS:
        if _bool(payload.get(field)) or _bool(authority.get(field)):
            blockers.append(f"unsafe_{label}_{field}_true")
    return blockers


def _forbidden_payload_keys(value: Any) -> list[str]:
    found: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            for key, child in node.items():
                key_text = str(key).lower()
                for term in FORBIDDEN_ORDER_PAYLOAD_KEY_TERMS:
                    if term in key_text and term not in found:
                        found.append(term)
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)
    return found


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _warnings(status: str) -> list[str]:
    warnings = [
        "broker_adapter_final_wire_model_only",
        "execution_authority_false",
        "no_oanda_call_performed",
        "no_broker_call_performed",
        "no_credentials_or_account_ids_read_or_persisted",
        "no_order_placement_performed",
        "manual_runtime_invocation_required",
    ]
    if status == FINAL_WIRE_READY_FOR_MANUAL_ONE_ORDER_DEMO_RUNTIME_ATTEMPT:
        warnings.append("separate_manual_runtime_run_still_required")
    return warnings


def _next_safe_action(status: str) -> str:
    return {
        FINAL_WIRE_BLOCKED_MISSING_RUNTIME_EXCEPTION: "provide_runtime_exception_result",
        FINAL_WIRE_BLOCKED_RUNTIME_EXCEPTION_NOT_READY: (
            "repair_runtime_exception_before_final_wire"
        ),
        FINAL_WIRE_BLOCKED_ADAPTER_CONTEXT: "provide_demo_only_adapter_runtime_context",
        FINAL_WIRE_BLOCKED_ORDER_PAYLOAD: "provide_sanitized_one_order_payload",
        FINAL_WIRE_BLOCKED_OWNER_APPROVAL: (
            "complete_owner_final_wire_approval_before_manual_runtime_run"
        ),
        FINAL_WIRE_READY_FOR_MANUAL_ONE_ORDER_DEMO_RUNTIME_ATTEMPT: (
            "manual_runtime_demo_order_attempt_with_one_order_cap"
        ),
        FINAL_WIRE_REJECTED: "remove_execution_authority_request_before_final_wire_review",
    }.get(status, "stop_and_review_final_wire_state")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _number(value: Any, default: float) -> float:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else default


def _positive_number(value: Any) -> bool:
    return _number(value, 0) > 0


def _sanitized_client_order_id(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    client_order_id = value.strip()
    if not client_order_id or client_order_id != value:
        return False
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.:")
    return all(character in allowed for character in client_order_id)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
