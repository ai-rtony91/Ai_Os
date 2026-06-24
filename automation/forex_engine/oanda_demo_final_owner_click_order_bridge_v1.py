from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-FINAL-OWNER-CLICK-ORDER-BRIDGE-V1"
BRIDGE_VERSION = "v1"

FINAL_CLICK_BLOCKED_MISSING_DIAGNOSTICS = "FINAL_CLICK_BLOCKED_MISSING_DIAGNOSTICS"
FINAL_CLICK_BLOCKED_DIAGNOSTICS_NOT_READY = "FINAL_CLICK_BLOCKED_DIAGNOSTICS_NOT_READY"
FINAL_CLICK_BLOCKED_ORDER_TICKET = "FINAL_CLICK_BLOCKED_ORDER_TICKET"
FINAL_CLICK_BLOCKED_OWNER_CLICK = "FINAL_CLICK_BLOCKED_OWNER_CLICK"
FINAL_CLICK_BLOCKED_RUNTIME_SAFETY = "FINAL_CLICK_BLOCKED_RUNTIME_SAFETY"
FINAL_CLICK_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTION_REVIEW = (
    "FINAL_CLICK_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTION_REVIEW"
)
FINAL_CLICK_REJECTED = "FINAL_CLICK_REJECTED"

DIAGNOSTIC_READY_STATUS = "DIAGNOSTIC_READY_FOR_DEMO_ATTEMPT_REVIEW"
ORDER_TICKET_READY_STATUS = "ORDER_TICKET_READY_FOR_OWNER_RUNTIME_REVIEW"
ORDER_TICKET_REVIEW_ONLY_STATUS = "REVIEW_ONLY_NOT_EXECUTABLE"
PREPARED_REVIEW_STATUS = "READY_FOR_EXTERNAL_RUNTIME_EXECUTOR_REVIEW_ONLY"

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

FIRST_EIGHT_DIAGNOSTICS = (
    "end_to_end_dry_run_ticket",
    "oanda_demo_read_only_connection_model",
    "fake_buy_sell_ticket_replay",
    "risk_failure_gate",
    "evidence_capture",
    "overnight_protection",
    "compounding_bucket",
    "final_owner_click_dry_run_rehearsal",
)


def evaluate_oanda_demo_final_owner_click_order_bridge_v1(
    plumbing_diagnostic_result: dict | None = None,
    runtime_order_ticket_result: dict | None = None,
    owner_final_click: dict | None = None,
    runtime_safety_context: dict | None = None,
) -> dict:
    diagnostics = _mapping(plumbing_diagnostic_result)
    if not diagnostics:
        return _result(
            status=FINAL_CLICK_BLOCKED_MISSING_DIAGNOSTICS,
            blockers=["missing_plumbing_diagnostic_result"],
            warnings=_warnings(FINAL_CLICK_BLOCKED_MISSING_DIAGNOSTICS),
            diagnostics=diagnostics,
            ticket_result=_mapping(runtime_order_ticket_result),
            owner_click=_mapping(owner_final_click),
            runtime_safety=_mapping(runtime_safety_context),
        )

    ticket_result = _mapping(runtime_order_ticket_result)
    owner_click = _mapping(owner_final_click)
    runtime_safety = _mapping(runtime_safety_context)

    unsafe_blockers = _unsafe_execution_blockers(diagnostics, ticket_result, owner_click, runtime_safety)
    diagnostic_blockers = _diagnostic_blockers(diagnostics)
    ticket_blockers = _ticket_blockers(ticket_result)
    owner_blockers = _owner_click_blockers(owner_click, _order_ticket(ticket_result))
    runtime_blockers = _runtime_safety_blockers(runtime_safety)

    blockers = _unique(
        unsafe_blockers + diagnostic_blockers + ticket_blockers + owner_blockers + runtime_blockers
    )
    status = _status(
        unsafe_blockers=unsafe_blockers,
        diagnostic_blockers=diagnostic_blockers,
        ticket_blockers=ticket_blockers,
        owner_blockers=owner_blockers,
        runtime_blockers=runtime_blockers,
    )

    return _result(
        status=status,
        blockers=blockers,
        warnings=_warnings(status),
        diagnostics=diagnostics,
        ticket_result=ticket_result,
        owner_click=owner_click,
        runtime_safety=runtime_safety,
    )


def _status(
    *,
    unsafe_blockers: list[str],
    diagnostic_blockers: list[str],
    ticket_blockers: list[str],
    owner_blockers: list[str],
    runtime_blockers: list[str],
) -> str:
    if unsafe_blockers:
        return FINAL_CLICK_REJECTED
    if diagnostic_blockers:
        return FINAL_CLICK_BLOCKED_DIAGNOSTICS_NOT_READY
    if ticket_blockers:
        return FINAL_CLICK_BLOCKED_ORDER_TICKET
    if owner_blockers:
        return FINAL_CLICK_BLOCKED_OWNER_CLICK
    if runtime_blockers:
        return FINAL_CLICK_BLOCKED_RUNTIME_SAFETY
    return FINAL_CLICK_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTION_REVIEW


def _diagnostic_blockers(diagnostics: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if diagnostics.get("status") != DIAGNOSTIC_READY_STATUS:
        blockers.append("plumbing_diagnostics_status_not_ready_for_demo_attempt_review")

    blockers.extend(_authority_blockers(diagnostics, "plumbing_diagnostics"))
    results_by_id = {
        _text(result.get("check_id")): _mapping(result)
        for result in _list_of_mappings(diagnostics.get("diagnostic_results"))
    }

    for check_id in FIRST_EIGHT_DIAGNOSTICS:
        if results_by_id.get(check_id, {}).get("status") != "PASS":
            blockers.append(f"{check_id}_must_pass")

    check_nine = results_by_id.get("demo_micro_trade_readiness_review_only", {})
    if check_nine.get("status") != "PASS":
        blockers.append("demo_micro_trade_readiness_review_only_must_pass")
    evidence = _mapping(check_nine.get("evidence_summary"))
    if not _bool(evidence.get("review_only_ready")):
        blockers.append("demo_micro_trade_readiness_must_be_review_only_ready")
    if _bool(evidence.get("order_placement_allowed")):
        blockers.append("diagnostic_order_placement_allowed_must_be_false")

    check_ten = results_by_id.get("morning_proof_review_model", {})
    if check_ten and check_ten.get("status") not in {"NOT_RUN", "PASS"}:
        blockers.append("morning_proof_review_model_must_be_pending_or_pass")
    if check_ten and _bool(check_ten.get("required")) and check_ten.get("status") != "PASS":
        blockers.append("morning_proof_review_model_must_not_be_required_before_attempt")

    return blockers


def _ticket_blockers(ticket_result: Mapping[str, Any]) -> list[str]:
    if not ticket_result:
        return ["missing_runtime_order_ticket_result"]

    blockers: list[str] = []
    if ticket_result.get("status") != ORDER_TICKET_READY_STATUS:
        blockers.append("runtime_order_ticket_status_not_ready")

    blockers.extend(_authority_blockers(ticket_result, "runtime_order_ticket"))
    ticket = _order_ticket(ticket_result)
    expected = {
        "status": ORDER_TICKET_REVIEW_ONLY_STATUS,
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "live_trading_allowed": False,
        "autonomous_order_allowed": False,
        "pre_trade_evidence_required": True,
        "post_trade_evidence_required": True,
        "owner_final_click_required": True,
        "runtime_only_credentials_required": True,
    }
    for field, expected_value in expected.items():
        if ticket.get(field) != expected_value:
            blockers.append(f"order_ticket_{field}_invalid")
    return blockers


def _owner_click_blockers(owner_click: Mapping[str, Any], ticket: Mapping[str, Any]) -> list[str]:
    if not owner_click:
        return ["missing_owner_final_click"]

    required_true = (
        "owner_final_click_required",
        "owner_clicked_final_demo_review",
        "owner_understands_demo_only",
        "owner_understands_no_profit_guarantee",
        "owner_understands_loss_possible",
        "owner_understands_stop_loss_required",
        "owner_understands_take_profit_required",
    )
    required_false = (
        "owner_approves_live_trading",
        "owner_approves_autonomous_execution",
    )

    blockers: list[str] = []
    for field in required_true:
        if not _bool(owner_click.get(field)):
            blockers.append(f"{field}_required")
    for field in required_false:
        if _bool(owner_click.get(field)):
            blockers.append(f"{field}_must_be_false")

    if _bool(ticket.get("hold_allowed_overnight")) and not _bool(
        owner_click.get("owner_approves_overnight_hold_if_ticket_allows")
    ):
        blockers.append("owner_overnight_hold_approval_required_for_overnight_ticket")

    return blockers


def _runtime_safety_blockers(runtime_safety: Mapping[str, Any]) -> list[str]:
    if not runtime_safety:
        return ["missing_runtime_safety_context"]

    required_true = (
        "demo_environment",
        "runtime_only_credentials_present",
        "kill_switch_ready",
        "daily_stop_ready",
        "max_loss_gate_ready",
        "stop_loss_attached_required",
        "take_profit_attached_required",
    )
    required_false = (
        "live_environment",
        "credential_persistence_detected",
        "account_id_persistence_detected",
        "broker_network_call_performed",
        "order_placement_performed",
    )

    blockers: list[str] = []
    if runtime_safety.get("broker") != "OANDA_DEMO":
        blockers.append("runtime_safety_broker_must_be_oanda_demo")
    for field in required_true:
        if not _bool(runtime_safety.get(field)):
            blockers.append(f"runtime_safety_{field}_required")
    for field in required_false:
        if _bool(runtime_safety.get(field)):
            blockers.append(f"runtime_safety_{field}_must_be_false")
    return blockers


def _unsafe_execution_blockers(*payloads: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for index, payload in enumerate(payloads):
        for field in EXECUTION_AUTHORITY_FIELDS:
            if _bool(payload.get(field)) or _bool(_mapping(payload.get("execution_authority")).get(field)):
                blockers.append(f"unsafe_payload_{index}_{field}_true")
    return blockers


def _result(
    *,
    status: str,
    blockers: list[str],
    warnings: list[str],
    diagnostics: Mapping[str, Any],
    ticket_result: Mapping[str, Any],
    owner_click: Mapping[str, Any],
    runtime_safety: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "packet_id": PACKET_ID,
        "bridge_version": BRIDGE_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "final_click_summary": _final_click_summary(owner_click),
        "runtime_safety_summary": _runtime_safety_summary(runtime_safety),
        "prepared_order_review": _prepared_order_review(status, ticket_result, owner_click),
        "required_runtime_actions": _required_runtime_actions(status),
        "required_owner_actions": _required_owner_actions(status),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }


def _prepared_order_review(
    status: str,
    ticket_result: Mapping[str, Any],
    owner_click: Mapping[str, Any],
) -> dict[str, Any]:
    ticket = _order_ticket(ticket_result)
    if status != FINAL_CLICK_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTION_REVIEW:
        return {
            "status": "NOT_READY",
            "broker": "OANDA_DEMO",
            "environment": "DEMO",
            "review_only": True,
            "executable": False,
        }

    return {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "instrument": ticket.get("instrument"),
        "direction": ticket.get("direction"),
        "order_type": ticket.get("order_type"),
        "time_in_force": ticket.get("time_in_force"),
        "planned_entry": ticket.get("planned_entry"),
        "stop_loss": ticket.get("stop_loss"),
        "take_profit": ticket.get("take_profit"),
        "position_size_units": ticket.get("position_size_units"),
        "risk_amount": ticket.get("risk_amount"),
        "reward_risk_ratio": ticket.get("reward_risk_ratio"),
        "hold_allowed_overnight": _bool(ticket.get("hold_allowed_overnight")),
        "final_owner_click_recorded": _bool(owner_click.get("owner_clicked_final_demo_review")),
        "runtime_only_credentials_required": True,
        "status": PREPARED_REVIEW_STATUS,
    }


def _final_click_summary(owner_click: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "owner_final_click_required": _bool(owner_click.get("owner_final_click_required")),
        "owner_clicked_final_demo_review": _bool(owner_click.get("owner_clicked_final_demo_review")),
        "owner_understands_demo_only": _bool(owner_click.get("owner_understands_demo_only")),
        "owner_understands_no_profit_guarantee": _bool(
            owner_click.get("owner_understands_no_profit_guarantee")
        ),
        "owner_understands_loss_possible": _bool(owner_click.get("owner_understands_loss_possible")),
        "owner_understands_stop_loss_required": _bool(
            owner_click.get("owner_understands_stop_loss_required")
        ),
        "owner_understands_take_profit_required": _bool(
            owner_click.get("owner_understands_take_profit_required")
        ),
        "owner_approves_overnight_hold_if_ticket_allows": _bool(
            owner_click.get("owner_approves_overnight_hold_if_ticket_allows")
        ),
        "owner_approves_live_trading": _bool(owner_click.get("owner_approves_live_trading")),
        "owner_approves_autonomous_execution": _bool(
            owner_click.get("owner_approves_autonomous_execution")
        ),
    }


def _runtime_safety_summary(runtime_safety: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker": _text(runtime_safety.get("broker"), "MISSING"),
        "demo_environment": _bool(runtime_safety.get("demo_environment")),
        "live_environment": _bool(runtime_safety.get("live_environment")),
        "runtime_only_credentials_present": _bool(
            runtime_safety.get("runtime_only_credentials_present")
        ),
        "credential_persistence_detected": _bool(
            runtime_safety.get("credential_persistence_detected")
        ),
        "account_id_persistence_detected": _bool(
            runtime_safety.get("account_id_persistence_detected")
        ),
        "kill_switch_ready": _bool(runtime_safety.get("kill_switch_ready")),
        "daily_stop_ready": _bool(runtime_safety.get("daily_stop_ready")),
        "max_loss_gate_ready": _bool(runtime_safety.get("max_loss_gate_ready")),
        "stop_loss_attached_required": _bool(runtime_safety.get("stop_loss_attached_required")),
        "take_profit_attached_required": _bool(
            runtime_safety.get("take_profit_attached_required")
        ),
        "broker_network_call_performed": _bool(
            runtime_safety.get("broker_network_call_performed")
        ),
        "order_placement_performed": _bool(runtime_safety.get("order_placement_performed")),
    }


def _required_runtime_actions(status: str) -> list[str]:
    actions = [
        "inject_runtime_only_demo_credentials_outside_repo",
        "confirm_oanda_demo_environment_outside_repo",
        "attach_stop_loss_and_take_profit_before_any_external_executor_review",
        "capture_sanitized_pre_trade_evidence",
        "capture_sanitized_post_trade_evidence_after_any_separate_approved_runtime_action",
    ]
    if status != FINAL_CLICK_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTION_REVIEW:
        actions.insert(0, "repair_blocked_final_click_bridge_inputs")
    return actions


def _required_owner_actions(status: str) -> list[str]:
    if status == FINAL_CLICK_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTION_REVIEW:
        return [
            "review_prepared_order_object",
            "approve_or_reject_separate_runtime_executor_packet",
            "do_not_merge_execution_authority_into_this_bridge",
        ]
    return ["repair_owner_click_acknowledgements_before_runtime_review"]


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _warnings(status: str) -> list[str]:
    warnings = [
        "review_only_bridge",
        "execution_authority_false",
        "no_broker_call_performed",
        "no_credentials_or_account_ids_read",
        "no_order_placement_performed",
    ]
    if status == FINAL_CLICK_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTION_REVIEW:
        warnings.append("separate_runtime_executor_packet_still_required")
    return warnings


def _next_safe_action(status: str) -> str:
    return {
        FINAL_CLICK_BLOCKED_MISSING_DIAGNOSTICS: "provide_ready_plumbing_diagnostic_result",
        FINAL_CLICK_BLOCKED_DIAGNOSTICS_NOT_READY: "repair_plumbing_diagnostics_before_final_click_review",
        FINAL_CLICK_BLOCKED_ORDER_TICKET: "provide_ready_review_only_runtime_order_ticket",
        FINAL_CLICK_BLOCKED_OWNER_CLICK: "complete_owner_final_click_acknowledgements_without_live_or_autonomous_approval",
        FINAL_CLICK_BLOCKED_RUNTIME_SAFETY: "repair_demo_only_runtime_safety_context",
        FINAL_CLICK_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTION_REVIEW: (
            "review_prepared_order_object_before_separate_runtime_executor_dryrun_packet"
        ),
        FINAL_CLICK_REJECTED: "remove_execution_authority_request_before_review",
    }.get(status, "stop_and_review_final_owner_click_bridge_state")


def _order_ticket(ticket_result: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(ticket_result.get("order_ticket"))


def _authority_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []
    authority = _mapping(payload.get("execution_authority"))
    for field in EXECUTION_AUTHORITY_FIELDS:
        if _bool(payload.get(field)) or _bool(authority.get(field)):
            blockers.append(f"{label}_{field}_must_remain_false")
    return blockers


def _list_of_mappings(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [_mapping(item) for item in value]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
