"""Forex Completion Campaign Part 2 metadata finisher evaluator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.forex_22h6d_supervised_operation_readiness_v1 import (
    TWENTY_TWO_HOUR_SIX_DAY_READINESS_PASSED,
    evaluate_forex_22h6d_supervised_operation_readiness_v1,
)
from automation.forex_engine.forex_post_execution_review_loop_v1 import (
    POST_EXECUTION_REVIEW_LOOP_READY,
    POST_EXECUTION_REVIEW_NOT_APPLICABLE_METADATA_ONLY,
    evaluate_forex_post_execution_review_loop_v1,
)
from automation.forex_engine.oanda_demo_owner_approved_one_order_protected_runtime_execution_v1 import (
    PROTECTED_ONE_ORDER_GATE_CLEARED,
    _bool,
    _number,
    _text,
    find_sensitive_data_blockers,
    hard_false_result,
    safety_false_result,
    safety_summary,
    unique,
)
from automation.forex_engine.owner_runtime_credential_session_bridge_v1 import (
    READY_FOR_OWNER_RUNTIME_CREDENTIAL_ENTRY_REVIEW,
    RUNTIME_CREDENTIAL_SESSION_BRIDGE_READY,
    evaluate_owner_runtime_credential_session_bridge_v1,
)


SCHEMA = "AIOS_FOREX_COMPLETION_CAMPAIGN_PART2_V1"
MODE = "READ_ONLY_METADATA_ONLY_FOREX_COMPLETION_CAMPAIGN_PART2"

FOREX_COMPLETION_CAMPAIGN_PART2_READY_FOR_OWNER_VALIDATION = (
    "FOREX_COMPLETION_CAMPAIGN_PART2_READY_FOR_OWNER_VALIDATION"
)
FOREX_COMPLETION_CAMPAIGN_PART2_READY_FOR_100_PLUS_REVIEW = (
    "FOREX_COMPLETION_CAMPAIGN_PART2_READY_FOR_100_PLUS_REVIEW"
)
FOREX_COMPLETION_CAMPAIGN_PART2_CONTINUE_EVIDENCE_CAPTURE = (
    "FOREX_COMPLETION_CAMPAIGN_PART2_CONTINUE_EVIDENCE_CAPTURE"
)
BLOCKED_BY_PROFIT_PROOF = "BLOCKED_BY_PROFIT_PROOF"
BLOCKED_BY_RETURN_TARGET_EVIDENCE = "BLOCKED_BY_RETURN_TARGET_EVIDENCE"
BLOCKED_BY_BROKER_RUNTIME_EVIDENCE = "BLOCKED_BY_BROKER_RUNTIME_EVIDENCE"
BLOCKED_BY_SAFETY_REAL_MONEY_GATE = "BLOCKED_BY_SAFETY_REAL_MONEY_GATE"
BLOCKED_BY_DASHBOARD_OWNER_CONTROL = "BLOCKED_BY_DASHBOARD_OWNER_CONTROL"
BLOCKED_BY_RUNTIME_CREDENTIAL_SESSION_BRIDGE = (
    "BLOCKED_BY_RUNTIME_CREDENTIAL_SESSION_BRIDGE"
)
BLOCKED_BY_PROTECTED_RUNTIME_EXECUTION_GATE = (
    "BLOCKED_BY_PROTECTED_RUNTIME_EXECUTION_GATE"
)
BLOCKED_BY_POST_EXECUTION_REVIEW_LOOP = "BLOCKED_BY_POST_EXECUTION_REVIEW_LOOP"
BLOCKED_BY_22H_6D_READINESS = "BLOCKED_BY_22H_6D_READINESS"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_PACKET_OWNER_VALIDATION = (
    "AIOS_FOREX_COMPLETION_CAMPAIGN_PART3_OWNER_VALIDATION_AND_PR_LANDING_V1"
)

PROTECTED_READY_STATUSES = frozenset({PROTECTED_ONE_ORDER_GATE_CLEARED})
CREDENTIAL_READY_STATUSES = frozenset(
    {
        RUNTIME_CREDENTIAL_SESSION_BRIDGE_READY,
        READY_FOR_OWNER_RUNTIME_CREDENTIAL_ENTRY_REVIEW,
    }
)
POST_REVIEW_READY_STATUSES = frozenset(
    {POST_EXECUTION_REVIEW_LOOP_READY, POST_EXECUTION_REVIEW_NOT_APPLICABLE_METADATA_ONLY}
)
RETURN_TARGET_REVIEW_STATUSES = frozenset({"PARTIAL", "REVIEW_REQUIRED"})
RETURN_TARGET_ALLOWED_STATUSES = frozenset(
    {"PROVEN", "PARTIAL", "REVIEW_REQUIRED", "BLOCKED"}
)
PROFIT_QUALITY_ALLOWED = frozenset({"PROVEN", "REVIEW_READY"})
OANDA_MODES = frozenset(
    {"PRACTICE", "DEMO", "OANDA_DEMO", "LIVE_EXCEPTION_REVIEW_ONLY"}
)
GENERATED_RESULT_FIELDS = frozenset(
    {
        "live_execution_and_capital_operation_campaign_result",
        "protected_runtime_execution_result",
        "credential_session_bridge_result",
        "post_execution_review_loop_result",
        "supervised_operation_readiness_result",
    }
)
RAW_SENSITIVE_KEYS = frozenset({"token"})


def evaluate_forex_completion_campaign_part2_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Evaluate Part 2 owner-validation readiness from sanitized metadata."""

    source = payload if isinstance(payload, Mapping) else {}
    sensitive_data_blockers = _part2_sensitive_data_blockers(source)
    sensitive_data_detected = bool(sensitive_data_blockers)

    protected_result = _protected_result(source)
    credential_result = _credential_result(source)
    post_review_result = _post_review_result(source)
    readiness_result = _readiness_result(source)
    protected_summary = _protected_summary(protected_result)
    credential_summary = _credential_summary(credential_result)
    post_review_summary = _post_review_summary(post_review_result)
    supervised_summary = _supervised_summary(readiness_result)

    profit_lane = _profit_proof_lane(_mapping(source.get("profit_proof_metadata")))
    return_lane = _return_target_validation_lane(
        _mapping(source.get("return_target_validation_metadata"))
    )
    broker_lane = _broker_runtime_evidence_lane(
        _mapping(source.get("broker_runtime_evidence_metadata")),
        source=source,
        protected_summary=protected_summary,
        credential_summary=credential_summary,
    )
    safety_lane = _safety_real_money_gate_lane(
        _mapping(source.get("safety_real_money_gate_metadata"))
    )
    dashboard_lane = _dashboard_owner_control_lane(
        _mapping(source.get("dashboard_truth_owner_control_metadata"))
    )
    capital_operation_summary = _capital_operation_summary(source)
    sos_summary = _sos_summary(source)

    five_lane_summary = {
        "profit_proof": profit_lane["passed"],
        "return_target_validation": return_lane["passed"],
        "broker_runtime_evidence": broker_lane["passed"],
        "safety_real_money_gate": safety_lane["passed"],
        "dashboard_truth_owner_control": dashboard_lane["passed"],
    }
    completion_score = _completion_score(
        five_lane_summary=five_lane_summary,
        protected_summary=protected_summary,
        credential_summary=credential_summary,
        post_review_summary=post_review_summary,
        supervised_summary=supervised_summary,
        capital_operation_summary=capital_operation_summary,
        sos_summary=sos_summary,
    )
    status, blockers = _campaign_status(
        source=source,
        sensitive_data_blockers=sensitive_data_blockers,
        protected_summary=protected_summary,
        credential_summary=credential_summary,
        post_review_summary=post_review_summary,
        supervised_summary=supervised_summary,
        profit_lane=profit_lane,
        return_lane=return_lane,
        broker_lane=broker_lane,
        safety_lane=safety_lane,
        dashboard_lane=dashboard_lane,
        completion_score=completion_score,
    )
    campaign_ready = status in {
        FOREX_COMPLETION_CAMPAIGN_PART2_READY_FOR_OWNER_VALIDATION,
        FOREX_COMPLETION_CAMPAIGN_PART2_READY_FOR_100_PLUS_REVIEW,
    }
    next_best_packet = _next_best_packet(status)

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "campaign_status": status,
        "campaign_ready": campaign_ready,
        "completion_score": completion_score,
        "completion_band": _completion_band(completion_score),
        "current_readiness_estimate": _current_readiness_estimate(completion_score),
        "owner_decision_required": True,
        "approval_token_required": True,
        "read_only": True,
        "metadata_only": True,
        "five_lane_summary": five_lane_summary,
        "profit_proof_lane": profit_lane,
        "return_target_validation_lane": return_lane,
        "broker_runtime_evidence_lane": broker_lane,
        "safety_real_money_gate_lane": safety_lane,
        "dashboard_truth_owner_control_lane": dashboard_lane,
        "protected_runtime_summary": protected_summary,
        "credential_session_bridge_summary": credential_summary,
        "post_execution_review_summary": post_review_summary,
        "supervised_operation_readiness_summary": supervised_summary,
        "capital_operation_summary": capital_operation_summary,
        "sos_summary": sos_summary,
        "owner_action_queue": _owner_action_queue(blockers, next_best_packet),
        "campaign_blockers": unique(blockers),
        "missing_inputs": _missing_inputs(
            profit_lane,
            return_lane,
            broker_lane,
            safety_lane,
            dashboard_lane,
            protected_summary,
            credential_summary,
            post_review_summary,
            supervised_summary,
        ),
        "sensitive_data_detected": sensitive_data_detected,
        "sensitive_data_blockers": list(sensitive_data_blockers),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": _safe_manual_next_action(status),
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "campaign_status": status,
            "campaign_ready": campaign_ready,
            "completion_score": completion_score,
            "input_redacted": sensitive_data_detected,
            "read_only": True,
            "metadata_only": True,
            **hard_false_result(),
            **safety_false_result(),
        },
        "safety": safety_summary(),
        **hard_false_result(),
        **safety_false_result(),
    }


def _protected_result(source: Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(source.get("protected_runtime_execution_result"), Mapping):
        return _mapping(source.get("protected_runtime_execution_result"))
    if isinstance(source.get("protected_runtime_payload"), Mapping):
        from automation.forex_engine.oanda_demo_owner_approved_one_order_protected_runtime_execution_v1 import (
            evaluate_oanda_demo_owner_approved_one_order_protected_runtime_execution_v1,
        )

        return evaluate_oanda_demo_owner_approved_one_order_protected_runtime_execution_v1(
            dict(_mapping(source.get("protected_runtime_payload")))
        )
    return {}


def _credential_result(source: Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(source.get("credential_session_bridge_result"), Mapping):
        return _mapping(source.get("credential_session_bridge_result"))
    if isinstance(source.get("credential_session_bridge_payload"), Mapping):
        return evaluate_owner_runtime_credential_session_bridge_v1(
            dict(_mapping(source.get("credential_session_bridge_payload")))
        )
    return {}


def _post_review_result(source: Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(source.get("post_execution_review_loop_result"), Mapping):
        return _mapping(source.get("post_execution_review_loop_result"))
    if isinstance(source.get("post_execution_review_payload"), Mapping):
        return evaluate_forex_post_execution_review_loop_v1(
            dict(_mapping(source.get("post_execution_review_payload")))
        )
    return {}


def _readiness_result(source: Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(source.get("supervised_operation_readiness_result"), Mapping):
        return _mapping(source.get("supervised_operation_readiness_result"))
    if isinstance(source.get("supervised_operation_readiness_payload"), Mapping):
        return evaluate_forex_22h6d_supervised_operation_readiness_v1(
            dict(_mapping(source.get("supervised_operation_readiness_payload")))
        )
    return {}


def _protected_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    status = _text(result.get("protected_runtime_status"), _text(result.get("status")))
    broker_called = _bool(result.get("broker_api_called"), default=False)
    credential_read = _bool(result.get("credential_read"), default=False)
    ready = status in PROTECTED_READY_STATUSES and broker_called is False and credential_read is False
    return {
        "ready": ready,
        "status": status,
        "broker_api_called": broker_called,
        "credential_read": credential_read,
        "blockers": []
        if ready
        else ["protected_runtime_execution_result_not_ready"],
    }


def _credential_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    status = _text(
        result.get("credential_session_bridge_status"), _text(result.get("status"))
    )
    ready = status in CREDENTIAL_READY_STATUSES
    return {
        "ready": ready,
        "status": status,
        "blockers": []
        if ready
        else ["credential_session_bridge_result_not_ready"],
    }


def _post_review_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    status = _text(
        result.get("post_execution_review_status"), _text(result.get("status"))
    )
    ready = status in POST_REVIEW_READY_STATUSES
    return {
        "ready": ready,
        "status": status,
        "blockers": [] if ready else ["post_execution_review_loop_result_not_ready"],
    }


def _supervised_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    status = _text(result.get("readiness_status"), _text(result.get("status")))
    total_score = int(_number(result.get("total_score")) or 0)
    ready = status == TWENTY_TWO_HOUR_SIX_DAY_READINESS_PASSED and total_score == 100
    return {
        "ready": ready,
        "status": status,
        "total_score": total_score,
        "blockers": [] if ready else ["22h6d_readiness_not_passed"],
    }


def _profit_proof_lane(data: Mapping[str, Any]) -> dict[str, Any]:
    min_count = int(_number(data.get("min_evidence_sample_count")) or 30)
    sample_count = int(_number(data.get("evidence_sample_count")) or 0)
    checks = {
        "sample_count_ready": sample_count >= min_count,
        "expectancy_positive": _bool(data.get("expectancy_positive")) is True,
        "profit_factor_meets_threshold": _bool(
            data.get("profit_factor_meets_threshold")
        )
        is True,
        "drawdown_within_limit": _bool(data.get("drawdown_within_limit")) is True,
        "walk_forward_gate_cleared": _bool(data.get("walk_forward_gate_cleared"))
        is True,
        "out_of_sample_passed": _bool(data.get("out_of_sample_passed")) is True,
        "spread_slippage_model_present": _bool(
            data.get("spread_slippage_model_present")
        )
        is True,
        "evidence_quality_ready": _text(data.get("evidence_quality_status"))
        in PROFIT_QUALITY_ALLOWED,
    }
    blockers = [key for key, passed in checks.items() if not passed]
    return {
        "lane": "Profit Proof",
        "passed": bool(data) and not blockers,
        "status": "PASS" if bool(data) and not blockers else "BLOCKED",
        "blockers": blockers,
        "evidence_sample_count": sample_count,
        "min_evidence_sample_count": min_count,
        **checks,
    }


def _return_target_validation_lane(data: Mapping[str, Any]) -> dict[str, Any]:
    target_status = _text(data.get("target_evidence_status"))
    guaranteed = _bool(data.get("guaranteed_profit_claimed"))
    fixed = _bool(data.get("fixed_return_target_promised"))
    checks = {
        "return_target_defined": _bool(data.get("return_target_defined")) is True,
        "target_evidence_status_allowed": target_status
        in RETURN_TARGET_ALLOWED_STATUSES,
        "fixed_return_target_promised_false": fixed is False,
        "guaranteed_profit_claimed_false": guaranteed is False,
        "owner_target_review_required": _bool(data.get("owner_target_review_required"))
        is True,
        "evidence_supports_target_review": _bool(
            data.get("evidence_supports_target_review")
        )
        is True,
    }
    review_required = target_status in RETURN_TARGET_REVIEW_STATUSES
    blockers = [key for key, passed in checks.items() if not passed]
    passed = bool(data) and not blockers and target_status == "PROVEN"
    status = "PASS" if passed else "REVIEW_REQUIRED" if review_required else "BLOCKED"
    return {
        "lane": "Return Target Validation",
        "passed": passed,
        "review_required": review_required,
        "status": status,
        "blockers": blockers,
        "target_evidence_status": target_status,
        **checks,
    }


def _broker_runtime_evidence_lane(
    data: Mapping[str, Any],
    *,
    source: Mapping[str, Any],
    protected_summary: Mapping[str, Any],
    credential_summary: Mapping[str, Any],
) -> dict[str, Any]:
    mode_data = _mapping(source.get("oanda_mode_declaration"))
    mode = _text(mode_data.get("mode"), _text(data.get("oanda_mode")))
    checks = {
        "protected_runtime_execution_result_ready": protected_summary["ready"] is True,
        "credential_session_bridge_result_ready": credential_summary["ready"] is True,
        "oanda_mode_declared": mode in OANDA_MODES,
        "one_order_protected_gate_present": _bool(
            data.get("one_order_protected_gate_present")
        )
        is True,
        "broker_api_called_false": _bool(data.get("broker_api_called")) is False,
        "credential_read_false": _bool(data.get("credential_read")) is False,
    }
    blockers = [key for key, passed in checks.items() if not passed]
    return {
        "lane": "Broker + Runtime Evidence",
        "passed": bool(data) and not blockers,
        "status": "PASS" if bool(data) and not blockers else "BLOCKED",
        "blockers": blockers,
        "oanda_mode": mode,
        **checks,
    }


def _safety_real_money_gate_lane(data: Mapping[str, Any]) -> dict[str, Any]:
    checks = {
        "kill_switch_ready": _bool(data.get("kill_switch_ready")) is True,
        "daily_loss_stop_ready": _bool(data.get("daily_loss_stop_ready")) is True,
        "max_loss_gate_ready": _bool(data.get("max_loss_gate_ready")) is True,
        "stop_loss_required": _bool(data.get("stop_loss_required")) is True,
        "take_profit_required": _bool(data.get("take_profit_required")) is True,
        "one_order_only": _bool(data.get("one_order_only")) is True,
        "money_movement_allowed_false": _bool(data.get("money_movement_allowed"))
        is False,
        "live_trading_allowed_false": _bool(data.get("live_trading_allowed"))
        is False,
        "owner_live_exception_required": _bool(
            data.get("owner_live_exception_required")
        )
        is True,
    }
    blockers = [key for key, passed in checks.items() if not passed]
    return {
        "lane": "Safety / Real-Money Gate",
        "passed": bool(data) and not blockers,
        "status": "PASS" if bool(data) and not blockers else "BLOCKED",
        "blockers": blockers,
        **checks,
    }


def _dashboard_owner_control_lane(data: Mapping[str, Any]) -> dict[str, Any]:
    checks = {
        "dashboard_truth_contract_present": _bool(
            data.get("dashboard_truth_contract_present")
        )
        is True,
        "owner_action_queue_present": _bool(data.get("owner_action_queue_present"))
        is True,
        "sos_ready": _bool(data.get("sos_ready")) is True,
        "audit_ready": _bool(data.get("audit_ready")) is True,
        "manual_owner_control_required": _bool(
            data.get("manual_owner_control_required")
        )
        is True,
        "no_dashboard_runtime_created": _bool(
            data.get("no_dashboard_runtime_created")
        )
        is True,
    }
    blockers = [key for key, passed in checks.items() if not passed]
    return {
        "lane": "Dashboard Truth / Owner Control",
        "passed": bool(data) and not blockers,
        "status": "PASS" if bool(data) and not blockers else "BLOCKED",
        "blockers": blockers,
        **checks,
    }


def _capital_operation_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    capital = _mapping(source.get("capital_planner_metadata"))
    owner_value = _mapping(source.get("owner_value_entry_metadata"))
    live_campaign = _mapping(source.get("live_execution_and_capital_operation_campaign_result"))
    ready = (
        _bool(capital.get("capital_planner_ready")) is True
        and _bool(owner_value.get("owner_control_ready"), default=True) is True
        and _bool(live_campaign.get("money_moved"), default=False) is False
    )
    return {
        "ready": ready,
        "capital_planner_ready": _bool(capital.get("capital_planner_ready")),
        "owner_control_ready": _bool(owner_value.get("owner_control_ready"), default=True),
        "money_moved": _bool(live_campaign.get("money_moved"), default=False),
        "blockers": [] if ready else ["capital_or_owner_control_metadata_not_ready"],
    }


def _sos_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    data = _mapping(source.get("sos_metadata"))
    ready = _bool(data.get("sos_ready")) is True
    return {
        "ready": ready,
        "sos_ready": _bool(data.get("sos_ready")),
        "blockers": [] if ready else ["sos_metadata_not_ready"],
    }


def _completion_score(
    *,
    five_lane_summary: Mapping[str, bool],
    protected_summary: Mapping[str, Any],
    credential_summary: Mapping[str, Any],
    post_review_summary: Mapping[str, Any],
    supervised_summary: Mapping[str, Any],
    capital_operation_summary: Mapping[str, Any],
    sos_summary: Mapping[str, Any],
) -> int:
    score = sum(15 for passed in five_lane_summary.values() if passed)
    score += 10 if protected_summary["ready"] else 0
    score += 10 if credential_summary["ready"] else 0
    score += 10 if post_review_summary["ready"] else 0
    score += 10 if supervised_summary["ready"] else 0
    score += 5 if capital_operation_summary["ready"] and sos_summary["ready"] else 0
    return min(score, 110)


def _campaign_status(
    *,
    source: Mapping[str, Any],
    sensitive_data_blockers: list[str],
    protected_summary: Mapping[str, Any],
    credential_summary: Mapping[str, Any],
    post_review_summary: Mapping[str, Any],
    supervised_summary: Mapping[str, Any],
    profit_lane: Mapping[str, Any],
    return_lane: Mapping[str, Any],
    broker_lane: Mapping[str, Any],
    safety_lane: Mapping[str, Any],
    dashboard_lane: Mapping[str, Any],
    completion_score: int,
) -> tuple[str, list[str]]:
    if sensitive_data_blockers:
        return BLOCKED_BY_SENSITIVE_DATA, list(sensitive_data_blockers)
    if not source:
        return INCOMPLETE_INPUTS, ["payload_missing"]
    if not protected_summary["ready"]:
        return BLOCKED_BY_PROTECTED_RUNTIME_EXECUTION_GATE, list(
            protected_summary["blockers"]
        )
    if not credential_summary["ready"]:
        return BLOCKED_BY_RUNTIME_CREDENTIAL_SESSION_BRIDGE, list(
            credential_summary["blockers"]
        )
    if not post_review_summary["ready"]:
        return BLOCKED_BY_POST_EXECUTION_REVIEW_LOOP, list(post_review_summary["blockers"])
    if not supervised_summary["ready"]:
        return BLOCKED_BY_22H_6D_READINESS, list(supervised_summary["blockers"])
    if not profit_lane["passed"]:
        return BLOCKED_BY_PROFIT_PROOF, list(profit_lane["blockers"])
    if return_lane["status"] == "REVIEW_REQUIRED":
        return FOREX_COMPLETION_CAMPAIGN_PART2_CONTINUE_EVIDENCE_CAPTURE, list(
            return_lane["blockers"]
        )
    if not return_lane["passed"]:
        return BLOCKED_BY_RETURN_TARGET_EVIDENCE, list(return_lane["blockers"])
    if not broker_lane["passed"]:
        return BLOCKED_BY_BROKER_RUNTIME_EVIDENCE, list(broker_lane["blockers"])
    if not safety_lane["passed"]:
        return BLOCKED_BY_SAFETY_REAL_MONEY_GATE, list(safety_lane["blockers"])
    if not dashboard_lane["passed"]:
        return BLOCKED_BY_DASHBOARD_OWNER_CONTROL, list(dashboard_lane["blockers"])
    if completion_score >= 110:
        return FOREX_COMPLETION_CAMPAIGN_PART2_READY_FOR_100_PLUS_REVIEW, []
    if completion_score >= 100:
        return FOREX_COMPLETION_CAMPAIGN_PART2_READY_FOR_OWNER_VALIDATION, []
    return FOREX_COMPLETION_CAMPAIGN_PART2_CONTINUE_EVIDENCE_CAPTURE, [
        "completion_score_below_100"
    ]


def _missing_inputs(*summaries: Mapping[str, Any]) -> list[str]:
    missing: list[str] = []
    for summary in summaries:
        if not summary.get("passed", summary.get("ready", False)):
            missing.extend(summary.get("blockers", []))
    return unique(missing)


def _completion_band(score: int) -> str:
    if score >= 110:
        return "POST_100_SUPERVISED_OPERATION_REVIEW_PACKAGE"
    if score >= 100:
        return "OWNER_VALIDATION_READINESS"
    if score >= 95:
        return "FIVE_LANE_REVIEW_READINESS"
    if score >= 90:
        return "SUPERVISED_READINESS_INDEX"
    if score >= 85:
        return "PROTECTED_RUNTIME_REVIEW_LAYER"
    if score >= 75:
        return "CURRENT_LOCAL_CAMPAIGN_STATE"
    return "EVIDENCE_CAPTURE_REQUIRED"


def _current_readiness_estimate(score: int) -> str:
    if score >= 110:
        return "100+%"
    if score >= 100:
        return "100%"
    if score >= 95:
        return "95%"
    if score >= 90:
        return "90%"
    if score >= 85:
        return "85%"
    if score >= 75:
        return "75/80%"
    return "BELOW_75%"


def _next_best_packet(status: str) -> str:
    if status in {
        FOREX_COMPLETION_CAMPAIGN_PART2_READY_FOR_OWNER_VALIDATION,
        FOREX_COMPLETION_CAMPAIGN_PART2_READY_FOR_100_PLUS_REVIEW,
    }:
        return NEXT_PACKET_OWNER_VALIDATION
    if status == BLOCKED_BY_PROTECTED_RUNTIME_EXECUTION_GATE:
        return "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_ONE_ORDER_PROTECTED_RUNTIME_EXECUTION_V1"
    if status == BLOCKED_BY_RUNTIME_CREDENTIAL_SESSION_BRIDGE:
        return "AIOS_FOREX_OWNER_RUNTIME_CREDENTIAL_SESSION_BRIDGE_V1"
    if status == BLOCKED_BY_POST_EXECUTION_REVIEW_LOOP:
        return "AIOS_FOREX_POST_EXECUTION_REVIEW_LOOP_V1"
    if status == BLOCKED_BY_22H_6D_READINESS:
        return "AIOS_FOREX_22H6D_SUPERVISED_OPERATION_READINESS_V1"
    return SCHEMA


def _owner_action_queue(
    blockers: list[str],
    next_best_packet: str,
) -> list[dict[str, Any]]:
    return [
        {
            "action_id": action_id,
            "owner_decision_required": True,
            "blocked_by": list(blockers),
            "next_best_packet": next_best_packet if action_id == "REVIEW_NEXT_PACKET" else None,
            **hard_false_result(),
            **safety_false_result(),
        }
        for action_id in (
            "REVIEW_PROFIT_PROOF",
            "REVIEW_RETURN_TARGET_VALIDATION",
            "REVIEW_BROKER_RUNTIME_EVIDENCE",
            "REVIEW_SAFETY_REAL_MONEY_GATE",
            "REVIEW_DASHBOARD_OWNER_CONTROL",
            "REVIEW_NEXT_PACKET",
        )
    ]


def _safe_manual_next_action(status: str) -> str:
    if status in {
        FOREX_COMPLETION_CAMPAIGN_PART2_READY_FOR_OWNER_VALIDATION,
        FOREX_COMPLETION_CAMPAIGN_PART2_READY_FOR_100_PLUS_REVIEW,
    }:
        return "Owner reviews the Part 2 validation package before any PR landing work."
    if status == FOREX_COMPLETION_CAMPAIGN_PART2_CONTINUE_EVIDENCE_CAPTURE:
        return "Continue sanitized evidence capture; do not claim fixed returns or profit."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys or values and rerun locally."
    return "Repair the blocking lane metadata and rerun the campaign finisher."


def _part2_sensitive_data_blockers(value: Any, path: str = "payload") -> list[str]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if path == "payload" and normalized in GENERATED_RESULT_FIELDS:
                continue

            key_blockers = _raw_sensitive_key_blockers(key_text, path)
            if key_blockers:
                blockers.extend(key_blockers)
                continue
            blockers.extend(_part2_sensitive_data_blockers(child, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_part2_sensitive_data_blockers(child, f"{path}[{index}]"))
    else:
        blockers.extend(find_sensitive_data_blockers(value, path))
    return unique(blockers)


def _raw_sensitive_key_blockers(key_text: str, path: str) -> list[str]:
    blockers = find_sensitive_data_blockers({key_text: None}, path)
    if blockers:
        return blockers

    normalized = key_text.lower().replace("-", "_")
    if normalized in RAW_SENSITIVE_KEYS:
        return [f"{path}.{key_text}:sensitive_key"]
    return []


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
