from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

VERSION = "oanda_demo_execution_truth_audit_v1"

OANDA_DEMO_EXECUTION_PATH_PRESENT_OWNER_MANUAL_RUN_REQUIRED = (
    "OANDA_DEMO_EXECUTION_PATH_PRESENT_OWNER_MANUAL_RUN_REQUIRED"
)
OANDA_DEMO_EXECUTION_PATH_PARTIAL_COMMAND_ONLY = (
    "OANDA_DEMO_EXECUTION_PATH_PARTIAL_COMMAND_ONLY"
)
OANDA_DEMO_EXECUTION_PATH_BLOCKED_MISSING_TRANSPORT = (
    "OANDA_DEMO_EXECUTION_PATH_BLOCKED_MISSING_TRANSPORT"
)
OANDA_DEMO_EXECUTION_PATH_BLOCKED_MISSING_OWNER_APPROVAL = (
    "OANDA_DEMO_EXECUTION_PATH_BLOCKED_MISSING_OWNER_APPROVAL"
)
OANDA_DEMO_EXECUTION_PATH_UNKNOWN = "OANDA_DEMO_EXECUTION_PATH_UNKNOWN"

REQUIRED_OPERATOR_SENTENCE = (
    "AIOS has an owner-run OANDA demo one-order path in the repo, "
    "but this packet does not execute it."
)

PROTECTED_PERMISSION_DEFAULTS = {
    "demo_execution_allowed": False,
    "broker_action_allowed": False,
    "real_money_allowed": False,
    "compounding_allowed": False,
    "bank_movement_allowed": False,
    "live_trading_allowed": False,
    "credential_access_allowed": False,
    "account_id_persistence_allowed": False,
    "autonomous_execution_allowed": False,
    "scheduler_allowed": False,
    "daemon_allowed": False,
    "webhook_allowed": False,
}

CURRENT_REPO_SOURCE_FILES_PRESENT = (
    "automation/forex_engine/oanda_demo_final_owner_runtime_run_one_order_v1.py",
    "automation/forex_engine/oanda_demo_broker_call_one_order_manual_run_v1.py",
    "automation/forex_engine/oanda_demo_owner_run_actual_one_order_command_v1.py",
    "automation/forex_engine/oanda_demo_runtime_http_transport_one_order_owner_run_v1.py",
    "automation/forex_engine/oanda_demo_vault_backed_one_order_transport_v1.py",
    "automation/forex_engine/oanda_demo_first_trade_actual_owner_command_run.py",
    "automation/forex_engine/oanda_demo_first_trade_owner_manual_execution_window_v1.py",
    "automation/forex_engine/oanda_demo_owner_one_trade_command_package_v1.py",
    "scripts/forex_delivery/run_oanda_demo_final_owner_runtime_run_one_order_v1.py",
    "scripts/forex_delivery/run_oanda_demo_broker_call_one_order_manual_run_v1.py",
    "scripts/forex_delivery/run_oanda_demo_owner_run_actual_one_order_command_v1.py",
    "scripts/forex_delivery/run_oanda_demo_runtime_http_transport_one_order_owner_run_v1.py",
    "scripts/forex_delivery/run_oanda_demo_first_trade_actual_owner_command_run.py",
    "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_FINAL_OWNER_RUNTIME_RUN_ONE_ORDER_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_BROKER_CALL_IMPLEMENTATION_ONE_ORDER_MANUAL_RUN_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_OWNER_RUN_ACTUAL_ONE_ORDER_COMMAND_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_RUNTIME_HTTP_TRANSPORT_ONE_ORDER_OWNER_RUN_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_FIRST_TRADE_ACTUAL_OWNER_COMMAND_RUN.md",
    "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_FINAL_OWNER_ORDER_COMMAND_REVIEW_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_OWNER_APPROVAL_EPIC_REPORT_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_TRADE_READINESS_EPIC_REPORT_V1.md",
)

CURRENT_REPO_SOURCE_FILES_MISSING = (
    "scripts/forex_delivery/run_oanda_demo_runtime_http_transport_one_order_v1.py",
)

EVIDENCE_LABELS = {
    "final_owner_runtime_run_present": "final owner runtime run evaluator/report present",
    "broker_call_implementation_present": "broker-call manual-run implementation present",
    "owner_actual_command_present": "owner actual one-order command package present",
    "runtime_http_transport_present": "runtime HTTP transport owner-run bridge present",
    "vault_backed_transport_present": "vault-backed one-order transport present",
    "owner_command_template_present": "owner command template/report present",
    "manual_execution_window_present": "manual execution window evidence present",
    "demo_endpoint_only_evidence_present": "demo endpoint only evidence present",
    "one_order_only_evidence_present": "one order only evidence present",
    "runtime_credentials_external_evidence_present": "runtime credentials external evidence present",
    "account_id_external_evidence_present": "account identifier external evidence present",
    "no_live_endpoint_evidence_present": "no live endpoint evidence present",
    "post_trade_evidence_plan_present": "post-trade evidence plan present",
    "owner_approval_gate_present": "owner approval gate present",
}


@dataclass(frozen=True)
class OandaDemoExecutionTruthAuditConfig:
    packet_id: str = (
        "AIOS-FOREX-OANDA-DEMO-EXECUTION-TRUTH-AUDIT-AND-"
        "PROFIT-PROOF-BRIDGE-EPIC-V1"
    )
    repo_path: str = "C:/Dev/Ai.Os"


@dataclass(frozen=True)
class OandaDemoExecutionTruthAuditInput:
    final_owner_runtime_run_present: bool
    broker_call_implementation_present: bool
    owner_actual_command_present: bool
    runtime_http_transport_present: bool
    vault_backed_transport_present: bool
    owner_command_template_present: bool
    manual_execution_window_present: bool
    demo_endpoint_only_evidence_present: bool
    one_order_only_evidence_present: bool
    runtime_credentials_external_evidence_present: bool
    account_id_external_evidence_present: bool
    no_live_endpoint_evidence_present: bool
    post_trade_evidence_plan_present: bool
    owner_approval_gate_present: bool
    source_files_read: tuple[str, ...] = field(default_factory=tuple)
    source_files_missing: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class OandaDemoExecutionTruthAuditResult:
    version: str
    packet_id: str
    classification: str
    demo_execution_distance_answer: str
    evidence_present: tuple[str, ...]
    evidence_missing: tuple[str, ...]
    evidence_map: Mapping[str, bool]
    exact_owner_run_surface: tuple[str, ...]
    exact_next_safe_action: str
    blocked_actions: tuple[str, ...]
    source_files_read: tuple[str, ...]
    source_files_missing: tuple[str, ...]
    permissions: Mapping[str, bool]
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool
    autonomous_execution_allowed: bool
    scheduler_allowed: bool
    daemon_allowed: bool
    webhook_allowed: bool


def build_sample_current_repo_execution_truth_input() -> OandaDemoExecutionTruthAuditInput:
    return OandaDemoExecutionTruthAuditInput(
        final_owner_runtime_run_present=True,
        broker_call_implementation_present=True,
        owner_actual_command_present=True,
        runtime_http_transport_present=True,
        vault_backed_transport_present=True,
        owner_command_template_present=True,
        manual_execution_window_present=True,
        demo_endpoint_only_evidence_present=True,
        one_order_only_evidence_present=True,
        runtime_credentials_external_evidence_present=True,
        account_id_external_evidence_present=True,
        no_live_endpoint_evidence_present=True,
        post_trade_evidence_plan_present=True,
        owner_approval_gate_present=True,
        source_files_read=CURRENT_REPO_SOURCE_FILES_PRESENT,
        source_files_missing=CURRENT_REPO_SOURCE_FILES_MISSING,
    )


def build_sample_blocked_missing_transport_input() -> OandaDemoExecutionTruthAuditInput:
    return OandaDemoExecutionTruthAuditInput(
        final_owner_runtime_run_present=True,
        broker_call_implementation_present=True,
        owner_actual_command_present=True,
        runtime_http_transport_present=False,
        vault_backed_transport_present=False,
        owner_command_template_present=True,
        manual_execution_window_present=True,
        demo_endpoint_only_evidence_present=True,
        one_order_only_evidence_present=True,
        runtime_credentials_external_evidence_present=True,
        account_id_external_evidence_present=True,
        no_live_endpoint_evidence_present=True,
        post_trade_evidence_plan_present=True,
        owner_approval_gate_present=True,
        source_files_read=tuple(
            path
            for path in CURRENT_REPO_SOURCE_FILES_PRESENT
            if "transport" not in path
        ),
        source_files_missing=(
            "automation/forex_engine/oanda_demo_runtime_http_transport_one_order_owner_run_v1.py",
            "automation/forex_engine/oanda_demo_vault_backed_one_order_transport_v1.py",
        ),
    )


def audit_oanda_demo_execution_truth(
    audit_input: OandaDemoExecutionTruthAuditInput | None = None,
    config: OandaDemoExecutionTruthAuditConfig | None = None,
) -> OandaDemoExecutionTruthAuditResult:
    active_input = audit_input or build_sample_current_repo_execution_truth_input()
    active_config = config or OandaDemoExecutionTruthAuditConfig()
    evidence_map = _evidence_map(active_input)
    classification = _classify_execution_path(active_input)
    permissions = dict(PROTECTED_PERMISSION_DEFAULTS)

    return OandaDemoExecutionTruthAuditResult(
        version=VERSION,
        packet_id=active_config.packet_id,
        classification=classification,
        demo_execution_distance_answer=_distance_answer(classification),
        evidence_present=_evidence_present(evidence_map),
        evidence_missing=_evidence_missing(evidence_map),
        evidence_map=evidence_map,
        exact_owner_run_surface=_owner_run_surface(active_input),
        exact_next_safe_action=_next_safe_action(classification),
        blocked_actions=_blocked_actions(),
        source_files_read=tuple(active_input.source_files_read),
        source_files_missing=tuple(active_input.source_files_missing),
        permissions=permissions,
        **permissions,
    )


def oanda_demo_execution_truth_to_jsonable_dict(
    result: OandaDemoExecutionTruthAuditResult,
) -> dict[str, Any]:
    return {
        "version": result.version,
        "packet_id": result.packet_id,
        "classification": result.classification,
        "demo_execution_distance_answer": result.demo_execution_distance_answer,
        "evidence_present": list(result.evidence_present),
        "evidence_missing": list(result.evidence_missing),
        "evidence_map": dict(result.evidence_map),
        "exact_owner_run_surface": list(result.exact_owner_run_surface),
        "exact_next_safe_action": result.exact_next_safe_action,
        "blocked_actions": list(result.blocked_actions),
        "source_files_read": list(result.source_files_read),
        "source_files_missing": list(result.source_files_missing),
        "permissions": dict(result.permissions),
        **dict(result.permissions),
        "no_trade_placed_by_this_packet": True,
        "no_broker_call_made_by_this_packet": True,
    }


def oanda_demo_execution_truth_to_operator_text(
    result: OandaDemoExecutionTruthAuditResult,
) -> str:
    return "\n".join(
        (
            REQUIRED_OPERATOR_SENTENCE,
            f"classification: {result.classification}",
            f"demo_execution_distance: {result.demo_execution_distance_answer}",
            f"next_safe_action: {result.exact_next_safe_action}",
            "no_trade_placed_by_this_packet: true",
            "no_broker_call_made_by_this_packet: true",
        )
    )


def oanda_demo_execution_truth_to_markdown(
    result: OandaDemoExecutionTruthAuditResult,
) -> str:
    lines = [
        "# AIOS Forex OANDA Demo Execution Truth Audit V1",
        "",
        "## Plain English Answer",
        REQUIRED_OPERATOR_SENTENCE,
        "",
        "## Classification",
        f"- `{result.classification}`",
        "",
        "## Demo Execution Distance",
        result.demo_execution_distance_answer,
        "",
        "## Exact Owner-Run Surface",
    ]
    lines.extend(f"- `{path}`" for path in result.exact_owner_run_surface)
    lines.extend(
        [
            "",
            "## Evidence Present",
            *[f"- {item}" for item in result.evidence_present],
            "",
            "## Evidence Missing",
            *([f"- {item}" for item in result.evidence_missing] or ["- none"]),
            "",
            "## Safety",
            "- No trade placed by this packet.",
            "- No broker call made by this packet.",
            "- All protected permission flags remain false.",
        ]
    )
    return "\n".join(lines) + "\n"


def _evidence_map(
    audit_input: OandaDemoExecutionTruthAuditInput,
) -> dict[str, bool]:
    return {field_name: bool(getattr(audit_input, field_name)) for field_name in EVIDENCE_LABELS}


def _evidence_present(evidence_map: Mapping[str, bool]) -> tuple[str, ...]:
    return tuple(EVIDENCE_LABELS[key] for key, value in evidence_map.items() if value)


def _evidence_missing(evidence_map: Mapping[str, bool]) -> tuple[str, ...]:
    return tuple(EVIDENCE_LABELS[key] for key, value in evidence_map.items() if not value)


def _classify_execution_path(audit_input: OandaDemoExecutionTruthAuditInput) -> str:
    transport_present = (
        audit_input.runtime_http_transport_present
        or audit_input.vault_backed_transport_present
    )
    command_present = (
        audit_input.owner_actual_command_present
        or audit_input.owner_command_template_present
    )
    if not audit_input.owner_approval_gate_present:
        return OANDA_DEMO_EXECUTION_PATH_BLOCKED_MISSING_OWNER_APPROVAL
    if command_present and not transport_present:
        return OANDA_DEMO_EXECUTION_PATH_BLOCKED_MISSING_TRANSPORT
    if (
        audit_input.final_owner_runtime_run_present
        and audit_input.broker_call_implementation_present
        and command_present
        and transport_present
        and audit_input.demo_endpoint_only_evidence_present
        and audit_input.one_order_only_evidence_present
    ):
        return OANDA_DEMO_EXECUTION_PATH_PRESENT_OWNER_MANUAL_RUN_REQUIRED
    if command_present:
        return OANDA_DEMO_EXECUTION_PATH_PARTIAL_COMMAND_ONLY
    return OANDA_DEMO_EXECUTION_PATH_UNKNOWN


def _distance_answer(classification: str) -> str:
    if classification == OANDA_DEMO_EXECUTION_PATH_PRESENT_OWNER_MANUAL_RUN_REQUIRED:
        return (
            "Demo execution is close: the repo contains the owner-run OANDA demo "
            "one-order path, but Anthony must run it manually outside Codex with "
            "runtime-only credentials and post-trade evidence capture ready."
        )
    if classification == OANDA_DEMO_EXECUTION_PATH_BLOCKED_MISSING_TRANSPORT:
        return "Demo execution is blocked because the owner-run transport layer is missing."
    if classification == OANDA_DEMO_EXECUTION_PATH_BLOCKED_MISSING_OWNER_APPROVAL:
        return "Demo execution is blocked because owner approval gating is missing."
    if classification == OANDA_DEMO_EXECUTION_PATH_PARTIAL_COMMAND_ONLY:
        return "Demo execution is partial: command scaffolding exists but not a complete owner-run path."
    return "Demo execution distance is unknown from the supplied evidence."


def _owner_run_surface(
    audit_input: OandaDemoExecutionTruthAuditInput,
) -> tuple[str, ...]:
    surfaces = []
    if audit_input.owner_actual_command_present:
        surfaces.append(
            "scripts/forex_delivery/run_oanda_demo_owner_run_actual_one_order_command_v1.py"
        )
    if audit_input.broker_call_implementation_present:
        surfaces.append(
            "scripts/forex_delivery/run_oanda_demo_broker_call_one_order_manual_run_v1.py"
        )
    if audit_input.runtime_http_transport_present:
        surfaces.append(
            "scripts/forex_delivery/run_oanda_demo_runtime_http_transport_one_order_owner_run_v1.py"
        )
    if audit_input.final_owner_runtime_run_present:
        surfaces.append(
            "scripts/forex_delivery/run_oanda_demo_final_owner_runtime_run_one_order_v1.py"
        )
    surfaces.append("OWNER MANUAL RUN ONLY; Codex must not execute it.")
    return tuple(surfaces)


def _next_safe_action(classification: str) -> str:
    if classification == OANDA_DEMO_EXECUTION_PATH_PRESENT_OWNER_MANUAL_RUN_REQUIRED:
        return (
            "Anthony may review the owner-run command surface manually; Codex must "
            "not call OANDA, supply credentials, or place the order."
        )
    if classification == OANDA_DEMO_EXECUTION_PATH_BLOCKED_MISSING_TRANSPORT:
        return "Build or restore the owner-run demo transport before any owner command review."
    if classification == OANDA_DEMO_EXECUTION_PATH_BLOCKED_MISSING_OWNER_APPROVAL:
        return "Build or restore the owner approval gate before any owner command review."
    return "Re-audit the owner command, transport, endpoint, and approval evidence."


def _blocked_actions() -> tuple[str, ...]:
    return (
        "codex_demo_order_execution",
        "broker_call_by_codex",
        "credential_or_account_identifier_access",
        "live_trading",
        "real_money",
        "compounding",
        "bank_movement",
        "autonomous_execution",
        "scheduler_or_daemon_or_webhook",
    )
