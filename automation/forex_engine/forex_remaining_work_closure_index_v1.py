"""Deterministic remaining-work closure index for Forex/autonomy packets."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "AIOS_FOREX_REMAINING_WORK_CLOSURE_INDEX_V1"
MODE = "READ_ONLY_REMAINING_WORK_INDEX"

RECOMMENDED_SEQUENCE = [
    "Owner-review dashboard/surface packet",
    "Capital withdrawal owner-review workflow packet",
    "Evidence depth / walk-forward sufficiency packet",
    "Candidate quality improvement packet",
    "Broker demo observability and exception review packet",
    "Risk and kill-switch surfacing packet",
    "Dashboard state cleanup/reduction packet",
    "Voice-AI owner review summary packet",
    "Security persistence gate packet",
    "Final autonomy supervisor readiness gate packet",
]

ALLOWED_COMPLETION_STATUSES = [
    "LANDED",
    "BLOCKED_WITH_REASON",
    "DEFERRED_BY_OWNER",
    "SUPERSEDED",
    "NEEDS_MORE_EVIDENCE",
]


def evaluate_forex_remaining_work_closure_index_v1(payload: dict | None = None) -> dict[str, Any]:
    source = payload if isinstance(payload, Mapping) else {}

    remaining_lanes = _normalize_or_default_lanes(_as_sequence(source.get("remaining_lanes")))
    if not remaining_lanes:
        remaining_lanes = _default_remaining_lanes()

    blocked_lanes = _coerce_string_list(source.get("blocked_lanes"))
    deferred_lanes = _coerce_string_list(source.get("deferred_lanes"))
    landed_lanes = _coerce_string_list(source.get("landed_lanes"))

    if not blocked_lanes:
        blocked_lanes = [
            lane["lane_id"] for lane in remaining_lanes if lane.get("status") == "BLOCKED_WITH_REASON"
        ]
    if not deferred_lanes:
        deferred_lanes = [
            lane["lane_id"] for lane in remaining_lanes if lane.get("status") == "DEFERRED_BY_OWNER"
        ]

    closure_index_status = "ACTIVE"
    if not remaining_lanes:
        closure_index_status = "EMPTY"

    next_best_packet = _resolve_next_best_packet(
        remaining_lanes=remaining_lanes,
        landed_lanes=set(landed_lanes),
    )

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "owner_decision_required": True,
        "closure_index_status": closure_index_status,
        "remaining_lanes": remaining_lanes,
        "recommended_sequence": list(RECOMMENDED_SEQUENCE),
        "next_best_packet": next_best_packet,
        "blocked_lanes": blocked_lanes,
        "deferred_lanes": deferred_lanes,
        "completion_policy": {
            "one_atomic_packet_at_a_time": True,
            "clean_main_before_next_packet": True,
            "no_live_trading_without_owner_gate": True,
            "no_money_movement_without_owner_gate": True,
            "no_credentials_in_repo": True,
            "allowed_terminal_statuses": list(ALLOWED_COMPLETION_STATUSES),
        },
        "safety": {
            "read_only": True,
            "no_repo_mutation_outside_packet": True,
            "live_trading_allowed": False,
            "money_movement_allowed": False,
            "broker_api_allowed": False,
            "bank_access_allowed": False,
            "credential_use_allowed": False,
            "owner_gate_required": True,
        },
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "source_fields_seen": sorted(set(str(key) for key in source.keys())),
            "remaining_lane_count": len(remaining_lanes),
            "recommended_sequence_count": len(RECOMMENDED_SEQUENCE),
        },
    }

def _as_sequence(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (str, bytes, bytearray)):
        return [value]
    if isinstance(value, Sequence):
        return list(value)
    return [value]


def _normalize_or_default_lanes(items: Sequence[Any]) -> list[dict[str, Any]]:
    if not items:
        return []
    normalized = []
    for item in items:
        if not isinstance(item, Mapping):
            continue
        normalized.append(_coerce_lane(item))
    if not normalized:
        return []
    return [lane for lane in normalized if lane.get("lane_id")]


def _default_remaining_lanes() -> list[dict[str, Any]]:
    return [
        _lane(
            "OWNER_REVIEW_DASHBOARD_SURFACING",
            "Owner-review dashboard/surface packet",
            "NEEDS_MORE_EVIDENCE",
            "critical",
            [],
            "AIOS_FOREX_OWNER_REVIEW_DASHBOARD_SURFACING_V1",
            ["owner_review_surface", "owner_gates_ready"],
            [
                "live_trading",
                "money_movement_without_owner_gate",
                "broker_api_calls",
                "deposit_execution",
                "withdrawal_execution",
                "scheduler_start",
                "daemon_start",
            ],
        ),
        _lane(
            "CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW",
            "Capital withdrawal owner-review workflow",
            "NEEDS_MORE_EVIDENCE",
            "critical",
            ["OWNER_REVIEW_DASHBOARD_SURFACING"],
            "AIOS_FOREX_CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW_V1",
            ["capital_bucket_summary", "rail_readiness_summary", "withdrawal_plan_ready"],
            [
                "withdrawal_execution",
                "money_movement_without_owner_gate",
                "broker_api_calls",
                "scheduler_start",
                "daemon_start",
            ],
        ),
        _lane(
            "FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY",
            "Evidence depth / walk-forward sufficiency packet",
            "NEEDS_MORE_EVIDENCE",
            "high",
            ["CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW"],
            "AIOS_FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY_V1",
            ["evidence_depth", "walk_forward_reports"],
            [
                "withdrawal_execution",
                "broker_api_calls",
                "money_movement_without_owner_gate",
            ],
        ),
        _lane(
            "PROFIT_CANDIDATE_QUALITY_IMPROVEMENT",
            "Candidate quality improvement packet",
            "NEEDS_MORE_EVIDENCE",
            "high",
            ["FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY"],
            "AIOS_FOREX_PROFIT_CANDIDATE_QUALITY_IMPROVEMENT_V1",
            ["candidate_quality_metrics", "quality_rejection_review"],
            [
                "trading_strategy_automation",
                "broker_api_calls",
                "withdrawal_execution",
            ],
        ),
        _lane(
            "BROKER_DEMO_OBSERVABILITY_AND_EXCEPTION_REVIEW",
            "Broker demo observability and exception review packet",
            "NEEDS_MORE_EVIDENCE",
            "high",
            ["PROFIT_CANDIDATE_QUALITY_IMPROVEMENT"],
            "AIOS_BROKER_DEMO_OBSERVABILITY_AND_EXCEPTION_REVIEW_V1",
            ["demo_observability", "exception_review_log"],
            [
                "live_demo_trade",
                "auto_order_submission",
                "broker_api_calls",
                "withdrawal_execution",
            ],
        ),
        _lane(
            "RISK_KILL_SWITCH_DAILY_STOP_SURFACING",
            "Risk and kill-switch surfacing packet",
            "NEEDS_MORE_EVIDENCE",
            "critical",
            ["BROKER_DEMO_OBSERVABILITY_AND_EXCEPTION_REVIEW"],
            "AIOS_RISK_KILL_SWITCH_DAILY_STOP_SURFACING_V1",
            ["risk_budget", "kill_switch_state", "daily_loss_stop_state"],
            [
                "live_trading",
                "withdrawal_execution",
                "broker_api_calls",
            ],
        ),
        _lane(
            "DASHBOARD_STATE_REDUCTION_AND_SOURCE_OF_TRUTH",
            "Dashboard state cleanup/reduction packet",
            "NEEDS_MORE_EVIDENCE",
            "high",
            ["RISK_KILL_SWITCH_DAILY_STOP_SURFACING"],
            "AIOS_DASHBOARD_STATE_REDUCTION_AND_SOURCE_OF_TRUTH_V1",
            ["dashboard_state_divergence", "legacy_unscoped_cards"],
            [
                "scheduler_start",
                "daemon_start",
                "manual_repo_mutation_outside_packet",
            ],
        ),
        _lane(
            "VOICE_AI_OWNER_REVIEW_SUMMARY",
            "Voice-AI owner review summary packet",
            "NEEDS_MORE_EVIDENCE",
            "medium",
            ["DASHBOARD_STATE_REDUCTION_AND_SOURCE_OF_TRUTH"],
            "AIOS_VOICE_AI_OWNER_REVIEW_SUMMARY_V1",
            ["voice_action_automation", "auto_trade_inference"],
            [
                "voice_to_money",
                "broker_api_calls",
                "withdrawal_execution",
            ],
        ),
        _lane(
            "SECURITY_CREDENTIAL_PERSISTENCE_GATE",
            "Security credential persistence gate packet",
            "NEEDS_MORE_EVIDENCE",
            "critical",
            ["VOICE_AI_OWNER_REVIEW_SUMMARY"],
            "AIOS_SECURITY_CREDENTIAL_PERSISTENCE_GATE_V1",
            ["credential_write", "password_reuse"],
            [
                "credential_use",
                "password_storage",
                "third_party_secret_upload",
            ],
        ),
        _lane(
            "FINAL_AUTONOMY_SUPERVISOR_READINESS_GATE",
            "Final autonomy supervisor readiness gate packet",
            "NEEDS_MORE_EVIDENCE",
            "critical",
            ["SECURITY_CREDENTIAL_PERSISTENCE_GATE"],
            "AIOS_FINAL_AUTONOMY_SUPERVISOR_READINESS_GATE_V1",
            ["owner_gate_bypass", "live_trading_authorization"],
            [
                "live_trading",
                "money_movement_without_owner_gate",
                "broker_api_calls",
                "withdrawal_execution",
            ],
        ),
    ]


def _lane(
    lane_id: str,
    title: str,
    status: str,
    priority: str,
    depends_on: list[str],
    safe_packet_name: str,
    evidence_needed: list[str],
    forbidden_actions: list[str],
) -> dict[str, Any]:
    normalized_status = status if status in ALLOWED_COMPLETION_STATUSES else "NEEDS_MORE_EVIDENCE"
    return {
        "lane_id": lane_id,
        "title": title,
        "status": normalized_status,
        "priority": priority,
        "depends_on": list(depends_on),
        "allowed_next_action": f"Run {safe_packet_name} when owner gate is approved.",
        "forbidden_actions": list(dict.fromkeys(item for item in forbidden_actions if str(item).strip())),
        "owner_gate_required": True,
        "evidence_needed": list(dict.fromkeys(str(item) for item in evidence_needed if str(item).strip())),
        "safe_packet_name": safe_packet_name,
    }


def _coerce_lane(payload: Mapping[str, Any]) -> dict[str, Any]:
    status = _as_text(payload.get("status"), "NEEDS_MORE_EVIDENCE")
    if status not in ALLOWED_COMPLETION_STATUSES:
        status = "NEEDS_MORE_EVIDENCE"

    return {
        "lane_id": _as_text(payload.get("lane_id")),
        "title": _as_text(payload.get("title"), _as_text(payload.get("lane_id"), "")),
        "status": status,
        "priority": _as_text(payload.get("priority"), "medium"),
        "depends_on": _coerce_string_list(payload.get("depends_on")),
        "allowed_next_action": _as_text(
            payload.get("allowed_next_action"),
            "Run safe next packet after owner approval.",
        ),
        "forbidden_actions": _coerce_string_list(payload.get("forbidden_actions"))
        or _lane("GENERIC", "Generic lane", "NEEDS_MORE_EVIDENCE", "medium", [], "AIOS_PLACEHOLDER_V1", [], [])[
            "forbidden_actions"
        ],
        "owner_gate_required": _as_bool(payload.get("owner_gate_required"), default=True),
        "evidence_needed": _coerce_string_list(payload.get("evidence_needed")),
        "safe_packet_name": _as_text(
            payload.get("safe_packet_name"),
            f"AIOS_{_as_text(payload.get('lane_id'), 'FOREX').upper()}_V1",
        ),
    }

def _resolve_next_best_packet(
    *,
    remaining_lanes: Sequence[Mapping[str, Any]],
    landed_lanes: set[str],
) -> str:
    for lane in remaining_lanes:
        lane_id = _as_text(lane.get("lane_id"))
        if lane_id and lane_id not in landed_lanes:
            return _as_text(lane.get("safe_packet_name"), "AIOS_FOREX_OWNER_REVIEW_DASHBOARD_SURFACING_V1")
    return _as_text(
        remaining_lanes[-1].get("safe_packet_name") if remaining_lanes else None,
        "AIOS_FOREX_OWNER_REVIEW_DASHBOARD_SURFACING_V1",
    )


def _as_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _coerce_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (str, bytes, bytearray)):
        return [_as_text(value)]
    if isinstance(value, Sequence):
        return [str(item).strip() for item in value if str(item).strip()]
    return [_as_text(value)]


def _as_bool(value: Any, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None or value == "":
        return default
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return default


__all__ = [
    "SCHEMA",
    "MODE",
    "evaluate_forex_remaining_work_closure_index_v1",
]
