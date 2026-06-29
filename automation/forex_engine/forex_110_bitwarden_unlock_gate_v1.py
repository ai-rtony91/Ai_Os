"""Repo-safe Forex 110 completion and Bitwarden lock gate.

This module builds deterministic local state only. It checks for named repo
artifacts and never reads secrets, contacts brokers, starts runtime services,
or performs order-capable actions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "Reports" / "forex_delivery"

MISSION_ID = "MISSION-AIOS-FOREX-FINISH-LINE-V1"
PROGRAM_ID = "PROGRAM-FOREX-PROFIT-AUTONOMY-V1"
EPIC_ID = "EPC-FOREX-AUTONOMY-COMPLETION-001"
BUCKET_ID = "BKT-FOREX-110-COMPLETION-BITWARDEN-LOCK-001"
PACKET_ID = "PKT-FOREX-110-COMPLETION-AND-BITWARDEN-UNLOCK-GATE-V1"

STATE_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_110_COMPLETION_AND_BITWARDEN_UNLOCK_GATE_V1_STATE.json"
)
REPORT_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_110_COMPLETION_AND_BITWARDEN_UNLOCK_GATE_V1_REPORT.md"
)
DASHBOARD_UX_OUTPUT_PATH = REPORTS_DIR / "AIOS_FOREX_DASHBOARD_END_USER_FINAL_UX_V1.md"
EMOJI_MAP_OUTPUT_PATH = REPORTS_DIR / "AIOS_FOREX_DASHBOARD_EMOJI_WINDOW_MAP_FINAL_V1.md"
BITWARDEN_LOCK_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_BITWARDEN_LOCKED_UNTIL_110_COMPLETE_V1.md"
)
BROKER_HANDOFF_OUTPUT_PATH = (
    REPORTS_DIR / "AIOS_FOREX_FINAL_PROTECTED_BROKER_BOUNDARY_HANDOFF_V1.md"
)

REQUIRED_FOREX_ARTIFACTS = (
    "Reports/forex_delivery/AIOS_FOREX_BROKER_CONNECTION_PROOF_BOUNDARY_READINESS_V1_STATE.json",
    "Reports/forex_delivery/AIOS_FOREX_OVERNIGHT_REPO_SAFE_CAMPAIGN_PLANNER_V1_STATE.json",
    "Reports/forex_delivery/AIOS_FOREX_EVIDENCE_DEPTH_WALKFORWARD_SUFFICIENCY_V1_STATE.json",
    "Reports/forex_delivery/AIOS_FOREX_CANDIDATE_SELECTOR_HARDENING_V1_STATE.json",
    "Reports/forex_delivery/AIOS_FOREX_DEMO_READINESS_DECISION_V1_STATE.json",
    "Reports/forex_delivery/AIOS_FOREX_NEXT_REPO_SAFE_QUEUE_V1_STATE.json",
)

DASHBOARD_CONTRACT_DOCS = (
    "docs/trading_lab/forex/FOREX_DASHBOARD_END_USER_FINAL_UX_V1.md",
    "docs/trading_lab/forex/FOREX_DASHBOARD_EMOJI_WINDOW_MAP_FINAL_V1.md",
)

DASHBOARD_EMOJI_WINDOWS = (
    "Command Center",
    "Safety Gate",
    "Candidate",
    "Evidence",
    "Broker Boundary",
    "Profit Readiness",
    "Reports",
    "SOS",
    "Settings",
    "Secrets Later",
)

DASHBOARD_WINDOW_DETAILS = (
    {"emoji": "🏛️", "label": "Command Center", "default": "overall Forex 110 status and next safe action"},
    {"emoji": "🛡️", "label": "Safety Gate", "default": "blocked/protected action state"},
    {"emoji": "🎯", "label": "Candidate", "default": "selected candidate readiness summary"},
    {"emoji": "📊", "label": "Evidence", "default": "evidence sufficiency summary"},
    {"emoji": "🚧", "label": "Broker Boundary", "default": "owner-gated broker boundary state"},
    {"emoji": "💰", "label": "Profit Readiness", "default": "profit readiness status only"},
    {"emoji": "📁", "label": "Reports", "default": "report index and expandable detail windows"},
    {"emoji": "🆘", "label": "SOS", "default": "critical stop/blocker escalation only"},
    {"emoji": "⚙️", "label": "Settings", "default": "display preferences without execution controls"},
    {"emoji": "🔒", "label": "Secrets Later", "default": "Bitwarden remains locked until merge and owner confirmation"},
)

DASHBOARD_CRITICAL_DISPLAY_RULES = (
    "Show critical status by default.",
    "Show active blocker by default.",
    "Show next safe action by default.",
    "Show safety state by default.",
    "Do not show secret values.",
    "Do not show broker account identifiers.",
    "Do not show order execution data.",
    "Do not show demo or live authorization controls.",
)

DASHBOARD_HIDDEN_HEAVY_DATA_RULES = (
    "Hide raw broker data behind report/detail windows.",
    "Hide raw trade data behind report/detail windows.",
    "Hide raw metadata behind report/detail windows.",
    "Hide long validator logs behind report/detail windows.",
    "Hide internal state dumps behind report/detail windows.",
)

DASHBOARD_OVERWHELM_PREVENTION_RULES = (
    "Use emoji/picture-style clickable button and window labels.",
    "Keep the first view to critical information only.",
    "No dashboard chaos.",
    "No micro-data overload.",
    "No broker-heavy raw data in the default view.",
)

PROTECTED_FALSE_FIELDS = (
    "broker_api_used",
    "credentials_used",
    "env_read",
    "account_identifiers_used",
    "order_execution",
    "demo_authorized",
    "live_authorized",
    "scheduler_started",
    "daemon_started",
    "webhook_started",
    "background_loop_started",
    "bitwarden_started",
    "vaultwarden_started",
    "secrets_migration_started",
    "token_storage_started",
)


def run_forex_110_bitwarden_unlock_gate_v1() -> dict[str, Any]:
    required_present = _artifact_presence(REQUIRED_FOREX_ARTIFACTS)
    missing_artifacts = [path for path, present in required_present.items() if not present]
    dashboard_docs_present = _artifact_presence(DASHBOARD_CONTRACT_DOCS)
    dashboard_ready = all(dashboard_docs_present.values())
    repo_safe_percent = 100 if not missing_artifacts else 0
    dashboard_extra_percent = 10 if dashboard_ready else 0
    total_percent = repo_safe_percent + dashboard_extra_percent
    forex_110_complete = total_percent == 110

    result: dict[str, Any] = {
        "gate_status": "FOREX_110_REPO_SAFE_GATE_COMPLETE" if forex_110_complete else "FOREX_110_REPO_SAFE_GATE_BLOCKED",
        "forex_repo_safe_completion_percent": repo_safe_percent,
        "dashboard_extra_completion_percent": dashboard_extra_percent,
        "total_forex_completion_percent": total_percent,
        "forex_110_complete": forex_110_complete,
        "bitwarden_unlocked": False,
        "bitwarden_blocked_reason": (
            "Bitwarden, Vaultwarden, secrets migration, and token storage remain locked "
            "inside this packet. Planning may begin only after this Forex 110 gate is "
            "merged to main and owner confirms."
        ),
        "required_forex_artifacts": list(REQUIRED_FOREX_ARTIFACTS),
        "required_forex_artifacts_present": required_present,
        "missing_forex_artifacts": missing_artifacts,
        "dashboard_end_user_contract_status": {
            "status": "DEFINED" if dashboard_ready else "MISSING_REQUIRED_DOCS",
            "required_contract_docs": list(DASHBOARD_CONTRACT_DOCS),
            "required_contract_docs_present": dashboard_docs_present,
        },
        "dashboard_emoji_windows": list(DASHBOARD_WINDOW_DETAILS),
        "dashboard_critical_display_rules": list(DASHBOARD_CRITICAL_DISPLAY_RULES),
        "dashboard_hidden_heavy_data_rules": list(DASHBOARD_HIDDEN_HEAVY_DATA_RULES),
        "dashboard_overwhelm_prevention_rules": list(DASHBOARD_OVERWHELM_PREVENTION_RULES),
        "protected_broker_boundary_status": "PROTECTED_AND_SEPARATE",
        "protected_broker_boundary_handoff": {
            "status": "OWNER_GATED",
            "blocked_actions": [
                "broker contact",
                "credential use",
                ".env access",
                "account identifier use",
                "broker account inspection",
                "order execution",
                "demo authorization",
                "live authorization",
                "scheduler daemon webhook worker watcher listener background loop",
            ],
        },
        "next_project_allowed": (
            "Bitwarden planning may begin only after this Forex 110 gate is merged to main and owner confirms."
        ),
        "safe_next_action": (
            "Review this local commit, open a PR when ready, merge the Forex 110 gate to main, "
            "then request owner confirmation before any Bitwarden planning begins."
        ),
        "mission_id": MISSION_ID,
        "program_id": PROGRAM_ID,
        "epic_id": EPIC_ID,
        "bucket_id": BUCKET_ID,
        "packet_id": PACKET_ID,
    }
    result.update({field: False for field in PROTECTED_FALSE_FIELDS})
    return result


def build_report_markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# AIOS Forex 110 Completion And Bitwarden Unlock Gate V1 Report",
        "",
        f"Gate status: {result.get('gate_status')}",
        f"Forex repo-safe completion percent: {result.get('forex_repo_safe_completion_percent')}",
        f"Dashboard extra completion percent: {result.get('dashboard_extra_completion_percent')}",
        f"Total Forex completion percent: {result.get('total_forex_completion_percent')}",
        f"Forex 110 complete: {result.get('forex_110_complete')}",
        f"Bitwarden unlocked: {result.get('bitwarden_unlocked')}",
        "",
        "Bitwarden blocked reason:",
        str(result.get("bitwarden_blocked_reason")),
        "",
        "Required Forex artifacts:",
    ]
    present = _mapping(result.get("required_forex_artifacts_present"))
    for path in _string_list(result.get("required_forex_artifacts")):
        lines.append(f"- {path}: {present.get(path)}")
    lines.extend(["", "Dashboard emoji windows:"])
    for window in _mapping_list(result.get("dashboard_emoji_windows")):
        lines.append(f"- {window.get('emoji')} {window.get('label')}: {window.get('default')}")
    lines.extend(["", "Critical display rules:"])
    lines.extend(f"- {item}" for item in _string_list(result.get("dashboard_critical_display_rules")))
    lines.extend(["", "Hidden heavy-data rules:"])
    lines.extend(f"- {item}" for item in _string_list(result.get("dashboard_hidden_heavy_data_rules")))
    lines.extend(["", "Overwhelm prevention rules:"])
    lines.extend(f"- {item}" for item in _string_list(result.get("dashboard_overwhelm_prevention_rules")))
    lines.extend(["", "Protected broker boundary:"])
    lines.append(str(result.get("protected_broker_boundary_status")))
    lines.extend(["", "Protected false fields:"])
    for field in PROTECTED_FALSE_FIELDS:
        lines.append(f"- {field}: {result.get(field)}")
    lines.extend(["", "Safe next action:", str(result.get("safe_next_action")), ""])
    return "\n".join(lines)


def build_dashboard_ux_markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# AIOS Forex Dashboard End User Final UX V1",
        "",
        "Forex is not finished for next-project purposes until the Forex 110 gate is merged.",
        "",
        "100% means repo-safe Forex completion: required readiness, evidence, candidate, demo-readiness, queue, and broker-boundary artifacts exist in the repo.",
        "",
        "The final 10% is dashboard end-user organization and UX clarity. The dashboard must present the operator with critical status, blocker, next safe action, and safety state first.",
        "",
        "Bitwarden and Vaultwarden remain locked until after Forex 110 is merged. No secrets migration starts here. No token storage starts here. Broker-facing activity remains protected and separate.",
        "",
        "Default display rules:",
    ]
    lines.extend(f"- {item}" for item in _string_list(result.get("dashboard_critical_display_rules")))
    lines.extend(["", "Hidden detail rules:"])
    lines.extend(f"- {item}" for item in _string_list(result.get("dashboard_hidden_heavy_data_rules")))
    lines.extend(["", "Overwhelm prevention rules:"])
    lines.extend(f"- {item}" for item in _string_list(result.get("dashboard_overwhelm_prevention_rules")))
    lines.append("")
    return "\n".join(lines)


def build_emoji_map_markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# AIOS Forex Dashboard Emoji Window Map Final V1",
        "",
        "Use emoji/picture-style clickable windows. Keep raw data and validator noise behind report/detail windows.",
        "",
    ]
    for window in _mapping_list(result.get("dashboard_emoji_windows")):
        lines.append(f"- {window.get('emoji')} {window.get('label')}: {window.get('default')}")
    lines.extend(
        [
            "",
            "Do not expose secret values, broker account identifiers, order execution data, demo authorization, or live authorization.",
            "",
        ]
    )
    return "\n".join(lines)


def build_bitwarden_lock_markdown(result: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# AIOS Forex Bitwarden Locked Until 110 Complete V1",
            "",
            f"Forex 110 complete: {result.get('forex_110_complete')}",
            f"Bitwarden unlocked: {result.get('bitwarden_unlocked')}",
            "",
            str(result.get("bitwarden_blocked_reason")),
            "",
            "Bitwarden build work remains locked here.",
            "Vaultwarden build work remains locked here.",
            "No secrets migration starts here.",
            "No token storage starts here.",
            "",
            f"Next project rule: {result.get('next_project_allowed')}",
            "",
        ]
    )


def build_broker_handoff_markdown(result: Mapping[str, Any]) -> str:
    handoff = _mapping(result.get("protected_broker_boundary_handoff"))
    lines = [
        "# AIOS Forex Final Protected Broker Boundary Handoff V1",
        "",
        f"Protected broker boundary status: {result.get('protected_broker_boundary_status')}",
        f"Handoff status: {handoff.get('status')}",
        "",
        "Broker-facing activity remains protected and separate.",
        "",
        "Blocked actions:",
    ]
    lines.extend(f"- {item}" for item in _string_list(handoff.get("blocked_actions")))
    lines.extend(
        [
            "",
            "This handoff does not approve broker contact, credentials, .env access, account identifiers, broker account inspection, order execution, demo authorization, live authorization, scheduler activation, daemon activation, webhook activation, or background-loop activation.",
            "",
        ]
    )
    return "\n".join(lines)


def _artifact_presence(paths: tuple[str, ...]) -> dict[str, bool]:
    return {path: (ROOT / path).exists() for path in paths}


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _mapping_list(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, Mapping)]
    return []


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    return []


def to_json_text(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, ensure_ascii=False) + "\n"


__all__ = [
    "BITWARDEN_LOCK_OUTPUT_PATH",
    "BROKER_HANDOFF_OUTPUT_PATH",
    "DASHBOARD_EMOJI_WINDOWS",
    "DASHBOARD_UX_OUTPUT_PATH",
    "EMOJI_MAP_OUTPUT_PATH",
    "PROTECTED_FALSE_FIELDS",
    "REPORT_OUTPUT_PATH",
    "REQUIRED_FOREX_ARTIFACTS",
    "STATE_OUTPUT_PATH",
    "build_bitwarden_lock_markdown",
    "build_broker_handoff_markdown",
    "build_dashboard_ux_markdown",
    "build_emoji_map_markdown",
    "build_report_markdown",
    "run_forex_110_bitwarden_unlock_gate_v1",
    "to_json_text",
]
