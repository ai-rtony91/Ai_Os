"""Read-only OANDA demo supervised execution-prep evaluator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from math import isfinite
from typing import Any


SCHEMA = "AIOS_FOREX_OANDA_DEMO_SUPERVISED_EXECUTION_PREP_V1"
MODE = "READ_ONLY_OANDA_DEMO_SUPERVISED_EXECUTION_PREP"

OANDA_DEMO_EXECUTION_PREP_READY = "OANDA_DEMO_EXECUTION_PREP_READY"
NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
BLOCKED_BY_SUPERVISED_DEMO_READINESS = "BLOCKED_BY_SUPERVISED_DEMO_READINESS"
BLOCKED_BY_OWNER_APPROVAL_GATE = "BLOCKED_BY_OWNER_APPROVAL_GATE"
BLOCKED_BY_OANDA_RUNTIME_BOUNDARY = "BLOCKED_BY_OANDA_RUNTIME_BOUNDARY"
BLOCKED_BY_CANDIDATE_TICKET = "BLOCKED_BY_CANDIDATE_TICKET"
BLOCKED_BY_ORDER_INTENT = "BLOCKED_BY_ORDER_INTENT"
BLOCKED_BY_RISK_GATES = "BLOCKED_BY_RISK_GATES"
BLOCKED_BY_ORDER_SAFETY = "BLOCKED_BY_ORDER_SAFETY"
BLOCKED_BY_TELEMETRY_PLAN = "BLOCKED_BY_TELEMETRY_PLAN"
BLOCKED_BY_ABORT_CONDITIONS = "BLOCKED_BY_ABORT_CONDITIONS"
BLOCKED_BY_DATA_QUALITY = "BLOCKED_BY_DATA_QUALITY"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

THIS_PACKET = SCHEMA
NEXT_PACKET_IF_READY = "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_RUNTIME_HANDOFF_V1"
CURRENT_LANE_ID = "OANDA_DEMO_SUPERVISED_EXECUTION_PREP"
NEXT_LANE_ID = "OANDA_DEMO_OWNER_APPROVED_RUNTIME_HANDOFF"

OPPORTUNITY_CAPTURE_OBJECTIVE = (
    "maximize validated risk-adjusted opportunity capture while preserving capital and proving edge"
)

DEFAULT_THRESHOLDS: dict[str, float] = {
    "min_execution_prep_score": 0.90,
    "min_supervised_demo_readiness_score": 0.85,
    "min_owner_approval_gate_score": 0.90,
    "min_oanda_runtime_boundary_score": 0.90,
    "min_candidate_ticket_score": 0.90,
    "min_order_intent_score": 0.90,
    "min_risk_gate_score": 0.90,
    "min_order_safety_score": 0.90,
    "min_telemetry_plan_score": 0.85,
    "min_abort_condition_score": 0.90,
    "min_data_quality_score": 0.80,
}

THRESHOLD_FLOORS: dict[str, float] = {
    "min_execution_prep_score": 0.85,
    "min_supervised_demo_readiness_score": 0.80,
    "min_owner_approval_gate_score": 0.85,
    "min_oanda_runtime_boundary_score": 0.85,
    "min_candidate_ticket_score": 0.85,
    "min_order_intent_score": 0.85,
    "min_risk_gate_score": 0.85,
    "min_order_safety_score": 0.85,
    "min_telemetry_plan_score": 0.80,
    "min_abort_condition_score": 0.85,
    "min_data_quality_score": 0.75,
}

SENSITIVE_KEY_PARTS = (
    "routing_number",
    "account_number",
    "debit_card_number",
    "card_number",
    "cvv",
    "password",
    "api_key",
    "broker_token",
    "access_token",
    "token",
    "secret",
)

SAFE_BOUNDARY_KEYS = frozenset(
    {
        "bank_access_allowed",
        "broker_api_allowed",
        "credential_redaction_required",
        "credential_use_allowed",
        "credentials_included",
        "credentials_persisted",
        "credentials_requested",
        "dashboard_runtime_created",
        "daemon_created",
        "demo_execution_allowed",
        "execution_authorized",
        "live_account_allowed",
        "money_movement_allowed",
        "order_placement_allowed",
        "owner_runtime_credential_entry_required",
        "real_money_allowed",
        "required_owner_approval",
        "runtime_credentials_required",
        "runtime_only_credentials_required",
        "scheduler_created",
        "secret_scan_required",
        "trade_execution_allowed",
        "webhook_created",
    }
)

CORE_EVIDENCE_KEYS = (
    "supervised_demo_readiness_packet",
    "owner_approval_gate",
    "oanda_runtime_boundary",
    "candidate_ticket",
    "order_intent",
    "risk_gates",
    "order_safety",
    "telemetry_plan",
    "abort_conditions",
)

READY_READINESS_STATUSES = frozenset({"SUPERVISED_DEMO_READY", "READY", "PASS"})
ALLOWED_BROKER_MODES = frozenset({"DEMO", "OANDA_DEMO", "PRACTICE", "PAPER_DEMO"})
ALLOWED_ACCOUNT_ENVIRONMENTS = frozenset({"PRACTICE", "DEMO", "OANDA_DEMO"})
ALLOWED_SIDES = frozenset({"BUY", "SELL", "LONG", "SHORT"})
ALLOWED_ORDER_TYPES = frozenset({"MARKET", "LIMIT", "PREP_ONLY"})


def evaluate_oanda_demo_supervised_execution_prep_v1(payload: dict | None = None) -> dict[str, Any]:
    """Evaluate sanitized OANDA demo execution-prep evidence without execution authority."""

    source = payload if isinstance(payload, Mapping) else {}
    threshold_policy = _threshold_policy(_mapping(source.get("thresholds")))
    thresholds = threshold_policy["active_thresholds"]

    if _contains_sensitive_key(source):
        return _sensitive_payload(source, threshold_policy)

    missing_information = _missing_information(source)
    missing_core_evidence = bool(missing_information)

    supervised_summary = _supervised_demo_readiness_summary(source, thresholds)
    owner_summary = _owner_approval_summary(source, thresholds)
    runtime_summary = _oanda_runtime_boundary_summary(source, thresholds)
    candidate_summary = _candidate_ticket_summary(source, thresholds)
    order_intent_summary = _order_intent_summary(source, thresholds)
    risk_summary = _risk_gate_summary(source, thresholds)
    order_safety_summary = _order_safety_summary(source, thresholds)
    telemetry_summary = _telemetry_plan_summary(source, thresholds)
    abort_summary = _abort_condition_summary(source, thresholds)
    data_quality_summary = _data_quality_summary(source, thresholds)

    sub_scores = {
        "supervised_demo_readiness_score": supervised_summary["score"],
        "owner_approval_gate_score": owner_summary["score"],
        "oanda_runtime_boundary_score": runtime_summary["score"],
        "candidate_ticket_score": candidate_summary["score"],
        "order_intent_score": order_intent_summary["score"],
        "risk_gate_score": risk_summary["score"],
        "order_safety_score": order_safety_summary["score"],
        "telemetry_plan_score": telemetry_summary["score"],
        "abort_condition_score": abort_summary["score"],
        "data_quality_score": data_quality_summary["score"],
    }
    explicit_execution_prep_score = _score_from_contexts(
        [_mapping(source.get("readiness_snapshot")), source],
        ("execution_prep_score",),
    )
    derived_execution_prep_score = _average_score(sub_scores.values())
    execution_prep_score = (
        explicit_execution_prep_score
        if explicit_execution_prep_score is not None
        else derived_execution_prep_score
    )

    prep_blockers = _unique(
        [
            *threshold_policy["threshold_blockers"],
            *missing_information,
            *supervised_summary["blockers"],
            *owner_summary["blockers"],
            *runtime_summary["blockers"],
            *candidate_summary["blockers"],
            *order_intent_summary["blockers"],
            *risk_summary["blockers"],
            *order_safety_summary["blockers"],
            *telemetry_summary["blockers"],
            *abort_summary["blockers"],
            *data_quality_summary["blockers"],
        ]
    )

    prep_status = _resolve_prep_status(
        missing_core_evidence=missing_core_evidence,
        threshold_blockers=threshold_policy["threshold_blockers"],
        supervised_summary=supervised_summary,
        owner_summary=owner_summary,
        runtime_summary=runtime_summary,
        candidate_summary=candidate_summary,
        order_intent_summary=order_intent_summary,
        risk_summary=risk_summary,
        order_safety_summary=order_safety_summary,
        telemetry_summary=telemetry_summary,
        abort_summary=abort_summary,
        data_quality_summary=data_quality_summary,
        execution_prep_score=execution_prep_score,
        min_execution_prep_score=thresholds["min_execution_prep_score"],
    )
    next_best_packet = NEXT_PACKET_IF_READY if prep_status == OANDA_DEMO_EXECUTION_PREP_READY else THIS_PACKET

    return _base_result(
        source=source,
        threshold_policy=threshold_policy,
        prep_status=prep_status,
        execution_prep_score=execution_prep_score,
        explicit_execution_prep_score=explicit_execution_prep_score,
        derived_execution_prep_score=derived_execution_prep_score,
        sub_scores=sub_scores,
        supervised_summary=supervised_summary,
        owner_summary=owner_summary,
        runtime_summary=runtime_summary,
        candidate_summary=candidate_summary,
        order_intent_summary=order_intent_summary,
        risk_summary=risk_summary,
        order_safety_summary=order_safety_summary,
        telemetry_summary=telemetry_summary,
        abort_summary=abort_summary,
        data_quality_summary=data_quality_summary,
        missing_information=missing_information,
        prep_blockers=prep_blockers,
        next_best_packet=next_best_packet,
    )


def _sensitive_payload(source: Mapping[str, Any], threshold_policy: Mapping[str, Any]) -> dict[str, Any]:
    blockers = ["sensitive_data_provided"]
    summary = _empty_summary("blocked_by_sensitive_data", blockers)
    result = _base_result(
        source=source,
        threshold_policy=threshold_policy,
        prep_status=BLOCKED_BY_DATA_QUALITY,
        execution_prep_score=None,
        explicit_execution_prep_score=None,
        derived_execution_prep_score=None,
        sub_scores={
            "supervised_demo_readiness_score": None,
            "owner_approval_gate_score": None,
            "oanda_runtime_boundary_score": None,
            "candidate_ticket_score": None,
            "order_intent_score": None,
            "risk_gate_score": None,
            "order_safety_score": None,
            "telemetry_plan_score": None,
            "abort_condition_score": None,
            "data_quality_score": None,
        },
        supervised_summary=summary,
        owner_summary=summary,
        runtime_summary=summary,
        candidate_summary=summary,
        order_intent_summary=summary,
        risk_summary=summary,
        order_safety_summary=summary,
        telemetry_summary=summary,
        abort_summary=summary,
        data_quality_summary=summary,
        missing_information=["remove_sensitive_data"],
        prep_blockers=blockers,
        next_best_packet=THIS_PACKET,
    )
    result["input_summary"]["input_redacted"] = True
    result["audit_record"]["input_redacted"] = True
    result["safe_manual_next_action"] = (
        "Remove sensitive data and rerun with sanitized execution-prep evidence. Keep broker, credential, "
        "order, bank, and money actions outside AIOS until owner approval."
    )
    return result


def _base_result(
    *,
    source: Mapping[str, Any],
    threshold_policy: Mapping[str, Any],
    prep_status: str,
    execution_prep_score: float | None,
    explicit_execution_prep_score: float | None,
    derived_execution_prep_score: float | None,
    sub_scores: Mapping[str, float | None],
    supervised_summary: Mapping[str, Any],
    owner_summary: Mapping[str, Any],
    runtime_summary: Mapping[str, Any],
    candidate_summary: Mapping[str, Any],
    order_intent_summary: Mapping[str, Any],
    risk_summary: Mapping[str, Any],
    order_safety_summary: Mapping[str, Any],
    telemetry_summary: Mapping[str, Any],
    abort_summary: Mapping[str, Any],
    data_quality_summary: Mapping[str, Any],
    missing_information: Sequence[str],
    prep_blockers: Sequence[str],
    next_best_packet: str,
) -> dict[str, Any]:
    prep_ready = prep_status == OANDA_DEMO_EXECUTION_PREP_READY
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "trade_execution_allowed": False,
        "demo_execution_allowed": False,
        "order_placement_allowed": False,
        "credential_use_allowed": False,
        "scheduler_created": False,
        "daemon_created": False,
        "webhook_created": False,
        "dashboard_runtime_created": False,
        "owner_decision_required": True,
        "prep_ready": prep_ready,
        "runtime_handoff_ready": prep_ready,
        "supervised_demo_execution_authorized": False,
        "prep_status": prep_status,
        "opportunity_capture_objective": OPPORTUNITY_CAPTURE_OBJECTIVE,
        "input_summary": _input_summary(
            source=source,
            explicit_execution_prep_score=explicit_execution_prep_score,
            derived_execution_prep_score=derived_execution_prep_score,
            sub_scores=sub_scores,
            missing_information=missing_information,
        ),
        "threshold_policy": dict(threshold_policy),
        "supervised_demo_readiness_summary": dict(supervised_summary),
        "owner_approval_summary": dict(owner_summary),
        "oanda_runtime_boundary_summary": dict(runtime_summary),
        "candidate_ticket_summary": dict(candidate_summary),
        "order_intent_summary": dict(order_intent_summary),
        "risk_gate_summary": dict(risk_summary),
        "order_safety_summary": dict(order_safety_summary),
        "telemetry_plan_summary": dict(telemetry_summary),
        "abort_condition_summary": dict(abort_summary),
        "data_quality_summary": dict(data_quality_summary),
        "execution_prep_score": execution_prep_score,
        "prep_blockers": list(prep_blockers),
        "missing_information": list(missing_information),
        "sanitized_execution_prep_package": _sanitized_execution_prep_package(source),
        "owner_action_queue": _owner_action_queue(
            supervised_summary=supervised_summary,
            owner_summary=owner_summary,
            runtime_summary=runtime_summary,
            candidate_summary=candidate_summary,
            order_intent_summary=order_intent_summary,
            risk_summary=risk_summary,
            order_safety_summary=order_safety_summary,
            telemetry_summary=telemetry_summary,
            abort_summary=abort_summary,
            prep_blockers=prep_blockers,
            next_best_packet=next_best_packet,
        ),
        "next_best_packet": next_best_packet,
        "next_remaining_lane": _next_remaining_lane(
            _mapping(source.get("remaining_work_closure_index")),
            next_best_packet,
        ),
        "safe_manual_next_action": _safe_manual_next_action(prep_status),
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "as_of_date": _text(source.get("as_of_date"), datetime.now(timezone.utc).isoformat()),
            "owner_name": _text(source.get("owner_name"), "Anthony"),
            "input_fields_seen": sorted(str(key) for key in source.keys()),
            "prep_status": prep_status,
            "execution_prep_score": execution_prep_score,
            "prep_ready": prep_ready,
            "runtime_handoff_ready": prep_ready,
            "supervised_demo_execution_authorized": False,
            "next_best_packet": next_best_packet,
            "read_only": True,
        },
        "safety": _safety(),
    }


def _threshold_policy(overrides: Mapping[str, Any]) -> dict[str, Any]:
    active = dict(DEFAULT_THRESHOLDS)
    rejected: list[dict[str, str]] = []
    for key, raw_value in overrides.items():
        if key not in DEFAULT_THRESHOLDS:
            continue
        value = _score(raw_value)
        if value is None or value < THRESHOLD_FLOORS[key]:
            rejected.append({"threshold": key, "reason": "threshold_override_rejected"})
            continue
        active[key] = value
    return {
        "default_thresholds": dict(DEFAULT_THRESHOLDS),
        "active_thresholds": active,
        "guardrails": dict(THRESHOLD_FLOORS),
        "rejected_overrides": rejected,
        "threshold_blockers": ["threshold_override_rejected"] if rejected else [],
    }


def _supervised_demo_readiness_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "supervised_demo_readiness_packet")
    readiness_status = _text_from_contexts(contexts, ("readiness_status",))
    supervised_demo_ready = _bool_from_contexts(contexts, ("supervised_demo_ready",))
    explicit_score = _score_from_contexts(contexts, ("readiness_score", "supervised_demo_readiness_score"))
    next_best_packet = _text_from_contexts(contexts, ("next_best_packet",))
    readiness_blockers = _blockers_from_contexts(contexts, ("readiness_blockers",))
    derived_score = _bool_score(
        [
            None if not readiness_status else readiness_status.upper() in READY_READINESS_STATUSES,
            supervised_demo_ready,
            not readiness_blockers,
        ]
    )
    active_score = explicit_score if explicit_score is not None else derived_score

    blockers: list[str] = []
    if readiness_status and readiness_status.upper() not in READY_READINESS_STATUSES:
        blockers.append("supervised_demo_readiness_status_not_ready")
    if supervised_demo_ready is not True:
        blockers.append(
            "supervised_demo_ready_missing" if supervised_demo_ready is None else "supervised_demo_ready_false"
        )
    if readiness_blockers:
        blockers.extend(readiness_blockers)
    if active_score is None:
        blockers.append("supervised_demo_readiness_score_missing")
    elif active_score < thresholds["min_supervised_demo_readiness_score"]:
        blockers.append("supervised_demo_readiness_score_below_threshold")

    return {
        "ready": not blockers,
        "readiness_status": readiness_status,
        "supervised_demo_ready": supervised_demo_ready,
        "readiness_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_supervised_demo_readiness_score"],
        "next_best_packet": next_best_packet,
        "readiness_blockers": readiness_blockers,
        "blockers": _unique(blockers),
    }


def _owner_approval_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "owner_approval_gate")
    expected_true = {
        "owner_approval_required": _bool_from_contexts(contexts, ("owner_approval_required",)),
        "owner_named_approval_required": _bool_from_contexts(contexts, ("owner_named_approval_required",)),
        "owner_review_required": _bool_from_contexts(contexts, ("owner_review_required",)),
        "approval_packet_required": _bool_from_contexts(contexts, ("approval_packet_required",)),
        "owner_can_cancel": _bool_from_contexts(contexts, ("owner_can_cancel",)),
        "manual_execution_only": _bool_from_contexts(contexts, ("manual_execution_only",)),
    }
    expected_false = {
        "final_execution_approval_collected": _false_authority_value(
            contexts,
            "final_execution_approval_collected",
        ),
        "execution_allowed": _false_authority_value(contexts, "execution_allowed"),
    }
    owner_blocks = _blockers_from_contexts(contexts, ("owner_approval_blocks", "approval_blocks"))
    explicit_score = _score_from_contexts(contexts, ("owner_approval_gate_score",))
    derived_score = _bool_score(
        [
            *expected_true.values(),
            *[_expected_false_score_value(value) for value in expected_false.values()],
            not owner_blocks,
        ]
    )
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers = _exact_bool_blockers(expected_true=expected_true, expected_false=expected_false)
    if owner_blocks:
        blockers.extend(owner_blocks)
    if active_score is None:
        blockers.append("owner_approval_gate_score_missing")
    elif active_score < thresholds["min_owner_approval_gate_score"]:
        blockers.append("owner_approval_gate_score_below_threshold")
    return {
        "ready": not blockers,
        **expected_true,
        **expected_false,
        "owner_approval_gate_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_owner_approval_gate_score"],
        "owner_approval_blocks": owner_blocks,
        "blockers": _unique(blockers),
    }


def _oanda_runtime_boundary_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "oanda_runtime_boundary")
    broker_name = _text_from_contexts(contexts, ("broker_name",))
    broker_mode = _text_from_contexts(contexts, ("broker_mode",))
    account_environment = _text_from_contexts(contexts, ("account_environment",))
    expected_true = {
        "demo_account_only": _bool_from_contexts(contexts, ("demo_account_only",)),
        "runtime_only_credentials_required": _bool_from_contexts(contexts, ("runtime_only_credentials_required",)),
        "owner_runtime_credential_entry_required": _bool_from_contexts(
            contexts,
            ("owner_runtime_credential_entry_required",),
        ),
        "credential_redaction_required": _bool_from_contexts(contexts, ("credential_redaction_required",)),
        "secret_scan_required": _bool_from_contexts(contexts, ("secret_scan_required",)),
    }
    expected_false = {
        "live_account_allowed": _false_authority_value(contexts, "live_account_allowed"),
        "real_money_allowed": _false_authority_value(contexts, "real_money_allowed"),
        "broker_api_allowed": _false_authority_value(contexts, "broker_api_allowed"),
        "trade_execution_allowed": _false_authority_value(contexts, "trade_execution_allowed"),
        "demo_execution_allowed": _false_authority_value(contexts, "demo_execution_allowed"),
        "order_placement_allowed": _false_authority_value(contexts, "order_placement_allowed"),
        "credential_use_allowed": _false_authority_value(contexts, "credential_use_allowed"),
        "credentials_persisted": _false_authority_value(contexts, "credentials_persisted"),
        "credentials_requested": _false_authority_value(contexts, "credentials_requested"),
    }
    explicit_score = _score_from_contexts(contexts, ("oanda_runtime_boundary_score",))
    derived_score = _bool_score(
        [
            _broker_name_ok(broker_name),
            _broker_mode_ok(broker_mode),
            _account_environment_ok(account_environment),
            *expected_true.values(),
            *[_expected_false_score_value(value) for value in expected_false.values()],
        ]
    )
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers: list[str] = []
    if broker_name and not _broker_name_ok(broker_name):
        blockers.append("broker_name_not_oanda")
    if broker_mode and not _broker_mode_ok(broker_mode):
        blockers.append("broker_mode_not_demo")
    if account_environment and not _account_environment_ok(account_environment):
        blockers.append("account_environment_not_demo")
    blockers.extend(_exact_bool_blockers(expected_true=expected_true, expected_false=expected_false))
    if active_score is None:
        blockers.append("oanda_runtime_boundary_score_missing")
    elif active_score < thresholds["min_oanda_runtime_boundary_score"]:
        blockers.append("oanda_runtime_boundary_score_below_threshold")
    return {
        "ready": not blockers,
        "broker_name": broker_name,
        "broker_mode": broker_mode,
        "account_environment": account_environment,
        **expected_true,
        **expected_false,
        "oanda_runtime_boundary_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_oanda_runtime_boundary_score"],
        "blockers": _unique(blockers),
    }


def _candidate_ticket_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "candidate_ticket")
    strategy_id = _text_from_contexts(contexts, ("strategy_id",))
    candidate_id = _text_from_contexts(contexts, ("candidate_id",))
    instrument = _text_from_contexts(contexts, ("instrument",))
    side = _text_from_contexts(contexts, ("side",))
    timeframe = _text_from_contexts(contexts, ("timeframe",))
    setup_timestamp = _text_from_contexts(contexts, ("setup_timestamp",))
    confidence_score = _score_from_contexts(contexts, ("confidence_score",))
    candidate_quality_score = _score_from_contexts(contexts, ("candidate_quality_score",))
    evidence_reference = _text_from_contexts(contexts, ("evidence_reference",))
    ticket_blocks = _blockers_from_contexts(contexts, ("ticket_blocks",))
    explicit_score = _score_from_contexts(contexts, ("ticket_score", "candidate_ticket_score"))
    derived_score = _bool_score(
        [
            _present(strategy_id),
            _present(candidate_id),
            _present(instrument),
            side.upper() in ALLOWED_SIDES if side else None,
            _present(timeframe),
            None if confidence_score is None else confidence_score >= 0.60,
            None if candidate_quality_score is None else candidate_quality_score >= 0.75,
            not ticket_blocks,
        ]
    )
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers: list[str] = []
    for key, value in {
        "strategy_id": strategy_id,
        "candidate_id": candidate_id,
        "instrument": instrument,
        "timeframe": timeframe,
    }.items():
        if not _present(value):
            blockers.append(f"{key}_missing")
    if not side:
        blockers.append("side_missing")
    elif side.upper() not in ALLOWED_SIDES:
        blockers.append("side_not_supported")
    if confidence_score is not None and confidence_score < 0.60:
        blockers.append("confidence_score_below_minimum")
    if candidate_quality_score is not None and candidate_quality_score < 0.75:
        blockers.append("candidate_quality_score_below_minimum")
    if ticket_blocks:
        blockers.extend(ticket_blocks)
    if active_score is None:
        blockers.append("candidate_ticket_score_missing")
    elif active_score < thresholds["min_candidate_ticket_score"]:
        blockers.append("candidate_ticket_score_below_threshold")
    return {
        "ready": not blockers,
        "strategy_id": strategy_id,
        "candidate_id": candidate_id,
        "instrument": instrument,
        "side": side,
        "timeframe": timeframe,
        "setup_timestamp": setup_timestamp,
        "confidence_score": confidence_score,
        "candidate_quality_score": candidate_quality_score,
        "evidence_reference": evidence_reference,
        "ticket_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_candidate_ticket_score"],
        "ticket_blocks": ticket_blocks,
        "blockers": _unique(blockers),
    }


def _order_intent_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "order_intent")
    order_type = _text_from_contexts(contexts, ("order_type",))
    units = _number_from_contexts(contexts, ("units",))
    max_position_units = _number_from_contexts(contexts, ("max_position_units",))
    stop_loss_required = _bool_from_contexts(contexts, ("stop_loss_required",))
    stop_loss_price = _number_from_contexts(contexts, ("stop_loss_price",))
    stop_loss_pips = _number_from_contexts(contexts, ("stop_loss_pips",))
    take_profit_required = _bool_from_contexts(contexts, ("take_profit_required",))
    take_profit_price = _number_from_contexts(contexts, ("take_profit_price",))
    take_profit_pips = _number_from_contexts(contexts, ("take_profit_pips",))
    max_spread_pips = _number_from_contexts(contexts, ("max_spread_pips",))
    max_slippage_pips = _number_from_contexts(contexts, ("max_slippage_pips",))
    one_order_only = _bool_from_contexts(contexts, ("one_order_only",))
    order_intent_blocks = _blockers_from_contexts(contexts, ("order_intent_blocks",))
    explicit_score = _score_from_contexts(contexts, ("order_intent_score",))
    stop_loss_present = stop_loss_price is not None or stop_loss_pips is not None
    take_profit_present = take_profit_price is not None or take_profit_pips is not None
    derived_score = _bool_score(
        [
            None if not order_type else order_type.upper() in ALLOWED_ORDER_TYPES,
            units is not None and units > 0,
            None if units is None or max_position_units is None else units <= max_position_units,
            stop_loss_required,
            stop_loss_present,
            take_profit_required,
            take_profit_present,
            max_spread_pips is not None,
            max_slippage_pips is not None,
            one_order_only,
            not order_intent_blocks,
        ]
    )
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers: list[str] = []
    if order_type and order_type.upper() not in ALLOWED_ORDER_TYPES:
        blockers.append("order_type_not_supported")
    if units is None:
        blockers.append("units_missing")
    elif units <= 0:
        blockers.append("units_not_positive")
    elif max_position_units is not None and units > max_position_units:
        blockers.append("units_above_max_position_units")
    if stop_loss_required is not True:
        blockers.append("stop_loss_required_missing" if stop_loss_required is None else "stop_loss_required_false")
    if not stop_loss_present:
        blockers.append("stop_loss_missing")
    if take_profit_required is not True:
        blockers.append(
            "take_profit_required_missing" if take_profit_required is None else "take_profit_required_false"
        )
    if not take_profit_present:
        blockers.append("take_profit_missing")
    if max_spread_pips is None:
        blockers.append("max_spread_pips_missing")
    if max_slippage_pips is None:
        blockers.append("max_slippage_pips_missing")
    if one_order_only is not True:
        blockers.append("one_order_only_missing" if one_order_only is None else "one_order_only_false")
    if order_intent_blocks:
        blockers.extend(order_intent_blocks)
    if active_score is None:
        blockers.append("order_intent_score_missing")
    elif active_score < thresholds["min_order_intent_score"]:
        blockers.append("order_intent_score_below_threshold")
    return {
        "ready": not blockers,
        "order_type": order_type,
        "units": units,
        "max_position_units": max_position_units,
        "stop_loss_required": stop_loss_required,
        "stop_loss_price": stop_loss_price,
        "stop_loss_pips": stop_loss_pips,
        "take_profit_required": take_profit_required,
        "take_profit_price": take_profit_price,
        "take_profit_pips": take_profit_pips,
        "max_spread_pips": max_spread_pips,
        "max_slippage_pips": max_slippage_pips,
        "one_order_only": one_order_only,
        "order_intent_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_order_intent_score"],
        "order_intent_blocks": order_intent_blocks,
        "blockers": _unique(blockers),
    }


def _risk_gate_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "risk_gates")
    expected_true = {
        "max_loss_gate_present": _bool_from_contexts(contexts, ("max_loss_gate_present",)),
        "daily_loss_stop_present": _bool_from_contexts(contexts, ("daily_loss_stop_present",)),
        "kill_switch_present": _bool_from_contexts(contexts, ("kill_switch_present",)),
        "position_size_limit_present": _bool_from_contexts(contexts, ("position_size_limit_present",)),
    }
    max_risk_per_trade_pct = _number_from_contexts(contexts, ("max_risk_per_trade_pct",))
    max_daily_loss_pct = _number_from_contexts(contexts, ("max_daily_loss_pct",))
    risk_reward_minimum = _number_from_contexts(contexts, ("risk_reward_minimum",))
    account_risk_mode = _text_from_contexts(contexts, ("account_risk_mode",))
    risk_gate_blocks = _blockers_from_contexts(contexts, ("risk_gate_blocks",))
    explicit_score = _score_from_contexts(contexts, ("risk_gate_score",))
    derived_score = _bool_score(
        [
            *expected_true.values(),
            None if max_risk_per_trade_pct is None else max_risk_per_trade_pct <= 0.01,
            None if max_daily_loss_pct is None else max_daily_loss_pct <= 0.03,
            None if risk_reward_minimum is None else risk_reward_minimum >= 1.0,
            not risk_gate_blocks,
        ]
    )
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers = _expected_true_blockers(expected_true)
    if max_risk_per_trade_pct is None:
        blockers.append("max_risk_per_trade_pct_missing")
    elif max_risk_per_trade_pct > 0.01:
        blockers.append("max_risk_per_trade_pct_above_limit")
    if max_daily_loss_pct is None:
        blockers.append("max_daily_loss_pct_missing")
    elif max_daily_loss_pct > 0.03:
        blockers.append("max_daily_loss_pct_above_limit")
    if risk_reward_minimum is not None and risk_reward_minimum < 1.0:
        blockers.append("risk_reward_minimum_below_one")
    if risk_gate_blocks:
        blockers.extend(risk_gate_blocks)
    if active_score is None:
        blockers.append("risk_gate_score_missing")
    elif active_score < thresholds["min_risk_gate_score"]:
        blockers.append("risk_gate_score_below_threshold")
    return {
        "ready": not blockers,
        **expected_true,
        "max_risk_per_trade_pct": max_risk_per_trade_pct,
        "max_daily_loss_pct": max_daily_loss_pct,
        "risk_reward_minimum": risk_reward_minimum,
        "account_risk_mode": account_risk_mode,
        "risk_gate_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_risk_gate_score"],
        "risk_gate_blocks": risk_gate_blocks,
        "blockers": _unique(blockers),
    }


def _order_safety_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "order_safety")
    expected_true = {
        "pair_whitelist_present": _bool_from_contexts(contexts, ("pair_whitelist_present",)),
        "spread_check_required": _bool_from_contexts(contexts, ("spread_check_required",)),
        "slippage_check_required": _bool_from_contexts(contexts, ("slippage_check_required",)),
        "stop_loss_validation_required": _bool_from_contexts(contexts, ("stop_loss_validation_required",)),
        "take_profit_validation_required": _bool_from_contexts(contexts, ("take_profit_validation_required",)),
        "duplicate_order_check_required": _bool_from_contexts(contexts, ("duplicate_order_check_required",)),
        "market_open_check_required": _bool_from_contexts(contexts, ("market_open_check_required",)),
        "order_preview_required": _bool_from_contexts(contexts, ("order_preview_required",)),
    }
    order_safety_blocks = _blockers_from_contexts(contexts, ("order_safety_blocks",))
    explicit_score = _score_from_contexts(contexts, ("order_safety_score",))
    derived_score = _bool_score([*expected_true.values(), not order_safety_blocks])
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers = _expected_true_blockers(expected_true)
    if order_safety_blocks:
        blockers.extend(order_safety_blocks)
    if active_score is None:
        blockers.append("order_safety_score_missing")
    elif active_score < thresholds["min_order_safety_score"]:
        blockers.append("order_safety_score_below_threshold")
    return {
        "ready": not blockers,
        **expected_true,
        "order_safety_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_order_safety_score"],
        "order_safety_blocks": order_safety_blocks,
        "blockers": _unique(blockers),
    }


def _telemetry_plan_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "telemetry_plan")
    expected_true = {
        "audit_log_required": _bool_from_contexts(contexts, ("audit_log_required",)),
        "sanitized_ticket_required": _bool_from_contexts(contexts, ("sanitized_ticket_required",)),
        "pre_trade_snapshot_required": _bool_from_contexts(contexts, ("pre_trade_snapshot_required",)),
        "order_preview_snapshot_required": _bool_from_contexts(contexts, ("order_preview_snapshot_required",)),
        "post_trade_snapshot_required": _bool_from_contexts(contexts, ("post_trade_snapshot_required",)),
        "exception_capture_required": _bool_from_contexts(contexts, ("exception_capture_required",)),
        "owner_review_report_required": _bool_from_contexts(contexts, ("owner_review_report_required",)),
    }
    telemetry_blocks = _blockers_from_contexts(contexts, ("telemetry_blocks",))
    explicit_score = _score_from_contexts(contexts, ("telemetry_plan_score",))
    derived_score = _bool_score([*expected_true.values(), not telemetry_blocks])
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers = _expected_true_blockers(expected_true)
    if telemetry_blocks:
        blockers.extend(telemetry_blocks)
    if active_score is None:
        blockers.append("telemetry_plan_score_missing")
    elif active_score < thresholds["min_telemetry_plan_score"]:
        blockers.append("telemetry_plan_score_below_threshold")
    return {
        "ready": not blockers,
        **expected_true,
        "telemetry_plan_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_telemetry_plan_score"],
        "telemetry_blocks": telemetry_blocks,
        "blockers": _unique(blockers),
    }


def _abort_condition_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "abort_conditions")
    expected_true = {
        "abort_if_owner_approval_missing": _bool_from_contexts(contexts, ("abort_if_owner_approval_missing",)),
        "abort_if_credentials_missing": _bool_from_contexts(contexts, ("abort_if_credentials_missing",)),
        "abort_if_broker_mode_not_demo": _bool_from_contexts(contexts, ("abort_if_broker_mode_not_demo",)),
        "abort_if_spread_above_max": _bool_from_contexts(contexts, ("abort_if_spread_above_max",)),
        "abort_if_slippage_above_max": _bool_from_contexts(contexts, ("abort_if_slippage_above_max",)),
        "abort_if_stop_loss_missing": _bool_from_contexts(contexts, ("abort_if_stop_loss_missing",)),
        "abort_if_take_profit_missing": _bool_from_contexts(contexts, ("abort_if_take_profit_missing",)),
        "abort_if_daily_loss_hit": _bool_from_contexts(contexts, ("abort_if_daily_loss_hit",)),
        "abort_if_kill_switch_active": _bool_from_contexts(contexts, ("abort_if_kill_switch_active",)),
        "abort_if_duplicate_order_detected": _bool_from_contexts(contexts, ("abort_if_duplicate_order_detected",)),
    }
    abort_condition_blocks = _blockers_from_contexts(contexts, ("abort_condition_blocks",))
    explicit_score = _score_from_contexts(contexts, ("abort_condition_score",))
    derived_score = _bool_score([*expected_true.values(), not abort_condition_blocks])
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers = _expected_true_blockers(expected_true)
    if abort_condition_blocks:
        blockers.extend(abort_condition_blocks)
    if active_score is None:
        blockers.append("abort_condition_score_missing")
    elif active_score < thresholds["min_abort_condition_score"]:
        blockers.append("abort_condition_score_below_threshold")
    return {
        "ready": not blockers,
        **expected_true,
        "abort_condition_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_abort_condition_score"],
        "abort_condition_blocks": abort_condition_blocks,
        "blockers": _unique(blockers),
    }


def _data_quality_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = [_mapping(source.get("data_quality")), _mapping(source.get("readiness_snapshot")), source]
    score = _score_from_contexts(contexts, ("data_quality_score",))
    missing_fields = _as_list(_value_from_contexts(contexts, ("missing_fields",)))
    invalid_rows = _number_from_contexts(contexts, ("invalid_rows",))
    duplicate_tickets = _number_from_contexts(contexts, ("duplicate_tickets",))
    malformed_timestamps = _number_from_contexts(contexts, ("malformed_timestamps",))
    blockers: list[str] = []
    if score is None:
        blockers.append("data_quality_score_missing")
    elif score < thresholds["min_data_quality_score"]:
        blockers.append("data_quality_score_below_threshold")
    if missing_fields:
        blockers.append("data_quality_missing_fields")
    for key, value in {
        "invalid_rows": invalid_rows,
        "duplicate_tickets": duplicate_tickets,
        "malformed_timestamps": malformed_timestamps,
    }.items():
        if value is not None and value > 0:
            blockers.append(f"{key}_present")
    return {
        "ready": not blockers,
        "data_quality_score": score,
        "score": score,
        "threshold": thresholds["min_data_quality_score"],
        "missing_fields": missing_fields,
        "invalid_rows": invalid_rows,
        "duplicate_tickets": duplicate_tickets,
        "malformed_timestamps": malformed_timestamps,
        "blockers": _unique(blockers),
    }


def _resolve_prep_status(
    *,
    missing_core_evidence: bool,
    threshold_blockers: Sequence[str],
    supervised_summary: Mapping[str, Any],
    owner_summary: Mapping[str, Any],
    runtime_summary: Mapping[str, Any],
    candidate_summary: Mapping[str, Any],
    order_intent_summary: Mapping[str, Any],
    risk_summary: Mapping[str, Any],
    order_safety_summary: Mapping[str, Any],
    telemetry_summary: Mapping[str, Any],
    abort_summary: Mapping[str, Any],
    data_quality_summary: Mapping[str, Any],
    execution_prep_score: float | None,
    min_execution_prep_score: float,
) -> str:
    if missing_core_evidence:
        return INCOMPLETE_INPUTS
    if not supervised_summary["ready"]:
        return BLOCKED_BY_SUPERVISED_DEMO_READINESS
    if not owner_summary["ready"]:
        return BLOCKED_BY_OWNER_APPROVAL_GATE
    if not runtime_summary["ready"]:
        return BLOCKED_BY_OANDA_RUNTIME_BOUNDARY
    if not candidate_summary["ready"]:
        return BLOCKED_BY_CANDIDATE_TICKET
    if not order_intent_summary["ready"]:
        return BLOCKED_BY_ORDER_INTENT
    if not risk_summary["ready"]:
        return BLOCKED_BY_RISK_GATES
    if not order_safety_summary["ready"]:
        return BLOCKED_BY_ORDER_SAFETY
    if not telemetry_summary["ready"]:
        return BLOCKED_BY_TELEMETRY_PLAN
    if not abort_summary["ready"]:
        return BLOCKED_BY_ABORT_CONDITIONS
    if not data_quality_summary["ready"]:
        return BLOCKED_BY_DATA_QUALITY
    if threshold_blockers:
        return NEEDS_MORE_EVIDENCE
    if execution_prep_score is None or execution_prep_score < min_execution_prep_score:
        return NEEDS_MORE_EVIDENCE
    return OANDA_DEMO_EXECUTION_PREP_READY


def _sanitized_execution_prep_package(source: Mapping[str, Any]) -> dict[str, Any]:
    runtime_contexts = _contexts(source, "oanda_runtime_boundary")
    ticket_contexts = _contexts(source, "candidate_ticket")
    order_contexts = _contexts(source, "order_intent")
    risk_contexts = _contexts(source, "risk_gates")
    stop_loss_present = (
        _number_from_contexts(order_contexts, ("stop_loss_price",)) is not None
        or _number_from_contexts(order_contexts, ("stop_loss_pips",)) is not None
    )
    take_profit_present = (
        _number_from_contexts(order_contexts, ("take_profit_price",)) is not None
        or _number_from_contexts(order_contexts, ("take_profit_pips",)) is not None
    )
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "broker_name": _text_from_contexts(runtime_contexts, ("broker_name",)),
        "broker_mode": _text_from_contexts(runtime_contexts, ("broker_mode",)),
        "account_environment": _text_from_contexts(runtime_contexts, ("account_environment",)),
        "strategy_id": _text_from_contexts(ticket_contexts, ("strategy_id",)),
        "candidate_id": _text_from_contexts(ticket_contexts, ("candidate_id",)),
        "instrument": _text_from_contexts(ticket_contexts, ("instrument",)),
        "side": _text_from_contexts(ticket_contexts, ("side",)),
        "timeframe": _text_from_contexts(ticket_contexts, ("timeframe",)),
        "order_type": _text_from_contexts(order_contexts, ("order_type",)),
        "units": _number_from_contexts(order_contexts, ("units",)),
        "stop_loss_present": stop_loss_present,
        "take_profit_present": take_profit_present,
        "max_spread_pips": _number_from_contexts(order_contexts, ("max_spread_pips",)),
        "max_slippage_pips": _number_from_contexts(order_contexts, ("max_slippage_pips",)),
        "risk_limits": {
            "max_position_units": _number_from_contexts(order_contexts, ("max_position_units",)),
            "max_risk_per_trade_pct": _number_from_contexts(risk_contexts, ("max_risk_per_trade_pct",)),
            "max_daily_loss_pct": _number_from_contexts(risk_contexts, ("max_daily_loss_pct",)),
            "risk_reward_minimum": _number_from_contexts(risk_contexts, ("risk_reward_minimum",)),
            "account_risk_mode": _text_from_contexts(risk_contexts, ("account_risk_mode",)),
        },
        "required_owner_approval": True,
        "runtime_credentials_required": True,
        "credentials_included": False,
        "execution_authorized": False,
        "order_placement_allowed": False,
    }


def _owner_action_queue(
    *,
    supervised_summary: Mapping[str, Any],
    owner_summary: Mapping[str, Any],
    runtime_summary: Mapping[str, Any],
    candidate_summary: Mapping[str, Any],
    order_intent_summary: Mapping[str, Any],
    risk_summary: Mapping[str, Any],
    order_safety_summary: Mapping[str, Any],
    telemetry_summary: Mapping[str, Any],
    abort_summary: Mapping[str, Any],
    prep_blockers: Sequence[str],
    next_best_packet: str,
) -> list[dict[str, Any]]:
    actions = [
        (
            "REVIEW_SUPERVISED_DEMO_READINESS",
            "Review supervised demo readiness",
            "high",
            supervised_summary.get("blockers", []),
            "Review the sanitized upstream readiness packet before runtime handoff planning.",
        ),
        (
            "REVIEW_OWNER_APPROVAL_GATE",
            "Review owner approval gate",
            "high",
            owner_summary.get("blockers", []),
            "Confirm Anthony review is required and execution remains blocked.",
        ),
        (
            "REVIEW_OANDA_RUNTIME_BOUNDARY",
            "Review OANDA runtime boundary",
            "high",
            runtime_summary.get("blockers", []),
            "Confirm demo-only OANDA boundaries and no broker, credential, bank, or money authority.",
        ),
        (
            "REVIEW_CANDIDATE_TICKET",
            "Review candidate ticket",
            "high",
            candidate_summary.get("blockers", []),
            "Review the sanitized candidate identity, instrument, side, timeframe, and quality evidence.",
        ),
        (
            "REVIEW_ORDER_INTENT",
            "Review order intent",
            "high",
            order_intent_summary.get("blockers", []),
            "Review order type, units, hard stop, hard take profit, spread cap, and slippage cap.",
        ),
        (
            "REVIEW_RISK_GATES",
            "Review risk gates",
            "high",
            risk_summary.get("blockers", []),
            "Review max loss, daily loss stop, kill switch, position cap, and risk percentages.",
        ),
        (
            "REVIEW_ORDER_SAFETY",
            "Review order safety",
            "high",
            order_safety_summary.get("blockers", []),
            "Review pair whitelist, spread, slippage, SL/TP, duplicate order, market-open, and preview checks.",
        ),
        (
            "REVIEW_TELEMETRY_PLAN",
            "Review telemetry plan",
            "medium",
            telemetry_summary.get("blockers", []),
            "Review sanitized audit, ticket, snapshots, exception capture, and owner report requirements.",
        ),
        (
            "REVIEW_ABORT_CONDITIONS",
            "Review abort conditions",
            "high",
            abort_summary.get("blockers", []),
            "Review every fail-closed abort condition before any separate owner-approved runtime packet.",
        ),
        (
            "REVIEW_SANITIZED_EXECUTION_PREP_PACKAGE",
            "Review sanitized execution-prep package",
            "high",
            prep_blockers,
            "Review the sanitized package only; do not provide credentials to this evaluator.",
        ),
        (
            "REVIEW_NEXT_PACKET",
            f"Review next packet: {next_best_packet}",
            "medium",
            ["owner_review_required"],
            "Review the next packet manually; no execution is authorized by this evaluator.",
        ),
    ]
    return [_action(action_id, title, priority, blocked_by, safe_action) for action_id, title, priority, blocked_by, safe_action in actions]


def _action(
    action_id: str,
    title: str,
    priority: str,
    blocked_by: Sequence[str],
    safe_action: str,
) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "title": title,
        "priority": priority,
        "owner_decision_required": True,
        "execution_allowed": False,
        "safe_action": safe_action,
        "blocked_by": list(blocked_by) or ["owner_review_required"],
    }


def _safe_manual_next_action(prep_status: str) -> str:
    if prep_status == OANDA_DEMO_EXECUTION_PREP_READY:
        return (
            "Owner may review the sanitized OANDA demo execution-prep package and queue the owner-approved "
            "runtime handoff packet. AIOS does not place orders, access brokers, authorize money movement, "
            "or use credentials in this packet."
        )
    if prep_status == INCOMPLETE_INPUTS:
        return (
            "Provide sanitized supervised-demo readiness, owner approval, OANDA runtime boundary, candidate "
            "ticket, order intent, risk gate, order safety, telemetry, and abort-condition evidence, then "
            "rerun this evaluator."
        )
    return (
        "Collect sanitized OANDA demo execution-prep evidence, rerun the read-only prep evaluator, and keep "
        "broker, credential, order, bank, and money actions outside AIOS until owner approval."
    )


def _next_remaining_lane(remaining: Mapping[str, Any], next_best_packet: str) -> dict[str, Any]:
    lanes = remaining.get("remaining_lanes")
    if isinstance(lanes, Sequence) and not isinstance(lanes, (str, bytes)):
        for item in lanes:
            lane = _mapping(item)
            if not lane:
                continue
            safe_packet_name = _text(lane.get("safe_packet_name"), "")
            lane_id = _text(lane.get("lane_id"), "")
            if safe_packet_name == next_best_packet or (
                next_best_packet == NEXT_PACKET_IF_READY and NEXT_LANE_ID in lane_id
            ):
                return {
                    "lane_id": lane_id or NEXT_LANE_ID,
                    "title": _text(lane.get("title"), "OANDA demo owner-approved runtime handoff"),
                    "status": _text(lane.get("status"), "OWNER_REVIEW_REQUIRED"),
                    "safe_packet_name": safe_packet_name or next_best_packet,
                }
    if next_best_packet == NEXT_PACKET_IF_READY:
        return {
            "lane_id": NEXT_LANE_ID,
            "title": "OANDA demo owner-approved runtime handoff",
            "status": "OWNER_REVIEW_REQUIRED",
            "safe_packet_name": NEXT_PACKET_IF_READY,
        }
    return {
        "lane_id": CURRENT_LANE_ID,
        "title": "OANDA demo supervised execution prep",
        "status": "LOCAL_EVIDENCE_REQUIRED",
        "safe_packet_name": THIS_PACKET,
    }


def _input_summary(
    *,
    source: Mapping[str, Any],
    explicit_execution_prep_score: float | None,
    derived_execution_prep_score: float | None,
    sub_scores: Mapping[str, float | None],
    missing_information: Sequence[str],
) -> dict[str, Any]:
    return {
        "input_fields_seen": sorted(str(key) for key in source.keys()),
        "meaningful_evidence_present": any(_has_meaningful_value(source.get(key)) for key in CORE_EVIDENCE_KEYS),
        "explicit_execution_prep_score": explicit_execution_prep_score,
        "derived_execution_prep_score": derived_execution_prep_score,
        "sub_scores": dict(sub_scores),
        "missing_information": list(missing_information),
    }


def _safety() -> dict[str, bool]:
    return {
        "read_only": True,
        "manual_execution_only": True,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "trade_execution_allowed": False,
        "demo_execution_allowed": False,
        "order_placement_allowed": False,
        "credential_use_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
        "dashboard_runtime_allowed": False,
        "owner_gate_required": True,
        "fixed_return_target_promised": False,
        "profit_claim_authorized": False,
    }


def _empty_summary(name: str, blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "ready": False,
        "summary": name,
        "score": None,
        "threshold": None,
        "blockers": list(blockers),
    }


def _missing_information(source: Mapping[str, Any]) -> list[str]:
    return [key for key in CORE_EVIDENCE_KEYS if not _has_meaningful_value(source.get(key))]


def _has_meaningful_value(value: Any) -> bool:
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return bool(value)
    return value is not None


def _contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            lowered = str(key).lower()
            if lowered not in SAFE_BOUNDARY_KEYS and any(part in lowered for part in SENSITIVE_KEY_PARTS):
                return True
            if _contains_sensitive_key(item):
                return True
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def _contexts(source: Mapping[str, Any], section: str) -> list[Mapping[str, Any]]:
    return [
        _mapping(source.get(section)),
        _mapping(source.get("readiness_snapshot")),
        source,
    ]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _value_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> Any:
    for context in contexts:
        for key in keys:
            if key in context:
                return context[key]
    return None


def _score_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> float | None:
    return _score(_value_from_contexts(contexts, keys))


def _number_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> float | None:
    return _number(_value_from_contexts(contexts, keys))


def _bool_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> bool | None:
    return _as_bool(_value_from_contexts(contexts, keys))


def _false_authority_value(contexts: Sequence[Mapping[str, Any]], key: str) -> bool | None:
    saw_false = False
    for context in contexts:
        if key not in context:
            continue
        value = _as_bool(context[key])
        if value is True:
            return True
        if value is False:
            saw_false = True
    return False if saw_false else None


def _text_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> str:
    return _text(_value_from_contexts(contexts, keys), "")


def _blockers_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> list[str]:
    blockers: list[str] = []
    for key in keys:
        value = _value_from_contexts(contexts, (key,))
        if isinstance(value, Mapping):
            for item in value.values():
                blockers.extend(_as_list(item))
        else:
            blockers.extend(_as_list(value))
    return _unique(str(item) for item in blockers if str(item))


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, Mapping):
        return list(value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return list(value)
    return [value]


def _score(value: Any) -> float | None:
    number = _number(value)
    if number is None:
        return None
    if number > 1.0:
        number = number / 100.0 if number <= 100.0 else 1.0
    return max(0.0, min(1.0, number))


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str):
        try:
            number = float(value.strip().removesuffix("%"))
        except ValueError:
            return None
    else:
        return None
    return number if isfinite(number) else None


def _as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "y", "1", "pass", "passed", "ready"}:
            return True
        if lowered in {"false", "no", "n", "0", "fail", "failed", "blocked"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return None


def _text(value: Any, default: str) -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _present(value: Any) -> bool:
    if value in (None, "", [], {}):
        return False
    if isinstance(value, str) and value.strip().upper() in {"UNAVAILABLE", "UNKNOWN", "MISSING"}:
        return False
    return True


def _broker_name_ok(value: str) -> bool:
    return not value or value.strip().upper() == "OANDA"


def _broker_mode_ok(value: str) -> bool:
    return not value or value.strip().upper() in ALLOWED_BROKER_MODES


def _account_environment_ok(value: str) -> bool:
    return not value or value.strip().upper() in ALLOWED_ACCOUNT_ENVIRONMENTS


def _expected_false_score_value(value: bool | None) -> bool | None:
    if value is None:
        return None
    return value is False


def _expected_true_blockers(values: Mapping[str, bool | None]) -> list[str]:
    blockers: list[str] = []
    for key, value in values.items():
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is False:
            blockers.append(f"{key}_false")
    return blockers


def _exact_bool_blockers(
    *,
    expected_true: Mapping[str, bool | None],
    expected_false: Mapping[str, bool | None],
) -> list[str]:
    blockers = _expected_true_blockers(expected_true)
    for key, value in expected_false.items():
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is True:
            blockers.append(f"{key}_true")
    return blockers


def _bool_score(values: Sequence[bool | None]) -> float | None:
    present = [value for value in values if value is not None]
    if not present:
        return None
    return sum(1.0 for value in present if value is True) / len(present)


def _average_score(values: Sequence[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    if not present:
        return None
    return round(sum(present) / len(present), 6)


def _unique(values: Sequence[str] | Any) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for raw_value in values:
        value = str(raw_value)
        if value and value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


__all__ = [
    "SCHEMA",
    "MODE",
    "evaluate_oanda_demo_supervised_execution_prep_v1",
]
