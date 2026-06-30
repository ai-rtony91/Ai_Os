"""Read-only owner-review surface for capital-state, rail, cadence, plan, and watchtower outputs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any

SCHEMA = "AIOS_FOREX_OWNER_REVIEW_CAPITAL_SURFACE_V1"
MODE = "READ_ONLY_OWNER_REVIEW_SURFACE"

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

REQUIRED_CARD_IDS = (
    "CAPITAL_BUCKETS",
    "RAILS",
    "WITHDRAWAL_CADENCE",
    "WITHDRAWAL_PLAN",
    "OANDA_FUNDING",
    "BIG_WINNER_WATCHTOWER",
    "REMAINING_WORK",
)


def evaluate_owner_review_capital_surface_v1(payload: dict | None = None) -> dict[str, Any]:
    source = payload if isinstance(payload, Mapping) else {}

    if _contains_sensitive_key(source):
        return _sensitive_block_payload(_as_text(source.get("owner_name"), "Anthony"))

    owner_name = _as_text(source.get("owner_name"), "Anthony")
    bucket_purge_controller = _as_mapping(source.get("bucket_purge_controller"))
    capital_rail_registry = _as_mapping(source.get("capital_rail_registry"))
    withdrawal_cadence_planner = _as_mapping(source.get("withdrawal_cadence_planner"))
    capital_rail_withdrawal_plan = _as_mapping(source.get("capital_rail_withdrawal_plan"))
    oanda_funding_rail_readiness = _as_mapping(source.get("oanda_funding_rail_readiness"))
    big_winner_watchtower = _as_mapping(source.get("big_winner_watchtower"))

    bucket_summary = _build_bucket_summary(bucket_purge_controller)
    rail_summary = _build_rail_summary(capital_rail_registry)
    cadence_summary = _build_cadence_summary(withdrawal_cadence_planner)
    plan_summary = _build_plan_summary(capital_rail_withdrawal_plan)
    oanda_summary = _build_oanda_summary(oanda_funding_rail_readiness)
    big_winner_summary = _build_big_winner_summary(big_winner_watchtower)

    missing_information: list[str] = _collect_missing_information(
        bucket_purge_present="bucket_purge_controller" in source,
        rail_registry_present="capital_rail_registry" in source,
        cadence_present="withdrawal_cadence_planner" in source,
        plan_present="capital_rail_withdrawal_plan" in source,
    )

    blockers: list[str] = []
    blockers.extend(bucket_summary["blockers"])
    blockers.extend(rail_summary["blockers"])
    blockers.extend(cadence_summary["blockers"])
    blockers.extend(plan_summary["blockers"])
    blockers.extend(oanda_summary["blockers"])
    blockers.extend(big_winner_summary["blockers"])
    blockers.extend(missing_information)

    surface_status = _resolve_surface_status(
        missing_information=missing_information,
        bucket_summary=bucket_summary,
        rail_summary=rail_summary,
        cadence_summary=cadence_summary,
        plan_summary=plan_summary,
        oanda_summary=oanda_summary,
    )

    owner_review_cards = [
        _build_card(
            card_id="CAPITAL_BUCKETS",
            title="Capital Buckets",
            status=_bucket_card_status(surface_status, bucket_summary),
            priority="high",
            summary={
                "bucket_state": bucket_summary["bucket_state"],
                "stale_bucket_flags": bucket_summary["stale_bucket_flags"],
                "purge_actions_count": bucket_summary["purge_actions_count"],
                "rollover_actions_count": bucket_summary["rollover_actions_count"],
                "sweep_actions_count": bucket_summary["sweep_actions_count"],
                "withdrawal_bucket_status": bucket_summary["withdrawal_bucket_status"],
                "margin_or_open_risk_block": bucket_summary["margin_or_open_risk_block"],
                "daily_loss_stop_active": bucket_summary["daily_loss_stop_active"],
                "protected_reserve_status": bucket_summary["protected_reserve_status"],
            },
            blockers=bucket_summary["blockers"],
            safe_next_action="Resolve stale bucket and reserve blockers before requesting a withdrawal review.",
        ),
        _build_card(
            card_id="RAILS",
            title="Rail Readiness",
            status=_rail_card_status(surface_status, rail_summary),
            priority="high",
            summary={
                "eligible_rail_count": rail_summary["eligible_rail_count"],
                "blocked_rail_count": rail_summary["blocked_rail_count"],
                "lowest_cost_rail_id": rail_summary["lowest_cost_rail_id"],
                "fastest_rail_id": rail_summary["fastest_rail_id"],
                "preferred_withdrawal_rail_id": rail_summary["preferred_withdrawal_rail_id"],
                "same_name_proof_status": rail_summary["same_name_proof_status"],
                "sensitive_data_blocked": rail_summary["sensitive_data_blocked"],
                "third_party_payment_blocked": rail_summary["third_party_payment_blocked"],
            },
            blockers=rail_summary["blockers"],
            safe_next_action="Use only same-name verified and unblocked rails. AIOS remains review-only.",
        ),
        _build_card(
            card_id="WITHDRAWAL_CADENCE",
            title="Withdrawal Cadence",
            status=_cadence_card_status(surface_status, cadence_summary),
            priority="medium",
            summary={
                "recommended_cadence": cadence_summary["recommended_cadence"],
                "weekly_eligible": cadence_summary["weekly_eligible"],
                "monthly_eligible": cadence_summary["monthly_eligible"],
                "bimonthly_eligible": cadence_summary["bimonthly_eligible"],
                "no_withdrawal_reasons": cadence_summary["no_withdrawal_reasons"],
                "risk_blocks": cadence_summary["risk_blocks"],
                "fee_efficiency": cadence_summary["fee_efficiency"],
            },
            blockers=cadence_summary["blockers"],
            safe_next_action="Resolve cadence blockers and rerun the surface read-only packet.",
        ),
        _build_card(
            card_id="WITHDRAWAL_PLAN",
            title="Withdrawal Plan",
            status=_plan_status_to_card_status(plan_summary["withdrawal_plan_status"]),
            priority="high",
            summary={
                "withdrawal_plan_status": plan_summary["withdrawal_plan_status"],
                "eligible_for_owner_review": plan_summary["eligible_for_owner_review"],
                "selected_review_rail": plan_summary["selected_review_rail"],
                "owner_gate": plan_summary["owner_gate"],
                "manual_execution_only": plan_summary["manual_execution_only"],
            },
            blockers=plan_summary["blockers"],
            safe_next_action=plan_summary["safe_next_action"],
        ),
        _build_card(
            card_id="OANDA_FUNDING",
            title="OANDA Funding Readiness",
            status=_oanda_card_status(surface_status, oanda_summary),
            priority="medium",
            summary={
                "readiness_status": oanda_summary["readiness_status"],
                "same_name_bank_required": oanda_summary["same_name_bank_required"],
                "withdrawal_hierarchy_notes": oanda_summary["withdrawal_hierarchy_notes"],
                "blockers": oanda_summary["blockers"],
            },
            blockers=oanda_summary["blockers"],
            safe_next_action=oanda_summary["safe_next_action"],
        ),
        _build_card(
            card_id="BIG_WINNER_WATCHTOWER",
            title="Big-Winner Watchtower",
            status=_big_winner_card_status(big_winner_summary["alert_level"]),
            priority="low",
            summary={
                "alert_level": big_winner_summary["alert_level"],
                "top_opportunity": big_winner_summary["top_opportunity"],
                "big_winner_candidate_count": big_winner_summary["big_winner_candidate_count"],
            },
            blockers=big_winner_summary["blockers"],
            safe_next_action=big_winner_summary["safe_next_action"],
        ),
        _build_card(
            card_id="REMAINING_WORK",
            title="Remaining Work",
            status=_normalize_status(surface_status),
            priority="low",
            summary={
                "next_best_action": "Use remaining-work closure packet to continue deterministic lane closure.",
            },
            blockers=[],
            safe_next_action=(
                "Use remaining-work closure index packet to continue lane-based owner review sequencing."
            ),
        ),
    ]

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "trade_execution_allowed": False,
        "owner_name": owner_name,
        "owner_decision_required": True,
        "surface_status": surface_status,
        "capital_bucket_summary": bucket_summary,
        "purge_rollover_sweep_summary": {
            "purge_actions_count": bucket_summary["purge_actions_count"],
            "rollover_actions_count": bucket_summary["rollover_actions_count"],
            "sweep_actions_count": bucket_summary["sweep_actions_count"],
            "withdrawal_bucket_status": bucket_summary["withdrawal_bucket_status"],
            "stale_bucket_flags": bucket_summary["stale_bucket_flags"],
        },
        "rail_readiness_summary": rail_summary,
        "withdrawal_cadence_summary": cadence_summary,
        "withdrawal_plan_summary": plan_summary,
        "oanda_funding_summary": oanda_summary,
        "big_winner_summary": big_winner_summary,
        "protected_reserve_summary": {
            "status": bucket_summary["protected_reserve_status"],
            "margin_or_open_risk_block": bucket_summary["margin_or_open_risk_block"],
            "daily_loss_stop_active": bucket_summary["daily_loss_stop_active"],
        },
        "blockers": _unique(blockers),
        "missing_information": _unique(missing_information),
        "owner_review_cards": owner_review_cards,
        "safe_manual_next_action": _safe_manual_next_action(surface_status),
        "audit_record": {
            "as_of": _as_text(source.get("as_of_date")),
            "schema": SCHEMA,
            "mode": MODE,
            "input_fields_seen": sorted(set(str(key) for key in source.keys())),
        },
        "safety": {
            "read_only": True,
            "money_movement_allowed": False,
            "bank_access_allowed": False,
            "broker_api_allowed": False,
            "trade_execution_allowed": False,
            "credential_use_allowed": False,
            "scheduler_allowed": False,
            "daemon_allowed": False,
            "webhook_allowed": False,
            "owner_gate_required": True,
            "manual_execution_only": True,
        },
    }


def _build_bucket_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    reserve_requirements = _as_mapping(payload.get("reserve_requirements"))
    operating_reserve_status = payload.get("operating_reserve_met")
    if operating_reserve_status is None:
        operating_reserve_status = payload.get("operating_reserve_status", None)
    tax_reserve_status = payload.get("tax_reserve_met")
    if tax_reserve_status is None:
        tax_reserve_status = payload.get("tax_reserve_status", None)
    protected_reserve_status = {
        "operating_reserve_met": _as_bool(
            reserve_requirements.get("operating_reserve_met"),
            default=_as_bool(operating_reserve_status, default=True),
        ),
        "tax_reserve_met": _as_bool(
            reserve_requirements.get("tax_reserve_met"),
            default=_as_bool(tax_reserve_status, default=True),
        ),
        "operating_reserve_current": reserve_requirements.get(
            "operating_reserve_current",
            reserve_requirements.get("operating_reserve_bucket", payload.get("operating_reserve_current", None)),
        ),
        "tax_reserve_current": reserve_requirements.get(
            "tax_reserve_current",
            reserve_requirements.get("tax_reserve_bucket", payload.get("tax_reserve_current", None)),
        ),
        "operating_reserve_minimum": reserve_requirements.get("operating_reserve_minimum"),
        "tax_reserve_minimum": reserve_requirements.get("tax_reserve_minimum"),
    }
    protected_reserve_blocked = (
        protected_reserve_status["operating_reserve_met"] is False
        or protected_reserve_status["tax_reserve_met"] is False
    )
    margin_or_open_risk_block = _as_bool(payload.get("margin_or_open_risk_block"))
    daily_loss_stop_active = _as_bool(payload.get("daily_loss_stop_active"))
    blockers: list[str] = []
    if margin_or_open_risk_block:
        blockers.append("margin_or_open_risk_block")
    if daily_loss_stop_active:
        blockers.append("daily_loss_stop_active")
    if protected_reserve_blocked:
        blockers.append("protected_reserve_status_blocked")

    return {
        "bucket_state": _as_mapping(payload.get("bucket_state")),
        "stale_bucket_flags": [str(item) for item in _as_sequence(payload.get("stale_bucket_flags"))],
        "purge_actions_count": _as_count(payload.get("purge_actions")),
        "rollover_actions_count": _as_count(payload.get("rollover_actions")),
        "sweep_actions_count": _as_count(payload.get("sweep_actions")),
        "withdrawal_bucket_status": _as_mapping(payload.get("withdrawal_bucket_status")),
        "protected_reserve_status": protected_reserve_status,
        "margin_or_open_risk_block": margin_or_open_risk_block,
        "daily_loss_stop_active": daily_loss_stop_active,
        "protected_reserve_blocked": protected_reserve_blocked,
        "blockers": blockers,
    }


def _build_rail_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    same_name_proof_status = _as_mapping(payload.get("same_name_proof_status"))
    if not same_name_proof_status:
        same_name_proof_status = {
            "required": _as_bool(payload.get("same_name_proof_required")),
            "satisfied": _as_bool(same_name_proof_status.get("satisfied")),
        }
    same_name_required = _as_bool(same_name_proof_status.get("required"))
    same_name_satisfied = _as_bool(same_name_proof_status.get("satisfied"))
    sensitive_data_blocked = _as_bool(payload.get("sensitive_data_blocked"))
    third_party_payment_blocked = _as_bool(payload.get("third_party_payment_blocked"))
    eligible_rails = _as_sequence(payload.get("eligible_rails"))
    blocked_rails = _as_sequence(payload.get("blocked_rails"))
    lowest_cost = _as_mapping(payload.get("lowest_cost_rail"))
    fastest = _as_mapping(payload.get("fastest_rail"))
    preferred = _as_mapping(payload.get("preferred_withdrawal_rail"))

    blockers: list[str] = []
    if sensitive_data_blocked:
        blockers.append("sensitive_financial_data_provided")
    if third_party_payment_blocked:
        blockers.append("third_party_payment_blocked")
    if same_name_required and not same_name_satisfied:
        blockers.append("same_name_proof_required")
    if not eligible_rails and (blocked_rails or third_party_payment_blocked or sensitive_data_blocked):
        blockers.append("no_eligible_rails")

    return {
        "eligible_rail_count": len(eligible_rails),
        "blocked_rail_count": len(blocked_rails),
        "lowest_cost_rail_id": _extract_id(lowest_cost),
        "fastest_rail_id": _extract_id(fastest),
        "preferred_withdrawal_rail_id": _extract_id(preferred),
        "same_name_proof_status": {
            "required": same_name_required,
            "satisfied": same_name_satisfied,
        },
        "sensitive_data_blocked": sensitive_data_blocked,
        "third_party_payment_blocked": third_party_payment_blocked,
        "blockers": blockers,
    }


def _build_cadence_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    weekly_plan = _as_mapping(payload.get("weekly_plan"))
    monthly_plan = _as_mapping(payload.get("monthly_plan"))
    bimonthly_plan = _as_mapping(payload.get("bimonthly_plan"))
    no_withdrawal_plan = _as_mapping(payload.get("no_withdrawal_plan"))
    recommended_cadence = _as_text(payload.get("recommended_cadence"), "no_withdrawal")
    no_withdrawal_reasons = [
        str(item) for item in _as_sequence(no_withdrawal_plan.get("reasons"))
    ]
    risk_blocks = [str(item) for item in _as_sequence(payload.get("risk_blocks"))]
    fee_efficiency = _as_mapping(payload.get("fee_efficiency"))
    blockers: list[str] = []
    blockers.extend(risk_blocks)
    if recommended_cadence == "no_withdrawal":
        blockers.append("no_withdrawal_recommended")
    blockers.extend(no_withdrawal_reasons)

    return {
        "recommended_cadence": recommended_cadence,
        "weekly_eligible": _as_bool(weekly_plan.get("eligible")),
        "monthly_eligible": _as_bool(monthly_plan.get("eligible")),
        "bimonthly_eligible": _as_bool(bimonthly_plan.get("eligible")),
        "no_withdrawal_reasons": no_withdrawal_reasons,
        "risk_blocks": risk_blocks,
        "fee_efficiency": fee_efficiency,
        "blockers": blockers,
    }


def _build_plan_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    owner_gate = _as_mapping(payload.get("owner_gate"))
    selected_review_rail = payload.get("selected_review_rail")
    if isinstance(selected_review_rail, Mapping):
        selected_review_rail = {"rail_id": _as_text(selected_review_rail.get("rail_id"))}
    else:
        selected_review_rail = None

    status = _as_text(payload.get("withdrawal_plan_status"), "BLOCKED_BY_RISK")
    if status not in {
        "READY_FOR_OWNER_REVIEW",
        "BLOCKED_BY_RISK",
        "BLOCKED_BY_RAIL",
        "BLOCKED_BY_RESERVE",
        "BLOCKED_BY_SENSITIVE_DATA",
    }:
        status = "BLOCKED_BY_RISK"

    blocked_reasons = [str(item) for item in _as_sequence(payload.get("blocked_reasons"))]
    if status == "BLOCKED_BY_RISK":
        blocked_reasons.append("withdrawal_plan_blocked_by_risk")
    if status == "BLOCKED_BY_RAIL":
        blocked_reasons.append("withdrawal_plan_blocked_by_rail")
    if status == "BLOCKED_BY_RESERVE":
        blocked_reasons.append("withdrawal_plan_blocked_by_reserve")

    return {
        "withdrawal_plan_status": status,
        "eligible_for_owner_review": _as_bool(payload.get("eligible_for_owner_review")),
        "selected_review_rail": selected_review_rail,
        "owner_gate": {
            "owner_name": _as_text(owner_gate.get("owner_name"), "Anthony"),
            "approval_required": _as_bool(owner_gate.get("approval_required"), default=True),
            "execution_allowed": False,
            "approval_scope": _as_text(owner_gate.get("approval_scope"), "manual_review_only"),
        },
        "manual_execution_only": _as_bool(payload.get("manual_execution_only"), default=True),
        "safe_next_action": _as_text(
            payload.get(
                "safe_next_action",
                "Owner may review manually. AIOS does not move money, access banks, access brokers, or execute trades.",
            ),
        ),
        "blockers": _unique(blocked_reasons),
    }


def _build_oanda_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    readiness_status = _as_text(payload.get("readiness_status"), "UNKNOWN")
    same_name_bank_required = _as_bool(payload.get("same_name_bank_required"), default=False)
    withdrawal_hierarchy_notes = [
        str(item) for item in _as_sequence(payload.get("withdrawal_hierarchy_notes"))
    ]
    blockers = [str(item) for item in _as_sequence(payload.get("blockers"))]

    return {
        "readiness_status": readiness_status,
        "same_name_bank_required": same_name_bank_required,
        "withdrawal_hierarchy_notes": withdrawal_hierarchy_notes,
        "blockers": blockers,
        "safe_next_action": _as_text(
            payload.get(
                "safe_next_action",
                "Keep OANDA funding proof and same-name controls in a read-only review posture.",
            ),
        ),
    }


def _build_big_winner_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    top_candidate = payload.get("top_opportunity")
    if not isinstance(top_candidate, Mapping):
        candidates = _as_sequence(payload.get("candidates"))
        top_candidate = candidates[0] if candidates and isinstance(candidates[0], Mapping) else None
    top_opportunity = None
    if isinstance(top_candidate, Mapping):
        pair = _as_text(top_candidate.get("pair"), "")
        direction = _as_text(top_candidate.get("direction"), "")
        if pair or direction:
            top_opportunity = _normalize_opportunity_pair(pair, direction)
    count = payload.get("big_winner_candidate_count")
    if isinstance(count, (int, str, float)):
        try:
            big_winner_candidate_count = int(count)
        except (TypeError, ValueError):
            big_winner_candidate_count = 0
    else:
        big_winner_candidate_count = 0

    alert_level = _as_text(payload.get("alert_level"), "WATCHLIST_ONLY").upper()
    if alert_level not in {"BIG_WINNER_REVIEW", "WATCHLIST_ONLY", "NO_VALID_CANDIDATES"}:
        alert_level = "WATCHLIST_ONLY"
    safe_next_action = _as_text(
        payload.get("safe_next_action"),
        "No qualified big-winner candidates. Continue read-only monitoring for owner review.",
    )

    return {
        "alert_level": alert_level,
        "top_opportunity": top_opportunity,
        "big_winner_candidate_count": max(0, big_winner_candidate_count),
        "safe_next_action": safe_next_action,
        "blockers": [str(item) for item in _as_sequence(payload.get("blockers"))],
    }


def _collect_missing_information(
    *,
    bucket_purge_present: bool,
    rail_registry_present: bool,
    cadence_present: bool,
    plan_present: bool,
) -> list[str]:
    missing: list[str] = []
    if not bucket_purge_present:
        missing.append("bucket_purge_controller")
    if not rail_registry_present:
        missing.append("capital_rail_registry")
    if not cadence_present:
        missing.append("withdrawal_cadence_planner")
    if not plan_present:
        missing.append("capital_rail_withdrawal_plan")
    return missing


def _resolve_surface_status(
    *,
    missing_information: Sequence[str],
    bucket_summary: Mapping[str, Any],
    rail_summary: Mapping[str, Any],
    cadence_summary: Mapping[str, Any],
    plan_summary: Mapping[str, Any],
    oanda_summary: Mapping[str, Any],
) -> str:
    if missing_information:
        return "INCOMPLETE_INPUTS"
    if plan_summary["withdrawal_plan_status"] == "BLOCKED_BY_SENSITIVE_DATA":
        return "BLOCKED_BY_SENSITIVE_DATA"
    if "sensitive_financial_data_provided" in plan_summary["blockers"]:
        return "BLOCKED_BY_SENSITIVE_DATA"
    if "sensitive_financial_data_provided" in oanda_summary["blockers"]:
        return "BLOCKED_BY_SENSITIVE_DATA"
    if bucket_summary["protected_reserve_blocked"]:
        return "BLOCKED_BY_RESERVE"
    if plan_summary["withdrawal_plan_status"] == "BLOCKED_BY_RESERVE":
        return "BLOCKED_BY_RESERVE"
    if bucket_summary["margin_or_open_risk_block"] or bucket_summary["daily_loss_stop_active"]:
        return "BLOCKED_BY_RISK"
    if any(item in {"margin_or_open_risk_block", "risk"} for item in plan_summary["blockers"]):
        return "BLOCKED_BY_RISK"
    if "sensitive_financial_data_provided" in rail_summary["blockers"]:
        return "BLOCKED_BY_SENSITIVE_DATA"
    if "third_party_payment_blocked" in rail_summary["blockers"]:
        return "BLOCKED_BY_RAIL"
    if plan_summary["withdrawal_plan_status"] == "BLOCKED_BY_RAIL":
        return "BLOCKED_BY_RAIL"
    if rail_summary["eligible_rail_count"] == 0:
        return "BLOCKED_BY_RAIL"
    if plan_summary["withdrawal_plan_status"] == "BLOCKED_BY_RISK":
        return "BLOCKED_BY_RISK"
    if cadence_summary["recommended_cadence"] == "no_withdrawal":
        return "WATCHLIST_ONLY"
    return "READY_FOR_OWNER_REVIEW"


def _build_card(
    *,
    card_id: str,
    title: str,
    status: str,
    priority: str,
    summary: Mapping[str, Any],
    blockers: Sequence[str],
    safe_next_action: str,
) -> dict[str, Any]:
    return {
        "card_id": card_id,
        "title": title,
        "status": _normalize_status(status),
        "priority": priority,
        "owner_decision_required": True,
        "execution_allowed": False,
        "summary": dict(summary),
        "blockers": [str(item) for item in blockers if str(item).strip()],
        "safe_next_action": safe_next_action,
    }


def _bucket_card_status(surface_status: str, bucket_summary: Mapping[str, Any]) -> str:
    if surface_status in {"INCOMPLETE_INPUTS", "BLOCKED_BY_SENSITIVE_DATA"}:
        return surface_status
    if bucket_summary.get("protected_reserve_blocked"):
        return "BLOCKED_BY_RESERVE"
    if bucket_summary.get("margin_or_open_risk_block") or bucket_summary.get("daily_loss_stop_active"):
        return "BLOCKED_BY_RISK"
    return "READY_FOR_OWNER_REVIEW"


def _rail_card_status(surface_status: str, rail_summary: Mapping[str, Any]) -> str:
    if surface_status in {"INCOMPLETE_INPUTS", "BLOCKED_BY_SENSITIVE_DATA"}:
        return surface_status
    if "sensitive_financial_data_provided" in rail_summary["blockers"]:
        return "BLOCKED_BY_SENSITIVE_DATA"
    if "third_party_payment_blocked" in rail_summary["blockers"]:
        return "BLOCKED_BY_RAIL"
    if rail_summary["eligible_rail_count"] == 0:
        return "BLOCKED_BY_RAIL"
    return "READY_FOR_OWNER_REVIEW"


def _cadence_card_status(surface_status: str, cadence_summary: Mapping[str, Any]) -> str:
    if surface_status in {"INCOMPLETE_INPUTS", "BLOCKED_BY_SENSITIVE_DATA"}:
        return surface_status
    if cadence_summary["recommended_cadence"] == "no_withdrawal":
        return "WATCHLIST_ONLY"
    return "READY_FOR_OWNER_REVIEW"


def _plan_status_to_card_status(plan_status: str) -> str:
    if plan_status in {
        "READY_FOR_OWNER_REVIEW",
        "BLOCKED_BY_RISK",
        "BLOCKED_BY_RAIL",
        "BLOCKED_BY_RESERVE",
        "BLOCKED_BY_SENSITIVE_DATA",
    }:
        return plan_status
    return "BLOCKED_BY_RISK"


def _oanda_card_status(surface_status: str, oanda_summary: Mapping[str, Any]) -> str:
    if surface_status in {"INCOMPLETE_INPUTS", "BLOCKED_BY_SENSITIVE_DATA"}:
        return surface_status
    if _as_bool(oanda_summary.get("same_name_bank_required")):
        return "BLOCKED_BY_RAIL"
    if oanda_summary["blockers"]:
        return "BLOCKED_BY_RAIL"
    readiness = _as_text(oanda_summary.get("readiness_status")).lower()
    if readiness in {"blocked", "not_ready", "needs_attention"}:
        return "BLOCKED_BY_RAIL"
    return "READY_FOR_OWNER_REVIEW"


def _big_winner_card_status(alert_level: str) -> str:
    if alert_level == "BIG_WINNER_REVIEW":
        return "READY_FOR_OWNER_REVIEW"
    if alert_level == "WATCHLIST_ONLY":
        return "WATCHLIST_ONLY"
    return "WATCHLIST_ONLY"


def _safe_manual_next_action(surface_status: str) -> str:
    if surface_status == "INCOMPLETE_INPUTS":
        return (
            "Provide sanitized upstream read-only outputs, then rerun owner-review surface."
        )
    if surface_status == "READY_FOR_OWNER_REVIEW":
        return (
            "Owner may review the capital withdrawal packet manually. AIOS does not move money, "
            "access banks, access brokers, or execute trades."
        )
    return (
        "Resolve listed blockers, rerun the read-only owner-review surface, and keep all "
        "real-world money movement/manual trading outside AIOS until owner approval."
    )


def _sensitive_block_payload(owner_name: str) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "trade_execution_allowed": False,
        "owner_name": owner_name,
        "owner_decision_required": True,
        "surface_status": "BLOCKED_BY_SENSITIVE_DATA",
        "capital_bucket_summary": {
            "bucket_state": {},
            "stale_bucket_flags": ["sensitive_financial_data_blocked"],
            "purge_actions_count": 0,
            "rollover_actions_count": 0,
            "sweep_actions_count": 0,
            "withdrawal_bucket_status": {"status": "BLOCKED"},
            "protected_reserve_status": {"operating_reserve_met": False, "tax_reserve_met": False},
            "margin_or_open_risk_block": False,
            "daily_loss_stop_active": False,
            "protected_reserve_blocked": True,
        },
        "purge_rollover_sweep_summary": {
            "purge_actions_count": 0,
            "rollover_actions_count": 0,
            "sweep_actions_count": 0,
            "stale_bucket_flags": ["sensitive_financial_data_blocked"],
            "withdrawal_bucket_status": {"status": "BLOCKED"},
        },
        "rail_readiness_summary": {
            "eligible_rail_count": 0,
            "blocked_rail_count": 0,
            "lowest_cost_rail_id": None,
            "fastest_rail_id": None,
            "preferred_withdrawal_rail_id": None,
            "same_name_proof_status": {"required": False, "satisfied": False},
            "sensitive_data_blocked": True,
            "third_party_payment_blocked": False,
        },
        "withdrawal_cadence_summary": {
            "recommended_cadence": "no_withdrawal",
            "weekly_eligible": False,
            "monthly_eligible": False,
            "bimonthly_eligible": False,
            "no_withdrawal_reasons": ["sensitive_financial_data_provided"],
            "risk_blocks": ["sensitive_financial_data_provided"],
            "fee_efficiency": {},
            "blockers": ["sensitive_financial_data_provided"],
        },
        "withdrawal_plan_summary": {
            "withdrawal_plan_status": "BLOCKED_BY_SENSITIVE_DATA",
            "eligible_for_owner_review": False,
            "selected_review_rail": None,
            "owner_gate": {
                "owner_name": owner_name,
                "approval_required": True,
                "execution_allowed": False,
                "approval_scope": "manual_review_only",
            },
            "manual_execution_only": True,
            "safe_next_action": (
                "Remove sensitive fields and rerun. AIOS does not move money, access banks, "
                "access brokers, or execute trades."
            ),
            "blockers": ["sensitive_financial_data_provided"],
        },
        "oanda_funding_summary": {
            "readiness_status": "BLOCKED",
            "same_name_bank_required": False,
            "withdrawal_hierarchy_notes": [],
            "blockers": ["sensitive_financial_data_provided"],
            "safe_next_action": "Remove sensitive fields and rerun owner-review surface.",
        },
        "big_winner_summary": {
            "alert_level": "WATCHLIST_ONLY",
            "top_opportunity": None,
            "big_winner_candidate_count": 0,
            "safe_next_action": "Remove sensitive fields and rerun owner-review surface.",
            "blockers": ["sensitive_financial_data_provided"],
        },
        "protected_reserve_summary": {
            "status": {"operating_reserve_met": False, "tax_reserve_met": False},
            "margin_or_open_risk_block": False,
            "daily_loss_stop_active": False,
        },
        "blockers": ["sensitive_financial_data_provided"],
        "missing_information": ["sensitive_data_check_failed"],
        "owner_review_cards": [
            _build_card(
                card_id=card_id,
                title=_normalize_title(card_id),
                status="BLOCKED_BY_SENSITIVE_DATA",
                priority="high" if card_id != "REMAINING_WORK" else "low",
                summary={"status": "sensitive_input_detected"},
                blockers=["sensitive_financial_data_provided"],
                safe_next_action=(
                    "Remove sensitive fields and rerun owner-review surface."
                ),
            )
            for card_id in REQUIRED_CARD_IDS
        ],
        "safe_manual_next_action": (
            "Remove sensitive fields from upstream payload and rerun the owner-review surface. "
            "AIOS does not move money, access banks, access brokers, or execute trades."
        ),
        "audit_record": {
            "as_of": now,
            "schema": SCHEMA,
            "mode": MODE,
            "surface_status": "BLOCKED_BY_SENSITIVE_DATA",
            "input_fields_seen": sorted(set(str(key) for key in {})),
            "safe_boundary": "read_only",
        },
        "safety": {
            "read_only": True,
            "money_movement_allowed": False,
            "bank_access_allowed": False,
            "broker_api_allowed": False,
            "trade_execution_allowed": False,
            "credential_use_allowed": False,
            "scheduler_allowed": False,
            "daemon_allowed": False,
            "webhook_allowed": False,
            "owner_gate_required": True,
            "manual_execution_only": True,
        },
    }


def _contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key).lower()
            if any(token in key_text for token in SENSITIVE_KEY_PARTS):
                return True
            if _contains_sensitive_key(item):
                return True
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def _as_mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _as_sequence(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (str, bytes, bytearray)):
        return [value]
    if isinstance(value, Sequence):
        return [item for item in value]
    return [value]


def _as_bool(value: Any, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None or value == "":
        return default
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value) if value is not None else default


def _as_text(value: Any, default: str | None = None) -> str:
    if value is None:
        return default if default is not None else ""
    text = str(value).strip()
    return text or (default if default is not None else "")


def _as_count(value: Any) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return len(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _extract_id(value: Mapping[str, Any] | None) -> str | None:
    if not isinstance(value, Mapping):
        return None
    rail_id = value.get("rail_id")
    if rail_id is None:
        return None
    text = str(rail_id).strip()
    return text or None


def _normalize_status(value: str) -> str:
    if value in {
        "READY_FOR_OWNER_REVIEW",
        "WATCHLIST_ONLY",
        "BLOCKED_BY_RISK",
        "BLOCKED_BY_RAIL",
        "BLOCKED_BY_RESERVE",
        "BLOCKED_BY_SENSITIVE_DATA",
        "INCOMPLETE_INPUTS",
    }:
        return value
    return "BLOCKED_BY_RISK"


def _normalize_title(card_id: str) -> str:
    return card_id.replace("_", " ").title()


def _normalize_opportunity_pair(pair: str | None, direction: str | None) -> dict[str, str]:
    return {
        "pair": _as_text(pair),
        "direction": _as_text(direction),
    }


def _unique(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(item for item in values if item))


__all__ = ["SCHEMA", "MODE", "evaluate_owner_review_capital_surface_v1"]
