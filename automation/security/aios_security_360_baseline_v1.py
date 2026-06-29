"""AIOS Security 360 Baseline V1.

Static, deterministic security posture baseline for AIOS. This module does not
read environment files, read credentials, call networks, call brokers, or mutate
files. It returns JSON-safe evidence for reports and review gates.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


SCHEMA_VERSION = "aios.security_360_baseline.v1"
PACKET_ID = "PKT-AIOS-SECURITY-360-ZERO-TO-100-BASELINE-V1"
BANK_STYLE_SECURITY_TARGET = "DEFENSE_IN_DEPTH_HIGH_ASSURANCE_INTERNAL_TARGET"
CERTIFICATION_CLAIM = "NO_EXTERNAL_BANK_CERTIFICATION_CLAIM"
SECURITY_BASELINE_STATUS = "BASELINE_CREATED_REVIEW_REQUIRED"
OVERALL_SECURITY_POSTURE = "REVIEW_REQUIRED"

PROTECTED_ACTION_NAMES = (
    "broker_contact",
    "broker_api_use",
    "credential_use",
    "env_read",
    "account_identifier_use",
    "order_execution",
    "demo_authorization",
    "live_authorization",
    "scheduler_start",
    "daemon_start",
    "webhook_start",
    "watcher_start",
    "listener_start",
    "background_loop_start",
    "remote_public_exposure",
    "tunnel_start",
    "bitwarden_start",
    "vaultwarden_start",
    "secrets_migration",
    "token_storage",
    "dashboard_execution_controls",
)

SECURITY_DOMAIN_NAMES = (
    "Identity and access control",
    "Repo permissions and branch protection",
    "Secret prevention and secret scanning",
    "Credential handling and runtime-only secrets",
    "Broker/API boundary protection",
    "Dashboard remote-access protection",
    "Mobile access protection",
    "Network exposure and tunnel control",
    "Scheduler/daemon/webhook/background-loop control",
    "Bitwarden/Vaultwarden readiness boundary",
    "Logging, audit trail, and evidence integrity",
    "Telemetry and runtime state protection",
    "File-system and generated-artifact hygiene",
    "Worker/Codex/ChatGPT/automation lane separation",
    "CI security gates",
    "Dependency and package risk",
    "Data privacy and account-identifier exclusion",
    "Trading kill switch, one-order-only, max-loss, daily stop, SL/TP gate",
    "Incident response and rollback",
    "Owner approval gates",
)

REQUIRED_STATIC_PATHS = {
    "root_risk_policy": "RISK_POLICY.md",
    "root_security_policy": "SECURITY.md",
    "compliance_baseline": "COMPLIANCE_BASELINE.md",
    "approval_model": "docs/security/approval-model.md",
    "secret_prevention": "docs/security/secret-prevention.md",
    "threat_model": "docs/security/threat-model.md",
    "audit_logging": "docs/security/audit-logging.md",
    "repo_hygiene": "docs/security/repo-hygiene.md",
    "privacy_credential_exclusion": "docs/security/PRIVACY_CREDENTIAL_EXCLUSION_CHECKLIST.md",
    "ci_workflow": ".github/workflows/ci.yml",
    "deploy_workflow": ".github/workflows/azure-deploy.yml",
    "governance_workflow": ".github/workflows/aios-governance.yml",
    "dependabot": ".github/dependabot.yml",
    "dashboard_runtime_state": "Reports/forex_delivery/AIOS_FOREX_DASHBOARD_RUNTIME_UI_V1_STATE.json",
    "remote_dashboard_architecture_state": "Reports/forex_delivery/AIOS_REMOTE_DASHBOARD_ACCESS_ARCHITECTURE_V1_STATE.json",
    "runtime_visibility_schema": "schemas/aios/orchestration/RUNTIME_VISIBILITY_SCHEMA.json",
}


def _status_for_path(repo_root: Path, relative_path: str) -> str:
    if (repo_root / relative_path).exists():
        return "PRESENT"
    return "MISSING_REVIEW_REQUIRED"


def _finding(
    finding_id: str,
    severity: str,
    domain: str,
    summary: str,
    required_action: str,
) -> dict[str, str]:
    return {
        "id": finding_id,
        "severity": severity,
        "domain": domain,
        "summary": summary,
        "required_action": required_action,
    }


def _gate(name: str, required_controls: tuple[str, ...]) -> dict[str, Any]:
    return {
        "name": name,
        "status": "BLOCKED_UNTIL_ALL_CONTROLS_PASS_AND_OWNER_APPROVES",
        "owner_approval_required": True,
        "required_controls": list(required_controls),
    }


def build_protected_actions() -> dict[str, dict[str, Any]]:
    return {
        action: {
            "status": "BLOCKED",
            "owner_approval_required": True,
            "future_gate_required": True,
        }
        for action in PROTECTED_ACTION_NAMES
    }


def build_gates() -> dict[str, dict[str, Any]]:
    return {
        "required_gates_before_remote_dashboard": _gate(
            "Remote Dashboard Gate",
            (
                "authenticated access",
                "private route or HTTPS",
                "read-only dashboard API",
                "no secrets in frontend",
                "no broker account identifiers",
                "no execution controls",
                "source freshness labels",
                "access logging",
                "owner approval",
            ),
        ),
        "required_gates_before_broker_readonly": _gate(
            "Broker Read-Only Gate",
            (
                "sanitized evidence format",
                "no credentials in repo",
                "no account identifiers in repo",
                "no raw broker payloads in repo",
                "runtime-only credentials if ever approved",
                "no order endpoints",
                "owner approval",
            ),
        ),
        "required_gates_before_bitwarden": _gate(
            "Bitwarden Gate",
            (
                "Forex 110 merged",
                "owner confirmation",
                "threat model",
                "backup/export plan",
                "recovery plan",
                "YubiKey/MFA option review",
                "no token storage before approval",
            ),
        ),
        "required_gates_before_demo": _gate(
            "Demo Gate",
            (
                "profitability proof",
                "broker-readonly evidence",
                "latency/canonical audit",
                "kill switch",
                "one-order-only enforcement",
                "micro-size enforcement",
                "stop loss",
                "take profit",
                "max loss",
                "daily stop",
                "owner approval",
                "runtime-only credentials",
                "post-trade evidence capture",
            ),
        ),
        "required_gates_before_live": _gate(
            "Live Gate",
            (
                "profitability proof",
                "broker-readonly evidence",
                "latency/canonical audit",
                "kill switch",
                "one-order-only enforcement",
                "micro-size enforcement",
                "stop loss",
                "take profit",
                "max loss",
                "daily stop",
                "owner approval",
                "runtime-only credentials",
                "post-trade evidence capture",
            ),
        ),
        "required_gates_before_scheduler_daemon_webhook": _gate(
            "Scheduler/Daemon/Webhook Gate",
            (
                "explicit owner approval",
                "bounded runtime",
                "kill switch",
                "logs",
                "alerting",
                "no broker execution by default",
                "safe shutdown",
                "rollback path",
            ),
        ),
    }


def build_security_domains(static_path_status: dict[str, str]) -> list[dict[str, Any]]:
    domain_notes = {
        "Identity and access control": "Human Owner remains final approval authority; remote/auth implementation still requires review.",
        "Repo permissions and branch protection": "Branch protection cannot be verified from local files and remains review-required.",
        "Secret prevention and secret scanning": "Secret-prevention docs and CI source scan exist; platform secret scanning must be verified in GitHub settings.",
        "Credential handling and runtime-only secrets": "Credentials remain blocked; future runtime-only flow requires owner-approved storage boundary.",
        "Broker/API boundary protection": "Broker/API contact remains blocked by root risk policy and dashboard state.",
        "Dashboard remote-access protection": "Remote architecture exists; authenticated read-only route is not implemented or approved.",
        "Mobile access protection": "Mobile access is future-only and must use auth plus private route or HTTPS.",
        "Network exposure and tunnel control": "Public exposure, tunnel start, Tailscale Serve/Funnel, and Cloudflare tunnel remain blocked.",
        "Scheduler/daemon/webhook/background-loop control": "Runtime loops, schedulers, daemons, listeners, and webhooks remain blocked without gates.",
        "Bitwarden/Vaultwarden readiness boundary": "Bitwarden and Vaultwarden remain locked pending owner confirmation and threat-model review.",
        "Logging, audit trail, and evidence integrity": "Audit logging spec exists; retention and tamper-evidence controls need review.",
        "Telemetry and runtime state protection": "Telemetry/runtime state is protected evidence; retention and sanitization policy needs review.",
        "File-system and generated-artifact hygiene": "Repo hygiene policy exists; generated Reports and telemetry require retention decisions.",
        "Worker/Codex/ChatGPT/automation lane separation": "Identity and lane governance exists; protected-action gates remain required.",
        "CI security gates": "CI and governance workflows exist; branch protection and required checks need owner/GitHub verification.",
        "Dependency and package risk": "Dependabot exists; deeper dependency audit tooling remains future hardening.",
        "Data privacy and account-identifier exclusion": "Privacy/credential exclusion checklist exists; future scans must verify no account IDs.",
        "Trading kill switch, one-order-only, max-loss, daily stop, SL/TP gate": "Root risk policy defines required live exception gates; current state remains blocked.",
        "Incident response and rollback": "Secret incident guidance exists; full incident playbook and rollback evidence require review.",
        "Owner approval gates": "Approval model exists; every protected action remains owner-gated.",
    }
    domain_status = {
        "Repo permissions and branch protection": "REVIEW_REQUIRED",
        "Dashboard remote-access protection": "REVIEW_REQUIRED",
        "Mobile access protection": "REVIEW_REQUIRED",
        "Network exposure and tunnel control": "BLOCKED_BY_DEFAULT",
        "Scheduler/daemon/webhook/background-loop control": "BLOCKED_BY_DEFAULT",
        "Bitwarden/Vaultwarden readiness boundary": "BLOCKED_BY_DEFAULT",
        "CI security gates": "REVIEW_REQUIRED",
        "Dependency and package risk": "REVIEW_REQUIRED",
        "Incident response and rollback": "REVIEW_REQUIRED",
    }
    missing_support = [
        key for key, status in static_path_status.items() if status != "PRESENT" and key != "remote_dashboard_architecture_state"
    ]
    domains: list[dict[str, Any]] = []
    for index, name in enumerate(SECURITY_DOMAIN_NAMES, start=1):
        status = domain_status.get(name, "FAIL_CLOSED_BASELINE")
        if missing_support and name in {
            "Secret prevention and secret scanning",
            "Logging, audit trail, and evidence integrity",
            "CI security gates",
        }:
            status = "REVIEW_REQUIRED"
        domains.append(
            {
                "id": index,
                "name": name,
                "status": status,
                "fail_closed": True,
                "notes": domain_notes[name],
            }
        )
    return domains


def build_findings(static_path_status: dict[str, str]) -> dict[str, list[dict[str, str]]]:
    missing_paths = [
        f"{key}: {value}"
        for key, value in static_path_status.items()
        if value != "PRESENT"
    ]
    critical = [
        _finding(
            "SEC360-CRIT-001",
            "CRITICAL",
            "Remote dashboard / broker / automation exposure",
            "Remote dashboard, broker/API, demo/live, Bitwarden, scheduler, daemon, webhook, tunnel, and deployment work must remain blocked until gates are implemented and owner-approved.",
            "Keep all protected actions blocked and complete owner security review before any exposure or execution path.",
        )
    ]
    high = [
        _finding(
            "SEC360-HIGH-001",
            "HIGH",
            "Repo permissions and branch protection",
            "Branch protection and required-check enforcement cannot be proven from local repo files.",
            "Verify GitHub branch protection, required CI checks, and restricted push/merge settings before remote or broker work.",
        ),
        _finding(
            "SEC360-HIGH-002",
            "HIGH",
            "Deployment boundary",
            "A workflow-dispatch Azure dashboard deployment workflow exists, so deployment must remain explicitly blocked until reviewed.",
            "Require owner deployment approval, secret review, and remote dashboard gate completion before use.",
        ),
        _finding(
            "SEC360-HIGH-003",
            "HIGH",
            "Remote dashboard protection",
            "Remote dashboard architecture is defined, but authenticated read-only server, access logging, and mobile/private-route proof are not implemented.",
            "Implement the Remote Dashboard Gate before any LAN, mesh, tunnel, host, or production exposure.",
        ),
        _finding(
            "SEC360-HIGH-004",
            "HIGH",
            "Credential and broker boundary",
            "Credential use, account identifiers, raw broker payloads, order endpoints, and broker contact remain blocked by policy.",
            "Use sanitized evidence only until Broker Read-Only Gate is approved.",
        ),
    ]
    medium = [
        _finding(
            "SEC360-MED-001",
            "MEDIUM",
            "Security authority maturity",
            "Current security docs are marked baseline scaffold or pending human review.",
            "Run owner security review and promote final control decisions in existing authority files through a separate packet.",
        ),
        _finding(
            "SEC360-MED-002",
            "MEDIUM",
            "Dependency risk",
            "Dependabot is configured, but deeper dependency scanning and vulnerability audit gates are not proven in this baseline.",
            "Add reviewed dependency audit gates before production or remote exposure.",
        ),
        _finding(
            "SEC360-MED-003",
            "MEDIUM",
            "Telemetry and generated artifact hygiene",
            "Telemetry, Reports, runtime state, and generated evidence remain protected until retention and sanitization are approved.",
            "Define retention, sanitization, and account-identifier exclusion checks before remote display.",
        ),
    ]
    low = [
        _finding(
            "SEC360-LOW-001",
            "LOW",
            "Documentation consolidation",
            "Some security guidance is split across root, docs/security, governance, workflows, and generated reports.",
            "Future edit should update existing authority only and avoid duplicate security authority.",
        )
    ]
    if missing_paths:
        high.append(
            _finding(
                "SEC360-HIGH-005",
                "HIGH",
                "Missing static controls",
                "Some expected baseline support files are missing or unavailable: " + "; ".join(missing_paths),
                "Create or restore missing support through a separate scoped packet, then rerun baseline.",
            )
        )
    return {
        "critical_blockers": critical,
        "high_priority_findings": high,
        "medium_priority_findings": medium,
        "low_priority_findings": low,
    }


def build_security_360_baseline(repo_root: str | Path = ".") -> dict[str, Any]:
    root = Path(repo_root)
    static_path_status = {
        key: _status_for_path(root, relative_path)
        for key, relative_path in REQUIRED_STATIC_PATHS.items()
    }
    gates = build_gates()
    findings = build_findings(static_path_status)
    current_allowed_state = {
        "read_only_static_repo_inspection": True,
        "dry_run_planning": True,
        "local_static_dashboard_preview": True,
        "sanitized_report_generation": True,
        "owner_review": True,
    }
    current_blocked_state = {
        action: True for action in PROTECTED_ACTION_NAMES
    }
    safe_next_actions = [
        "Owner reviews Security 360 Baseline V1.",
        "Verify GitHub branch protection and required checks.",
        "Run a repo hygiene and account-identifier exclusion review before any remote exposure.",
        "Implement Remote Dashboard Gate before LAN, private mesh, tunnel, host, or production dashboard access.",
        "Keep broker, credential, Bitwarden, demo/live, scheduler, daemon, webhook, tunnel, and deployment work blocked until separate approved gates pass.",
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "packet_id": PACKET_ID,
        "security_baseline_status": SECURITY_BASELINE_STATUS,
        "overall_security_posture": OVERALL_SECURITY_POSTURE,
        "bank_style_security_target": BANK_STYLE_SECURITY_TARGET,
        "certification_claim": CERTIFICATION_CLAIM,
        "protected_actions": build_protected_actions(),
        "security_domains": build_security_domains(static_path_status),
        "critical_blockers": findings["critical_blockers"],
        "high_priority_findings": findings["high_priority_findings"],
        "medium_priority_findings": findings["medium_priority_findings"],
        "low_priority_findings": findings["low_priority_findings"],
        "required_gates_before_remote_dashboard": gates["required_gates_before_remote_dashboard"],
        "required_gates_before_broker_readonly": gates["required_gates_before_broker_readonly"],
        "required_gates_before_bitwarden": gates["required_gates_before_bitwarden"],
        "required_gates_before_demo": gates["required_gates_before_demo"],
        "required_gates_before_live": gates["required_gates_before_live"],
        "required_gates_before_scheduler_daemon_webhook": gates["required_gates_before_scheduler_daemon_webhook"],
        "current_allowed_state": current_allowed_state,
        "current_blocked_state": current_blocked_state,
        "safe_next_actions": safe_next_actions,
        "static_path_status": static_path_status,
        "tool_behavior": {
            "static_repo_checks_only": True,
            "reads_env_files": False,
            "reads_secrets": False,
            "calls_network": False,
            "calls_broker": False,
            "mutates_files": False,
            "json_safe_output": True,
            "unknown_missing_controls_fail_closed": True,
        },
    }
