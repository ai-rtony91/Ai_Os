from __future__ import annotations

from typing import Any, Mapping


STATUS_READY = "KILL_SWITCH_READY"
STATUS_MORE_INFO = "KILL_SWITCH_MORE_INFORMATION_REQUIRED"
STATUS_BLOCKED = "KILL_SWITCH_BLOCKED"
STATUS_REJECTED = "KILL_SWITCH_REJECTED"

REQUIRED_FIELDS = [
    "kill_switch_declared",
    "manual_operator_stop_declared",
    "max_daily_loss_stop_declared",
    "max_drawdown_stop_declared",
    "emergency_disable_declared",
    "credential_revoke_path_declared",
    "audit_logging_declared",
    "notification_path_declared",
    "operator_override_declared",
    "paper_only_review",
]


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "kill_switch_executed": False,
        "broker_connection_active": False,
        "credentials_accessed": False,
        "network_access": False,
        "order_execution_enabled": False,
        "live_trading_authorized": False,
        "capital_allocation_modified": False,
        "operator_review_required": True,
    }


def evaluate_live_kill_switch_readiness(metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    metadata = dict(metadata or {})
    approved_controls: list[str] = []
    blocked_controls: list[str] = []
    blocked_reasons: list[str] = []

    missing = [field for field in REQUIRED_FIELDS if field not in metadata]
    if missing:
        blocked_reasons.extend(f"missing_kill_switch_metadata:{field}" for field in missing)
        return {
            "kill_switch_readiness_completed": True,
            "kill_switch_ready": False,
            "kill_switch_status": STATUS_MORE_INFO,
            "approved_controls": [],
            "blocked_controls": [],
            "blocked_reasons": blocked_reasons,
            "next_safe_action": "collect_complete_kill_switch_governance_metadata",
            "operator_review_required": True,
            "safety": _safety(),
        }

    checks = [
        ("kill_switch_declared", "kill switch declared"),
        ("manual_operator_stop_declared", "manual stop declared"),
        ("max_daily_loss_stop_declared", "daily loss stop declared"),
        ("max_drawdown_stop_declared", "drawdown stop declared"),
        ("emergency_disable_declared", "emergency disable declared"),
        ("credential_revoke_path_declared", "credential revoke path declared"),
        ("audit_logging_declared", "audit logging declared"),
        ("notification_path_declared", "notification path declared"),
        ("operator_override_declared", "operator override declared"),
        ("paper_only_review", "paper-only review enforced"),
    ]

    for field, control in checks:
        if bool(metadata.get(field)) is True:
            approved_controls.append(control)
        else:
            blocked_controls.append(control)
            blocked_reasons.append(f"kill_switch_control_failed:{field}")

    status = STATUS_READY if not blocked_reasons else STATUS_BLOCKED

    return {
        "kill_switch_readiness_completed": True,
        "kill_switch_ready": status == STATUS_READY,
        "kill_switch_status": status,
        "approved_controls": sorted(set(approved_controls)),
        "blocked_controls": sorted(set(blocked_controls)),
        "blocked_reasons": blocked_reasons,
        "next_safe_action": "operator_review_kill_switch_policy_before_future_live_candidate_advancement"
        if status == STATUS_READY
        else "resolve_kill_switch_governance_blockers_before_live_candidate_advancement",
        "operator_review_required": True,
        "safety": _safety(),
    }
