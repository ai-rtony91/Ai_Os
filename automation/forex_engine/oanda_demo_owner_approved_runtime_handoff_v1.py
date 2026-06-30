"""Read-only OANDA demo owner-approved runtime handoff evaluator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from math import isfinite
from typing import Any


SCHEMA = "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_RUNTIME_HANDOFF_V1"
MODE = "READ_ONLY_OANDA_DEMO_OWNER_APPROVED_RUNTIME_HANDOFF"

OANDA_DEMO_RUNTIME_HANDOFF_READY = "OANDA_DEMO_RUNTIME_HANDOFF_READY"
NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
BLOCKED_BY_EXECUTION_PREP = "BLOCKED_BY_EXECUTION_PREP"
BLOCKED_BY_OWNER_APPROVAL = "BLOCKED_BY_OWNER_APPROVAL"
BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY = "BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY"
BLOCKED_BY_OANDA_ACCOUNT_BOUNDARY = "BLOCKED_BY_OANDA_ACCOUNT_BOUNDARY"
BLOCKED_BY_ORDER_PREVIEW = "BLOCKED_BY_ORDER_PREVIEW"
BLOCKED_BY_RISK_GATES = "BLOCKED_BY_RISK_GATES"
BLOCKED_BY_ABORT_CONDITIONS = "BLOCKED_BY_ABORT_CONDITIONS"
BLOCKED_BY_TELEMETRY = "BLOCKED_BY_TELEMETRY"
BLOCKED_BY_POST_TRADE_REVIEW = "BLOCKED_BY_POST_TRADE_REVIEW"
BLOCKED_BY_DATA_QUALITY = "BLOCKED_BY_DATA_QUALITY"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

THIS_PACKET = SCHEMA
NEXT_PACKET_IF_READY = "AIOS_FOREX_OANDA_DEMO_SUPERVISED_ORDER_EXECUTION_V1"
CURRENT_LANE_ID = "OANDA_DEMO_OWNER_APPROVED_RUNTIME_HANDOFF"
NEXT_LANE_ID = "OANDA_DEMO_SUPERVISED_ORDER_EXECUTION"

OPPORTUNITY_CAPTURE_OBJECTIVE = (
    "maximize validated risk-adjusted opportunity capture while preserving capital and proving edge"
)

DEFAULT_THRESHOLDS: dict[str, float] = {
    "min_runtime_handoff_score": 0.92,
    "min_execution_prep_score": 0.90,
    "min_owner_approval_score": 0.95,
    "min_runtime_credential_boundary_score": 0.95,
    "min_oanda_account_boundary_score": 0.95,
    "min_order_preview_score": 0.90,
    "min_risk_gate_score": 0.90,
    "min_abort_condition_score": 0.95,
    "min_telemetry_score": 0.85,
    "min_post_trade_review_score": 0.80,
    "min_data_quality_score": 0.80,
}

THRESHOLD_FLOORS: dict[str, float] = {
    "min_runtime_handoff_score": 0.90,
    "min_execution_prep_score": 0.85,
    "min_owner_approval_score": 0.90,
    "min_runtime_credential_boundary_score": 0.90,
    "min_oanda_account_boundary_score": 0.90,
    "min_order_preview_score": 0.85,
    "min_risk_gate_score": 0.85,
    "min_abort_condition_score": 0.90,
    "min_telemetry_score": 0.80,
    "min_post_trade_review_score": 0.75,
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
        "execution_allowed",
        "execution_authorized",
        "live_account_allowed",
        "money_movement_allowed",
        "order_placement_allowed",
        "owner_runtime_credential_entry_required",
        "real_money_allowed",
        "runtime_credentials_required",
        "runtime_only_credentials_required",
        "scheduler_created",
        "secret_scan_required",
        "trade_execution_allowed",
        "webhook_created",
    }
)

CORE_EVIDENCE_KEYS = (
    "execution_prep_package",
    "owner_approval",
    "runtime_credential_boundary",
    "oanda_account_boundary",
    "order_preview",
    "risk_gates",
    "abort_conditions",
    "telemetry",
    "post_trade_review",
)

READY_PREP_STATUSES = frozenset({"OANDA_DEMO_EXECUTION_PREP_READY", "READY", "PASS"})
ALLOWED_BROKER_MODES = frozenset({"DEMO", "OANDA_DEMO", "PRACTICE", "PAPER_DEMO"})
ALLOWED_ACCOUNT_ENVIRONMENTS = frozenset({"PRACTICE", "DEMO", "OANDA_DEMO"})
ALLOWED_SIDES = frozenset({"BUY", "SELL", "LONG", "SHORT"})
ALLOWED_ORDER_TYPES = frozenset({"MARKET", "LIMIT", "PREP_ONLY"})


def evaluate_oanda_demo_owner_approved_runtime_handoff_v1(payload: dict | None = None) -> dict[str, Any]:
    """Evaluate sanitized runtime-handoff evidence without broker or order authority."""

    source = payload if isinstance(payload, Mapping) else {}
    threshold_policy = _threshold_policy(_mapping(source.get("thresholds")))
    thresholds = threshold_policy["active_thresholds"]

    if _contains_sensitive_key(source):
        return _sensitive_payload(source, threshold_policy)

    missing_information = _missing_information(source)
    missing_core_evidence = bool(missing_information)

    execution_prep_summary = _execution_prep_summary(source, thresholds)
    owner_summary = _owner_approval_summary(source, thresholds)
    credential_summary = _runtime_credential_boundary_summary(source, thresholds)
    account_summary = _oanda_account_boundary_summary(source, thresholds)
    order_summary = _order_preview_summary(source, thresholds)
    risk_summary = _risk_gate_summary(source, thresholds)
    abort_summary = _abort_condition_summary(source, thresholds)
    telemetry_summary = _telemetry_summary(source, thresholds)
    post_trade_summary = _post_trade_review_summary(source, thresholds)
    data_quality_summary = _data_quality_summary(source, thresholds)

    sub_scores = {
        "execution_prep_score": execution_prep_summary["score"],
        "owner_approval_score": owner_summary["score"],
        "credential_boundary_score": credential_summary["score"],
        "oanda_account_boundary_score": account_summary["score"],
        "order_preview_score": order_summary["score"],
        "risk_gate_score": risk_summary["score"],
        "abort_condition_score": abort_summary["score"],
        "telemetry_score": telemetry_summary["score"],
        "post_trade_review_score": post_trade_summary["score"],
        "data_quality_score": data_quality_summary["score"],
    }
    explicit_runtime_handoff_score = _score_from_contexts(
        [_mapping(source.get("readiness_snapshot")), source],
        ("runtime_handoff_score",),
    )
    derived_runtime_handoff_score = _average_score(sub_scores.values())
    runtime_handoff_score = (
        explicit_runtime_handoff_score
        if explicit_runtime_handoff_score is not None
        else derived_runtime_handoff_score
    )

    handoff_blockers = _unique(
        [
            *threshold_policy["threshold_blockers"],
            *missing_information,
            *execution_prep_summary["blockers"],
            *owner_summary["blockers"],
            *credential_summary["blockers"],
            *account_summary["blockers"],
            *order_summary["blockers"],
            *risk_summary["blockers"],
            *abort_summary["blockers"],
            *telemetry_summary["blockers"],
            *post_trade_summary["blockers"],
            *data_quality_summary["blockers"],
        ]
    )

    handoff_status = _resolve_handoff_status(
        missing_core_evidence=missing_core_evidence,
        threshold_blockers=threshold_policy["threshold_blockers"],
        execution_prep_summary=execution_prep_summary,
        owner_summary=owner_summary,
        credential_summary=credential_summary,
        account_summary=account_summary,
        order_summary=order_summary,
        risk_summary=risk_summary,
        abort_summary=abort_summary,
        telemetry_summary=telemetry_summary,
        post_trade_summary=post_trade_summary,
        data_quality_summary=data_quality_summary,
        runtime_handoff_score=runtime_handoff_score,
        min_runtime_handoff_score=thresholds["min_runtime_handoff_score"],
    )
    next_best_packet = NEXT_PACKET_IF_READY if handoff_status == OANDA_DEMO_RUNTIME_HANDOFF_READY else THIS_PACKET

    return _base_result(
        source=source,
        threshold_policy=threshold_policy,
        handoff_status=handoff_status,
        runtime_handoff_score=runtime_handoff_score,
        explicit_runtime_handoff_score=explicit_runtime_handoff_score,
        derived_runtime_handoff_score=derived_runtime_handoff_score,
        sub_scores=sub_scores,
        execution_prep_summary=execution_prep_summary,
        owner_summary=owner_summary,
        credential_summary=credential_summary,
        account_summary=account_summary,
        order_summary=order_summary,
        risk_summary=risk_summary,
        abort_summary=abort_summary,
        telemetry_summary=telemetry_summary,
        post_trade_summary=post_trade_summary,
        data_quality_summary=data_quality_summary,
        missing_information=missing_information,
        handoff_blockers=handoff_blockers,
        next_best_packet=next_best_packet,
    )


def _sensitive_payload(source: Mapping[str, Any], threshold_policy: Mapping[str, Any]) -> dict[str, Any]:
    blockers = ["sensitive_data_provided"]
    summary = _empty_summary("blocked_by_sensitive_data", blockers)
    result = _base_result(
        source=source,
        threshold_policy=threshold_policy,
        handoff_status=BLOCKED_BY_DATA_QUALITY,
        runtime_handoff_score=None,
        explicit_runtime_handoff_score=None,
        derived_runtime_handoff_score=None,
        sub_scores={
            "execution_prep_score": None,
            "owner_approval_score": None,
            "credential_boundary_score": None,
            "oanda_account_boundary_score": None,
            "order_preview_score": None,
            "risk_gate_score": None,
            "abort_condition_score": None,
            "telemetry_score": None,
            "post_trade_review_score": None,
            "data_quality_score": None,
        },
        execution_prep_summary=summary,
        owner_summary=summary,
        credential_summary=summary,
        account_summary=summary,
        order_summary=summary,
        risk_summary=summary,
        abort_summary=summary,
        telemetry_summary=summary,
        post_trade_summary=summary,
        data_quality_summary=summary,
        missing_information=["remove_sensitive_data"],
        handoff_blockers=blockers,
        next_best_packet=THIS_PACKET,
    )
    result["input_summary"]["input_redacted"] = True
    result["audit_record"]["input_redacted"] = True
    result["safe_manual_next_action"] = (
        "Remove sensitive data and rerun with sanitized runtime-handoff evidence. Keep broker, credential, "
        "order, bank, and fund-transfer actions outside AIOS until owner approval."
    )
    return result


def _base_result(
    *,
    source: Mapping[str, Any],
    threshold_policy: Mapping[str, Any],
    handoff_status: str,
    runtime_handoff_score: float | None,
    explicit_runtime_handoff_score: float | None,
    derived_runtime_handoff_score: float | None,
    sub_scores: Mapping[str, float | None],
    execution_prep_summary: Mapping[str, Any],
    owner_summary: Mapping[str, Any],
    credential_summary: Mapping[str, Any],
    account_summary: Mapping[str, Any],
    order_summary: Mapping[str, Any],
    risk_summary: Mapping[str, Any],
    abort_summary: Mapping[str, Any],
    telemetry_summary: Mapping[str, Any],
    post_trade_summary: Mapping[str, Any],
    data_quality_summary: Mapping[str, Any],
    missing_information: Sequence[str],
    handoff_blockers: Sequence[str],
    next_best_packet: str,
) -> dict[str, Any]:
    runtime_handoff_ready = handoff_status == OANDA_DEMO_RUNTIME_HANDOFF_READY
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
        "owner_named_approval_required": True,
        "runtime_handoff_ready": runtime_handoff_ready,
        "supervised_demo_execution_authorized": False,
        "handoff_status": handoff_status,
        "opportunity_capture_objective": OPPORTUNITY_CAPTURE_OBJECTIVE,
        "input_summary": _input_summary(
            source=source,
            explicit_runtime_handoff_score=explicit_runtime_handoff_score,
            derived_runtime_handoff_score=derived_runtime_handoff_score,
            sub_scores=sub_scores,
            missing_information=missing_information,
        ),
        "threshold_policy": dict(threshold_policy),
        "execution_prep_summary": dict(execution_prep_summary),
        "owner_approval_summary": dict(owner_summary),
        "runtime_credential_boundary_summary": dict(credential_summary),
        "oanda_account_boundary_summary": dict(account_summary),
        "order_preview_summary": dict(order_summary),
        "risk_gate_summary": dict(risk_summary),
        "abort_condition_summary": dict(abort_summary),
        "telemetry_summary": dict(telemetry_summary),
        "post_trade_review_summary": dict(post_trade_summary),
        "data_quality_summary": dict(data_quality_summary),
        "runtime_handoff_score": runtime_handoff_score,
        "handoff_blockers": list(handoff_blockers),
        "missing_information": list(missing_information),
        "sanitized_runtime_handoff_package": _sanitized_runtime_handoff_package(source),
        "owner_action_queue": _owner_action_queue(
            execution_prep_summary=execution_prep_summary,
            owner_summary=owner_summary,
            credential_summary=credential_summary,
            account_summary=account_summary,
            order_summary=order_summary,
            risk_summary=risk_summary,
            abort_summary=abort_summary,
            telemetry_summary=telemetry_summary,
            post_trade_summary=post_trade_summary,
            handoff_blockers=handoff_blockers,
            next_best_packet=next_best_packet,
        ),
        "next_best_packet": next_best_packet,
        "next_remaining_lane": _next_remaining_lane(
            _mapping(source.get("remaining_work_closure_index")),
            next_best_packet,
        ),
        "safe_manual_next_action": _safe_manual_next_action(handoff_status),
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "as_of_date": _text(source.get("as_of_date"), datetime.now(timezone.utc).isoformat()),
            "owner_name": _text(source.get("owner_name"), _text(owner_summary.get("owner_name"), "Anthony")),
            "input_fields_seen": sorted(str(key) for key in source.keys()),
            "handoff_status": handoff_status,
            "runtime_handoff_score": runtime_handoff_score,
            "runtime_handoff_ready": runtime_handoff_ready,
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


def _execution_prep_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "execution_prep_package")
    prep_status = _text_from_contexts(contexts, ("prep_status", "status"))
    prep_ready = _bool_from_contexts(contexts, ("prep_ready",))
    runtime_handoff_ready = _bool_from_contexts(contexts, ("runtime_handoff_ready",))
    explicit_score = _score_from_contexts(contexts, ("execution_prep_score",))
    next_best_packet = _text_from_contexts(contexts, ("next_best_packet",))
    prep_blockers = _blockers_from_contexts(contexts, ("prep_blockers", "blockers"))
    derived_score = _bool_score(
        [
            None if not prep_status else prep_status.upper() in READY_PREP_STATUSES,
            prep_ready,
            runtime_handoff_ready,
            not prep_blockers,
        ]
    )
    active_score = explicit_score if explicit_score is not None else derived_score

    blockers: list[str] = []
    if not prep_status:
        blockers.append("prep_status_missing")
    elif prep_status.upper() not in READY_PREP_STATUSES:
        blockers.append("prep_status_not_ready")
    if prep_ready is not True:
        blockers.append("prep_ready_missing" if prep_ready is None else "prep_ready_false")
    if runtime_handoff_ready is not True:
        blockers.append(
            "execution_prep_runtime_handoff_ready_missing"
            if runtime_handoff_ready is None
            else "execution_prep_runtime_handoff_ready_false"
        )
    if prep_blockers:
        blockers.extend(prep_blockers)
    if active_score is None:
        blockers.append("execution_prep_score_missing")
    elif active_score < thresholds["min_execution_prep_score"]:
        blockers.append("execution_prep_score_below_threshold")

    return {
        "ready": not blockers,
        "prep_status": prep_status,
        "prep_ready": prep_ready,
        "runtime_handoff_ready": runtime_handoff_ready,
        "execution_prep_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_execution_prep_score"],
        "next_best_packet": next_best_packet,
        "prep_blockers": prep_blockers,
        "sanitized_execution_prep_package_present": bool(
            _mapping(_first_present(contexts, ("sanitized_execution_prep_package",)))
        ),
        "blockers": _unique(blockers),
    }


def _owner_approval_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "owner_approval")
    owner_name = _text_from_contexts(contexts, ("owner_name",))
    expected_true = {
        "owner_approval_required": _bool_from_contexts(contexts, ("owner_approval_required",)),
        "owner_named_approval_required": _bool_from_contexts(contexts, ("owner_named_approval_required",)),
        "owner_review_required": _bool_from_contexts(contexts, ("owner_review_required",)),
        "owner_accepts_sanitized_package": _bool_from_contexts(contexts, ("owner_accepts_sanitized_package",)),
        "owner_accepts_demo_only_boundary": _bool_from_contexts(contexts, ("owner_accepts_demo_only_boundary",)),
        "owner_accepts_runtime_credential_entry": _bool_from_contexts(
            contexts,
            ("owner_accepts_runtime_credential_entry",),
        ),
        "owner_accepts_one_order_only": _bool_from_contexts(contexts, ("owner_accepts_one_order_only",)),
        "owner_can_cancel": _bool_from_contexts(contexts, ("owner_can_cancel",)),
    }
    expected_false = {
        "execution_allowed": _false_authority_value(contexts, "execution_allowed"),
    }
    explicit_score = _score_from_contexts(contexts, ("owner_approval_score",))
    derived_score = _bool_score(
        [
            None if not owner_name else owner_name == "Anthony",
            *expected_true.values(),
            *[_expected_false_score_value(value) for value in expected_false.values()],
        ]
    )
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers: list[str] = []
    if owner_name and owner_name != "Anthony":
        blockers.append("owner_name_not_anthony")
    blockers.extend(_exact_bool_blockers(expected_true=expected_true, expected_false=expected_false))
    if active_score is None:
        blockers.append("owner_approval_score_missing")
    elif active_score < thresholds["min_owner_approval_score"]:
        blockers.append("owner_approval_score_below_threshold")
    return {
        "ready": not blockers,
        "owner_name": owner_name,
        **expected_true,
        **expected_false,
        "owner_approval_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_owner_approval_score"],
        "blockers": _unique(blockers),
    }


def _runtime_credential_boundary_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "runtime_credential_boundary")
    expected_true = {
        "runtime_credentials_required": _bool_from_contexts(contexts, ("runtime_credentials_required",)),
        "runtime_only_credentials_required": _bool_from_contexts(contexts, ("runtime_only_credentials_required",)),
        "owner_runtime_credential_entry_required": _bool_from_contexts(
            contexts,
            ("owner_runtime_credential_entry_required",),
        ),
        "credential_redaction_required": _bool_from_contexts(contexts, ("credential_redaction_required",)),
        "secret_scan_required": _bool_from_contexts(contexts, ("secret_scan_required",)),
    }
    expected_false = {
        "credentials_included": _false_authority_value(contexts, "credentials_included"),
        "credentials_persisted": _false_authority_value(contexts, "credentials_persisted"),
        "credentials_requested": _false_authority_value(contexts, "credentials_requested"),
        "credential_use_allowed": _false_authority_value(contexts, "credential_use_allowed"),
    }
    explicit_score = _score_from_contexts(contexts, ("credential_boundary_score",))
    derived_score = _bool_score(
        [
            *expected_true.values(),
            *[_expected_false_score_value(value) for value in expected_false.values()],
        ]
    )
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers = _exact_bool_blockers(expected_true=expected_true, expected_false=expected_false)
    if active_score is None:
        blockers.append("credential_boundary_score_missing")
    elif active_score < thresholds["min_runtime_credential_boundary_score"]:
        blockers.append("credential_boundary_score_below_threshold")
    return {
        "ready": not blockers,
        **expected_true,
        **expected_false,
        "credential_boundary_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_runtime_credential_boundary_score"],
        "blockers": _unique(blockers),
    }


def _oanda_account_boundary_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "oanda_account_boundary")
    broker_name = _text_from_contexts(contexts, ("broker_name",))
    broker_mode = _text_from_contexts(contexts, ("broker_mode",))
    account_environment = _text_from_contexts(contexts, ("account_environment",))
    expected_true = {
        "demo_account_only": _bool_from_contexts(contexts, ("demo_account_only",)),
    }
    expected_false = {
        "live_account_allowed": _false_authority_value(contexts, "live_account_allowed"),
        "real_money_allowed": _false_authority_value(contexts, "real_money_allowed"),
        "bank_access_allowed": _false_authority_value(contexts, "bank_access_allowed"),
        "money_movement_allowed": _false_authority_value(contexts, "money_movement_allowed"),
        "broker_api_allowed": _false_authority_value(contexts, "broker_api_allowed"),
        "trade_execution_allowed": _false_authority_value(contexts, "trade_execution_allowed"),
        "demo_execution_allowed": _false_authority_value(contexts, "demo_execution_allowed"),
        "order_placement_allowed": _false_authority_value(contexts, "order_placement_allowed"),
    }
    explicit_score = _score_from_contexts(contexts, ("oanda_account_boundary_score",))
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
        blockers.append("oanda_account_boundary_score_missing")
    elif active_score < thresholds["min_oanda_account_boundary_score"]:
        blockers.append("oanda_account_boundary_score_below_threshold")
    return {
        "ready": not blockers,
        "broker_name": broker_name,
        "broker_mode": broker_mode,
        "account_environment": account_environment,
        **expected_true,
        **expected_false,
        "oanda_account_boundary_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_oanda_account_boundary_score"],
        "blockers": _unique(blockers),
    }


def _order_preview_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "order_preview")
    strategy_id = _text_from_contexts(contexts, ("strategy_id",))
    candidate_id = _text_from_contexts(contexts, ("candidate_id",))
    instrument = _text_from_contexts(contexts, ("instrument",))
    side = _text_from_contexts(contexts, ("side",))
    order_type = _text_from_contexts(contexts, ("order_type",))
    units = _number_from_contexts(contexts, ("units",))
    max_position_units = _number_from_contexts(contexts, ("max_position_units",))
    stop_loss_present = _bool_from_contexts(contexts, ("stop_loss_present",))
    take_profit_present = _bool_from_contexts(contexts, ("take_profit_present",))
    max_spread_pips = _number_from_contexts(contexts, ("max_spread_pips",))
    max_slippage_pips = _number_from_contexts(contexts, ("max_slippage_pips",))
    order_preview_snapshot_required = _bool_from_contexts(contexts, ("order_preview_snapshot_required",))
    order_preview_accepted_by_owner = _bool_from_contexts(contexts, ("order_preview_accepted_by_owner",))
    order_preview_blocks = _blockers_from_contexts(contexts, ("order_preview_blocks",))
    explicit_score = _score_from_contexts(contexts, ("order_preview_score",))
    derived_score = _bool_score(
        [
            _present(strategy_id),
            _present(candidate_id),
            _present(instrument),
            side.upper() in ALLOWED_SIDES if side else None,
            None if not order_type else order_type.upper() in ALLOWED_ORDER_TYPES,
            units is not None and units > 0,
            None if units is None or max_position_units is None else units <= max_position_units,
            stop_loss_present,
            take_profit_present,
            max_spread_pips is not None,
            max_slippage_pips is not None,
            order_preview_snapshot_required,
            order_preview_accepted_by_owner,
            not order_preview_blocks,
        ]
    )
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers: list[str] = []
    for key, value in {
        "strategy_id": strategy_id,
        "candidate_id": candidate_id,
        "instrument": instrument,
    }.items():
        if not _present(value):
            blockers.append(f"{key}_missing")
    if not side:
        blockers.append("side_missing")
    elif side.upper() not in ALLOWED_SIDES:
        blockers.append("side_not_supported")
    if order_type and order_type.upper() not in ALLOWED_ORDER_TYPES:
        blockers.append("order_type_not_supported")
    if units is None:
        blockers.append("units_missing")
    elif units <= 0:
        blockers.append("units_not_positive")
    elif max_position_units is not None and units > max_position_units:
        blockers.append("units_above_max_position_units")
    if stop_loss_present is not True:
        blockers.append("stop_loss_present_missing" if stop_loss_present is None else "stop_loss_present_false")
    if take_profit_present is not True:
        blockers.append(
            "take_profit_present_missing" if take_profit_present is None else "take_profit_present_false"
        )
    if max_spread_pips is None:
        blockers.append("max_spread_pips_missing")
    if max_slippage_pips is None:
        blockers.append("max_slippage_pips_missing")
    if order_preview_snapshot_required is not True:
        blockers.append(
            "order_preview_snapshot_required_missing"
            if order_preview_snapshot_required is None
            else "order_preview_snapshot_required_false"
        )
    if order_preview_accepted_by_owner is not True:
        blockers.append(
            "order_preview_accepted_by_owner_missing"
            if order_preview_accepted_by_owner is None
            else "order_preview_accepted_by_owner_false"
        )
    if order_preview_blocks:
        blockers.extend(order_preview_blocks)
    if active_score is None:
        blockers.append("order_preview_score_missing")
    elif active_score < thresholds["min_order_preview_score"]:
        blockers.append("order_preview_score_below_threshold")
    return {
        "ready": not blockers,
        "strategy_id": strategy_id,
        "candidate_id": candidate_id,
        "instrument": instrument,
        "side": side,
        "order_type": order_type,
        "units": units,
        "max_position_units": max_position_units,
        "stop_loss_present": stop_loss_present,
        "take_profit_present": take_profit_present,
        "max_spread_pips": max_spread_pips,
        "max_slippage_pips": max_slippage_pips,
        "order_preview_snapshot_required": order_preview_snapshot_required,
        "order_preview_accepted_by_owner": order_preview_accepted_by_owner,
        "order_preview_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_order_preview_score"],
        "order_preview_blocks": order_preview_blocks,
        "blockers": _unique(blockers),
    }


def _risk_gate_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "risk_gates")
    expected_true = {
        "max_loss_gate_present": _bool_from_contexts(contexts, ("max_loss_gate_present",)),
        "daily_loss_stop_present": _bool_from_contexts(contexts, ("daily_loss_stop_present",)),
        "kill_switch_present": _bool_from_contexts(contexts, ("kill_switch_present",)),
        "position_size_limit_present": _bool_from_contexts(contexts, ("position_size_limit_present",)),
        "one_order_only": _bool_from_contexts(contexts, ("one_order_only",)),
    }
    max_risk_per_trade_pct = _number_from_contexts(contexts, ("max_risk_per_trade_pct",))
    max_daily_loss_pct = _number_from_contexts(contexts, ("max_daily_loss_pct",))
    risk_reward_minimum = _number_from_contexts(contexts, ("risk_reward_minimum",))
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
        "risk_gate_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_risk_gate_score"],
        "risk_gate_blocks": risk_gate_blocks,
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
        "abort_if_wrong_account_detected": _bool_from_contexts(contexts, ("abort_if_wrong_account_detected",)),
        "abort_if_live_account_detected": _bool_from_contexts(contexts, ("abort_if_live_account_detected",)),
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


def _telemetry_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "telemetry")
    expected_true = {
        "audit_log_required": _bool_from_contexts(contexts, ("audit_log_required",)),
        "sanitized_ticket_required": _bool_from_contexts(contexts, ("sanitized_ticket_required",)),
        "pre_trade_snapshot_required": _bool_from_contexts(contexts, ("pre_trade_snapshot_required",)),
        "order_preview_snapshot_required": _bool_from_contexts(contexts, ("order_preview_snapshot_required",)),
        "post_trade_snapshot_required": _bool_from_contexts(contexts, ("post_trade_snapshot_required",)),
        "exception_capture_required": _bool_from_contexts(contexts, ("exception_capture_required",)),
        "owner_review_report_required": _bool_from_contexts(contexts, ("owner_review_report_required",)),
        "runtime_handoff_report_required": _bool_from_contexts(contexts, ("runtime_handoff_report_required",)),
    }
    telemetry_blocks = _blockers_from_contexts(contexts, ("telemetry_blocks",))
    explicit_score = _score_from_contexts(contexts, ("telemetry_score",))
    derived_score = _bool_score([*expected_true.values(), not telemetry_blocks])
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers = _expected_true_blockers(expected_true)
    if telemetry_blocks:
        blockers.extend(telemetry_blocks)
    if active_score is None:
        blockers.append("telemetry_score_missing")
    elif active_score < thresholds["min_telemetry_score"]:
        blockers.append("telemetry_score_below_threshold")
    return {
        "ready": not blockers,
        **expected_true,
        "telemetry_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_telemetry_score"],
        "telemetry_blocks": telemetry_blocks,
        "blockers": _unique(blockers),
    }


def _post_trade_review_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "post_trade_review")
    expected_true = {
        "post_trade_review_required": _bool_from_contexts(contexts, ("post_trade_review_required",)),
        "pnl_review_required": _bool_from_contexts(contexts, ("pnl_review_required",)),
        "risk_review_required": _bool_from_contexts(contexts, ("risk_review_required",)),
        "execution_quality_review_required": _bool_from_contexts(contexts, ("execution_quality_review_required",)),
        "next_trade_blocked_until_review": _bool_from_contexts(contexts, ("next_trade_blocked_until_review",)),
    }
    post_trade_review_blocks = _blockers_from_contexts(contexts, ("post_trade_review_blocks",))
    explicit_score = _score_from_contexts(contexts, ("post_trade_review_score",))
    derived_score = _bool_score([*expected_true.values(), not post_trade_review_blocks])
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers = _expected_true_blockers(expected_true)
    if post_trade_review_blocks:
        blockers.extend(post_trade_review_blocks)
    if active_score is None:
        blockers.append("post_trade_review_score_missing")
    elif active_score < thresholds["min_post_trade_review_score"]:
        blockers.append("post_trade_review_score_below_threshold")
    return {
        "ready": not blockers,
        **expected_true,
        "post_trade_review_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_post_trade_review_score"],
        "post_trade_review_blocks": post_trade_review_blocks,
        "blockers": _unique(blockers),
    }


def _data_quality_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "data_quality")
    explicit_score = _score_from_contexts(contexts, ("data_quality_score",))
    missing_fields = _blockers_from_contexts(contexts, ("missing_fields",))
    invalid_rows = _number_from_contexts(contexts, ("invalid_rows",))
    duplicate_tickets = _number_from_contexts(contexts, ("duplicate_tickets",))
    malformed_timestamps = _number_from_contexts(contexts, ("malformed_timestamps",))
    derived_score = _bool_score(
        [
            not missing_fields,
            None if invalid_rows is None else invalid_rows == 0,
            None if duplicate_tickets is None else duplicate_tickets == 0,
            None if malformed_timestamps is None else malformed_timestamps == 0,
        ]
    )
    active_score = explicit_score if explicit_score is not None else derived_score
    blockers: list[str] = []
    if missing_fields:
        blockers.append("data_quality_missing_fields_present")
        blockers.extend(f"missing_field_{field}" for field in missing_fields)
    if invalid_rows is not None and invalid_rows > 0:
        blockers.append("invalid_rows_present")
    if duplicate_tickets is not None and duplicate_tickets > 0:
        blockers.append("duplicate_tickets_present")
    if malformed_timestamps is not None and malformed_timestamps > 0:
        blockers.append("malformed_timestamps_present")
    if active_score is None:
        blockers.append("data_quality_score_missing")
    elif active_score < thresholds["min_data_quality_score"]:
        blockers.append("data_quality_score_below_threshold")
    return {
        "ready": not blockers,
        "data_quality_score": active_score,
        "score": active_score,
        "explicit_score": explicit_score,
        "derived_score": derived_score,
        "threshold": thresholds["min_data_quality_score"],
        "missing_fields": missing_fields,
        "invalid_rows": invalid_rows,
        "duplicate_tickets": duplicate_tickets,
        "malformed_timestamps": malformed_timestamps,
        "blockers": _unique(blockers),
    }


def _resolve_handoff_status(
    *,
    missing_core_evidence: bool,
    threshold_blockers: Sequence[str],
    execution_prep_summary: Mapping[str, Any],
    owner_summary: Mapping[str, Any],
    credential_summary: Mapping[str, Any],
    account_summary: Mapping[str, Any],
    order_summary: Mapping[str, Any],
    risk_summary: Mapping[str, Any],
    abort_summary: Mapping[str, Any],
    telemetry_summary: Mapping[str, Any],
    post_trade_summary: Mapping[str, Any],
    data_quality_summary: Mapping[str, Any],
    runtime_handoff_score: float | None,
    min_runtime_handoff_score: float,
) -> str:
    if missing_core_evidence:
        return INCOMPLETE_INPUTS
    if not execution_prep_summary["ready"]:
        return BLOCKED_BY_EXECUTION_PREP
    if not owner_summary["ready"]:
        return BLOCKED_BY_OWNER_APPROVAL
    if not credential_summary["ready"]:
        return BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY
    if not account_summary["ready"]:
        return BLOCKED_BY_OANDA_ACCOUNT_BOUNDARY
    if not order_summary["ready"]:
        return BLOCKED_BY_ORDER_PREVIEW
    if not risk_summary["ready"]:
        return BLOCKED_BY_RISK_GATES
    if not abort_summary["ready"]:
        return BLOCKED_BY_ABORT_CONDITIONS
    if not telemetry_summary["ready"]:
        return BLOCKED_BY_TELEMETRY
    if not post_trade_summary["ready"]:
        return BLOCKED_BY_POST_TRADE_REVIEW
    if not data_quality_summary["ready"]:
        return BLOCKED_BY_DATA_QUALITY
    if threshold_blockers:
        return NEEDS_MORE_EVIDENCE
    if runtime_handoff_score is None or runtime_handoff_score < min_runtime_handoff_score:
        return NEEDS_MORE_EVIDENCE
    return OANDA_DEMO_RUNTIME_HANDOFF_READY


def _input_summary(
    *,
    source: Mapping[str, Any],
    explicit_runtime_handoff_score: float | None,
    derived_runtime_handoff_score: float | None,
    sub_scores: Mapping[str, float | None],
    missing_information: Sequence[str],
) -> dict[str, Any]:
    return {
        "input_fields_seen": sorted(str(key) for key in source.keys()),
        "meaningful_runtime_handoff_evidence_supplied": any(key in source for key in CORE_EVIDENCE_KEYS),
        "explicit_runtime_handoff_score": explicit_runtime_handoff_score,
        "derived_runtime_handoff_score": derived_runtime_handoff_score,
        "sub_scores": dict(sub_scores),
        "missing_information": list(missing_information),
        "input_redacted": False,
    }


def _sanitized_runtime_handoff_package(source: Mapping[str, Any]) -> dict[str, Any]:
    owner_contexts = _contexts(source, "owner_approval")
    account_contexts = _contexts(source, "oanda_account_boundary")
    order_contexts = _contexts(source, "order_preview")
    risk_contexts = _contexts(source, "risk_gates")
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "owner_name": _text_from_contexts(owner_contexts, ("owner_name",)) or "Anthony",
        "broker_name": _text_from_contexts(account_contexts, ("broker_name",)),
        "broker_mode": _text_from_contexts(account_contexts, ("broker_mode",)),
        "account_environment": _text_from_contexts(account_contexts, ("account_environment",)),
        "strategy_id": _text_from_contexts(order_contexts, ("strategy_id",)),
        "candidate_id": _text_from_contexts(order_contexts, ("candidate_id",)),
        "instrument": _text_from_contexts(order_contexts, ("instrument",)),
        "side": _text_from_contexts(order_contexts, ("side",)),
        "order_type": _text_from_contexts(order_contexts, ("order_type",)),
        "units": _number_from_contexts(order_contexts, ("units",)),
        "stop_loss_present": _bool_from_contexts(order_contexts, ("stop_loss_present",)),
        "take_profit_present": _bool_from_contexts(order_contexts, ("take_profit_present",)),
        "max_spread_pips": _number_from_contexts(order_contexts, ("max_spread_pips",)),
        "max_slippage_pips": _number_from_contexts(order_contexts, ("max_slippage_pips",)),
        "risk_limits": {
            "max_position_units": _number_from_contexts(order_contexts, ("max_position_units",)),
            "max_risk_per_trade_pct": _number_from_contexts(risk_contexts, ("max_risk_per_trade_pct",)),
            "max_daily_loss_pct": _number_from_contexts(risk_contexts, ("max_daily_loss_pct",)),
            "risk_reward_minimum": _number_from_contexts(risk_contexts, ("risk_reward_minimum",)),
            "one_order_only": _bool_from_contexts(risk_contexts, ("one_order_only",)),
        },
        "runtime_credentials_required": True,
        "credentials_included": False,
        "owner_named_approval_required": True,
        "owner_can_cancel": True,
        "demo_only": True,
        "execution_authorized": False,
        "order_placement_allowed": False,
    }


def _owner_action_queue(
    *,
    execution_prep_summary: Mapping[str, Any],
    owner_summary: Mapping[str, Any],
    credential_summary: Mapping[str, Any],
    account_summary: Mapping[str, Any],
    order_summary: Mapping[str, Any],
    risk_summary: Mapping[str, Any],
    abort_summary: Mapping[str, Any],
    telemetry_summary: Mapping[str, Any],
    post_trade_summary: Mapping[str, Any],
    handoff_blockers: Sequence[str],
    next_best_packet: str,
) -> list[dict[str, Any]]:
    actions = [
        ("REVIEW_EXECUTION_PREP", "Review execution-prep package", 1, execution_prep_summary["blockers"]),
        ("REVIEW_OWNER_APPROVAL", "Review owner approval evidence", 2, owner_summary["blockers"]),
        (
            "REVIEW_RUNTIME_CREDENTIAL_BOUNDARY",
            "Review runtime credential boundary",
            3,
            credential_summary["blockers"],
        ),
        ("REVIEW_OANDA_ACCOUNT_BOUNDARY", "Review OANDA account boundary", 4, account_summary["blockers"]),
        ("REVIEW_ORDER_PREVIEW", "Review order preview", 5, order_summary["blockers"]),
        ("REVIEW_RISK_GATES", "Review risk gates", 6, risk_summary["blockers"]),
        ("REVIEW_ABORT_CONDITIONS", "Review abort conditions", 7, abort_summary["blockers"]),
        ("REVIEW_TELEMETRY", "Review telemetry requirements", 8, telemetry_summary["blockers"]),
        ("REVIEW_POST_TRADE_REVIEW", "Review post-trade review plan", 9, post_trade_summary["blockers"]),
        (
            "REVIEW_SANITIZED_RUNTIME_HANDOFF_PACKAGE",
            "Review sanitized runtime handoff package",
            10,
            handoff_blockers,
        ),
        ("REVIEW_NEXT_PACKET", f"Review next packet: {next_best_packet}", 11, handoff_blockers),
    ]
    return [
        {
            "action_id": action_id,
            "title": title,
            "priority": priority,
            "owner_decision_required": True,
            "execution_allowed": False,
            "safe_action": f"{title}; keep execution authority outside this evaluator.",
            "blocked_by": list(blocked_by),
        }
        for action_id, title, priority, blocked_by in actions
    ]


def _next_remaining_lane(remaining_work_closure_index: Mapping[str, Any], next_best_packet: str) -> dict[str, Any]:
    lanes = remaining_work_closure_index.get("remaining_lanes")
    if isinstance(lanes, Sequence) and not isinstance(lanes, (str, bytes)):
        for lane in lanes:
            lane_map = _mapping(lane)
            if lane_map.get("safe_packet_name") == next_best_packet:
                return dict(lane_map)
    lane_id = NEXT_LANE_ID if next_best_packet == NEXT_PACKET_IF_READY else CURRENT_LANE_ID
    return {
        "lane_id": lane_id,
        "safe_packet_name": next_best_packet,
        "status": "OWNER_REVIEW_REQUIRED",
    }


def _safe_manual_next_action(handoff_status: str) -> str:
    if handoff_status == OANDA_DEMO_RUNTIME_HANDOFF_READY:
        return (
            "Owner may review the sanitized OANDA demo runtime handoff package and queue supervised "
            "OANDA demo order execution. AIOS does not place orders, access brokers, transfer funds, "
            "or use credentials in this packet."
        )
    if handoff_status == INCOMPLETE_INPUTS:
        return (
            "Provide sanitized execution-prep, owner approval, runtime credential boundary, OANDA account "
            "boundary, order preview, risk gate, abort condition, telemetry, and post-trade review evidence, "
            "then rerun this evaluator."
        )
    return (
        "Collect sanitized OANDA demo runtime-handoff evidence, rerun the read-only handoff evaluator, "
        "and keep broker, credential, order, bank, and fund-transfer actions outside AIOS until owner approval."
    )


def _safety() -> dict[str, Any]:
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


def _missing_information(source: Mapping[str, Any]) -> list[str]:
    return [key for key in CORE_EVIDENCE_KEYS if not isinstance(source.get(key), Mapping)]


def _empty_summary(reason: str, blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "ready": False,
        "reason": reason,
        "score": None,
        "blockers": list(blockers),
    }


def _contexts(source: Mapping[str, Any], section: str) -> list[Mapping[str, Any]]:
    contexts: list[Mapping[str, Any]] = []
    section_value = _mapping(source.get(section))
    if section_value:
        contexts.append(section_value)
    snapshot = _mapping(source.get("readiness_snapshot"))
    if snapshot:
        contexts.append(snapshot)
    contexts.append(source)
    return contexts


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key).lower()
            if key_text not in SAFE_BOUNDARY_KEYS and any(part in key_text for part in SENSITIVE_KEY_PARTS):
                return True
            if _contains_sensitive_key(nested):
                return True
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def _first_present(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> Any:
    for context in contexts:
        for key in keys:
            if key in context:
                return context[key]
    return None


def _text_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> str | None:
    return _text(_first_present(contexts, keys), None)


def _bool_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> bool | None:
    return _bool(_first_present(contexts, keys))


def _number_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> float | None:
    return _number(_first_present(contexts, keys))


def _score_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> float | None:
    return _score(_first_present(contexts, keys))


def _blockers_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> list[str]:
    blockers: list[str] = []
    for context in contexts:
        for key in keys:
            value = context.get(key)
            if isinstance(value, str) and value.strip():
                blockers.append(value.strip())
            elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                blockers.extend(str(item) for item in value if str(item).strip())
    return _unique(blockers)


def _false_authority_value(contexts: Sequence[Mapping[str, Any]], key: str) -> bool | None:
    saw_false = False
    for context in contexts:
        if key not in context:
            continue
        value = _bool(context[key])
        if value is True:
            return True
        if value is False:
            saw_false = True
    return False if saw_false else None


def _expected_false_score_value(value: bool | None) -> bool | None:
    return None if value is None else value is False


def _exact_bool_blockers(
    *,
    expected_true: Mapping[str, bool | None],
    expected_false: Mapping[str, bool | None],
) -> list[str]:
    blockers = _expected_true_blockers(expected_true)
    for key, value in expected_false.items():
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is not False:
            blockers.append(f"{key}_true")
    return blockers


def _expected_true_blockers(expected_true: Mapping[str, bool | None]) -> list[str]:
    blockers: list[str] = []
    for key, value in expected_true.items():
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is not True:
            blockers.append(f"{key}_false")
    return blockers


def _bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "1", "pass"}:
            return True
        if lowered in {"false", "no", "0", "fail"}:
            return False
    return None


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and isfinite(float(value)):
        return float(value)
    if isinstance(value, str):
        try:
            number = float(value.strip())
        except ValueError:
            return None
        return number if isfinite(number) else None
    return None


def _score(value: Any) -> float | None:
    number = _number(value)
    if number is None or number < 0:
        return None
    return number


def _text(value: Any, default: str | None = "") -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _present(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def _bool_score(values: Sequence[bool | None]) -> float | None:
    known = [value for value in values if value is not None]
    if not known:
        return None
    return sum(1 for value in known if value is True) / len(known)


def _average_score(values: Sequence[float | None]) -> float | None:
    known = [value for value in values if value is not None]
    if not known:
        return None
    return sum(known) / len(known)


def _broker_name_ok(broker_name: str | None) -> bool | None:
    return None if not broker_name else broker_name.upper() == "OANDA"


def _broker_mode_ok(broker_mode: str | None) -> bool | None:
    return None if not broker_mode else broker_mode.upper() in ALLOWED_BROKER_MODES


def _account_environment_ok(account_environment: str | None) -> bool | None:
    return None if not account_environment else account_environment.upper() in ALLOWED_ACCOUNT_ENVIRONMENTS


def _unique(values: Sequence[Any]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        item = str(value)
        if item and item not in seen:
            seen.add(item)
            unique.append(item)
    return unique
