"""Read-only Forex supervised demo readiness packet evaluator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from math import isfinite
from typing import Any


SCHEMA = "AIOS_FOREX_SUPERVISED_DEMO_READINESS_PACKET_V1"
MODE = "READ_ONLY_SUPERVISED_DEMO_READINESS_PACKET"

SUPERVISED_DEMO_READY = "SUPERVISED_DEMO_READY"
NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
BLOCKED_BY_DEMO_CANDIDATE_REVIEW = "BLOCKED_BY_DEMO_CANDIDATE_REVIEW"
BLOCKED_BY_OANDA_DEMO_BOUNDARY = "BLOCKED_BY_OANDA_DEMO_BOUNDARY"
BLOCKED_BY_OWNER_APPROVAL_GATE = "BLOCKED_BY_OWNER_APPROVAL_GATE"
BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY = "BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY"
BLOCKED_BY_RISK_CONTROLS = "BLOCKED_BY_RISK_CONTROLS"
BLOCKED_BY_ORDER_SAFETY = "BLOCKED_BY_ORDER_SAFETY"
BLOCKED_BY_TELEMETRY = "BLOCKED_BY_TELEMETRY"
BLOCKED_BY_POST_DEMO_REVIEW = "BLOCKED_BY_POST_DEMO_REVIEW"
BLOCKED_BY_DATA_QUALITY = "BLOCKED_BY_DATA_QUALITY"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

THIS_PACKET = SCHEMA
NEXT_PACKET_IF_READY = "AIOS_FOREX_OANDA_DEMO_SUPERVISED_EXECUTION_PREP_V1"
CURRENT_LANE_ID = "SUPERVISED_DEMO_READINESS"
NEXT_LANE_ID = "OANDA_DEMO_SUPERVISED_EXECUTION_PREP"

OPPORTUNITY_CAPTURE_OBJECTIVE = (
    "maximize validated risk-adjusted opportunity capture while preserving capital and proving edge"
)

DEFAULT_THRESHOLDS: dict[str, float] = {
    "min_readiness_score": 0.85,
    "min_demo_candidate_review_score": 0.80,
    "min_oanda_demo_boundary_score": 0.90,
    "min_owner_approval_gate_score": 0.90,
    "min_runtime_credential_boundary_score": 0.90,
    "min_risk_control_score": 0.85,
    "min_order_safety_score": 0.90,
    "min_telemetry_score": 0.80,
    "min_post_demo_review_score": 0.75,
    "min_data_quality_score": 0.80,
}

THRESHOLD_FLOORS: dict[str, float] = {
    "min_readiness_score": 0.80,
    "min_demo_candidate_review_score": 0.75,
    "min_oanda_demo_boundary_score": 0.85,
    "min_owner_approval_gate_score": 0.85,
    "min_runtime_credential_boundary_score": 0.85,
    "min_risk_control_score": 0.80,
    "min_order_safety_score": 0.85,
    "min_telemetry_score": 0.75,
    "min_post_demo_review_score": 0.70,
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
    "token",
    "secret",
    "credential",
    "credentials",
    "broker_token",
    "access_token",
)

SAFE_BOUNDARY_KEYS = frozenset(
    {
        "runtime_credential_boundary",
        "runtime_credential_boundary_score",
        "runtime_credential_boundary_summary",
        "credential_use_allowed",
        "credential_redaction_required",
        "credentials_persisted",
        "credentials_requested",
        "runtime_only_credentials_required",
        "secret_scan_required",
        "broker_api_allowed",
        "demo_execution_allowed",
        "trade_execution_allowed",
        "money_movement_allowed",
        "bank_access_allowed",
        "live_account_allowed",
        "real_money_allowed",
    }
)

CORE_EVIDENCE_KEYS = (
    "demo_candidate_review_readiness",
    "oanda_demo_boundary",
    "owner_approval_gate",
    "runtime_credential_boundary",
    "risk_controls",
    "order_safety",
    "telemetry",
    "post_demo_review",
)

FALSE_AUTHORITY_FIELDS = (
    "broker_api_allowed",
    "trade_execution_allowed",
    "demo_execution_allowed",
    "credential_use_allowed",
)


def evaluate_supervised_demo_readiness_packet_v1(payload: dict | None = None) -> dict[str, Any]:
    """Evaluate sanitized supervised-demo readiness evidence without execution authority."""

    source = payload if isinstance(payload, Mapping) else {}
    threshold_policy = _threshold_policy(_mapping(source.get("thresholds")))
    thresholds = threshold_policy["active_thresholds"]

    if _contains_sensitive_key(source):
        return _sensitive_payload(source, threshold_policy)

    missing_information = _missing_information(source)
    missing_core_evidence = bool(missing_information)

    demo_candidate_summary = _demo_candidate_review_summary(source, thresholds)
    oanda_boundary_summary = _oanda_demo_boundary_summary(source, thresholds)
    owner_gate_summary = _owner_approval_gate_summary(source, thresholds)
    runtime_boundary_summary = _runtime_credential_boundary_summary(source, thresholds)
    risk_summary = _risk_control_summary(source, thresholds)
    order_summary = _order_safety_summary(source, thresholds)
    telemetry_summary = _telemetry_summary(source, thresholds)
    post_demo_summary = _post_demo_review_summary(source, thresholds)
    data_quality_summary = _data_quality_summary(source, thresholds)

    sub_scores = {
        "demo_candidate_review_score": demo_candidate_summary["score"],
        "oanda_demo_boundary_score": oanda_boundary_summary["score"],
        "owner_approval_gate_score": owner_gate_summary["score"],
        "runtime_credential_boundary_score": runtime_boundary_summary["score"],
        "risk_control_score": risk_summary["score"],
        "order_safety_score": order_summary["score"],
        "telemetry_score": telemetry_summary["score"],
        "post_demo_review_score": post_demo_summary["score"],
        "data_quality_score": data_quality_summary["score"],
    }
    explicit_readiness_score = _score_from_contexts(
        _contexts(source, "readiness_snapshot"),
        ("readiness_score",),
    )
    derived_readiness_score = _average_score(sub_scores.values())
    readiness_score = explicit_readiness_score if explicit_readiness_score is not None else derived_readiness_score

    readiness_blockers = _unique(
        [
            *threshold_policy["threshold_blockers"],
            *missing_information,
            *demo_candidate_summary["blockers"],
            *oanda_boundary_summary["blockers"],
            *owner_gate_summary["blockers"],
            *runtime_boundary_summary["blockers"],
            *risk_summary["blockers"],
            *order_summary["blockers"],
            *telemetry_summary["blockers"],
            *post_demo_summary["blockers"],
            *data_quality_summary["blockers"],
        ]
    )

    readiness_status = _resolve_readiness_status(
        missing_core_evidence=missing_core_evidence,
        demo_candidate_summary=demo_candidate_summary,
        oanda_boundary_summary=oanda_boundary_summary,
        owner_gate_summary=owner_gate_summary,
        runtime_boundary_summary=runtime_boundary_summary,
        risk_summary=risk_summary,
        order_summary=order_summary,
        telemetry_summary=telemetry_summary,
        post_demo_summary=post_demo_summary,
        data_quality_summary=data_quality_summary,
        readiness_score=readiness_score,
        min_readiness_score=thresholds["min_readiness_score"],
    )
    next_best_packet = NEXT_PACKET_IF_READY if readiness_status == SUPERVISED_DEMO_READY else THIS_PACKET

    return _base_result(
        source=source,
        threshold_policy=threshold_policy,
        readiness_status=readiness_status,
        readiness_score=readiness_score,
        explicit_readiness_score=explicit_readiness_score,
        derived_readiness_score=derived_readiness_score,
        sub_scores=sub_scores,
        demo_candidate_summary=demo_candidate_summary,
        oanda_boundary_summary=oanda_boundary_summary,
        owner_gate_summary=owner_gate_summary,
        runtime_boundary_summary=runtime_boundary_summary,
        risk_summary=risk_summary,
        order_summary=order_summary,
        telemetry_summary=telemetry_summary,
        post_demo_summary=post_demo_summary,
        data_quality_summary=data_quality_summary,
        missing_information=missing_information,
        readiness_blockers=readiness_blockers,
        next_best_packet=next_best_packet,
    )


def _sensitive_payload(source: Mapping[str, Any], threshold_policy: Mapping[str, Any]) -> dict[str, Any]:
    blockers = ["sensitive_data_provided"]
    summary = _empty_summary("blocked_by_sensitive_data", blockers)
    result = _base_result(
        source=source,
        threshold_policy=threshold_policy,
        readiness_status=BLOCKED_BY_DATA_QUALITY,
        readiness_score=None,
        explicit_readiness_score=None,
        derived_readiness_score=None,
        sub_scores={
            "demo_candidate_review_score": None,
            "oanda_demo_boundary_score": None,
            "owner_approval_gate_score": None,
            "runtime_credential_boundary_score": None,
            "risk_control_score": None,
            "order_safety_score": None,
            "telemetry_score": None,
            "post_demo_review_score": None,
            "data_quality_score": None,
        },
        demo_candidate_summary=summary,
        oanda_boundary_summary=summary,
        owner_gate_summary=summary,
        runtime_boundary_summary=summary,
        risk_summary=summary,
        order_summary=summary,
        telemetry_summary=summary,
        post_demo_summary=summary,
        data_quality_summary=summary,
        missing_information=["remove_sensitive_data"],
        readiness_blockers=blockers,
        next_best_packet=THIS_PACKET,
    )
    result["input_summary"]["input_redacted"] = True
    result["audit_record"]["input_redacted"] = True
    result["safe_manual_next_action"] = (
        "Remove sensitive data and rerun with sanitized demo-readiness evidence. Keep broker, credential, "
        "order, bank, and money actions outside AIOS until owner approval."
    )
    return result


def _base_result(
    *,
    source: Mapping[str, Any],
    threshold_policy: Mapping[str, Any],
    readiness_status: str,
    readiness_score: float | None,
    explicit_readiness_score: float | None,
    derived_readiness_score: float | None,
    sub_scores: Mapping[str, float | None],
    demo_candidate_summary: Mapping[str, Any],
    oanda_boundary_summary: Mapping[str, Any],
    owner_gate_summary: Mapping[str, Any],
    runtime_boundary_summary: Mapping[str, Any],
    risk_summary: Mapping[str, Any],
    order_summary: Mapping[str, Any],
    telemetry_summary: Mapping[str, Any],
    post_demo_summary: Mapping[str, Any],
    data_quality_summary: Mapping[str, Any],
    missing_information: Sequence[str],
    readiness_blockers: Sequence[str],
    next_best_packet: str,
) -> dict[str, Any]:
    supervised_demo_ready = readiness_status == SUPERVISED_DEMO_READY
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "trade_execution_allowed": False,
        "demo_execution_allowed": False,
        "credential_use_allowed": False,
        "scheduler_created": False,
        "daemon_created": False,
        "webhook_created": False,
        "dashboard_runtime_created": False,
        "owner_decision_required": True,
        "supervised_demo_ready": supervised_demo_ready,
        "supervised_demo_execution_authorized": False,
        "readiness_status": readiness_status,
        "opportunity_capture_objective": OPPORTUNITY_CAPTURE_OBJECTIVE,
        "input_summary": _input_summary(
            source=source,
            explicit_readiness_score=explicit_readiness_score,
            derived_readiness_score=derived_readiness_score,
            sub_scores=sub_scores,
            missing_information=missing_information,
        ),
        "threshold_policy": dict(threshold_policy),
        "demo_candidate_review_summary": dict(demo_candidate_summary),
        "oanda_demo_boundary_summary": dict(oanda_boundary_summary),
        "owner_approval_gate_summary": dict(owner_gate_summary),
        "runtime_credential_boundary_summary": dict(runtime_boundary_summary),
        "risk_control_summary": dict(risk_summary),
        "order_safety_summary": dict(order_summary),
        "telemetry_summary": dict(telemetry_summary),
        "post_demo_review_summary": dict(post_demo_summary),
        "data_quality_summary": dict(data_quality_summary),
        "readiness_score": readiness_score,
        "readiness_blockers": list(readiness_blockers),
        "missing_information": list(missing_information),
        "owner_action_queue": _owner_action_queue(
            demo_candidate_summary=demo_candidate_summary,
            oanda_boundary_summary=oanda_boundary_summary,
            owner_gate_summary=owner_gate_summary,
            runtime_boundary_summary=runtime_boundary_summary,
            risk_summary=risk_summary,
            order_summary=order_summary,
            telemetry_summary=telemetry_summary,
            post_demo_summary=post_demo_summary,
            next_best_packet=next_best_packet,
        ),
        "next_best_packet": next_best_packet,
        "next_remaining_lane": _next_remaining_lane(
            _mapping(source.get("remaining_work_closure_index")),
            next_best_packet,
        ),
        "safe_manual_next_action": _safe_manual_next_action(readiness_status),
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "as_of_date": _text(source.get("as_of_date"), datetime.now(timezone.utc).isoformat()),
            "owner_name": _text(source.get("owner_name"), "Anthony"),
            "input_fields_seen": sorted(str(key) for key in source.keys()),
            "readiness_status": readiness_status,
            "readiness_score": readiness_score,
            "supervised_demo_ready": supervised_demo_ready,
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
        "rejected_overrides": rejected,
        "threshold_blockers": ["threshold_override_rejected"] if rejected else [],
        "guardrails": dict(THRESHOLD_FLOORS),
    }


def _demo_candidate_review_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "demo_candidate_review_readiness")
    readiness_status = _text_from_contexts(contexts, ("readiness_status",))
    demo_review_ready = _bool_from_contexts(contexts, ("demo_review_ready",))
    score = _score_from_contexts(contexts, ("readiness_score", "demo_candidate_review_score"))
    next_best_packet = _text_from_contexts(contexts, ("next_best_packet",))
    review_blockers = _blockers_from_contexts(contexts, ("readiness_blockers",))
    blockers: list[str] = []
    if score is None:
        blockers.append("demo_candidate_review_score_missing")
    elif score < thresholds["min_demo_candidate_review_score"]:
        blockers.append("demo_candidate_review_score_below_threshold")
    if readiness_status and readiness_status.upper() not in {
        "DEMO_REVIEW_READY",
        "SUPERVISED_DEMO_READY",
        "READY",
        "PASS",
    }:
        blockers.append("demo_candidate_readiness_status_not_ready")
    if demo_review_ready is not True:
        blockers.append("demo_review_ready_missing" if demo_review_ready is None else "demo_review_ready_false")
    if review_blockers:
        blockers.extend(review_blockers)
    if not readiness_status and demo_review_ready is not True and score is None:
        blockers.append("demo_candidate_review_signal_missing")
    return {
        "ready": not blockers,
        "readiness_status": readiness_status,
        "demo_review_ready": demo_review_ready,
        "readiness_score": score,
        "score": score,
        "threshold": thresholds["min_demo_candidate_review_score"],
        "next_best_packet": next_best_packet,
        "readiness_blockers": review_blockers,
        "blockers": _unique(blockers),
    }


def _oanda_demo_boundary_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "oanda_demo_boundary")
    broker_name = _text_from_contexts(contexts, ("broker_name",))
    broker_mode = _text_from_contexts(contexts, ("broker_mode",))
    expected_true = {
        "demo_account_only": _bool_from_contexts(contexts, ("demo_account_only",)),
    }
    expected_false = {
        "live_account_allowed": _false_authority_value(contexts, "live_account_allowed"),
        "real_money_allowed": _false_authority_value(contexts, "real_money_allowed"),
        "broker_api_allowed": _false_authority_value(contexts, "broker_api_allowed"),
        "trade_execution_allowed": _false_authority_value(contexts, "trade_execution_allowed"),
        "demo_execution_allowed": _false_authority_value(contexts, "demo_execution_allowed"),
        "credential_use_allowed": _false_authority_value(contexts, "credential_use_allowed"),
    }
    explicit_score = _score_from_contexts(contexts, ("oanda_demo_boundary_score",))
    derived_score = _bool_score(
        [
            _broker_name_ok(broker_name),
            _broker_mode_ok(broker_mode),
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
    for key, value in expected_true.items():
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is False:
            blockers.append(f"{key}_false")
    for key, value in expected_false.items():
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is True:
            blockers.append(f"{key}_true")
    if active_score is None:
        blockers.append("oanda_demo_boundary_score_missing")
    elif active_score < thresholds["min_oanda_demo_boundary_score"]:
        blockers.append("oanda_demo_boundary_score_below_threshold")
    return {
        "ready": not blockers,
        "broker_name": broker_name,
        "broker_mode": broker_mode,
        **expected_true,
        **expected_false,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_oanda_demo_boundary_score"],
        "blockers": _unique(blockers),
    }


def _owner_approval_gate_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "owner_approval_gate")
    expected_true = {
        "owner_approval_required": _bool_from_contexts(contexts, ("owner_approval_required",)),
        "owner_review_required": _bool_from_contexts(contexts, ("owner_review_required",)),
        "owner_named_approval_required": _bool_from_contexts(contexts, ("owner_named_approval_required",)),
        "manual_execution_only": _bool_from_contexts(contexts, ("manual_execution_only",)),
        "approval_packet_required": _bool_from_contexts(contexts, ("approval_packet_required",)),
        "owner_can_cancel": _bool_from_contexts(contexts, ("owner_can_cancel",)),
    }
    execution_allowed = _false_authority_value(contexts, "execution_allowed")
    explicit_score = _score_from_contexts(contexts, ("owner_approval_gate_score",))
    derived_score = _bool_score([*expected_true.values(), _expected_false_score_value(execution_allowed)])
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers = _exact_bool_blockers(expected_true=expected_true, expected_false={"execution_allowed": execution_allowed})
    if active_score is None:
        blockers.append("owner_approval_gate_score_missing")
    elif active_score < thresholds["min_owner_approval_gate_score"]:
        blockers.append("owner_approval_gate_score_below_threshold")
    return {
        "ready": not blockers,
        **expected_true,
        "execution_allowed": execution_allowed,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_owner_approval_gate_score"],
        "blockers": _unique(blockers),
    }


def _runtime_credential_boundary_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "runtime_credential_boundary")
    expected_true = {
        "runtime_only_credentials_required": _bool_from_contexts(contexts, ("runtime_only_credentials_required",)),
        "credential_redaction_required": _bool_from_contexts(contexts, ("credential_redaction_required",)),
        "secret_scan_required": _bool_from_contexts(contexts, ("secret_scan_required",)),
    }
    expected_false = {
        "credentials_persisted": _false_authority_value(contexts, "credentials_persisted"),
        "credentials_requested": _false_authority_value(contexts, "credentials_requested"),
        "credential_use_allowed": _false_authority_value(contexts, "credential_use_allowed"),
    }
    explicit_score = _score_from_contexts(contexts, ("runtime_credential_boundary_score",))
    derived_score = _bool_score(
        [*expected_true.values(), *[_expected_false_score_value(value) for value in expected_false.values()]]
    )
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers = _exact_bool_blockers(expected_true=expected_true, expected_false=expected_false)
    if active_score is None:
        blockers.append("runtime_credential_boundary_score_missing")
    elif active_score < thresholds["min_runtime_credential_boundary_score"]:
        blockers.append("runtime_credential_boundary_score_below_threshold")
    return {
        "ready": not blockers,
        **expected_false,
        **expected_true,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_runtime_credential_boundary_score"],
        "blockers": _unique(blockers),
    }


def _risk_control_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "risk_controls")
    controls = {
        "max_loss_gate_present": _bool_from_contexts(contexts, ("max_loss_gate_present",)),
        "daily_loss_stop_present": _bool_from_contexts(contexts, ("daily_loss_stop_present",)),
        "kill_switch_present": _bool_from_contexts(contexts, ("kill_switch_present",)),
        "position_size_limit_present": _bool_from_contexts(contexts, ("position_size_limit_present",)),
    }
    max_position_units = _number_from_contexts(contexts, ("max_position_units",))
    max_risk_per_trade_pct = _number_from_contexts(contexts, ("max_risk_per_trade_pct",))
    max_daily_loss_pct = _number_from_contexts(contexts, ("max_daily_loss_pct",))
    risk_blocks = _blockers_from_contexts(contexts, ("risk_blocks",))
    explicit_score = _score_from_contexts(contexts, ("risk_control_score",))
    derived_score = _bool_score(
        [
            *controls.values(),
            _limit_at_or_below(max_risk_per_trade_pct, 0.01),
            _limit_at_or_below(max_daily_loss_pct, 0.03),
            not risk_blocks,
        ]
    )
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers = _expected_true_blockers(controls)
    if max_risk_per_trade_pct is None:
        blockers.append("max_risk_per_trade_pct_missing")
    elif max_risk_per_trade_pct > 0.01:
        blockers.append("max_risk_per_trade_pct_above_limit")
    if max_daily_loss_pct is None:
        blockers.append("max_daily_loss_pct_missing")
    elif max_daily_loss_pct > 0.03:
        blockers.append("max_daily_loss_pct_above_limit")
    if risk_blocks:
        blockers.extend(risk_blocks)
    if active_score is None:
        blockers.append("risk_control_score_missing")
    elif active_score < thresholds["min_risk_control_score"]:
        blockers.append("risk_control_score_below_threshold")
    return {
        "ready": not blockers,
        **controls,
        "max_position_units": max_position_units,
        "max_risk_per_trade_pct": max_risk_per_trade_pct,
        "max_daily_loss_pct": max_daily_loss_pct,
        "risk_control_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_risk_control_score"],
        "risk_blocks": risk_blocks,
        "blockers": _unique(blockers),
    }


def _order_safety_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "order_safety")
    expected_true = {
        "stop_loss_required": _bool_from_contexts(contexts, ("stop_loss_required",)),
        "take_profit_required": _bool_from_contexts(contexts, ("take_profit_required",)),
        "one_order_only": _bool_from_contexts(contexts, ("one_order_only",)),
        "order_size_capped": _bool_from_contexts(contexts, ("order_size_capped",)),
        "pair_whitelist_present": _bool_from_contexts(contexts, ("pair_whitelist_present",)),
        "spread_check_required": _bool_from_contexts(contexts, ("spread_check_required",)),
        "slippage_check_required": _bool_from_contexts(contexts, ("slippage_check_required",)),
    }
    expected_false = {
        "market_order_allowed": _false_authority_value(contexts, "market_order_allowed"),
        "pending_order_allowed": _false_authority_value(contexts, "pending_order_allowed"),
    }
    order_safety_blocks = _blockers_from_contexts(contexts, ("order_safety_blocks",))
    explicit_score = _score_from_contexts(contexts, ("order_safety_score",))
    derived_score = _bool_score(
        [
            *expected_true.values(),
            *[_expected_false_score_value(value) for value in expected_false.values()],
            not order_safety_blocks,
        ]
    )
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers = _exact_bool_blockers(expected_true=expected_true, expected_false=expected_false)
    if order_safety_blocks:
        blockers.extend(order_safety_blocks)
    if active_score is None:
        blockers.append("order_safety_score_missing")
    elif active_score < thresholds["min_order_safety_score"]:
        blockers.append("order_safety_score_below_threshold")
    return {
        "ready": not blockers,
        **expected_true,
        **expected_false,
        "order_safety_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_order_safety_score"],
        "order_safety_blocks": order_safety_blocks,
        "blockers": _unique(blockers),
    }


def _telemetry_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "telemetry")
    evidence = {
        "audit_log_required": _bool_from_contexts(contexts, ("audit_log_required",)),
        "sanitized_evidence_required": _bool_from_contexts(contexts, ("sanitized_evidence_required",)),
        "pre_trade_snapshot_required": _bool_from_contexts(contexts, ("pre_trade_snapshot_required",)),
        "post_trade_snapshot_required": _bool_from_contexts(contexts, ("post_trade_snapshot_required",)),
        "exception_capture_required": _bool_from_contexts(contexts, ("exception_capture_required",)),
        "owner_review_report_required": _bool_from_contexts(contexts, ("owner_review_report_required",)),
    }
    telemetry_blocks = _blockers_from_contexts(contexts, ("telemetry_blocks",))
    explicit_score = _score_from_contexts(contexts, ("telemetry_score",))
    derived_score = _bool_score([*evidence.values(), not telemetry_blocks])
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers = _expected_true_blockers(evidence)
    if telemetry_blocks:
        blockers.extend(telemetry_blocks)
    if active_score is None:
        blockers.append("telemetry_score_missing")
    elif active_score < thresholds["min_telemetry_score"]:
        blockers.append("telemetry_score_below_threshold")
    return {
        "ready": not blockers,
        **evidence,
        "telemetry_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_telemetry_score"],
        "telemetry_blocks": telemetry_blocks,
        "blockers": _unique(blockers),
    }


def _post_demo_review_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "post_demo_review")
    evidence = {
        "post_trade_review_required": _bool_from_contexts(contexts, ("post_trade_review_required",)),
        "pnl_review_required": _bool_from_contexts(contexts, ("pnl_review_required",)),
        "risk_review_required": _bool_from_contexts(contexts, ("risk_review_required",)),
        "execution_quality_review_required": _bool_from_contexts(contexts, ("execution_quality_review_required",)),
        "screenshot_or_snapshot_review_required": _bool_from_contexts(
            contexts,
            ("screenshot_or_snapshot_review_required",),
        ),
        "next_trade_blocked_until_review": _bool_from_contexts(contexts, ("next_trade_blocked_until_review",)),
    }
    post_demo_review_blocks = _blockers_from_contexts(contexts, ("post_demo_review_blocks",))
    explicit_score = _score_from_contexts(contexts, ("post_demo_review_score",))
    derived_score = _bool_score([*evidence.values(), not post_demo_review_blocks])
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers = _expected_true_blockers(evidence)
    if post_demo_review_blocks:
        blockers.extend(post_demo_review_blocks)
    if active_score is None:
        blockers.append("post_demo_review_score_missing")
    elif active_score < thresholds["min_post_demo_review_score"]:
        blockers.append("post_demo_review_score_below_threshold")
    return {
        "ready": not blockers,
        **evidence,
        "post_demo_review_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_post_demo_review_score"],
        "post_demo_review_blocks": post_demo_review_blocks,
        "blockers": _unique(blockers),
    }


def _data_quality_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = [
        _mapping(source.get("data_quality")),
        _mapping(source.get("readiness_snapshot")),
        source,
    ]
    score = _score_from_contexts(contexts, ("data_quality_score",))
    missing_fields = _as_list(_value_from_contexts(contexts, ("missing_fields",)))
    invalid_rows = _number_from_contexts(contexts, ("invalid_rows",))
    duplicate_trades = _number_from_contexts(contexts, ("duplicate_trades",))
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
        "duplicate_trades": duplicate_trades,
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
        "duplicate_trades": duplicate_trades,
        "malformed_timestamps": malformed_timestamps,
        "blockers": _unique(blockers),
    }


def _resolve_readiness_status(
    *,
    missing_core_evidence: bool,
    demo_candidate_summary: Mapping[str, Any],
    oanda_boundary_summary: Mapping[str, Any],
    owner_gate_summary: Mapping[str, Any],
    runtime_boundary_summary: Mapping[str, Any],
    risk_summary: Mapping[str, Any],
    order_summary: Mapping[str, Any],
    telemetry_summary: Mapping[str, Any],
    post_demo_summary: Mapping[str, Any],
    data_quality_summary: Mapping[str, Any],
    readiness_score: float | None,
    min_readiness_score: float,
) -> str:
    if missing_core_evidence:
        return INCOMPLETE_INPUTS
    if not demo_candidate_summary["ready"]:
        return BLOCKED_BY_DEMO_CANDIDATE_REVIEW
    if not oanda_boundary_summary["ready"]:
        return BLOCKED_BY_OANDA_DEMO_BOUNDARY
    if not owner_gate_summary["ready"]:
        return BLOCKED_BY_OWNER_APPROVAL_GATE
    if not runtime_boundary_summary["ready"]:
        return BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY
    if not risk_summary["ready"]:
        return BLOCKED_BY_RISK_CONTROLS
    if not order_summary["ready"]:
        return BLOCKED_BY_ORDER_SAFETY
    if not telemetry_summary["ready"]:
        return BLOCKED_BY_TELEMETRY
    if not post_demo_summary["ready"]:
        return BLOCKED_BY_POST_DEMO_REVIEW
    if not data_quality_summary["ready"]:
        return BLOCKED_BY_DATA_QUALITY
    if readiness_score is None or readiness_score < min_readiness_score:
        return NEEDS_MORE_EVIDENCE
    return SUPERVISED_DEMO_READY


def _owner_action_queue(
    *,
    demo_candidate_summary: Mapping[str, Any],
    oanda_boundary_summary: Mapping[str, Any],
    owner_gate_summary: Mapping[str, Any],
    runtime_boundary_summary: Mapping[str, Any],
    risk_summary: Mapping[str, Any],
    order_summary: Mapping[str, Any],
    telemetry_summary: Mapping[str, Any],
    post_demo_summary: Mapping[str, Any],
    next_best_packet: str,
) -> list[dict[str, Any]]:
    actions = [
        (
            "REVIEW_DEMO_CANDIDATE_READINESS",
            "Review demo candidate readiness",
            "high",
            demo_candidate_summary.get("blockers", []),
            "Review sanitized candidate-review readiness before any owner decision.",
        ),
        (
            "REVIEW_OANDA_DEMO_BOUNDARY",
            "Review OANDA demo boundary",
            "high",
            oanda_boundary_summary.get("blockers", []),
            "Confirm demo-account-only OANDA boundary and no broker, execution, credential, bank, or money authority.",
        ),
        (
            "REVIEW_OWNER_APPROVAL_GATE",
            "Review owner approval gate",
            "high",
            owner_gate_summary.get("blockers", []),
            "Confirm Anthony review is required and execution remains blocked.",
        ),
        (
            "REVIEW_RUNTIME_CREDENTIAL_BOUNDARY",
            "Review runtime credential boundary",
            "high",
            runtime_boundary_summary.get("blockers", []),
            "Confirm credentials are runtime-only, redacted, unpersisted, and unused by this packet.",
        ),
        (
            "REVIEW_RISK_CONTROLS",
            "Review risk controls",
            "high",
            risk_summary.get("blockers", []),
            "Review loss gates, daily stop, kill switch, position cap, and risk percentages.",
        ),
        (
            "REVIEW_ORDER_SAFETY",
            "Review order safety",
            "high",
            order_summary.get("blockers", []),
            "Review stop loss, take profit, one-order rule, pair whitelist, spread checks, and slippage checks.",
        ),
        (
            "REVIEW_TELEMETRY",
            "Review telemetry",
            "medium",
            telemetry_summary.get("blockers", []),
            "Review audit, sanitized evidence, snapshots, exception capture, and owner report requirements.",
        ),
        (
            "REVIEW_POST_DEMO_REVIEW",
            "Review post-demo review",
            "medium",
            post_demo_summary.get("blockers", []),
            "Review post-trade, PnL, risk, execution quality, and snapshot review requirements.",
        ),
        (
            "REVIEW_NEXT_PACKET",
            f"Review next packet: {next_best_packet}",
            "medium",
            ["owner_review_required"],
            "Review the next packet manually; no execution is authorized.",
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


def _safe_manual_next_action(readiness_status: str) -> str:
    if readiness_status == SUPERVISED_DEMO_READY:
        return (
            "Owner may review the supervised demo readiness packet and queue OANDA demo supervised execution "
            "preparation. AIOS does not place orders, access brokers, authorize money movement, or use "
            "credentials in this packet."
        )
    if readiness_status == INCOMPLETE_INPUTS:
        return (
            "Provide sanitized demo-candidate review, OANDA demo boundary, owner approval gate, runtime "
            "credential boundary, risk control, order safety, telemetry, and post-demo review evidence, "
            "then rerun this evaluator."
        )
    return (
        "Collect sanitized supervised-demo readiness evidence, rerun the read-only readiness evaluator, and "
        "keep broker, credential, order, bank, and money actions outside AIOS until owner approval."
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
                    "title": _text(lane.get("title"), "OANDA demo supervised execution prep"),
                    "status": _text(lane.get("status"), "OWNER_REVIEW_REQUIRED"),
                    "safe_packet_name": safe_packet_name or next_best_packet,
                }
    if next_best_packet == NEXT_PACKET_IF_READY:
        return {
            "lane_id": NEXT_LANE_ID,
            "title": "OANDA demo supervised execution prep",
            "status": "OWNER_REVIEW_REQUIRED",
            "safe_packet_name": NEXT_PACKET_IF_READY,
        }
    return {
        "lane_id": CURRENT_LANE_ID,
        "title": "Supervised demo readiness",
        "status": "LOCAL_EVIDENCE_REQUIRED",
        "safe_packet_name": THIS_PACKET,
    }


def _input_summary(
    *,
    source: Mapping[str, Any],
    explicit_readiness_score: float | None,
    derived_readiness_score: float | None,
    sub_scores: Mapping[str, float | None],
    missing_information: Sequence[str],
) -> dict[str, Any]:
    return {
        "input_fields_seen": sorted(str(key) for key in source.keys()),
        "meaningful_evidence_present": any(_has_meaningful_value(source.get(key)) for key in CORE_EVIDENCE_KEYS),
        "explicit_readiness_score": explicit_readiness_score,
        "derived_readiness_score": derived_readiness_score,
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
            number = float(value.strip())
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


def _broker_name_ok(value: str) -> bool:
    return not value or value.strip().upper() == "OANDA"


def _broker_mode_ok(value: str) -> bool:
    return not value or value.strip().upper() in {"DEMO", "OANDA_DEMO", "PAPER_DEMO"}


def _limit_at_or_below(value: float | None, limit: float) -> bool | None:
    if value is None:
        return None
    return value <= limit


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
    "evaluate_supervised_demo_readiness_packet_v1",
]
