from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-RUNTIME-EXECUTOR-ONE-ORDER-ONLY-V1"
EXECUTOR_VERSION = "v1"

ONE_ORDER_BLOCKED_MISSING_FINAL_GATE = "ONE_ORDER_BLOCKED_MISSING_FINAL_GATE"
ONE_ORDER_BLOCKED_FINAL_GATE_NOT_READY = "ONE_ORDER_BLOCKED_FINAL_GATE_NOT_READY"
ONE_ORDER_BLOCKED_RUNTIME_CONTEXT = "ONE_ORDER_BLOCKED_RUNTIME_CONTEXT"
ONE_ORDER_BLOCKED_OWNER_CONFIRMATION = "ONE_ORDER_BLOCKED_OWNER_CONFIRMATION"
ONE_ORDER_READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET = (
    "ONE_ORDER_READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET"
)
ONE_ORDER_REJECTED = "ONE_ORDER_REJECTED"

FINAL_GATED_READY_STATUS = "FINAL_GATED_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTOR_PACKET"
FINAL_GATED_PACKAGE_STATUS = "READY_FOR_SEPARATE_RUNTIME_EXECUTOR_PACKET"
ONE_ORDER_CONTRACT_READY_STATUS = "READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET"

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

EXECUTION_REHEARSAL_STEPS = (
    "verify OANDA demo environment",
    "verify no live environment",
    "verify one-order-only state",
    "verify no existing open or pending orders",
    "verify runtime-only credentials are present outside repo",
    "verify stop loss and take profit are ready",
    "verify pre-trade evidence is ready",
    "prepare separate broker execution packet",
    "stop before broker call",
)


def evaluate_oanda_demo_runtime_executor_one_order_only_v1(
    final_gated_result: dict | None = None,
    runtime_one_order_context: dict | None = None,
    owner_runtime_confirmation: dict | None = None,
) -> dict:
    final_gate = _mapping(final_gated_result)
    if not final_gate:
        return _result(
            status=ONE_ORDER_BLOCKED_MISSING_FINAL_GATE,
            blockers=["missing_final_gated_result"],
            warnings=_warnings(ONE_ORDER_BLOCKED_MISSING_FINAL_GATE),
            final_gate=final_gate,
            runtime_context=_mapping(runtime_one_order_context),
            owner_confirmation=_mapping(owner_runtime_confirmation),
        )

    runtime_context = _mapping(runtime_one_order_context)
    owner_confirmation = _mapping(owner_runtime_confirmation)

    unsafe_blockers = _unsafe_execution_blockers(final_gate, runtime_context, owner_confirmation)
    final_gate_blockers = _final_gate_blockers(final_gate)
    runtime_blockers = _runtime_context_blockers(runtime_context)
    owner_blockers = _owner_confirmation_blockers(owner_confirmation)

    blockers = _unique(
        unsafe_blockers + final_gate_blockers + runtime_blockers + owner_blockers
    )
    status = _status(
        unsafe_blockers=unsafe_blockers,
        final_gate_blockers=final_gate_blockers,
        runtime_blockers=runtime_blockers,
        owner_blockers=owner_blockers,
    )

    return _result(
        status=status,
        blockers=blockers,
        warnings=_warnings(status),
        final_gate=final_gate,
        runtime_context=runtime_context,
        owner_confirmation=owner_confirmation,
    )


def _status(
    *,
    unsafe_blockers: list[str],
    final_gate_blockers: list[str],
    runtime_blockers: list[str],
    owner_blockers: list[str],
) -> str:
    if unsafe_blockers:
        return ONE_ORDER_REJECTED
    if final_gate_blockers:
        return ONE_ORDER_BLOCKED_FINAL_GATE_NOT_READY
    if runtime_blockers:
        return ONE_ORDER_BLOCKED_RUNTIME_CONTEXT
    if owner_blockers:
        return ONE_ORDER_BLOCKED_OWNER_CONFIRMATION
    return ONE_ORDER_READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET


def _final_gate_blockers(final_gate: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if final_gate.get("status") != FINAL_GATED_READY_STATUS:
        blockers.append("final_gated_status_not_ready")
    package = _prepared_runtime_package(final_gate)
    if package.get("package_status") != FINAL_GATED_PACKAGE_STATUS:
        blockers.append("prepared_runtime_package_status_not_ready")
    blockers.extend(_authority_blockers(final_gate, "final_gated_result"))
    return blockers


def _runtime_context_blockers(runtime_context: Mapping[str, Any]) -> list[str]:
    if not runtime_context:
        return ["missing_runtime_one_order_context"]

    required_true = (
        "demo_environment",
        "runtime_only_credentials_present",
        "one_order_only",
        "kill_switch_ready",
        "daily_stop_ready",
        "max_loss_gate_ready",
        "hard_stop_loss_ready",
        "hard_take_profit_ready",
        "pre_trade_evidence_ready",
        "post_trade_evidence_plan_ready",
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

    if _number(runtime_context.get("existing_open_orders"), -1) != 0:
        blockers.append("runtime_context_existing_open_orders_must_be_zero")
    if _number(runtime_context.get("existing_pending_orders"), -1) != 0:
        blockers.append("runtime_context_existing_pending_orders_must_be_zero")

    blockers.extend(_authority_blockers(runtime_context, "runtime_context"))
    return blockers


def _owner_confirmation_blockers(owner_confirmation: Mapping[str, Any]) -> list[str]:
    if not owner_confirmation:
        return ["missing_owner_runtime_confirmation"]

    required_true = (
        "owner_confirmed_demo_only",
        "owner_confirmed_one_order_only",
        "owner_confirmed_no_live_money",
        "owner_confirmed_stop_loss",
        "owner_confirmed_take_profit",
        "owner_confirmed_loss_possible",
        "owner_confirmed_no_profit_guarantee",
        "owner_confirmed_runtime_credentials_outside_repo",
        "owner_confirmed_no_autonomous_execution",
        "owner_confirmed_separate_broker_execution_packet_required",
    )

    blockers: list[str] = []
    for field in required_true:
        if not _bool(owner_confirmation.get(field)):
            blockers.append(f"{field}_required")
    blockers.extend(_authority_blockers(owner_confirmation, "owner_confirmation"))
    return blockers


def _result(
    *,
    status: str,
    blockers: list[str],
    warnings: list[str],
    final_gate: Mapping[str, Any],
    runtime_context: Mapping[str, Any],
    owner_confirmation: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "packet_id": PACKET_ID,
        "executor_version": EXECUTOR_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "one_order_contract": _one_order_contract(status, final_gate),
        "runtime_context_summary": _runtime_context_summary(runtime_context),
        "owner_confirmation_summary": _owner_confirmation_summary(owner_confirmation),
        "execution_rehearsal": _execution_rehearsal(status),
        "required_runtime_actions": _required_runtime_actions(status),
        "required_owner_actions": _required_owner_actions(status),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }


def _one_order_contract(status: str, final_gate: Mapping[str, Any]) -> dict[str, Any]:
    package = _prepared_runtime_package(final_gate)
    contract = {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "contract_status": "NOT_READY",
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
        "morning_proof_required_if_overnight": True,
        "instrument": package.get("instrument"),
        "direction": package.get("direction"),
        "order_type": package.get("order_type"),
        "time_in_force": package.get("time_in_force"),
        "planned_entry": package.get("planned_entry"),
        "stop_loss": package.get("stop_loss"),
        "take_profit": package.get("take_profit"),
        "position_size_units": package.get("position_size_units"),
        "risk_amount": package.get("risk_amount"),
        "reward_risk_ratio": package.get("reward_risk_ratio"),
        "hold_allowed_overnight": _bool(package.get("hold_allowed_overnight")),
    }
    if status == ONE_ORDER_READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET:
        contract["contract_status"] = ONE_ORDER_CONTRACT_READY_STATUS
    return contract


def _runtime_context_summary(runtime_context: Mapping[str, Any]) -> dict[str, Any]:
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
        "one_order_only": _bool(runtime_context.get("one_order_only")),
        "existing_open_orders": _number(runtime_context.get("existing_open_orders"), 0),
        "existing_pending_orders": _number(runtime_context.get("existing_pending_orders"), 0),
        "order_already_attempted": _bool(runtime_context.get("order_already_attempted")),
        "kill_switch_ready": _bool(runtime_context.get("kill_switch_ready")),
        "daily_stop_ready": _bool(runtime_context.get("daily_stop_ready")),
        "max_loss_gate_ready": _bool(runtime_context.get("max_loss_gate_ready")),
        "hard_stop_loss_ready": _bool(runtime_context.get("hard_stop_loss_ready")),
        "hard_take_profit_ready": _bool(runtime_context.get("hard_take_profit_ready")),
        "pre_trade_evidence_ready": _bool(runtime_context.get("pre_trade_evidence_ready")),
        "post_trade_evidence_plan_ready": _bool(
            runtime_context.get("post_trade_evidence_plan_ready")
        ),
        "broker_network_call_performed": _bool(
            runtime_context.get("broker_network_call_performed")
        ),
        "order_placement_performed": _bool(runtime_context.get("order_placement_performed")),
    }


def _owner_confirmation_summary(owner_confirmation: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "owner_confirmed_demo_only": _bool(owner_confirmation.get("owner_confirmed_demo_only")),
        "owner_confirmed_one_order_only": _bool(
            owner_confirmation.get("owner_confirmed_one_order_only")
        ),
        "owner_confirmed_no_live_money": _bool(
            owner_confirmation.get("owner_confirmed_no_live_money")
        ),
        "owner_confirmed_stop_loss": _bool(owner_confirmation.get("owner_confirmed_stop_loss")),
        "owner_confirmed_take_profit": _bool(
            owner_confirmation.get("owner_confirmed_take_profit")
        ),
        "owner_confirmed_loss_possible": _bool(
            owner_confirmation.get("owner_confirmed_loss_possible")
        ),
        "owner_confirmed_no_profit_guarantee": _bool(
            owner_confirmation.get("owner_confirmed_no_profit_guarantee")
        ),
        "owner_confirmed_runtime_credentials_outside_repo": _bool(
            owner_confirmation.get("owner_confirmed_runtime_credentials_outside_repo")
        ),
        "owner_confirmed_no_autonomous_execution": _bool(
            owner_confirmation.get("owner_confirmed_no_autonomous_execution")
        ),
        "owner_confirmed_separate_broker_execution_packet_required": _bool(
            owner_confirmation.get("owner_confirmed_separate_broker_execution_packet_required")
        ),
    }


def _execution_rehearsal(status: str) -> dict[str, Any]:
    return {
        "status": "REHEARSAL_READY"
        if status == ONE_ORDER_READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET
        else "REHEARSAL_BLOCKED",
        "steps": list(EXECUTION_REHEARSAL_STEPS),
        "broker_call_performed": False,
        "order_placement_performed": False,
    }


def _required_runtime_actions(status: str) -> list[str]:
    actions = [
        "run separate broker execution packet",
        "inject credentials runtime-only outside repo",
        "confirm OANDA demo account only",
        "submit no more than one order attempt",
        "attach hard stop loss",
        "attach hard take profit",
        "capture pre-trade evidence",
        "capture post-trade evidence",
        "stop after one order attempt",
    ]
    if status != ONE_ORDER_READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET:
        return ["repair blocked one-order-only contract inputs"] + actions
    return actions


def _required_owner_actions(status: str) -> list[str]:
    actions = [
        "approve separate broker execution packet",
        "confirm demo-only",
        "confirm no live money",
        "confirm one order only",
        "confirm stop loss",
        "confirm take profit",
        "confirm loss possible",
        "confirm no profit guarantee",
    ]
    if status != ONE_ORDER_READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET:
        return ["repair owner confirmation before broker execution packet review"] + actions
    return actions


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


def _prepared_runtime_package(final_gate: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(final_gate.get("prepared_runtime_package"))


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _warnings(status: str) -> list[str]:
    warnings = [
        "one_order_contract_only",
        "execution_authority_false",
        "no_broker_call_performed",
        "no_credentials_or_account_ids_read_or_persisted",
        "no_order_placement_performed",
    ]
    if status == ONE_ORDER_READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET:
        warnings.append("separate_broker_execution_packet_still_required")
    return warnings


def _next_safe_action(status: str) -> str:
    return {
        ONE_ORDER_BLOCKED_MISSING_FINAL_GATE: "provide_ready_final_gated_runtime_package",
        ONE_ORDER_BLOCKED_FINAL_GATE_NOT_READY: "repair_final_gated_runtime_package_before_one_order_contract",
        ONE_ORDER_BLOCKED_RUNTIME_CONTEXT: "provide_demo_only_one_order_runtime_context",
        ONE_ORDER_BLOCKED_OWNER_CONFIRMATION: "complete_owner_runtime_confirmation_without_live_or_autonomous_authority",
        ONE_ORDER_READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET: (
            "owner_review_separate_broker_execution_packet_before_any_oanda_call"
        ),
        ONE_ORDER_REJECTED: "remove_execution_authority_request_before_one_order_contract_review",
    }.get(status, "stop_and_review_one_order_only_executor_state")


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
