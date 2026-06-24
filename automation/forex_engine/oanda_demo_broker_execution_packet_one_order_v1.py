from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-BROKER-EXECUTION-PACKET-ONE-ORDER-V1"
EXECUTION_PACKET_VERSION = "v1"

BROKER_PACKET_BLOCKED_MISSING_ONE_ORDER_CONTRACT = (
    "BROKER_PACKET_BLOCKED_MISSING_ONE_ORDER_CONTRACT"
)
BROKER_PACKET_BLOCKED_ONE_ORDER_CONTRACT_NOT_READY = (
    "BROKER_PACKET_BLOCKED_ONE_ORDER_CONTRACT_NOT_READY"
)
BROKER_PACKET_BLOCKED_BROKER_CONTEXT = "BROKER_PACKET_BLOCKED_BROKER_CONTEXT"
BROKER_PACKET_BLOCKED_OWNER_APPROVAL = "BROKER_PACKET_BLOCKED_OWNER_APPROVAL"
BROKER_PACKET_READY_FOR_SEPARATE_RUNTIME_ONLY_DEMO_ORDER_ATTEMPT = (
    "BROKER_PACKET_READY_FOR_SEPARATE_RUNTIME_ONLY_DEMO_ORDER_ATTEMPT"
)
BROKER_PACKET_REJECTED = "BROKER_PACKET_REJECTED"

ONE_ORDER_READY_STATUS = "ONE_ORDER_READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET"
ONE_ORDER_CONTRACT_READY_STATUS = "READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET"
BROKER_PACKET_READY_STATUS = "READY_FOR_EXTERNAL_RUNTIME_ONLY_ORDER_ATTEMPT"

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

PRE_TRADE_EVIDENCE_REQUIREMENTS = (
    "broker_environment",
    "instrument",
    "direction",
    "order_type",
    "planned_entry",
    "stop_loss",
    "take_profit",
    "position_size_units",
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


def evaluate_oanda_demo_broker_execution_packet_one_order_v1(
    one_order_contract_result: dict | None = None,
    broker_execution_context: dict | None = None,
    owner_broker_execution_approval: dict | None = None,
) -> dict:
    one_order = _mapping(one_order_contract_result)
    if not one_order:
        return _result(
            status=BROKER_PACKET_BLOCKED_MISSING_ONE_ORDER_CONTRACT,
            blockers=["missing_one_order_contract_result"],
            warnings=_warnings(BROKER_PACKET_BLOCKED_MISSING_ONE_ORDER_CONTRACT),
            one_order=one_order,
            broker_context=_mapping(broker_execution_context),
            owner_approval=_mapping(owner_broker_execution_approval),
        )

    broker_context = _mapping(broker_execution_context)
    owner_approval = _mapping(owner_broker_execution_approval)

    unsafe_blockers = _unsafe_execution_blockers(one_order, broker_context, owner_approval)
    one_order_blockers = _one_order_blockers(one_order)
    broker_context_blockers = _broker_context_blockers(broker_context)
    owner_approval_blockers = _owner_approval_blockers(owner_approval)

    blockers = _unique(
        unsafe_blockers + one_order_blockers + broker_context_blockers + owner_approval_blockers
    )
    status = _status(
        unsafe_blockers=unsafe_blockers,
        one_order_blockers=one_order_blockers,
        broker_context_blockers=broker_context_blockers,
        owner_approval_blockers=owner_approval_blockers,
    )

    return _result(
        status=status,
        blockers=blockers,
        warnings=_warnings(status),
        one_order=one_order,
        broker_context=broker_context,
        owner_approval=owner_approval,
    )


def _status(
    *,
    unsafe_blockers: list[str],
    one_order_blockers: list[str],
    broker_context_blockers: list[str],
    owner_approval_blockers: list[str],
) -> str:
    if unsafe_blockers:
        return BROKER_PACKET_REJECTED
    if one_order_blockers:
        return BROKER_PACKET_BLOCKED_ONE_ORDER_CONTRACT_NOT_READY
    if broker_context_blockers:
        return BROKER_PACKET_BLOCKED_BROKER_CONTEXT
    if owner_approval_blockers:
        return BROKER_PACKET_BLOCKED_OWNER_APPROVAL
    return BROKER_PACKET_READY_FOR_SEPARATE_RUNTIME_ONLY_DEMO_ORDER_ATTEMPT


def _one_order_blockers(one_order: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if one_order.get("status") != ONE_ORDER_READY_STATUS:
        blockers.append("one_order_contract_status_not_ready")
    contract = _one_order_contract(one_order)
    if contract.get("contract_status") != ONE_ORDER_CONTRACT_READY_STATUS:
        blockers.append("one_order_contract_payload_not_ready")
    blockers.extend(_authority_blockers(one_order, "one_order_contract_result"))
    return blockers


def _broker_context_blockers(broker_context: Mapping[str, Any]) -> list[str]:
    if not broker_context:
        return ["missing_broker_execution_context"]

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
    if broker_context.get("broker") != "OANDA_DEMO":
        blockers.append("broker_context_broker_must_be_oanda_demo")
    if broker_context.get("environment") != "DEMO":
        blockers.append("broker_context_environment_must_be_demo")
    for field in required_true:
        if not _bool(broker_context.get(field)):
            blockers.append(f"broker_context_{field}_required")
    for field in required_false:
        if _bool(broker_context.get(field)):
            blockers.append(f"broker_context_{field}_must_be_false")

    if _number(broker_context.get("max_order_attempts"), -1) != 1:
        blockers.append("broker_context_max_order_attempts_must_be_one")
    if _number(broker_context.get("existing_open_orders"), -1) != 0:
        blockers.append("broker_context_existing_open_orders_must_be_zero")
    if _number(broker_context.get("existing_pending_orders"), -1) != 0:
        blockers.append("broker_context_existing_pending_orders_must_be_zero")

    blockers.extend(_authority_blockers(broker_context, "broker_context"))
    return blockers


def _owner_approval_blockers(owner_approval: Mapping[str, Any]) -> list[str]:
    if not owner_approval:
        return ["missing_owner_broker_execution_approval"]

    required_true = (
        "owner_approved_separate_runtime_demo_order_attempt",
        "owner_confirmed_demo_only",
        "owner_confirmed_no_live_money",
        "owner_confirmed_one_order_only",
        "owner_confirmed_max_one_attempt",
        "owner_confirmed_stop_loss",
        "owner_confirmed_take_profit",
        "owner_confirmed_loss_possible",
        "owner_confirmed_no_profit_guarantee",
        "owner_confirmed_runtime_credentials_outside_repo",
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
    one_order: Mapping[str, Any],
    broker_context: Mapping[str, Any],
    owner_approval: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "packet_id": PACKET_ID,
        "execution_packet_version": EXECUTION_PACKET_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "broker_execution_packet": _broker_execution_packet(status, one_order),
        "broker_context_summary": _broker_context_summary(broker_context),
        "owner_approval_summary": _owner_approval_summary(owner_approval),
        "pre_trade_evidence_requirements": list(PRE_TRADE_EVIDENCE_REQUIREMENTS),
        "post_trade_evidence_requirements": list(POST_TRADE_EVIDENCE_REQUIREMENTS),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }


def _broker_execution_packet(status: str, one_order: Mapping[str, Any]) -> dict[str, Any]:
    contract = _one_order_contract(one_order)
    packet = {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "packet_status": "NOT_READY",
        "order_attempt_limit": 1,
        "one_order_only": True,
        "live_trading_allowed": False,
        "autonomous_execution_allowed": False,
        "credential_persistence_allowed": False,
        "account_id_persistence_allowed": False,
        "hard_stop_loss_required": True,
        "hard_take_profit_required": True,
        "pre_trade_evidence_required": True,
        "post_trade_evidence_required": True,
        "stop_after_order_attempt": True,
        "morning_proof_required_if_overnight": True,
        "instrument": contract.get("instrument"),
        "direction": contract.get("direction"),
        "order_type": contract.get("order_type"),
        "time_in_force": contract.get("time_in_force"),
        "planned_entry": contract.get("planned_entry"),
        "stop_loss": contract.get("stop_loss"),
        "take_profit": contract.get("take_profit"),
        "position_size_units": contract.get("position_size_units"),
        "risk_amount": contract.get("risk_amount"),
        "reward_risk_ratio": contract.get("reward_risk_ratio"),
        "hold_allowed_overnight": _bool(contract.get("hold_allowed_overnight")),
    }
    if status == BROKER_PACKET_READY_FOR_SEPARATE_RUNTIME_ONLY_DEMO_ORDER_ATTEMPT:
        packet["packet_status"] = BROKER_PACKET_READY_STATUS
    return packet


def _broker_context_summary(broker_context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker": _text(broker_context.get("broker"), "MISSING"),
        "environment": _text(broker_context.get("environment"), "MISSING"),
        "demo_environment": _bool(broker_context.get("demo_environment")),
        "live_environment": _bool(broker_context.get("live_environment")),
        "runtime_only_credentials_present": _bool(
            broker_context.get("runtime_only_credentials_present")
        ),
        "credential_persistence_detected": _bool(
            broker_context.get("credential_persistence_detected")
        ),
        "account_id_persistence_detected": _bool(
            broker_context.get("account_id_persistence_detected")
        ),
        "one_order_only": _bool(broker_context.get("one_order_only")),
        "max_order_attempts": _number(broker_context.get("max_order_attempts"), 0),
        "existing_open_orders": _number(broker_context.get("existing_open_orders"), 0),
        "existing_pending_orders": _number(broker_context.get("existing_pending_orders"), 0),
        "order_already_attempted": _bool(broker_context.get("order_already_attempted")),
        "kill_switch_ready": _bool(broker_context.get("kill_switch_ready")),
        "daily_stop_ready": _bool(broker_context.get("daily_stop_ready")),
        "max_loss_gate_ready": _bool(broker_context.get("max_loss_gate_ready")),
        "hard_stop_loss_ready": _bool(broker_context.get("hard_stop_loss_ready")),
        "hard_take_profit_ready": _bool(broker_context.get("hard_take_profit_ready")),
        "pre_trade_evidence_ready": _bool(broker_context.get("pre_trade_evidence_ready")),
        "post_trade_evidence_plan_ready": _bool(
            broker_context.get("post_trade_evidence_plan_ready")
        ),
        "broker_network_call_performed": _bool(
            broker_context.get("broker_network_call_performed")
        ),
        "order_placement_performed": _bool(broker_context.get("order_placement_performed")),
    }


def _owner_approval_summary(owner_approval: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "owner_approved_separate_runtime_demo_order_attempt": _bool(
            owner_approval.get("owner_approved_separate_runtime_demo_order_attempt")
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
        "owner_confirmed_take_profit": _bool(owner_approval.get("owner_confirmed_take_profit")),
        "owner_confirmed_loss_possible": _bool(
            owner_approval.get("owner_confirmed_loss_possible")
        ),
        "owner_confirmed_no_profit_guarantee": _bool(
            owner_approval.get("owner_confirmed_no_profit_guarantee")
        ),
        "owner_confirmed_runtime_credentials_outside_repo": _bool(
            owner_approval.get("owner_confirmed_runtime_credentials_outside_repo")
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


def _one_order_contract(one_order: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(one_order.get("one_order_contract"))


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _warnings(status: str) -> list[str]:
    warnings = [
        "broker_execution_packet_model_only",
        "execution_authority_false",
        "no_broker_call_performed",
        "no_credentials_or_account_ids_read_or_persisted",
        "no_order_placement_performed",
    ]
    if status == BROKER_PACKET_READY_FOR_SEPARATE_RUNTIME_ONLY_DEMO_ORDER_ATTEMPT:
        warnings.append("separate_runtime_only_order_attempt_still_required")
    return warnings


def _next_safe_action(status: str) -> str:
    return {
        BROKER_PACKET_BLOCKED_MISSING_ONE_ORDER_CONTRACT: "provide_ready_one_order_contract_result",
        BROKER_PACKET_BLOCKED_ONE_ORDER_CONTRACT_NOT_READY: (
            "repair_one_order_contract_before_broker_packet"
        ),
        BROKER_PACKET_BLOCKED_BROKER_CONTEXT: "provide_demo_only_broker_execution_context",
        BROKER_PACKET_BLOCKED_OWNER_APPROVAL: (
            "complete_owner_broker_execution_approval_without_live_or_autonomous_authority"
        ),
        BROKER_PACKET_READY_FOR_SEPARATE_RUNTIME_ONLY_DEMO_ORDER_ATTEMPT: (
            "owner_review_separate_runtime_only_demo_order_attempt_packet"
        ),
        BROKER_PACKET_REJECTED: "remove_execution_authority_request_before_broker_packet_review",
    }.get(status, "stop_and_review_broker_execution_packet_state")


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
