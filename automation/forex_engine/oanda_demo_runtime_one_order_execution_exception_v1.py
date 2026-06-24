from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-RUNTIME-ONE-ORDER-EXECUTION-EXCEPTION-V1"
EXCEPTION_VERSION = "v1"

EXCEPTION_BLOCKED_MISSING_BROKER_PACKET = "EXCEPTION_BLOCKED_MISSING_BROKER_PACKET"
EXCEPTION_BLOCKED_BROKER_PACKET_NOT_READY = "EXCEPTION_BLOCKED_BROKER_PACKET_NOT_READY"
EXCEPTION_BLOCKED_RUNTIME_CONTEXT = "EXCEPTION_BLOCKED_RUNTIME_CONTEXT"
EXCEPTION_BLOCKED_OWNER_APPROVAL = "EXCEPTION_BLOCKED_OWNER_APPROVAL"
EXCEPTION_READY_FOR_MANUAL_RUNTIME_DEMO_ORDER_ATTEMPT = (
    "EXCEPTION_READY_FOR_MANUAL_RUNTIME_DEMO_ORDER_ATTEMPT"
)
EXCEPTION_REJECTED = "EXCEPTION_REJECTED"

BROKER_PACKET_READY_STATUS = "BROKER_PACKET_READY_FOR_SEPARATE_RUNTIME_ONLY_DEMO_ORDER_ATTEMPT"
BROKER_PACKET_PAYLOAD_READY_STATUS = "READY_FOR_EXTERNAL_RUNTIME_ONLY_ORDER_ATTEMPT"

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


def evaluate_oanda_demo_runtime_one_order_execution_exception_v1(
    broker_execution_packet_result: dict | None = None,
    runtime_exception_context: dict | None = None,
    owner_runtime_exception_approval: dict | None = None,
) -> dict:
    broker_packet_result = _mapping(broker_execution_packet_result)
    if not broker_packet_result:
        return _result(
            status=EXCEPTION_BLOCKED_MISSING_BROKER_PACKET,
            blockers=["missing_broker_execution_packet_result"],
            warnings=_warnings(EXCEPTION_BLOCKED_MISSING_BROKER_PACKET),
            broker_packet_result=broker_packet_result,
            runtime_context=_mapping(runtime_exception_context),
            owner_approval=_mapping(owner_runtime_exception_approval),
        )

    runtime_context = _mapping(runtime_exception_context)
    owner_approval = _mapping(owner_runtime_exception_approval)

    unsafe_blockers = _unsafe_execution_blockers(
        broker_packet_result,
        runtime_context,
        owner_approval,
    )
    broker_packet_blockers = _broker_packet_blockers(broker_packet_result)
    runtime_blockers = _runtime_context_blockers(runtime_context)
    owner_blockers = _owner_approval_blockers(owner_approval)

    blockers = _unique(
        unsafe_blockers + broker_packet_blockers + runtime_blockers + owner_blockers
    )
    status = _status(
        unsafe_blockers=unsafe_blockers,
        broker_packet_blockers=broker_packet_blockers,
        runtime_blockers=runtime_blockers,
        owner_blockers=owner_blockers,
    )

    return _result(
        status=status,
        blockers=blockers,
        warnings=_warnings(status),
        broker_packet_result=broker_packet_result,
        runtime_context=runtime_context,
        owner_approval=owner_approval,
    )


def _status(
    *,
    unsafe_blockers: list[str],
    broker_packet_blockers: list[str],
    runtime_blockers: list[str],
    owner_blockers: list[str],
) -> str:
    if unsafe_blockers:
        return EXCEPTION_REJECTED
    if broker_packet_blockers:
        return EXCEPTION_BLOCKED_BROKER_PACKET_NOT_READY
    if runtime_blockers:
        return EXCEPTION_BLOCKED_RUNTIME_CONTEXT
    if owner_blockers:
        return EXCEPTION_BLOCKED_OWNER_APPROVAL
    return EXCEPTION_READY_FOR_MANUAL_RUNTIME_DEMO_ORDER_ATTEMPT


def _broker_packet_blockers(broker_packet_result: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if broker_packet_result.get("status") != BROKER_PACKET_READY_STATUS:
        blockers.append("broker_execution_packet_status_not_ready")

    packet = _broker_packet(broker_packet_result)
    if packet.get("packet_status") != BROKER_PACKET_PAYLOAD_READY_STATUS:
        blockers.append("broker_execution_packet_payload_not_ready")
    if packet.get("broker") != "OANDA_DEMO":
        blockers.append("broker_execution_packet_broker_must_be_oanda_demo")
    if packet.get("environment") != "DEMO":
        blockers.append("broker_execution_packet_environment_must_be_demo")
    if _number(packet.get("order_attempt_limit"), -1) != 1:
        blockers.append("broker_execution_packet_order_attempt_limit_must_be_one")

    required_true = (
        "one_order_only",
        "hard_stop_loss_required",
        "hard_take_profit_required",
        "pre_trade_evidence_required",
        "post_trade_evidence_required",
    )
    required_false = (
        "live_trading_allowed",
        "autonomous_execution_allowed",
    )
    for field in required_true:
        if not _bool(packet.get(field)):
            blockers.append(f"broker_execution_packet_{field}_required")
    for field in required_false:
        if _bool(packet.get(field)):
            blockers.append(f"broker_execution_packet_{field}_must_be_false")

    blockers.extend(_authority_blockers(broker_packet_result, "broker_execution_packet_result"))
    return blockers


def _runtime_context_blockers(runtime_context: Mapping[str, Any]) -> list[str]:
    if not runtime_context:
        return ["missing_runtime_exception_context"]

    required_true = (
        "demo_environment",
        "runtime_only_credentials_present",
        "account_id_runtime_only",
        "token_runtime_only",
        "one_order_only",
        "kill_switch_ready",
        "daily_stop_ready",
        "max_loss_gate_ready",
        "hard_stop_loss_ready",
        "hard_take_profit_ready",
        "pre_trade_evidence_ready",
        "post_trade_evidence_plan_ready",
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
    if runtime_context.get("broker") != "OANDA_DEMO":
        blockers.append("runtime_context_broker_must_be_oanda_demo")
    if runtime_context.get("environment") != "DEMO":
        blockers.append("runtime_context_environment_must_be_demo")
    for field in required_true:
        if not _bool(runtime_context.get(field)):
            blockers.append(f"runtime_context_{field}_required")
    for field in required_false:
        if _bool(runtime_context.get(field)):
            blockers.append(f"runtime_context_{field}_must_be_false")

    if _number(runtime_context.get("max_order_attempts"), -1) != 1:
        blockers.append("runtime_context_max_order_attempts_must_be_one")
    if _number(runtime_context.get("existing_open_orders"), -1) != 0:
        blockers.append("runtime_context_existing_open_orders_must_be_zero")
    if _number(runtime_context.get("existing_pending_orders"), -1) != 0:
        blockers.append("runtime_context_existing_pending_orders_must_be_zero")

    blockers.extend(_authority_blockers(runtime_context, "runtime_context"))
    return blockers


def _owner_approval_blockers(owner_approval: Mapping[str, Any]) -> list[str]:
    if not owner_approval:
        return ["missing_owner_runtime_exception_approval"]

    required_true = (
        "owner_approved_manual_runtime_demo_order_attempt",
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
    broker_packet_result: Mapping[str, Any],
    runtime_context: Mapping[str, Any],
    owner_approval: Mapping[str, Any],
) -> dict[str, Any]:
    allowed = status == EXCEPTION_READY_FOR_MANUAL_RUNTIME_DEMO_ORDER_ATTEMPT
    return {
        "packet_id": PACKET_ID,
        "exception_version": EXCEPTION_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "runtime_exception_summary": _runtime_exception_summary(runtime_context),
        "broker_packet_summary": _broker_packet_summary(broker_packet_result),
        "owner_approval_summary": _owner_approval_summary(owner_approval),
        "allowed_manual_runtime_invocation": allowed,
        "one_order_runtime_contract": _one_order_runtime_contract(
            status,
            broker_packet_result,
        ),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }


def _one_order_runtime_contract(
    status: str,
    broker_packet_result: Mapping[str, Any],
) -> dict[str, Any]:
    packet = _broker_packet(broker_packet_result)
    return {
        "contract_status": "READY_FOR_MANUAL_RUNTIME_INVOCATION"
        if status == EXCEPTION_READY_FOR_MANUAL_RUNTIME_DEMO_ORDER_ATTEMPT
        else "NOT_READY",
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "manual_runtime_invocation_required": True,
        "one_order_only": True,
        "max_order_attempts": 1,
        "live_trading_allowed": False,
        "autonomous_execution_allowed": False,
        "credential_persistence_allowed": False,
        "account_id_persistence_allowed": False,
        "hard_stop_loss_required": True,
        "hard_take_profit_required": True,
        "pre_trade_evidence_required": True,
        "post_trade_evidence_required": True,
        "instrument": packet.get("instrument"),
        "direction": packet.get("direction"),
        "order_type": packet.get("order_type"),
        "time_in_force": packet.get("time_in_force"),
        "planned_entry": packet.get("planned_entry"),
        "stop_loss": packet.get("stop_loss"),
        "take_profit": packet.get("take_profit"),
        "position_size_units": packet.get("position_size_units"),
        "risk_amount": packet.get("risk_amount"),
        "reward_risk_ratio": packet.get("reward_risk_ratio"),
    }


def _runtime_exception_summary(runtime_context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker": _text(runtime_context.get("broker"), "MISSING"),
        "environment": _text(runtime_context.get("environment"), "MISSING"),
        "demo_environment": _bool(runtime_context.get("demo_environment")),
        "live_environment": _bool(runtime_context.get("live_environment")),
        "runtime_only_credentials_present": _bool(
            runtime_context.get("runtime_only_credentials_present")
        ),
        "credential_persistence_detected": _bool(
            runtime_context.get("credential_persistence_detected")
        ),
        "account_id_persistence_detected": _bool(
            runtime_context.get("account_id_persistence_detected")
        ),
        "account_id_runtime_only": _bool(runtime_context.get("account_id_runtime_only")),
        "token_runtime_only": _bool(runtime_context.get("token_runtime_only")),
        "one_order_only": _bool(runtime_context.get("one_order_only")),
        "max_order_attempts": _number(runtime_context.get("max_order_attempts"), 0),
        "existing_open_orders": _number(runtime_context.get("existing_open_orders"), 0),
        "existing_pending_orders": _number(runtime_context.get("existing_pending_orders"), 0),
        "order_already_attempted": _bool(runtime_context.get("order_already_attempted")),
        "manual_runtime_invocation_required": _bool(
            runtime_context.get("manual_runtime_invocation_required")
        ),
    }


def _broker_packet_summary(broker_packet_result: Mapping[str, Any]) -> dict[str, Any]:
    packet = _broker_packet(broker_packet_result)
    return {
        "status": _text(broker_packet_result.get("status"), "MISSING"),
        "packet_status": _text(packet.get("packet_status"), "MISSING"),
        "broker": _text(packet.get("broker"), "MISSING"),
        "environment": _text(packet.get("environment"), "MISSING"),
        "order_attempt_limit": _number(packet.get("order_attempt_limit"), 0),
        "one_order_only": _bool(packet.get("one_order_only")),
        "live_trading_allowed": _bool(packet.get("live_trading_allowed")),
        "autonomous_execution_allowed": _bool(packet.get("autonomous_execution_allowed")),
        "hard_stop_loss_required": _bool(packet.get("hard_stop_loss_required")),
        "hard_take_profit_required": _bool(packet.get("hard_take_profit_required")),
        "pre_trade_evidence_required": _bool(packet.get("pre_trade_evidence_required")),
        "post_trade_evidence_required": _bool(packet.get("post_trade_evidence_required")),
    }


def _owner_approval_summary(owner_approval: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "owner_approved_manual_runtime_demo_order_attempt": _bool(
            owner_approval.get("owner_approved_manual_runtime_demo_order_attempt")
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
        "owner_confirmed_loss_possible": _bool(
            owner_approval.get("owner_confirmed_loss_possible")
        ),
        "owner_confirmed_no_profit_guarantee": _bool(
            owner_approval.get("owner_confirmed_no_profit_guarantee")
        ),
        "owner_confirmed_manual_invocation_required": _bool(
            owner_approval.get("owner_confirmed_manual_invocation_required")
        ),
        "owner_confirmed_no_autonomous_execution": _bool(
            owner_approval.get("owner_confirmed_no_autonomous_execution")
        ),
    }


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


def _broker_packet(broker_packet_result: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(broker_packet_result.get("broker_execution_packet"))


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _warnings(status: str) -> list[str]:
    warnings = [
        "runtime_exception_shell_only",
        "execution_authority_false",
        "no_broker_call_performed",
        "no_credentials_or_account_ids_read_or_persisted",
        "no_order_placement_performed",
    ]
    if status == EXCEPTION_READY_FOR_MANUAL_RUNTIME_DEMO_ORDER_ATTEMPT:
        warnings.append("manual_runtime_invocation_allowed_only_with_one_order_cap")
    return warnings


def _next_safe_action(status: str) -> str:
    return {
        EXCEPTION_BLOCKED_MISSING_BROKER_PACKET: "provide_ready_broker_execution_packet",
        EXCEPTION_BLOCKED_BROKER_PACKET_NOT_READY: (
            "repair_broker_execution_packet_before_runtime_exception"
        ),
        EXCEPTION_BLOCKED_RUNTIME_CONTEXT: "provide_demo_only_runtime_exception_context",
        EXCEPTION_BLOCKED_OWNER_APPROVAL: (
            "complete_owner_runtime_exception_approval_before_manual_invocation"
        ),
        EXCEPTION_READY_FOR_MANUAL_RUNTIME_DEMO_ORDER_ATTEMPT: (
            "manual_runtime_invocation_with_one_order_cap_after_explicit_owner_review"
        ),
        EXCEPTION_REJECTED: "remove_execution_authority_request_before_runtime_exception_review",
    }.get(status, "stop_and_review_runtime_one_order_exception_state")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _number(value: Any, default: float) -> float:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else default


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
