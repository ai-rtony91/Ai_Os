from __future__ import annotations

from typing import Any, Mapping


STATUS_READY = "CREDENTIAL_VAULT_READY"
STATUS_MORE_INFO = "CREDENTIAL_VAULT_MORE_INFORMATION_REQUIRED"
STATUS_BLOCKED = "CREDENTIAL_VAULT_BLOCKED"
STATUS_REJECTED = "CREDENTIAL_VAULT_REJECTED"

REQUIRED_FIELDS = [
    "vault_provider_declared",
    "vault_access_method_declared",
    "secret_names_declared_only",
    "no_plaintext_secret_storage",
    "no_secret_values_present",
    "rotation_policy_declared",
    "access_audit_required",
    "least_privilege_required",
    "operator_approval_required",
    "emergency_revoke_plan_declared",
    "credential_scope_declared",
    "paper_only_credential_review",
]


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "credential_values_accessed": False,
        "credential_values_stored": False,
        "credential_values_printed": False,
        "env_files_read": False,
        "vault_connection_active": False,
        "broker_connection_active": False,
        "broker_access": False,
        "network_access": False,
        "order_execution_enabled": False,
        "live_trading_authorized": False,
        "demo_execution_active": False,
        "capital_allocation_modified": False,
        "operator_review_required": True,
    }


def evaluate_credential_vault_readiness(metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    metadata = dict(metadata or {})
    approved_controls: list[str] = []
    blocked_controls: list[str] = []
    blocked_reasons: list[str] = []

    missing = [field for field in REQUIRED_FIELDS if field not in metadata]
    if missing:
        blocked_reasons.extend(f"missing_credential_metadata:{field}" for field in missing)
        return {
            "credential_readiness_completed": True,
            "credential_vault_ready": False,
            "credential_policy_status": STATUS_MORE_INFO,
            "approved_controls": [],
            "blocked_controls": blocked_controls,
            "blocked_reasons": blocked_reasons,
            "next_safe_action": "collect_complete_credential_governance_metadata",
            "operator_review_required": True,
            "safety": _safety(),
        }

    checks = [
        ("vault_provider_declared", "vault provider declared"),
        ("vault_access_method_declared", "access method declared"),
        ("secret_names_declared_only", "secret names only, no values"),
        ("no_plaintext_secret_storage", "plaintext secret storage forbidden"),
        ("no_secret_values_present", "no secret values present"),
        ("rotation_policy_declared", "rotation policy declared"),
        ("access_audit_required", "access audit required"),
        ("least_privilege_required", "least privilege required"),
        ("operator_approval_required", "operator approval required"),
        ("emergency_revoke_plan_declared", "emergency revoke plan declared"),
        ("credential_scope_declared", "credential scope declared"),
        ("paper_only_credential_review", "paper-only review enforced"),
    ]

    for field, control in checks:
        if bool(metadata.get(field)) is True:
            approved_controls.append(control)
        else:
            blocked_controls.append(control)
            blocked_reasons.append(f"credential_control_failed:{field}")

    status = STATUS_READY if not blocked_reasons else STATUS_BLOCKED

    return {
        "credential_readiness_completed": True,
        "credential_vault_ready": status == STATUS_READY,
        "credential_policy_status": status,
        "approved_controls": sorted(set(approved_controls)),
        "blocked_controls": sorted(set(blocked_controls)),
        "blocked_reasons": blocked_reasons,
        "next_safe_action": "operator_review_credential_policy_before_any_future_secret_handoff"
        if status == STATUS_READY
        else "resolve_credential_governance_blockers_before_any_secret_handoff",
        "operator_review_required": True,
        "safety": _safety(),
    }
