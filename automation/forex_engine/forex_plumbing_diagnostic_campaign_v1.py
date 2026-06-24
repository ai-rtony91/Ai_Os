from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-PLUMBING-DIAGNOSTIC-CAMPAIGN-V1"
CAMPAIGN_VERSION = "v1"

DIAGNOSTIC_BLOCKED_MISSING_INPUTS = "DIAGNOSTIC_BLOCKED_MISSING_INPUTS"
DIAGNOSTIC_BLOCKED_FAILURES = "DIAGNOSTIC_BLOCKED_FAILURES"
DIAGNOSTIC_READY_FOR_OWNER_REVIEW = "DIAGNOSTIC_READY_FOR_OWNER_REVIEW"
DIAGNOSTIC_READY_FOR_DEMO_ATTEMPT_REVIEW = "DIAGNOSTIC_READY_FOR_DEMO_ATTEMPT_REVIEW"
DIAGNOSTIC_REJECTED = "DIAGNOSTIC_REJECTED"

PASS = "PASS"
FAIL = "FAIL"
BLOCKED = "BLOCKED"
NOT_RUN = "NOT_RUN"

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

DIAGNOSTIC_CHECKS = (
    ("end_to_end_dry_run_ticket", "End-to-end dry-run ticket", True),
    ("oanda_demo_read_only_connection_model", "OANDA demo read-only connection readiness model", True),
    ("fake_buy_sell_ticket_replay", "Fake BUY/SELL order-ticket replay", True),
    ("risk_failure_gate", "Risk failure gate test", True),
    ("evidence_capture", "Evidence capture test", True),
    ("overnight_protection", "Overnight protection test", True),
    ("compounding_bucket", "Compounding bucket test", True),
    ("final_owner_click_dry_run_rehearsal", "Final owner-click dry-run rehearsal", True),
    ("demo_micro_trade_readiness_review_only", "Actual OANDA demo micro-trade readiness gate, review-only", True),
    ("morning_proof_review_model", "Morning proof review model", False),
)


def evaluate_forex_plumbing_diagnostic_campaign_v1(
    diagnostic_inputs: dict | None = None,
) -> dict:
    inputs = _mapping(diagnostic_inputs)
    if not inputs:
        return _result(
            status=DIAGNOSTIC_BLOCKED_MISSING_INPUTS,
            blockers=["missing_diagnostic_inputs"],
            warnings=_warnings(DIAGNOSTIC_BLOCKED_MISSING_INPUTS),
            diagnostic_results=_default_results(),
        )

    checks_input = _mapping(inputs.get("checks"))
    if _unsafe_execution_requested(inputs):
        diagnostic_results = _diagnostic_results(checks_input)
        return _result(
            status=DIAGNOSTIC_REJECTED,
            blockers=["unsafe_execution_authority_requested"],
            warnings=_warnings(DIAGNOSTIC_REJECTED),
            diagnostic_results=diagnostic_results,
        )

    diagnostic_results = _diagnostic_results(checks_input)
    blockers = _campaign_blockers(diagnostic_results)
    status = _campaign_status(diagnostic_results, blockers)

    return _result(
        status=status,
        blockers=blockers,
        warnings=_warnings(status),
        diagnostic_results=diagnostic_results,
    )


def _diagnostic_results(checks_input: Mapping[str, Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for check_id, name, required in DIAGNOSTIC_CHECKS:
        check = _mapping(checks_input.get(check_id))
        results.append(_diagnostic_result(check_id, name, required, check))
    return results


def _diagnostic_result(check_id: str, name: str, required: bool, check: Mapping[str, Any]) -> dict[str, Any]:
    if not check:
        return {
            "check_id": check_id,
            "name": name,
            "status": NOT_RUN,
            "required": required,
            "blockers": [f"missing_{check_id}"],
            "evidence_summary": {},
            "next_action": f"provide_{check_id}_diagnostic_evidence",
        }

    blockers = _check_blockers(check_id, check)
    status = _check_status(check, blockers)
    if check_id == "morning_proof_review_model" and _bool(check.get("pending")) and status != PASS:
        status = NOT_RUN
        blockers = ["morning_proof_pending_until_after_overnight_result"]

    return {
        "check_id": check_id,
        "name": name,
        "status": status,
        "required": required,
        "blockers": blockers,
        "evidence_summary": _evidence_summary(check_id, check),
        "next_action": _check_next_action(check_id, status),
    }


def _check_status(check: Mapping[str, Any], blockers: list[str]) -> str:
    explicit_status = _upper(check.get("status"))
    if explicit_status in {PASS, FAIL, BLOCKED, NOT_RUN}:
        if explicit_status == PASS and blockers:
            return BLOCKED
        return explicit_status
    if _bool(check.get("blocked")):
        return BLOCKED
    if _bool(check.get("pending")):
        return NOT_RUN
    if check.get("passed") is False or _bool(check.get("failed")):
        return FAIL
    if _bool(check.get("passed")) and not blockers:
        return PASS
    return NOT_RUN


def _check_blockers(check_id: str, check: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []

    if check_id == "end_to_end_dry_run_ticket":
        if not _bool(check.get("ticket_created")):
            blockers.append("dry_run_ticket_not_created")
        if not _bool(check.get("review_only")):
            blockers.append("dry_run_ticket_must_be_review_only")

    if check_id == "oanda_demo_read_only_connection_model":
        if not _bool(check.get("read_only_model_ready")):
            blockers.append("read_only_connection_model_not_ready")
        if _bool(check.get("broker_network_call_performed")):
            blockers.append("broker_network_call_must_not_be_performed")
        if _bool(check.get("credential_read_performed")):
            blockers.append("credential_read_must_not_be_performed")

    if check_id == "fake_buy_sell_ticket_replay":
        if not _bool(check.get("buy_replay_passed")):
            blockers.append("fake_buy_replay_not_passed")
        if not _bool(check.get("sell_replay_passed")):
            blockers.append("fake_sell_replay_not_passed")

    if check_id == "risk_failure_gate":
        if not _bool(check.get("risk_failure_blocked")):
            blockers.append("risk_failure_not_blocked")
        if not _bool(check.get("stop_loss_failure_blocked")):
            blockers.append("stop_loss_failure_not_blocked")
        if not _bool(check.get("take_profit_failure_blocked")):
            blockers.append("take_profit_failure_not_blocked")

    if check_id == "evidence_capture":
        if not _bool(check.get("pre_trade_capture_ready")):
            blockers.append("pre_trade_capture_not_ready")
        if not _bool(check.get("post_trade_capture_ready")):
            blockers.append("post_trade_capture_not_ready")
        if not _bool(check.get("sanitized_evidence_only")):
            blockers.append("sanitized_evidence_only_required")

    if check_id == "overnight_protection":
        if not _bool(check.get("kill_switch_ready")):
            blockers.append("kill_switch_not_ready")
        if not _bool(check.get("daily_stop_ready")):
            blockers.append("daily_stop_not_ready")
        if not _bool(check.get("max_loss_gate_ready")):
            blockers.append("max_loss_gate_not_ready")
        if not _bool(check.get("overnight_risk_note_ready")):
            blockers.append("overnight_risk_note_not_ready")

    if check_id == "compounding_bucket":
        if not _bool(check.get("bucket_supervisor_ready")):
            blockers.append("bucket_supervisor_not_ready")
        if _bool(check.get("force_trades_to_hit_quota")):
            blockers.append("force_trades_to_hit_quota_must_be_false")
        if not _bool(check.get("eligible_pair_allocation_ready")):
            blockers.append("eligible_pair_allocation_not_ready")

    if check_id == "final_owner_click_dry_run_rehearsal":
        if not _bool(check.get("owner_click_rehearsed")):
            blockers.append("owner_click_not_rehearsed")
        if not _bool(check.get("final_confirmation_required")):
            blockers.append("final_confirmation_required_not_set")
        if _bool(check.get("order_placement_performed")):
            blockers.append("order_placement_must_not_be_performed")

    if check_id == "demo_micro_trade_readiness_review_only":
        if not _bool(check.get("review_only_ready")):
            blockers.append("demo_micro_trade_review_only_not_ready")
        if not _bool(check.get("owner_review_required")):
            blockers.append("owner_review_required_not_set")
        if _execution_authority_true(check):
            blockers.append("demo_micro_trade_execution_authority_must_remain_false")

    if check_id == "morning_proof_review_model" and not _bool(check.get("pending")):
        if not _bool(check.get("proof_review_model_ready")):
            blockers.append("morning_proof_review_model_not_ready")
        if not _bool(check.get("realized_pl_capture_ready")):
            blockers.append("realized_pl_capture_not_ready")

    return blockers


def _campaign_blockers(diagnostic_results: list[dict[str, Any]]) -> list[str]:
    blockers: list[str] = []
    for result in diagnostic_results:
        if result["required"] and result["status"] in {FAIL, BLOCKED, NOT_RUN}:
            blockers.append(f"{result['check_id']}_{result['status'].lower()}")
        if result["required"]:
            blockers.extend(result["blockers"])
    return _unique(blockers)


def _campaign_status(diagnostic_results: list[dict[str, Any]], blockers: list[str]) -> str:
    results_by_id = {result["check_id"]: result for result in diagnostic_results}
    first_eight_pass = all(result["status"] == PASS for result in diagnostic_results[:8])
    check_nine_ready = (
        results_by_id["demo_micro_trade_readiness_review_only"]["status"] == PASS
        and results_by_id["demo_micro_trade_readiness_review_only"]["evidence_summary"].get("review_only_ready") is True
    )
    morning_proof_status = results_by_id["morning_proof_review_model"]["status"]

    if all(result["status"] == PASS for result in diagnostic_results):
        return DIAGNOSTIC_READY_FOR_OWNER_REVIEW
    if first_eight_pass and check_nine_ready and morning_proof_status == NOT_RUN:
        return DIAGNOSTIC_READY_FOR_DEMO_ATTEMPT_REVIEW
    if blockers:
        return DIAGNOSTIC_BLOCKED_FAILURES
    return DIAGNOSTIC_BLOCKED_FAILURES


def _result(
    *,
    status: str,
    blockers: list[str],
    warnings: list[str],
    diagnostic_results: list[dict[str, Any]],
) -> dict:
    pass_count = sum(1 for result in diagnostic_results if result["status"] == PASS)
    fail_count = sum(1 for result in diagnostic_results if result["status"] in {FAIL, BLOCKED})
    return {
        "packet_id": PACKET_ID,
        "campaign_version": CAMPAIGN_VERSION,
        "status": status,
        "blockers": _unique(blockers),
        "warnings": warnings,
        "diagnostic_results": diagnostic_results,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "required_followups": _required_followups(diagnostic_results),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }


def _default_results() -> list[dict[str, Any]]:
    return [
        {
            "check_id": check_id,
            "name": name,
            "status": NOT_RUN,
            "required": required,
            "blockers": [f"missing_{check_id}"],
            "evidence_summary": {},
            "next_action": f"provide_{check_id}_diagnostic_evidence",
        }
        for check_id, name, required in DIAGNOSTIC_CHECKS
    ]


def _required_followups(diagnostic_results: list[dict[str, Any]]) -> list[str]:
    followups: list[str] = []
    for result in diagnostic_results:
        if result["status"] != PASS:
            followups.append(result["next_action"])
    return _unique(followups)


def _evidence_summary(check_id: str, check: Mapping[str, Any]) -> dict[str, Any]:
    summary = _mapping(check.get("evidence_summary"))
    output = {
        "check_id": check_id,
        "review_only": _bool(check.get("review_only")) or _bool(check.get("review_only_ready")),
        "broker_network_call_performed": _bool(check.get("broker_network_call_performed")),
        "order_placement_performed": _bool(check.get("order_placement_performed")),
        "credential_read_performed": _bool(check.get("credential_read_performed")),
    }
    output.update(dict(summary))
    if check_id == "demo_micro_trade_readiness_review_only":
        output["review_only_ready"] = _bool(check.get("review_only_ready"))
        output["order_placement_allowed"] = False
    if check_id == "morning_proof_review_model":
        output["pending_until_after_overnight_result"] = _bool(check.get("pending"))
    return output


def _check_next_action(check_id: str, status: str) -> str:
    if status == PASS:
        return "no_action_required"
    if check_id == "morning_proof_review_model" and status == NOT_RUN:
        return "run_morning_proof_review_after_demo_attempt_result"
    return f"repair_{check_id}_diagnostic_before_demo_attempt_review"


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _warnings(status: str) -> list[str]:
    warnings = [
        "diagnostic_campaign_only",
        "execution_authority_false",
        "no_broker_call_performed",
        "no_credentials_or_account_ids_read",
        "no_order_placement_performed",
    ]
    if status == DIAGNOSTIC_READY_FOR_DEMO_ATTEMPT_REVIEW:
        warnings.append("demo_attempt_still_requires_separate_owner_final_click_packet")
    if status == DIAGNOSTIC_READY_FOR_OWNER_REVIEW:
        warnings.append("owner_review_ready_not_execution_authorized")
    return warnings


def _next_safe_action(status: str) -> str:
    return {
        DIAGNOSTIC_BLOCKED_MISSING_INPUTS: "provide_sanitized_diagnostic_inputs",
        DIAGNOSTIC_BLOCKED_FAILURES: "repair_failed_or_blocked_required_diagnostics",
        DIAGNOSTIC_READY_FOR_DEMO_ATTEMPT_REVIEW: "review_diagnostic_results_before_separate_owner_final_click_order_bridge",
        DIAGNOSTIC_READY_FOR_OWNER_REVIEW: "owner_review_complete_diagnostic_campaign_before_any_separate_demo_attempt_lane",
        DIAGNOSTIC_REJECTED: "remove_any_execution_authority_request_from_diagnostic_inputs",
    }.get(status, "stop_and_review_diagnostic_campaign_state")


def _unsafe_execution_requested(inputs: Mapping[str, Any]) -> bool:
    if _execution_authority_true(inputs):
        return True
    for check in _mapping(inputs.get("checks")).values():
        if _execution_authority_true(_mapping(check)):
            return True
    return False


def _execution_authority_true(payload: Mapping[str, Any]) -> bool:
    authority = _mapping(payload.get("execution_authority"))
    for field in EXECUTION_AUTHORITY_FIELDS:
        if _bool(payload.get(field)) or _bool(authority.get(field)):
            return True
    return False


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _upper(value: Any) -> str:
    return value.strip().upper() if isinstance(value, str) else ""


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
