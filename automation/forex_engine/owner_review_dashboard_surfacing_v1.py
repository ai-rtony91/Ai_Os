"""Read-only owner-review dashboard projection for owner-review + remaining-work surfacing."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any

SCHEMA = "AIOS_FOREX_OWNER_REVIEW_DASHBOARD_SURFACING_V1"
MODE = "READ_ONLY_DASHBOARD_SURFACE_PROJECTION"

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

ALLOWED_DASHBOARD_STATUSES = {
    "READY_FOR_OWNER_REVIEW",
    "WATCHLIST_ONLY",
    "BLOCKED_BY_RISK",
    "BLOCKED_BY_RAIL",
    "BLOCKED_BY_RESERVE",
    "BLOCKED_BY_SENSITIVE_DATA",
    "INCOMPLETE_INPUTS",
}

REQUIRED_CARD_IDS = (
    "OWNER_REVIEW_STATUS",
    "CAPITAL_BUCKETS",
    "RAILS",
    "WITHDRAWAL_CADENCE",
    "WITHDRAWAL_PLAN",
    "OANDA_FUNDING",
    "BIG_WINNER_WATCHTOWER",
    "REMAINING_WORK",
    "NEXT_PACKET",
    "SAFETY_BOUNDARY",
)

CARD_METADATA = {
    "OWNER_REVIEW_STATUS": {
        "title": "Owner-Review Status",
        "priority": "high",
        "display_group": "summary",
        "sort_order": 10,
    },
    "CAPITAL_BUCKETS": {
        "title": "Capital Buckets",
        "priority": "high",
        "display_group": "capital",
        "sort_order": 20,
    },
    "RAILS": {
        "title": "Rails",
        "priority": "high",
        "display_group": "capital",
        "sort_order": 30,
    },
    "WITHDRAWAL_CADENCE": {
        "title": "Withdrawal Cadence",
        "priority": "medium",
        "display_group": "capital",
        "sort_order": 40,
    },
    "WITHDRAWAL_PLAN": {
        "title": "Withdrawal Plan",
        "priority": "high",
        "display_group": "capital",
        "sort_order": 50,
    },
    "OANDA_FUNDING": {
        "title": "OANDA Funding",
        "priority": "medium",
        "display_group": "capital",
        "sort_order": 60,
    },
    "BIG_WINNER_WATCHTOWER": {
        "title": "Big Winner Watchtower",
        "priority": "low",
        "display_group": "signals",
        "sort_order": 70,
    },
    "REMAINING_WORK": {
        "title": "Remaining Work",
        "priority": "medium",
        "display_group": "workflow",
        "sort_order": 80,
    },
    "NEXT_PACKET": {
        "title": "Next Packet",
        "priority": "medium",
        "display_group": "workflow",
        "sort_order": 90,
    },
    "SAFETY_BOUNDARY": {
        "title": "Safety Boundary",
        "priority": "critical",
        "display_group": "safety",
        "sort_order": 100,
    },
}


def evaluate_owner_review_dashboard_surfacing_v1(payload: dict | None = None) -> dict[str, Any]:
    source = payload if isinstance(payload, Mapping) else {}

    if _contains_sensitive_key(source):
        owner_name = _as_text(source.get("owner_name"), "Anthony")
        return _sensitive_payload(owner_name)

    owner_name = _as_text(source.get("owner_name"), "Anthony")
    as_of_date = _as_text(source.get("as_of_date"), datetime.now(timezone.utc).isoformat())

    owner_review_input = source.get("owner_review_capital_surface")
    remaining_work_input = source.get("remaining_work_closure_index")

    owner_review_capital_surface = (
        owner_review_input if isinstance(owner_review_input, Mapping) else {}
    )
    remaining_work_closure_index = (
        remaining_work_input if isinstance(remaining_work_input, Mapping) else {}
    )

    missing_information: list[str] = []
    if not isinstance(owner_review_input, Mapping):
        missing_information.append("owner_review_capital_surface")
    if not isinstance(remaining_work_input, Mapping):
        missing_information.append("remaining_work_closure_index")

    owner_review_cards = _as_sequence(owner_review_capital_surface.get("owner_review_cards"))
    owner_review_cards_by_id = {
        _as_text(item.get("card_id")): _as_mapping(item)
        for item in owner_review_cards
        if isinstance(item, Mapping) and _as_text(item.get("card_id"))
    }

    owner_review_surface_status = _as_text(
        owner_review_capital_surface.get("surface_status"),
        "INCOMPLETE_INPUTS",
    )
    owner_review_missing_information = _as_str_list(
        owner_review_capital_surface.get("missing_information")
    )
    owner_review_blockers = _as_str_list(owner_review_capital_surface.get("blockers"))
    if owner_review_missing_information:
        missing_information.extend(owner_review_missing_information)

    remaining_lanes = _normalize_remaining_lanes(
        _as_sequence(remaining_work_closure_index.get("remaining_lanes"))
    )
    blocked_lanes = _coerce_string_list(remaining_work_closure_index.get("blocked_lanes"))
    deferred_lanes = _coerce_string_list(remaining_work_closure_index.get("deferred_lanes"))
    remaining_work_blockers = _coerce_string_list(remaining_work_closure_index.get("blocked_lanes"))

    remaining_work_summary_status = _as_text(
        remaining_work_closure_index.get("closure_index_status"),
        "ACTIVE",
    )
    completion_policy = _as_mapping(remaining_work_closure_index.get("completion_policy"))
    completion_policy_statuses = _coerce_string_list(
        completion_policy.get("allowed_terminal_statuses")
    )
    next_best_packet = _as_text(
        remaining_work_closure_index.get("next_best_packet"),
        "AIOS_FOREX_OWNER_REVIEW_DASHBOARD_SURFACING_V1",
    )

    capital_bucket_summary = _as_mapping(owner_review_capital_surface.get("capital_bucket_summary"))
    rail_readiness_summary = _as_mapping(owner_review_capital_surface.get("rail_readiness_summary"))
    withdrawal_cadence_summary = _as_mapping(
        owner_review_capital_surface.get("withdrawal_cadence_summary")
    )
    withdrawal_plan_summary = _as_mapping(owner_review_capital_surface.get("withdrawal_plan_summary"))
    oanda_funding_summary = _as_mapping(owner_review_capital_surface.get("oanda_funding_summary"))
    big_winner_summary = _as_mapping(owner_review_capital_surface.get("big_winner_summary"))
    protected_reserve_summary = _as_mapping(owner_review_capital_surface.get("protected_reserve_summary"))
    remaining_work_summary = _as_mapping(owner_review_capital_surface.get("remaining_work_summary"))

    dashboard_status = _resolve_dashboard_status(
        owner_review_surface_status=owner_review_surface_status,
        missing_information=missing_information,
        owner_review_cards=_as_sequence(owner_review_capital_surface.get("owner_review_cards")),
    )

    risk_blockers = _collect_risk_blockers(
        owner_review_capital_surface,
        owner_review_blockers,
    )
    rail_blockers = _collect_rail_blockers(
        owner_review_capital_surface,
        owner_review_blockers,
    )
    reserve_blockers = _collect_reserve_blockers(
        owner_review_capital_surface,
        protected_reserve_summary,
        owner_review_blockers,
    )
    incomplete_input_blockers = _unique(
        [
            "owner_review_capital_surface_missing"
            if "owner_review_capital_surface" in missing_information
            else "",
            "remaining_work_closure_index_missing"
            if "remaining_work_closure_index" in missing_information
            else "",
        ]
        + owner_review_missing_information
    )

    blocker_summary = {
        "risk_blockers": risk_blockers,
        "rail_blockers": rail_blockers,
        "reserve_blockers": reserve_blockers,
        "sensitive_data_blockers": [],
        "incomplete_input_blockers": incomplete_input_blockers,
        "remaining_work_blockers": remaining_work_blockers,
        "all_blockers": _unique(
            risk_blockers
            + rail_blockers
            + reserve_blockers
            + remaining_work_blockers
            + incomplete_input_blockers
        ),
    }

    safe_manual_next_action = _safe_manual_next_action(dashboard_status)

    remaining_work_top_lanes = [
        lane.get("lane_id") for lane in remaining_lanes[:3] if lane.get("lane_id")
    ]

    next_best_summary = {
        "lane_count": len(remaining_lanes),
        "next_packet": next_best_packet,
        "closure_status": remaining_work_summary_status,
        "top_lanes": remaining_work_top_lanes,
    }

    dashboard_cards = _build_dashboard_cards(
        owner_review_cards_by_id=owner_review_cards_by_id,
        owner_review_capital_surface=owner_review_capital_surface,
        dashboard_status=dashboard_status,
        capital_bucket_summary=capital_bucket_summary,
        rail_readiness_summary=rail_readiness_summary,
        withdrawal_cadence_summary=withdrawal_cadence_summary,
        withdrawal_plan_summary=withdrawal_plan_summary,
        oanda_funding_summary=oanda_funding_summary,
        big_winner_summary=big_winner_summary,
        remaining_work_summary=remaining_work_summary,
        next_best_packet=next_best_packet,
        remaining_lanes=remaining_lanes,
        remaining_work_blockers=remaining_work_blockers,
        next_best_status=_resolve_next_packet_status(
            next_best_packet,
            remaining_work_summary_status,
        ),
        blocked_lanes=blocked_lanes,
    )

    dashboard_summary = {
        "headline_status": dashboard_status,
        "owner_name": owner_name,
        "ready_card_count": len([card for card in dashboard_cards if card["status"] == "READY_FOR_OWNER_REVIEW"]),
        "blocked_card_count": len([card for card in dashboard_cards if card["status"].startswith("BLOCKED_BY")]),
        "watchlist_card_count": len([card for card in dashboard_cards if card["status"] == "WATCHLIST_ONLY"]),
        "incomplete_card_count": len([card for card in dashboard_cards if card["status"] == "INCOMPLETE_INPUTS"]),
        "top_blockers": blocker_summary["all_blockers"][:5],
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": safe_manual_next_action,
        "last_updated_source": (
            _as_text(owner_review_capital_surface.get("audit_record", {}).get("as_of"))
            or _as_text(remaining_work_closure_index.get("audit_record", {}).get("as_of"))
            or as_of_date
        ),
    }

    owner_action_queue = _build_owner_action_queue(
        dashboard_status=dashboard_status,
        risk_blockers=risk_blockers,
        rail_blockers=rail_blockers,
        reserve_blockers=reserve_blockers,
        incomplete_inputs=missing_information,
        next_best_packet=next_best_packet,
    )

    remaining_work_summary_projection = {
        "closure_index_status": remaining_work_summary_status,
        "remaining_lane_count": len(remaining_lanes),
        "next_best_packet": next_best_packet,
        "blocked_lanes": blocked_lanes,
        "deferred_lanes": deferred_lanes,
        "top_remaining_lanes": remaining_work_top_lanes,
        "completion_policy_statuses": completion_policy_statuses,
    }

    display_contract = {
        "display_only": True,
        "mutates_repo": False,
        "creates_dashboard_runtime": False,
        "source_of_truth": "owner_review_capital_surface + remaining_work_closure_index",
        "cards_are_projection_only": True,
        "owner_action_required_for_real_world_steps": True,
    }

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "dashboard_runtime_created": False,
        "scheduler_created": False,
        "daemon_created": False,
        "webhook_created": False,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "trade_execution_allowed": False,
        "credential_use_allowed": False,
        "owner_name": owner_name,
        "owner_decision_required": True,
        "dashboard_status": dashboard_status,
        "dashboard_cards": dashboard_cards,
        "dashboard_summary": dashboard_summary,
        "owner_action_queue": owner_action_queue,
        "blocker_summary": blocker_summary,
        "missing_information": missing_information,
        "next_best_packet": next_best_packet,
        "remaining_work_summary": remaining_work_summary_projection,
        "safe_manual_next_action": safe_manual_next_action,
        "display_contract": display_contract,
        "audit_record": {
            "as_of_date": as_of_date,
            "schema": SCHEMA,
            "mode": MODE,
            "projection_of": [
                "owner_review_capital_surface",
                "remaining_work_closure_index",
            ],
            "input_fields_seen": sorted(set(str(key) for key in source.keys())),
            "next_best_packet": next_best_packet,
            "dashboard_card_count": len(dashboard_cards),
            "remaining_work_top_lanes": remaining_work_top_lanes,
            "next_best_summary": next_best_summary,
        },
        "safety": {
            "read_only": True,
            "display_only": True,
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
            "manual_execution_only": True,
        },
    }


def _build_dashboard_cards(
    *,
    owner_review_cards_by_id: Mapping[str, dict[str, Any]],
    owner_review_capital_surface: Mapping[str, Any],
    dashboard_status: str,
    capital_bucket_summary: Mapping[str, Any],
    rail_readiness_summary: Mapping[str, Any],
    withdrawal_cadence_summary: Mapping[str, Any],
    withdrawal_plan_summary: Mapping[str, Any],
    oanda_funding_summary: Mapping[str, Any],
    big_winner_summary: Mapping[str, Any],
    remaining_work_summary: Mapping[str, Any],
    next_best_packet: str,
    remaining_lanes: Sequence[Mapping[str, Any]],
    remaining_work_blockers: Sequence[str],
    next_best_status: str,
    blocked_lanes: Sequence[str],
) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    normalized_remaining_lanes = [dict(lane) for lane in remaining_lanes]

    defaults = {
        "OWNER_REVIEW_STATUS": {
            "summary": {
                "surface_status": _as_text(owner_review_capital_surface.get("surface_status")),
                "missing_information": _as_str_list(owner_review_capital_surface.get("missing_information")),
                "owner_gate": _as_mapping(owner_review_capital_surface.get("withdrawal_plan_summary", {}).get("owner_gate")),
            }
        },
        "CAPITAL_BUCKETS": {
            "summary": {
                "capital_bucket_summary": capital_bucket_summary,
            }
        },
        "RAILS": {
            "summary": {
                "rail_readiness_summary": rail_readiness_summary,
            }
        },
        "WITHDRAWAL_CADENCE": {
            "summary": {
                "withdrawal_cadence_summary": withdrawal_cadence_summary,
            }
        },
        "WITHDRAWAL_PLAN": {
            "summary": {
                "withdrawal_plan_summary": withdrawal_plan_summary,
            }
        },
        "OANDA_FUNDING": {
            "summary": {
                "oanda_funding_summary": oanda_funding_summary,
            }
        },
        "BIG_WINNER_WATCHTOWER": {
            "summary": {
                "big_winner_summary": big_winner_summary,
            }
        },
        "REMAINING_WORK": {
            "summary": {
                "remaining_work_summary": remaining_work_summary,
                "remaining_lanes": normalized_remaining_lanes,
            }
        },
        "NEXT_PACKET": {
            "summary": {
                "safe_packet_name": next_best_packet,
                "blocked_lanes": list(blocked_lanes),
                "remaining_lane_count": len(normalized_remaining_lanes),
            }
        },
        "SAFETY_BOUNDARY": {
            "summary": {
                "read_only": True,
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
                "manual_execution_only": True,
            }
        },
    }

    card_default_statuses = {
        "OWNER_REVIEW_STATUS": dashboard_status,
        "CAPITAL_BUCKETS": _infer_capital_status(capital_bucket_summary, dashboard_status),
        "RAILS": _infer_rails_status(rail_readiness_summary, dashboard_status),
        "WITHDRAWAL_CADENCE": _infer_cadence_status(withdrawal_cadence_summary, dashboard_status),
        "WITHDRAWAL_PLAN": _as_text(withdrawal_plan_summary.get("withdrawal_plan_status"), dashboard_status),
        "OANDA_FUNDING": _infer_oanda_status(oanda_funding_summary, dashboard_status),
        "BIG_WINNER_WATCHTOWER": _infer_watchtower_status(big_winner_summary),
        "REMAINING_WORK": _infer_remaining_work_status(remaining_work_blockers, dashboard_status),
        "NEXT_PACKET": next_best_status,
        "SAFETY_BOUNDARY": "READY_FOR_OWNER_REVIEW",
    }

    for card_id in REQUIRED_CARD_IDS:
        metadata = CARD_METADATA[card_id]
        source_card = owner_review_cards_by_id.get(card_id, {})
        summary = dict(defaults[card_id]["summary"])
        status = _normalize_status(
            _as_text(source_card.get("status"), card_default_statuses.get(card_id, dashboard_status))
        )
        if card_id == "OWNER_REVIEW_STATUS" and not source_card:
            status = dashboard_status

        if card_id == "REMAINING_WORK" and not source_card:
            summary["remaining_work_blockers"] = list(remaining_work_blockers)

        cards.append(
            _normalize_card(
                card_id=card_id,
                metadata=metadata,
                source_card=source_card,
                status=status,
                summary=summary,
                dashboard_status=dashboard_status,
            )
        )

    return sorted(cards, key=lambda item: item["sort_order"])


def _normalize_card(
    *,
    card_id: str,
    metadata: Mapping[str, Any],
    source_card: Mapping[str, Any],
    status: str,
    summary: Mapping[str, Any],
    dashboard_status: str,
) -> dict[str, Any]:
    return {
        "card_id": card_id,
        "title": _as_text(source_card.get("title"), metadata["title"]),
        "status": status,
        "priority": _as_text(source_card.get("priority"), metadata["priority"]),
        "owner_decision_required": True,
        "execution_allowed": False,
        "summary": dict(summary),
        "blockers": _as_str_list(
            source_card.get("blockers"),
            default=_blockers_for_status(status, dashboard_status),
        ),
        "safe_next_action": _as_text(
            source_card.get("safe_next_action"),
            _safe_action_by_status(status, dashboard_status),
        ),
        "display_group": metadata["display_group"],
        "sort_order": metadata["sort_order"],
    }


def _blockers_for_status(status: str, dashboard_status: str) -> list[str]:
    if status == "BLOCKED_BY_RISK":
        return ["dashboard_blocked_by_risk"]
    if status == "BLOCKED_BY_RAIL":
        return ["dashboard_blocked_by_rail"]
    if status == "BLOCKED_BY_RESERVE":
        return ["dashboard_blocked_by_reserve"]
    if status == "BLOCKED_BY_SENSITIVE_DATA":
        return ["sensitive_financial_data_provided"]
    if status == "INCOMPLETE_INPUTS":
        return ["missing_projection_inputs"]
    if status == "WATCHLIST_ONLY":
        return ["watchlist_only"]
    if dashboard_status == "INCOMPLETE_INPUTS":
        return ["missing_projection_inputs"]
    return []


def _safe_action_by_status(status: str, dashboard_status: str) -> str:
    if status == "INCOMPLETE_INPUTS" or dashboard_status == "INCOMPLETE_INPUTS":
        return "Provide sanitized owner-review and remaining-work inputs, then rerun dashboard surfacing."
    if status == "BLOCKED_BY_RISK":
        return "Resolve listed risk blockers and rerun the read-only projection."
    if status == "BLOCKED_BY_RAIL":
        return "Resolve rail blockers and rerun the read-only projection."
    if status == "BLOCKED_BY_RESERVE":
        return "Resolve reserve blockers and rerun the read-only projection."
    if status == "WATCHLIST_ONLY":
        return "Watchlist state is read-only. Continue monitoring and keep money movement outside AIOS."
    if status == "BLOCKED_BY_SENSITIVE_DATA":
        return "Remove sensitive data and rerun dashboard surfacing."
    return "Review cards and continue owner-only manual execution steps."


def _resolve_next_packet_status(next_best_packet: str, closure_index_status: str) -> str:
    if closure_index_status == "EMPTY":
        return "READY_FOR_OWNER_REVIEW"
    if next_best_packet:
        return "READY_FOR_OWNER_REVIEW"
    return "INCOMPLETE_INPUTS"


def _resolve_dashboard_status(
    *,
    owner_review_surface_status: str,
    missing_information: Sequence[str],
    owner_review_cards: Sequence[Any],
) -> str:
    if missing_information:
        return "INCOMPLETE_INPUTS"
    status = _normalize_status(owner_review_surface_status)
    if status != "BLOCKED_BY_RISK" and status != "BLOCKED_BY_RAIL":
        return status
    for card in owner_review_cards:
        if not isinstance(card, Mapping):
            continue
        source_status = _normalize_status(_as_text(card.get("status")))
        if source_status in ALLOWED_DASHBOARD_STATUSES and source_status.startswith("BLOCKED_BY"):
            return source_status
    return status


def _infer_capital_status(
    capital_bucket_summary: Mapping[str, Any],
    dashboard_status: str,
) -> str:
    if dashboard_status in {"INCOMPLETE_INPUTS", "BLOCKED_BY_SENSITIVE_DATA"}:
        return dashboard_status
    if _as_bool(capital_bucket_summary.get("margin_or_open_risk_block"), default=False):
        return "BLOCKED_BY_RISK"
    if not _as_bool(_as_mapping(capital_bucket_summary.get("protected_reserve_status")).get("operating_reserve_met"), default=True):
        return "BLOCKED_BY_RESERVE"
    if not _as_bool(_as_mapping(capital_bucket_summary.get("protected_reserve_status")).get("tax_reserve_met"), default=True):
        return "BLOCKED_BY_RESERVE"
    if _as_bool(capital_bucket_summary.get("daily_loss_stop_active"), default=False):
        return "BLOCKED_BY_RISK"
    return dashboard_status


def _infer_rails_status(
    rail_readiness_summary: Mapping[str, Any],
    dashboard_status: str,
) -> str:
    if dashboard_status in {"INCOMPLETE_INPUTS", "BLOCKED_BY_SENSITIVE_DATA"}:
        return dashboard_status
    same_name_status = _as_mapping(rail_readiness_summary.get("same_name_proof_status"))
    required = _as_bool(same_name_status.get("required"), default=False)
    satisfied = _as_bool(same_name_status.get("satisfied"), default=not required)
    if required and not satisfied:
        return "BLOCKED_BY_RAIL"
    if _as_bool(rail_readiness_summary.get("third_party_payment_blocked"), default=False):
        return "BLOCKED_BY_RAIL"
    if _as_bool(rail_readiness_summary.get("sensitive_data_blocked"), default=False):
        return "BLOCKED_BY_RISK"
    if _as_count(rail_readiness_summary.get("eligible_rail_count")) == 0:
        return "BLOCKED_BY_RAIL"
    return dashboard_status


def _infer_cadence_status(
    withdrawal_cadence_summary: Mapping[str, Any],
    dashboard_status: str,
) -> str:
    if dashboard_status in {"INCOMPLETE_INPUTS", "BLOCKED_BY_SENSITIVE_DATA"}:
        return dashboard_status
    cadence = _as_text(withdrawal_cadence_summary.get("recommended_cadence"))
    if cadence == "no_withdrawal":
        return "WATCHLIST_ONLY"
    return dashboard_status


def _infer_oanda_status(
    oanda_funding_summary: Mapping[str, Any],
    dashboard_status: str,
) -> str:
    if dashboard_status in {"INCOMPLETE_INPUTS", "BLOCKED_BY_SENSITIVE_DATA"}:
        return dashboard_status
    if _as_bool(oanda_funding_summary.get("same_name_bank_required"), default=False):
        return "BLOCKED_BY_RAIL"
    if _as_str_list(oanda_funding_summary.get("blockers")):
        return "BLOCKED_BY_RAIL"
    if _as_text(oanda_funding_summary.get("readiness_status"), "blocked").lower() == "ready":
        return "READY_FOR_OWNER_REVIEW"
    if _as_text(oanda_funding_summary.get("readiness_status"), "ready").lower() in {
        "blocked",
        "not_ready",
        "needs_attention",
    }:
        return "BLOCKED_BY_RAIL"
    return dashboard_status


def _infer_watchtower_status(big_winner_summary: Mapping[str, Any]) -> str:
    if _as_text(big_winner_summary.get("alert_level"), "WATCHLIST_ONLY") == "BIG_WINNER_REVIEW":
        return "READY_FOR_OWNER_REVIEW"
    return "WATCHLIST_ONLY"


def _infer_remaining_work_status(
    remaining_work_blockers: Sequence[str],
    dashboard_status: str,
) -> str:
    if remaining_work_blockers:
        return "BLOCKED_BY_RAIL"
    if dashboard_status == "INCOMPLETE_INPUTS":
        return dashboard_status
    return "READY_FOR_OWNER_REVIEW"


def _collect_risk_blockers(
    owner_review_capital_surface: Mapping[str, Any],
    surface_blockers: Sequence[str],
) -> list[str]:
    risk_blockers: list[str] = []
    bucket_summary = _as_mapping(owner_review_capital_surface.get("capital_bucket_summary"))

    if _as_bool(bucket_summary.get("margin_or_open_risk_block"), default=False):
        risk_blockers.append("margin_or_open_risk_block")
    if _as_bool(bucket_summary.get("daily_loss_stop_active"), default=False):
        risk_blockers.append("daily_loss_stop_active")

    for blocker in surface_blockers:
        blocker_norm = _as_text(blocker).lower()
        if "risk" in blocker_norm or blocker_norm in {"daily_loss_stop_active", "margin_or_open_risk_block"}:
            risk_blockers.append(blocker)

    plan_blockers = _as_str_list(owner_review_capital_surface.get("withdrawal_plan_summary", {}).get("blockers"))
    for blocker in plan_blockers:
        blocker_norm = _as_text(blocker).lower()
        if "risk" in blocker_norm:
            risk_blockers.append(blocker)

    return _unique(risk_blockers)


def _collect_rail_blockers(
    owner_review_capital_surface: Mapping[str, Any],
    surface_blockers: Sequence[str],
) -> list[str]:
    rail_blockers: list[str] = []
    rail_summary = _as_mapping(owner_review_capital_surface.get("rail_readiness_summary"))
    if _as_bool(rail_summary.get("third_party_payment_blocked"), default=False):
        rail_blockers.append("third_party_payment_blocked")
    if _as_bool(rail_summary.get("sensitive_data_blocked"), default=False):
        rail_blockers.append("sensitive_financial_data_provided")

    same_name_status = _as_mapping(rail_summary.get("same_name_proof_status"))
    if _as_bool(same_name_status.get("required"), default=False) and not _as_bool(
        same_name_status.get("satisfied"),
        default=False,
    ):
        rail_blockers.append("same_name_proof_required")

    for blocker in surface_blockers:
        blocker_norm = _as_text(blocker).lower()
        if "rail" in blocker_norm or blocker_norm in {
            "same_name_proof_required",
            "no_eligible_rails",
        }:
            if blocker not in rail_blockers:
                rail_blockers.append(blocker)
        elif blocker not in rail_blockers and blocker_norm in {"third_party_payment_blocked"}:
            rail_blockers.append(blocker)

    if _as_count(rail_summary.get("eligible_rail_count")) == 0:
        rail_blockers.append("no_eligible_rails")

    return _unique(rail_blockers)


def _collect_reserve_blockers(
    owner_review_capital_surface: Mapping[str, Any],
    protected_reserve_summary: Mapping[str, Any],
    surface_blockers: Sequence[str],
) -> list[str]:
    reserve_blockers: list[str] = []
    reserve_status = _as_mapping(protected_reserve_summary)
    operating = _as_bool(_as_mapping(reserve_status.get("status", {})).get("operating_reserve_met"), default=True) is False
    tax = _as_bool(_as_mapping(reserve_status.get("status", {})).get("tax_reserve_met"), default=True) is False
    if operating:
        reserve_blockers.append("protected_reserve_operating_not_met")
    if tax:
        reserve_blockers.append("protected_reserve_tax_not_met")
    for blocker in surface_blockers:
        blocker_norm = _as_text(blocker).lower()
        if "reserve" in blocker_norm and blocker not in reserve_blockers:
            reserve_blockers.append(blocker)
    return _unique(reserve_blockers)


def _build_owner_action_queue(
    *,
    dashboard_status: str,
    risk_blockers: Sequence[str],
    rail_blockers: Sequence[str],
    reserve_blockers: Sequence[str],
    incomplete_inputs: Sequence[str],
    next_best_packet: str,
) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []

    if dashboard_status == "INCOMPLETE_INPUTS":
        _append_action(
            actions,
            {
                "action_id": "REVIEW_REMAINING_WORK_NEXT_PACKET",
                "title": "Review remaining-work packet inputs",
                "priority": "high",
                "source_card_id": "REMAINING_WORK",
                "owner_decision_required": True,
                "execution_allowed": False,
                "safe_action": (
                    "Provide sanitized owner-review and remaining-work inputs, then rerun dashboard "
                    "surfacing."
                ),
                "blocked_by": list(_unique(incomplete_inputs)) or ["missing_projection_inputs"],
            },
        )

    if risk_blockers:
        _append_action(
            actions,
            {
                "action_id": "REVIEW_RISK_BLOCKERS",
                "title": "Review risk blockers",
                "priority": "high",
                "source_card_id": "CAPITAL_BUCKETS",
                "owner_decision_required": True,
                "execution_allowed": False,
                "safe_action": "Review risk blockers and rerun with updated read-only risk evidence.",
                "blocked_by": list(risk_blockers),
            },
        )

    if rail_blockers:
        _append_action(
            actions,
            {
                "action_id": "REVIEW_RAIL_PROOF",
                "title": "Review rail proof",
                "priority": "high",
                "source_card_id": "RAILS",
                "owner_decision_required": True,
                "execution_allowed": False,
                "safe_action": "Review rail proof and rerun owner-review dashboard projection.",
                "blocked_by": list(rail_blockers),
            },
        )

    if reserve_blockers:
        _append_action(
            actions,
            {
                "action_id": "REVIEW_CAPITAL_WITHDRAWAL_PACKET",
                "title": "Review capital withdrawal packet",
                "priority": "medium",
                "source_card_id": "WITHDRAWAL_PLAN",
                "owner_decision_required": True,
                "execution_allowed": False,
                "safe_action": "Resolve reserve blockers and rerun withdrawal plan review manually.",
                "blocked_by": list(reserve_blockers),
            },
        )

    if dashboard_status == "READY_FOR_OWNER_REVIEW":
        _append_action(
            actions,
            {
                "action_id": "REVIEW_CAPITAL_WITHDRAWAL_PACKET",
                "title": "Review capital withdrawal packet",
                "priority": "medium",
                "source_card_id": "WITHDRAWAL_PLAN",
                "owner_decision_required": True,
                "execution_allowed": False,
                "safe_action": "Review withdrawal plan manually for owner sign-off.",
                "blocked_by": ["owner_approval_required"],
            },
        )

    _append_action(
        actions,
        {
            "action_id": "REVIEW_REMAINING_WORK_NEXT_PACKET",
            "title": "Review next remaining-work packet",
            "priority": "medium",
            "source_card_id": "NEXT_PACKET",
            "owner_decision_required": True,
            "execution_allowed": False,
            "safe_action": f"Read safety summary and queue the next packet: {next_best_packet}.",
            "blocked_by": ["owner_decision_required"],
        },
    )

    _append_action(
        actions,
        {
            "action_id": "REVIEW_BIG_WINNER_WATCHLIST",
            "title": "Review big-winner watchlist",
            "priority": "low",
            "source_card_id": "BIG_WINNER_WATCHTOWER",
            "owner_decision_required": True,
            "execution_allowed": False,
            "safe_action": "Review watchlist candidates manually; no automation or execution.",
            "blocked_by": ["manual_review_only"],
        },
    )

    return actions


def _append_action(actions: list[dict[str, Any]], action: dict[str, Any]) -> None:
    if not any(item["action_id"] == action["action_id"] for item in actions):
        actions.append(action)


def _safe_manual_next_action(dashboard_status: str) -> str:
    if dashboard_status == "READY_FOR_OWNER_REVIEW":
        return (
            "Owner may review dashboard cards manually. AIOS does not move money, access banks, "
            "access brokers, execute trades, or start dashboard runtimes."
        )
    if dashboard_status == "INCOMPLETE_INPUTS":
        return (
            "Provide sanitized owner-review surface and remaining-work closure index outputs, "
            "then rerun dashboard surfacing."
        )
    return (
        "Resolve dashboard blockers, rerun the read-only projection, and keep money/trading/"
        "broker/bank actions outside AIOS until owner approval."
    )


def _sensitive_payload(owner_name: str) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    cards = [
        _normalize_card(
            card_id=card_id,
            metadata=CARD_METADATA[card_id],
            source_card={},
            status="BLOCKED_BY_SENSITIVE_DATA",
            summary={"status": "sensitive_financial_data_provided"},
            dashboard_status="BLOCKED_BY_SENSITIVE_DATA",
        )
        for card_id in REQUIRED_CARD_IDS
    ]
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "dashboard_runtime_created": False,
        "scheduler_created": False,
        "daemon_created": False,
        "webhook_created": False,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "trade_execution_allowed": False,
        "credential_use_allowed": False,
        "owner_name": owner_name,
        "owner_decision_required": True,
        "dashboard_status": "BLOCKED_BY_SENSITIVE_DATA",
        "dashboard_cards": cards,
        "safe_manual_next_action": (
            "Remove sensitive financial fields from payload and rerun dashboard surfacing."
        ),
        "dashboard_summary": {
            "headline_status": "BLOCKED_BY_SENSITIVE_DATA",
            "owner_name": owner_name,
            "ready_card_count": 0,
            "blocked_card_count": len(REQUIRED_CARD_IDS),
            "watchlist_card_count": 0,
            "incomplete_card_count": 0,
            "top_blockers": ["sensitive_financial_data_provided"],
            "next_best_packet": "AIOS_FOREX_OWNER_REVIEW_DASHBOARD_SURFACING_V1",
            "safe_manual_next_action": (
                "Remove sensitive financial fields from payload and rerun dashboard surfacing."
            ),
            "last_updated_source": now,
        },
        "owner_action_queue": [
            {
                "action_id": "REVIEW_REMAINING_WORK_NEXT_PACKET",
                "title": "Remove sensitive payload values",
                "priority": "high",
                "source_card_id": "SAFETY_BOUNDARY",
                "owner_decision_required": True,
                "execution_allowed": False,
                "safe_action": "Remove sensitive financial keys and rerun dashboard surfacing.",
                "blocked_by": ["sensitive_financial_data_provided"],
            }
        ],
        "blocker_summary": {
            "risk_blockers": [],
            "rail_blockers": [],
            "reserve_blockers": [],
            "sensitive_data_blockers": ["sensitive_financial_data_provided"],
            "incomplete_input_blockers": [],
            "remaining_work_blockers": [],
            "all_blockers": ["sensitive_financial_data_provided"],
        },
        "missing_information": ["sensitive_financial_data_provided"],
        "next_best_packet": "AIOS_FOREX_OWNER_REVIEW_DASHBOARD_SURFACING_V1",
        "remaining_work_summary": {
            "closure_index_status": "INCOMPLETE_INPUTS",
            "remaining_lane_count": 0,
            "next_best_packet": "AIOS_FOREX_OWNER_REVIEW_DASHBOARD_SURFACING_V1",
            "blocked_lanes": [],
            "deferred_lanes": [],
            "top_remaining_lanes": [],
            "completion_policy_statuses": [
                "LANDED",
                "BLOCKED_WITH_REASON",
                "DEFERRED_BY_OWNER",
                "SUPERSEDED",
                "NEEDS_MORE_EVIDENCE",
            ],
        },
        "display_contract": {
            "display_only": True,
            "mutates_repo": False,
            "creates_dashboard_runtime": False,
            "source_of_truth": "owner_review_capital_surface + remaining_work_closure_index",
            "cards_are_projection_only": True,
            "owner_action_required_for_real_world_steps": True,
        },
        "audit_record": {
            "as_of_date": now,
            "schema": SCHEMA,
            "mode": MODE,
            "source_fields_seen": ["owner_review_capital_surface", "remaining_work_closure_index"],
            "input_redacted": True,
        },
        "safety": {
            "read_only": True,
            "display_only": True,
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
            "manual_execution_only": True,
        },
    }


def _normalize_status(value: str) -> str:
    if value in ALLOWED_DASHBOARD_STATUSES:
        return value
    return "BLOCKED_BY_RISK"


def _contains_sensitive_key(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False
    for key in value.keys():
        key_text = str(key).lower()
        if any(token in key_text for token in SENSITIVE_KEY_PARTS):
            return True
    return False


def _normalize_remaining_lanes(
    remaining_lanes: Sequence[Mapping[str, Any]] | Sequence[Any],
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for lane in remaining_lanes:
        if not isinstance(lane, Mapping):
            continue
        lane_id = _as_text(lane.get("lane_id"))
        if not lane_id:
            continue
        normalized.append(
            {
                "lane_id": lane_id,
                "title": _as_text(lane.get("title"), lane_id),
                "status": _as_text(lane.get("status")),
                "priority": _as_text(lane.get("priority"), "medium"),
                "safe_packet_name": _as_text(lane.get("safe_packet_name")),
            }
        )
    return normalized


def _as_mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _as_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _as_bool(value: Any, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None or value == "":
        return default
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _as_sequence(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (str, bytes, bytearray)):
        return [value]
    if isinstance(value, Sequence):
        return list(value)
    return [value]


def _coerce_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (str, bytes, bytearray)):
        text = str(value).strip()
        return [text] if text else []
    if isinstance(value, Sequence):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _as_str_list(value: Any, default: Sequence[str] | None = None) -> list[str]:
    values = _as_sequence(value)
    if not values and default is not None:
        return list(default)
    return [str(item).strip() for item in values if str(item).strip()]


def _as_count(value: Any) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return 0
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return len(value)
    return 0


def _unique(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(item for item in values if item))


__all__ = [
    "SCHEMA",
    "MODE",
    "evaluate_owner_review_dashboard_surfacing_v1",
]
