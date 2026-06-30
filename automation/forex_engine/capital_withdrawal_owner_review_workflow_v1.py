"""Read-only owner-review workflow packet for capital withdrawal readiness."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_FOREX_CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW_V1"
MODE = "READ_ONLY_CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW"

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
)

READY = "READY_FOR_OWNER_REVIEW"
WATCHLIST = "WATCHLIST_ONLY"
BLOCKED_RISK = "BLOCKED_BY_RISK"
BLOCKED_RAIL = "BLOCKED_BY_RAIL"
BLOCKED_RESERVE = "BLOCKED_BY_RESERVE"
BLOCKED_SENSITIVE = "BLOCKED_BY_SENSITIVE_DATA"
INCOMPLETE = "INCOMPLETE_INPUTS"
NO_WITHDRAWAL = "NO_WITHDRAWAL_RECOMMENDED"

CURRENT_LANE_ID = "CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW"
NEXT_PACKET_AFTER_THIS = "AIOS_FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY_V1"

REQUIRED_CORE_INPUTS = (
    "owner_review_dashboard_surfacing",
    "owner_review_capital_surface",
    "capital_rail_withdrawal_plan",
    "withdrawal_cadence_planner",
    "capital_rail_registry",
    "capital_bucket_purge_controller",
    "remaining_work_closure_index",
)

REQUIRED_CHECKLIST_IDS = (
    "CONFIRM_OWNER_IDENTITY",
    "REVIEW_WITHDRAWAL_CADENCE",
    "REVIEW_PROTECTED_RESERVES",
    "REVIEW_RISK_BLOCKERS",
    "REVIEW_RAIL_PROOF",
    "REVIEW_SELECTED_RAIL",
    "REVIEW_BUCKET_PURGE_STATE",
    "REVIEW_FEE_AND_TIMING",
    "REVIEW_OANDA_HIERARCHY",
    "CONFIRM_MANUAL_EXECUTION_ONLY",
    "CONFIRM_NO_AI_EXECUTION",
)


def evaluate_capital_withdrawal_owner_review_workflow_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Build a deterministic manual owner-review workflow from read-only inputs."""

    source = payload if isinstance(payload, Mapping) else {}
    owner_name = _as_text(source.get("owner_name"), "Anthony")

    if _contains_sensitive_key(source):
        return _sensitive_payload(owner_name)

    dashboard = _mapping(source.get("owner_review_dashboard_surfacing"))
    surface = _mapping(source.get("owner_review_capital_surface"))
    plan = _mapping(source.get("capital_rail_withdrawal_plan"))
    cadence = _mapping(source.get("withdrawal_cadence_planner"))
    rail = _mapping(source.get("capital_rail_registry"))
    bucket = _mapping(source.get("capital_bucket_purge_controller"))
    remaining = _mapping(source.get("remaining_work_closure_index"))

    missing_inputs = _missing_core_inputs(source)
    missing_information = _unique(
        [
            *missing_inputs,
            *_strings(dashboard.get("missing_information")),
            *_strings(surface.get("missing_information")),
            *_strings(plan.get("missing_information")),
            *_strings(cadence.get("missing_information")),
            *_strings(rail.get("missing_information")),
            *_strings(bucket.get("missing_information")),
        ]
    )

    recommended_cadence = _resolve_cadence(dashboard, surface, plan, cadence)
    risk_blockers = _risk_blockers(surface, plan, cadence, bucket)
    reserve_blockers = _reserve_blockers(surface, plan, cadence, bucket)
    rail_blockers = _rail_blockers(surface, plan, rail)
    cadence_blockers = _cadence_blockers(cadence, recommended_cadence)
    bucket_blockers = _bucket_blockers(bucket, plan)
    sensitive_blockers = _sensitive_blockers(dashboard, surface, plan, rail)

    workflow_status = _workflow_status(
        sensitive_blockers=sensitive_blockers,
        missing_information=missing_information,
        risk_blockers=risk_blockers,
        reserve_blockers=reserve_blockers,
        rail_blockers=rail_blockers,
        recommended_cadence=recommended_cadence,
        plan=plan,
    )
    eligible_for_owner_review = workflow_status == READY

    remaining_lanes = _normalize_remaining_lanes(_sequence(remaining.get("remaining_lanes")))
    next_remaining_lane = _next_lane_after_current(remaining_lanes)
    next_best_packet = _resolve_next_best_packet(remaining, next_remaining_lane)

    selected_review_rail = _selected_rail(plan)
    selected_rail_present = bool(selected_review_rail)
    selected_rail_is_redacted = selected_rail_present and not _contains_sensitive_key(selected_review_rail)

    same_name_status = _mapping(rail.get("same_name_proof_status"))
    same_name_required = _bool(
        same_name_status.get("required"),
        default=_bool(rail.get("same_name_proof_required"), default=False),
    )
    same_name_satisfied = _bool(same_name_status.get("satisfied"), default=False)
    rail_proof_required = same_name_required or _bool(plan.get("rail_proof_required"), default=False)
    rail_proof_ok = (not rail_proof_required) or same_name_satisfied

    reserve_status = _reserve_status(surface, plan, cadence, bucket)
    risk_status = _risk_status(surface, cadence, bucket)
    bucket_review = _bucket_purge_review(bucket, plan, bucket_blockers)
    manual_packet = _manual_execution_packet()
    blocker_summary = _blocker_summary(
        risk_blockers=risk_blockers,
        rail_blockers=rail_blockers,
        reserve_blockers=reserve_blockers,
        cadence_blockers=cadence_blockers,
        bucket_blockers=bucket_blockers,
        sensitive_blockers=sensitive_blockers,
        incomplete_blockers=missing_information,
    )

    withdrawal_review_packet = {
        "packet_status": workflow_status,
        "eligible_for_owner_review": eligible_for_owner_review,
        "recommended_cadence": recommended_cadence,
        "selected_review_rail": selected_review_rail,
        "withdrawal_plan_status": _as_text(plan.get("withdrawal_plan_status"), WATCHLIST),
        "protected_reserves_ok": reserve_status["tax_reserve_met"]
        and reserve_status["operating_reserve_met"],
        "rail_proof_ok": rail_proof_ok,
        "risk_gate_ok": not risk_blockers,
        "bucket_purge_ok": not bucket_blockers,
        "manual_execution_only": True,
        "owner_gate_required": True,
        "review_notes": _review_notes(blocker_summary["all_blockers"]),
    }

    owner_approval_checklist = _owner_approval_checklist(
        owner_name=owner_name,
        workflow_status=workflow_status,
        recommended_cadence=recommended_cadence,
        selected_rail_present=selected_rail_present,
        selected_rail_is_redacted=selected_rail_is_redacted,
        rail_proof_ok=rail_proof_ok,
        reserve_ok=withdrawal_review_packet["protected_reserves_ok"],
        risk_ok=withdrawal_review_packet["risk_gate_ok"],
        bucket_ok=withdrawal_review_packet["bucket_purge_ok"],
        cadence_blockers=cadence_blockers,
        manual_execution_only=True,
    )

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "trade_execution_allowed": False,
        "credential_use_allowed": False,
        "scheduler_created": False,
        "daemon_created": False,
        "webhook_created": False,
        "dashboard_runtime_created": False,
        "owner_name": owner_name,
        "owner_decision_required": True,
        "workflow_status": workflow_status,
        "eligible_for_owner_review": eligible_for_owner_review,
        "recommended_cadence": recommended_cadence,
        "withdrawal_review_packet": withdrawal_review_packet,
        "owner_approval_checklist": owner_approval_checklist,
        "withdrawal_cadence_review": _cadence_review(cadence, recommended_cadence, cadence_blockers),
        "rail_proof_checklist": _rail_proof_checklist(
            rail=rail,
            selected_review_rail=selected_review_rail,
            same_name_required=rail_proof_required,
            same_name_satisfied=same_name_satisfied,
            rail_blockers=rail_blockers,
        ),
        "reserve_gate_checklist": _reserve_gate_checklist(plan, reserve_status, reserve_blockers),
        "risk_gate_checklist": _risk_gate_checklist(risk_status, risk_blockers),
        "bucket_purge_review": bucket_review,
        "selected_review_rail_review": {
            "selected_review_rail": selected_review_rail,
            "selected_rail_present": selected_rail_present,
            "selected_rail_is_redacted": selected_rail_is_redacted,
            "selected_rail_execution_allowed": False,
            "owner_review_required": True,
            "blocker": None if selected_rail_present else "selected_review_rail_missing",
        },
        "manual_execution_packet": manual_packet,
        "blocker_summary": blocker_summary,
        "missing_information": missing_information,
        "owner_action_queue": _owner_action_queue(
            risk_blockers=risk_blockers,
            rail_blockers=rail_blockers,
            reserve_blockers=reserve_blockers,
            bucket_blockers=bucket_blockers,
            cadence_blockers=cadence_blockers,
            next_best_packet=next_best_packet,
        ),
        "next_best_packet": next_best_packet,
        "next_remaining_lane": next_remaining_lane,
        "safe_manual_next_action": _safe_manual_next_action(workflow_status),
        "audit_record": {
            "as_of_date": _as_text(source.get("as_of_date"), datetime.now(timezone.utc).isoformat()),
            "schema": SCHEMA,
            "mode": MODE,
            "workflow_status": workflow_status,
            "input_fields_seen": sorted(str(key) for key in source.keys()),
            "next_best_packet": next_best_packet,
            "next_remaining_lane": next_remaining_lane,
            "recommended_cadence": recommended_cadence,
            "eligible_for_owner_review": eligible_for_owner_review,
            "remaining_lane_count": len(remaining_lanes),
        },
        "safety": _safety(),
    }


def _sensitive_payload(owner_name: str) -> dict[str, Any]:
    blocker_summary = _blocker_summary(
        risk_blockers=[],
        rail_blockers=[],
        reserve_blockers=[],
        cadence_blockers=[],
        bucket_blockers=[],
        sensitive_blockers=["sensitive_financial_data_provided"],
        incomplete_blockers=[],
    )
    manual_packet = _manual_execution_packet()
    selected_review_rail = None
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "trade_execution_allowed": False,
        "credential_use_allowed": False,
        "scheduler_created": False,
        "daemon_created": False,
        "webhook_created": False,
        "dashboard_runtime_created": False,
        "owner_name": owner_name,
        "owner_decision_required": True,
        "workflow_status": BLOCKED_SENSITIVE,
        "eligible_for_owner_review": False,
        "recommended_cadence": "no_withdrawal",
        "withdrawal_review_packet": {
            "packet_status": BLOCKED_SENSITIVE,
            "eligible_for_owner_review": False,
            "recommended_cadence": "no_withdrawal",
            "selected_review_rail": selected_review_rail,
            "withdrawal_plan_status": BLOCKED_SENSITIVE,
            "protected_reserves_ok": False,
            "rail_proof_ok": False,
            "risk_gate_ok": False,
            "bucket_purge_ok": False,
            "manual_execution_only": True,
            "owner_gate_required": True,
            "review_notes": ["Remove sensitive financial fields and rerun."],
        },
        "owner_approval_checklist": [
            _checklist_item(checklist_id, "Blocked by sensitive input", "BLOCKED", "sensitive_financial_data_provided")
            for checklist_id in REQUIRED_CHECKLIST_IDS
        ],
        "withdrawal_cadence_review": {
            "recommended_cadence": "no_withdrawal",
            "weekly_eligible": False,
            "monthly_eligible": False,
            "bimonthly_eligible": False,
            "no_withdrawal_reasons": ["sensitive_financial_data_provided"],
            "cadence_blockers": ["sensitive_financial_data_provided"],
            "owner_review_required": True,
        },
        "rail_proof_checklist": {
            "same_name_proof_required": False,
            "same_name_proof_satisfied": False,
            "selected_review_rail": selected_review_rail,
            "eligible_rail_count": 0,
            "blocked_rail_count": 0,
            "lowest_cost_rail": None,
            "fastest_rail": None,
            "preferred_withdrawal_rail": None,
            "rail_blockers": ["sensitive_financial_data_provided"],
            "owner_review_required": True,
            "execution_allowed": False,
        },
        "reserve_gate_checklist": {
            "tax_reserve_met": False,
            "operating_reserve_met": False,
            "protected_buckets": [],
            "reserve_blockers": ["sensitive_financial_data_provided"],
            "owner_review_required": True,
            "execution_allowed": False,
        },
        "risk_gate_checklist": {
            "margin_or_open_risk_block": False,
            "daily_loss_stop_active": False,
            "risk_blockers": ["sensitive_financial_data_provided"],
            "owner_review_required": True,
            "execution_allowed": False,
        },
        "bucket_purge_review": {
            "stale_bucket_flags": [],
            "purge_actions_count": 0,
            "rollover_actions_count": 0,
            "sweep_actions_count": 0,
            "bucket_purge_required": False,
            "bucket_purge_blockers": ["sensitive_financial_data_provided"],
            "owner_review_required": True,
            "execution_allowed": False,
        },
        "selected_review_rail_review": {
            "selected_review_rail": selected_review_rail,
            "selected_rail_present": False,
            "selected_rail_is_redacted": False,
            "selected_rail_execution_allowed": False,
            "owner_review_required": True,
            "blocker": "sensitive_financial_data_provided",
        },
        "manual_execution_packet": manual_packet,
        "blocker_summary": blocker_summary,
        "missing_information": ["remove_sensitive_financial_data"],
        "owner_action_queue": _owner_action_queue(
            risk_blockers=[],
            rail_blockers=["sensitive_financial_data_provided"],
            reserve_blockers=[],
            bucket_blockers=[],
            cadence_blockers=[],
            next_best_packet=NEXT_PACKET_AFTER_THIS,
        ),
        "next_best_packet": NEXT_PACKET_AFTER_THIS,
        "next_remaining_lane": {},
        "safe_manual_next_action": "Remove sensitive data and rerun the read-only workflow.",
        "audit_record": {
            "as_of_date": datetime.now(timezone.utc).isoformat(),
            "schema": SCHEMA,
            "mode": MODE,
            "workflow_status": BLOCKED_SENSITIVE,
            "input_redacted": True,
        },
        "safety": _safety(),
    }


def _workflow_status(
    *,
    sensitive_blockers: Sequence[str],
    missing_information: Sequence[str],
    risk_blockers: Sequence[str],
    reserve_blockers: Sequence[str],
    rail_blockers: Sequence[str],
    recommended_cadence: str,
    plan: Mapping[str, Any],
) -> str:
    if sensitive_blockers:
        return BLOCKED_SENSITIVE
    if missing_information:
        return INCOMPLETE
    if risk_blockers:
        return BLOCKED_RISK
    if reserve_blockers:
        return BLOCKED_RESERVE
    if rail_blockers:
        return BLOCKED_RAIL
    if recommended_cadence == "no_withdrawal":
        return NO_WITHDRAWAL
    if _bool(plan.get("eligible_for_owner_review"), default=False):
        return READY
    return WATCHLIST


def _resolve_cadence(
    dashboard: Mapping[str, Any],
    surface: Mapping[str, Any],
    plan: Mapping[str, Any],
    cadence: Mapping[str, Any],
) -> str:
    dashboard_summary = _mapping(dashboard.get("dashboard_summary"))
    surface_summary = _mapping(surface.get("withdrawal_cadence_summary"))
    candidates = (
        cadence.get("recommended_cadence"),
        surface_summary.get("recommended_cadence"),
        dashboard_summary.get("recommended_cadence"),
        plan.get("recommended_cadence"),
    )
    for candidate in candidates:
        text = _as_text(candidate)
        if text in {"weekly", "monthly", "bimonthly", "no_withdrawal"}:
            return text
    return "no_withdrawal"


def _risk_blockers(
    surface: Mapping[str, Any],
    plan: Mapping[str, Any],
    cadence: Mapping[str, Any],
    bucket: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    surface_bucket = _mapping(surface.get("capital_bucket_summary"))
    withdrawal_status = _mapping(bucket.get("withdrawal_bucket_status"))
    if _bool(surface_bucket.get("margin_or_open_risk_block")) or _bool(withdrawal_status.get("margin_or_open_risk_block")):
        blockers.append("margin_or_open_risk_block")
    if _bool(surface_bucket.get("daily_loss_stop_active")) or _bool(withdrawal_status.get("daily_loss_stop_active")):
        blockers.append("daily_loss_stop_active")
    if _as_text(plan.get("withdrawal_plan_status")) == BLOCKED_RISK:
        blockers.append("withdrawal_plan_blocked_by_risk")
    for item in [
        *_strings(plan.get("blocked_reasons")),
        *_strings(cadence.get("risk_blocks")),
        *_strings(cadence.get("blocked_reasons")),
        *_strings(bucket.get("blocked_reasons")),
        *_strings(surface.get("blockers")),
    ]:
        text = str(item)
        if any(part in text for part in ("risk", "margin", "daily_loss", "drawdown")):
            blockers.append(text)
    return _unique(blockers)


def _reserve_blockers(
    surface: Mapping[str, Any],
    plan: Mapping[str, Any],
    cadence: Mapping[str, Any],
    bucket: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    status = _reserve_status(surface, plan, cadence, bucket)
    if not status["operating_reserve_met"]:
        blockers.append("operating_reserve_underfunded")
    if not status["tax_reserve_met"]:
        blockers.append("tax_reserve_underfunded")
    if _as_text(plan.get("withdrawal_plan_status")) == BLOCKED_RESERVE:
        blockers.append("withdrawal_plan_blocked_by_reserve")
    for item in [*_strings(plan.get("blocked_reasons")), *_strings(bucket.get("blocked_reasons"))]:
        text = str(item)
        if "reserve" in text or "underfund" in text:
            blockers.append(text)
    return _unique(blockers)


def _rail_blockers(
    surface: Mapping[str, Any],
    plan: Mapping[str, Any],
    rail: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    proof_status = _mapping(rail.get("same_name_proof_status"))
    proof_required = _bool(proof_status.get("required"), default=_bool(rail.get("same_name_proof_required"), default=False))
    proof_satisfied = _bool(proof_status.get("satisfied"), default=False)
    eligible_rails = _sequence(rail.get("eligible_rails"))
    if proof_required and not proof_satisfied:
        blockers.append("same_name_proof_required")
    if _bool(rail.get("third_party_payment_blocked"), default=False):
        blockers.append("third_party_payment_blocked")
    if not eligible_rails:
        blockers.append("no_eligible_rails")
    if _as_text(plan.get("withdrawal_plan_status")) == BLOCKED_RAIL:
        blockers.append("withdrawal_plan_blocked_by_rail")
    for item in [
        *_strings(rail.get("blocked_reasons")),
        *_strings(plan.get("blocked_reasons")),
        *_strings(surface.get("blockers")),
    ]:
        text = str(item)
        if any(part in text for part in ("rail", "same_name", "third_party")):
            blockers.append(text)
    return _unique(blockers)


def _cadence_blockers(cadence: Mapping[str, Any], recommended_cadence: str) -> list[str]:
    blockers = [*_strings(cadence.get("blocked_reasons"))]
    no_plan = _mapping(cadence.get("no_withdrawal_plan"))
    blockers.extend(_strings(no_plan.get("blocked_reasons")))
    blockers.extend(_strings(no_plan.get("reasons")))
    if recommended_cadence == "no_withdrawal":
        blockers.append("no_withdrawal_recommended")
    return _unique(blockers)


def _bucket_blockers(bucket: Mapping[str, Any], plan: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    stale_flags = _strings(bucket.get("stale_bucket_flags"))
    if _bool(plan.get("bucket_purge_required"), default=False):
        blockers.append("bucket_purge_required")
    blockers.extend(item for item in stale_flags if "stale" in item)
    return _unique(blockers)


def _sensitive_blockers(
    dashboard: Mapping[str, Any],
    surface: Mapping[str, Any],
    plan: Mapping[str, Any],
    rail: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if _as_text(dashboard.get("dashboard_status")) == BLOCKED_SENSITIVE:
        blockers.append("sensitive_financial_data_provided")
    if _as_text(surface.get("surface_status")) == BLOCKED_SENSITIVE:
        blockers.append("sensitive_financial_data_provided")
    if _as_text(plan.get("withdrawal_plan_status")) == BLOCKED_SENSITIVE:
        blockers.append("sensitive_financial_data_provided")
    if _bool(rail.get("sensitive_data_blocked"), default=False):
        blockers.append("sensitive_financial_data_provided")
    return _unique(blockers)


def _reserve_status(
    surface: Mapping[str, Any],
    plan: Mapping[str, Any],
    cadence: Mapping[str, Any],
    bucket: Mapping[str, Any],
) -> dict[str, bool]:
    bucket_reserve = _mapping(bucket.get("reserve_requirements"))
    cadence_reserve = _mapping(cadence.get("reserve_requirements"))
    plan_reserve = _mapping(plan.get("reserve_summary"))
    surface_reserve = _mapping(_mapping(surface.get("protected_reserve_summary")).get("status"))
    operating = _first_bool(
        bucket_reserve.get("operating_reserve_met"),
        cadence_reserve.get("operating_reserve_met"),
        plan_reserve.get("operating_reserve_met"),
        surface_reserve.get("operating_reserve_met"),
        default=True,
    )
    tax = _first_bool(
        bucket_reserve.get("tax_reserve_met"),
        cadence_reserve.get("tax_reserve_met"),
        plan_reserve.get("tax_reserve_met"),
        surface_reserve.get("tax_reserve_met"),
        default=True,
    )
    return {"operating_reserve_met": operating, "tax_reserve_met": tax}


def _risk_status(
    surface: Mapping[str, Any],
    cadence: Mapping[str, Any],
    bucket: Mapping[str, Any],
) -> dict[str, bool]:
    surface_bucket = _mapping(surface.get("capital_bucket_summary"))
    withdrawal_status = _mapping(bucket.get("withdrawal_bucket_status"))
    eligibility = _mapping(cadence.get("withdrawal_eligibility"))
    return {
        "margin_or_open_risk_block": _bool(surface_bucket.get("margin_or_open_risk_block"))
        or _bool(withdrawal_status.get("margin_or_open_risk_block"))
        or _bool(eligibility.get("margin_or_open_risk_block")),
        "daily_loss_stop_active": _bool(surface_bucket.get("daily_loss_stop_active"))
        or _bool(withdrawal_status.get("daily_loss_stop_active"))
        or _bool(eligibility.get("daily_loss_stop_active")),
    }


def _bucket_purge_review(
    bucket: Mapping[str, Any],
    plan: Mapping[str, Any],
    blockers: Sequence[str],
) -> dict[str, Any]:
    return {
        "stale_bucket_flags": _strings(bucket.get("stale_bucket_flags")),
        "purge_actions_count": len(_sequence(bucket.get("purge_actions"))),
        "rollover_actions_count": len(_sequence(bucket.get("rollover_actions"))),
        "sweep_actions_count": len(_sequence(bucket.get("sweep_actions"))),
        "bucket_purge_required": _bool(plan.get("bucket_purge_required"), default=False),
        "bucket_purge_blockers": _strings(blockers),
        "owner_review_required": True,
        "execution_allowed": False,
    }


def _cadence_review(
    cadence: Mapping[str, Any],
    recommended_cadence: str,
    blockers: Sequence[str],
) -> dict[str, Any]:
    return {
        "recommended_cadence": recommended_cadence,
        "weekly_eligible": _bool(_mapping(cadence.get("weekly_plan")).get("eligible")),
        "monthly_eligible": _bool(_mapping(cadence.get("monthly_plan")).get("eligible")),
        "bimonthly_eligible": _bool(_mapping(cadence.get("bimonthly_plan")).get("eligible")),
        "no_withdrawal_reasons": _strings(_mapping(cadence.get("no_withdrawal_plan")).get("blocked_reasons")),
        "cadence_blockers": _strings(blockers),
        "owner_review_required": True,
    }


def _rail_proof_checklist(
    *,
    rail: Mapping[str, Any],
    selected_review_rail: dict[str, Any] | None,
    same_name_required: bool,
    same_name_satisfied: bool,
    rail_blockers: Sequence[str],
) -> dict[str, Any]:
    return {
        "same_name_proof_required": same_name_required,
        "same_name_proof_satisfied": same_name_satisfied,
        "selected_review_rail": selected_review_rail,
        "eligible_rail_count": len(_sequence(rail.get("eligible_rails"))),
        "blocked_rail_count": len(_sequence(rail.get("blocked_rails"))),
        "lowest_cost_rail": _rail_summary(rail.get("lowest_cost_rail")),
        "fastest_rail": _rail_summary(rail.get("fastest_rail")),
        "preferred_withdrawal_rail": _rail_summary(rail.get("preferred_withdrawal_rail")),
        "rail_blockers": _strings(rail_blockers),
        "owner_review_required": True,
        "execution_allowed": False,
    }


def _reserve_gate_checklist(
    plan: Mapping[str, Any],
    status: Mapping[str, bool],
    reserve_blockers: Sequence[str],
) -> dict[str, Any]:
    return {
        "tax_reserve_met": bool(status.get("tax_reserve_met")),
        "operating_reserve_met": bool(status.get("operating_reserve_met")),
        "protected_buckets": _strings(plan.get("protected_buckets")),
        "reserve_blockers": _strings(reserve_blockers),
        "owner_review_required": True,
        "execution_allowed": False,
    }


def _risk_gate_checklist(status: Mapping[str, bool], risk_blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "margin_or_open_risk_block": bool(status.get("margin_or_open_risk_block")),
        "daily_loss_stop_active": bool(status.get("daily_loss_stop_active")),
        "risk_blockers": _strings(risk_blockers),
        "owner_review_required": True,
        "execution_allowed": False,
    }


def _owner_approval_checklist(
    *,
    owner_name: str,
    workflow_status: str,
    recommended_cadence: str,
    selected_rail_present: bool,
    selected_rail_is_redacted: bool,
    rail_proof_ok: bool,
    reserve_ok: bool,
    risk_ok: bool,
    bucket_ok: bool,
    cadence_blockers: Sequence[str],
    manual_execution_only: bool,
) -> list[dict[str, Any]]:
    return [
        _checklist_item("CONFIRM_OWNER_IDENTITY", "Confirm owner identity", "PASS" if owner_name else "MISSING", None),
        _checklist_item(
            "REVIEW_WITHDRAWAL_CADENCE",
            "Review withdrawal cadence",
            "REVIEW_REQUIRED" if recommended_cadence != "no_withdrawal" else "BLOCKED",
            None if recommended_cadence != "no_withdrawal" else "no_withdrawal_recommended",
        ),
        _checklist_item("REVIEW_PROTECTED_RESERVES", "Review protected reserves", "PASS" if reserve_ok else "BLOCKED", None if reserve_ok else "reserve_blockers_present"),
        _checklist_item("REVIEW_RISK_BLOCKERS", "Review risk blockers", "PASS" if risk_ok else "BLOCKED", None if risk_ok else "risk_blockers_present"),
        _checklist_item("REVIEW_RAIL_PROOF", "Review rail proof", "PASS" if rail_proof_ok else "BLOCKED", None if rail_proof_ok else "rail_proof_blockers_present"),
        _checklist_item("REVIEW_SELECTED_RAIL", "Review selected rail", "PASS" if selected_rail_present and selected_rail_is_redacted else "MISSING", None if selected_rail_present else "selected_review_rail_missing"),
        _checklist_item("REVIEW_BUCKET_PURGE_STATE", "Review bucket purge state", "PASS" if bucket_ok else "REVIEW_REQUIRED", None if bucket_ok else "bucket_review_required"),
        _checklist_item("REVIEW_FEE_AND_TIMING", "Review fee and timing", "PASS" if not cadence_blockers else "REVIEW_REQUIRED", None if not cadence_blockers else "cadence_blockers_present"),
        _checklist_item("REVIEW_OANDA_HIERARCHY", "Review OANDA hierarchy", "REVIEW_REQUIRED", "manual_hierarchy_review_required"),
        _checklist_item("CONFIRM_MANUAL_EXECUTION_ONLY", "Confirm manual execution only", "PASS" if manual_execution_only else "BLOCKED", None),
        _checklist_item("CONFIRM_NO_AI_EXECUTION", "Confirm no AI execution", "PASS" if workflow_status != BLOCKED_SENSITIVE else "BLOCKED", None),
    ]


def _checklist_item(checklist_id: str, title: str, status: str, blocker: str | None) -> dict[str, Any]:
    return {
        "checklist_id": checklist_id,
        "title": title,
        "status": status,
        "required": True,
        "owner_decision_required": True,
        "execution_allowed": False,
        "evidence_source": "read_only_upstream_outputs",
        "blocker": blocker,
    }


def _manual_execution_packet() -> dict[str, Any]:
    return {
        "manual_execution_only": True,
        "ai_execution_allowed": False,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "trade_execution_allowed": False,
        "credential_use_allowed": False,
        "owner_must_execute_outside_aios": True,
        "external_action_requires_owner_confirmation": True,
        "instruction": "Review only. AIOS does not move money, access banks, access brokers, or execute trades.",
    }


def _owner_action_queue(
    *,
    risk_blockers: Sequence[str],
    rail_blockers: Sequence[str],
    reserve_blockers: Sequence[str],
    bucket_blockers: Sequence[str],
    cadence_blockers: Sequence[str],
    next_best_packet: str,
) -> list[dict[str, Any]]:
    return [
        _action("REVIEW_WITHDRAWAL_PACKET", "Review withdrawal packet", "high", _combined_blockers(risk_blockers, rail_blockers, reserve_blockers)),
        _action("REVIEW_CADENCE_CHOICE", "Review cadence choice", "high", cadence_blockers),
        _action("REVIEW_RAIL_PROOF", "Review rail proof", "high", rail_blockers),
        _action("REVIEW_RESERVE_GATE", "Review reserve gate", "high", reserve_blockers),
        _action("REVIEW_RISK_GATE", "Review risk gate", "high", risk_blockers),
        _action("REVIEW_BUCKET_PURGE_STATE", "Review bucket purge state", "medium", bucket_blockers),
        _action("REVIEW_NEXT_REMAINING_WORK_PACKET", f"Review next packet: {next_best_packet}", "medium", ["owner_decision_required"]),
    ]


def _action(action_id: str, title: str, priority: str, blocked_by: Sequence[str]) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "title": title,
        "priority": priority,
        "owner_decision_required": True,
        "execution_allowed": False,
        "safe_action": "Review the evidence manually. AIOS does not move money or access external accounts.",
        "blocked_by": _strings(blocked_by),
    }


def _blocker_summary(
    *,
    risk_blockers: Sequence[str],
    rail_blockers: Sequence[str],
    reserve_blockers: Sequence[str],
    cadence_blockers: Sequence[str],
    bucket_blockers: Sequence[str],
    sensitive_blockers: Sequence[str],
    incomplete_blockers: Sequence[str],
) -> dict[str, list[str]]:
    all_blockers = _unique(
        [
            *risk_blockers,
            *rail_blockers,
            *reserve_blockers,
            *cadence_blockers,
            *bucket_blockers,
            *sensitive_blockers,
            *incomplete_blockers,
        ]
    )
    return {
        "risk_blockers": _strings(risk_blockers),
        "rail_blockers": _strings(rail_blockers),
        "reserve_blockers": _strings(reserve_blockers),
        "cadence_blockers": _strings(cadence_blockers),
        "bucket_blockers": _strings(bucket_blockers),
        "sensitive_data_blockers": _strings(sensitive_blockers),
        "incomplete_input_blockers": _strings(incomplete_blockers),
        "all_blockers": all_blockers,
    }


def _safe_manual_next_action(workflow_status: str) -> str:
    if workflow_status == READY:
        return "Owner may review the withdrawal workflow packet manually. AIOS does not move money, access banks, access brokers, execute trades, or use credentials."
    if workflow_status == NO_WITHDRAWAL:
        return "No withdrawal is recommended for owner review. Continue monitoring, preserve reserves, and rerun after new read-only evidence."
    if workflow_status == INCOMPLETE:
        return "Provide sanitized upstream read-only outputs, then rerun the capital withdrawal owner-review workflow."
    if workflow_status == BLOCKED_SENSITIVE:
        return "Remove sensitive data and rerun the read-only workflow."
    return "Resolve listed blockers, rerun the read-only workflow, and keep all money, broker, bank, and trading actions outside AIOS until owner approval."


def _safety() -> dict[str, bool]:
    return {
        "read_only": True,
        "manual_execution_only": True,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "trade_execution_allowed": False,
        "credential_use_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
        "dashboard_runtime_allowed": False,
        "owner_gate_required": True,
    }


def _missing_core_inputs(source: Mapping[str, Any]) -> list[str]:
    return [
        key
        for key in REQUIRED_CORE_INPUTS
        if not isinstance(source.get(key), Mapping)
    ]


def _normalize_remaining_lanes(items: Sequence[Any]) -> list[dict[str, Any]]:
    normalized = []
    for item in items:
        if not isinstance(item, Mapping):
            continue
        lane_id = _as_text(item.get("lane_id"))
        if lane_id:
            normalized.append(
                {
                    "lane_id": lane_id,
                    "title": _as_text(item.get("title"), lane_id),
                    "status": _as_text(item.get("status")),
                    "priority": _as_text(item.get("priority")),
                    "safe_packet_name": _as_text(item.get("safe_packet_name")),
                }
            )
    return normalized


def _next_lane_after_current(lanes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    for index, lane in enumerate(lanes):
        if _as_text(lane.get("lane_id")) == CURRENT_LANE_ID and index + 1 < len(lanes):
            return dict(lanes[index + 1])
    return {}


def _resolve_next_best_packet(remaining: Mapping[str, Any], next_remaining_lane: Mapping[str, Any]) -> str:
    current = _as_text(remaining.get("next_best_packet"), SCHEMA)
    if current == SCHEMA:
        return _as_text(next_remaining_lane.get("safe_packet_name"), NEXT_PACKET_AFTER_THIS)
    return current or NEXT_PACKET_AFTER_THIS


def _selected_rail(plan: Mapping[str, Any]) -> dict[str, Any] | None:
    rail = _mapping(plan.get("selected_review_rail"))
    if not rail:
        return None
    output = {"rail_id": _as_text(rail.get("rail_id"))}
    for key in ("rail_type", "nickname", "institution_name_redacted", "last4_only"):
        if rail.get(key) not in (None, ""):
            output[key] = _as_text(rail.get(key))
    return output if output["rail_id"] else None


def _rail_summary(value: Any) -> dict[str, Any] | None:
    rail = _mapping(value)
    if not rail:
        return None
    rail_id = _as_text(rail.get("rail_id"))
    return {"rail_id": rail_id} if rail_id else None


def _review_notes(blockers: Sequence[str]) -> list[str]:
    if blockers:
        return [f"Blocked by {blocker}" for blocker in blockers]
    return ["Ready for manual owner review only. No real-world transfer instruction is authorized."]


def _combined_blockers(*groups: Sequence[str]) -> list[str]:
    combined: list[str] = []
    for group in groups:
        combined.extend(_strings(group))
    return _unique(combined) or ["owner_review_required"]


def _contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for raw_key, nested in value.items():
            key = str(raw_key).strip().lower()
            if any(part in key for part in SENSITIVE_KEY_PARTS):
                return True
            if _contains_sensitive_key(nested):
                return True
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (str, bytes, bytearray)):
        return [value]
    if isinstance(value, Sequence):
        return list(value)
    return [value]


def _strings(value: Any) -> list[str]:
    return [str(item).strip() for item in _sequence(value) if str(item).strip()]


def _as_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _bool(value: Any, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None or value == "":
        return default
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _first_bool(*values: Any, default: bool) -> bool:
    for value in values:
        if value is not None:
            return _bool(value, default=default)
    return default


def _unique(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values if str(value).strip()))


__all__ = [
    "MODE",
    "SCHEMA",
    "evaluate_capital_withdrawal_owner_review_workflow_v1",
]
