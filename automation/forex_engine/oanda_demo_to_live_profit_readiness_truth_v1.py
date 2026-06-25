from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Mapping

VERSION = "oanda_demo_to_live_profit_readiness_truth_v1"

LIVE_PROFITABLE_EXECUTION_BLOCKED_NO_LIVE_EVIDENCE_BUNDLE = (
    "LIVE_PROFITABLE_EXECUTION_BLOCKED_NO_LIVE_EVIDENCE_BUNDLE"
)
LIVE_PROFITABLE_EXECUTION_BLOCKED_NO_REPEATED_DEMO_PROFIT_PROOF = (
    "LIVE_PROFITABLE_EXECUTION_BLOCKED_NO_REPEATED_DEMO_PROFIT_PROOF"
)
LIVE_PROFITABLE_EXECUTION_BLOCKED_NO_LIVE_MICRO_EXCEPTION = (
    "LIVE_PROFITABLE_EXECUTION_BLOCKED_NO_LIVE_MICRO_EXCEPTION"
)
LIVE_PROFITABLE_EXECUTION_REVIEW_READY_NOT_EXECUTION_READY = (
    "LIVE_PROFITABLE_EXECUTION_REVIEW_READY_NOT_EXECUTION_READY"
)
LIVE_PROFITABLE_EXECUTION_UNKNOWN = "LIVE_PROFITABLE_EXECUTION_UNKNOWN"

REQUIRED_OPERATOR_SENTENCE = (
    "Live profitable execution is blocked until repeated demo profit proof "
    "and the live evidence bundle exist."
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
    "RISK_POLICY.md",
    "Reports/forex_delivery/AIOS_FOREX_FIRST_LIVE_MICRO_TRADE_EXECUTION_PATH_V2.md",
    "Reports/forex_delivery/AIOS_FOREX_LIVE_ARMING_EVIDENCE_GAP_DRY_RUN_V1_REPORT.md",
    "docs/forex/SINGLE_LIVE_MICRO_TRADE_EXCEPTION_CHECKLIST_TEMPLATE.md",
    "docs/forex/LIVE_ARMING_EVIDENCE_BUNDLE_TEMPLATE.md",
)

EVIDENCE_LABELS = {
    "live_micro_trade_execution_path_report_present": "live micro-trade execution path report present",
    "risk_policy_present": "RISK_POLICY.md present",
    "single_live_micro_trade_exception_template_present": "single live micro-trade exception template present",
    "live_arming_evidence_bundle_template_present": "live arming evidence bundle template present",
    "live_arming_gap_report_present": "live arming evidence gap report present",
    "completed_live_evidence_bundle_present": "completed live evidence bundle present",
    "human_owner_live_exception_present": "Human Owner live exception approval present",
    "external_credential_boundary_proof_present": "external credential-boundary proof present",
    "external_account_boundary_proof_present": "external account-boundary proof present",
    "demo_practice_broker_proof_present": "demo/practice broker proof present",
    "live_endpoint_denial_proof_present": "live endpoint denial proof present",
    "kill_switch_proof_present": "kill-switch proof present",
    "timeout_proof_present": "timeout proof present",
    "rollback_proof_present": "rollback proof present",
    "final_disarm_proof_present": "final disarm proof present",
    "post_trade_journal_proof_present": "post-trade journal proof present",
    "reconciliation_proof_present": "reconciliation proof present",
    "repeated_demo_profit_proof_present": "repeated demo profit proof present",
}


@dataclass(frozen=True)
class OandaDemoToLiveProfitReadinessTruthConfig:
    packet_id: str = (
        "AIOS-FOREX-OANDA-DEMO-EXECUTION-TRUTH-AUDIT-AND-"
        "PROFIT-PROOF-BRIDGE-EPIC-V1"
    )
    minimum_repeated_demo_profit_proof_count: int = 3
    maximum_live_readiness_score_without_bundle: Decimal = Decimal("0")


@dataclass(frozen=True)
class OandaDemoToLiveProfitReadinessTruthInput:
    live_micro_trade_execution_path_report_present: bool
    risk_policy_present: bool
    single_live_micro_trade_exception_template_present: bool
    live_arming_evidence_bundle_template_present: bool
    live_arming_gap_report_present: bool
    completed_live_evidence_bundle_present: bool
    human_owner_live_exception_present: bool
    external_credential_boundary_proof_present: bool
    external_account_boundary_proof_present: bool
    demo_practice_broker_proof_present: bool
    live_endpoint_denial_proof_present: bool
    kill_switch_proof_present: bool
    timeout_proof_present: bool
    rollback_proof_present: bool
    final_disarm_proof_present: bool
    post_trade_journal_proof_present: bool
    reconciliation_proof_present: bool
    repeated_demo_profit_proof_present: bool
    source_files_read: tuple[str, ...] = field(default_factory=tuple)
    source_files_missing: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class OandaDemoToLiveProfitReadinessTruthResult:
    version: str
    packet_id: str
    classification: str
    live_profit_distance_answer: str
    live_blockers: tuple[str, ...]
    evidence_present: tuple[str, ...]
    evidence_missing: tuple[str, ...]
    evidence_map: Mapping[str, bool]
    exact_next_live_blocker_to_build: str
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


def build_sample_current_repo_live_profit_truth_input() -> OandaDemoToLiveProfitReadinessTruthInput:
    return OandaDemoToLiveProfitReadinessTruthInput(
        live_micro_trade_execution_path_report_present=True,
        risk_policy_present=True,
        single_live_micro_trade_exception_template_present=True,
        live_arming_evidence_bundle_template_present=True,
        live_arming_gap_report_present=True,
        completed_live_evidence_bundle_present=False,
        human_owner_live_exception_present=False,
        external_credential_boundary_proof_present=False,
        external_account_boundary_proof_present=False,
        demo_practice_broker_proof_present=True,
        live_endpoint_denial_proof_present=False,
        kill_switch_proof_present=False,
        timeout_proof_present=False,
        rollback_proof_present=False,
        final_disarm_proof_present=False,
        post_trade_journal_proof_present=False,
        reconciliation_proof_present=False,
        repeated_demo_profit_proof_present=False,
        source_files_read=CURRENT_REPO_SOURCE_FILES_PRESENT,
        source_files_missing=tuple(),
    )


def build_sample_blocked_live_truth_input() -> OandaDemoToLiveProfitReadinessTruthInput:
    return OandaDemoToLiveProfitReadinessTruthInput(
        live_micro_trade_execution_path_report_present=False,
        risk_policy_present=True,
        single_live_micro_trade_exception_template_present=False,
        live_arming_evidence_bundle_template_present=False,
        live_arming_gap_report_present=False,
        completed_live_evidence_bundle_present=False,
        human_owner_live_exception_present=False,
        external_credential_boundary_proof_present=False,
        external_account_boundary_proof_present=False,
        demo_practice_broker_proof_present=False,
        live_endpoint_denial_proof_present=False,
        kill_switch_proof_present=False,
        timeout_proof_present=False,
        rollback_proof_present=False,
        final_disarm_proof_present=False,
        post_trade_journal_proof_present=False,
        reconciliation_proof_present=False,
        repeated_demo_profit_proof_present=False,
        source_files_read=("RISK_POLICY.md",),
        source_files_missing=(
            "Reports/forex_delivery/AIOS_FOREX_FIRST_LIVE_MICRO_TRADE_EXECUTION_PATH_V2.md",
            "docs/forex/LIVE_ARMING_EVIDENCE_BUNDLE_TEMPLATE.md",
        ),
    )


def evaluate_oanda_demo_to_live_profit_readiness_truth(
    truth_input: OandaDemoToLiveProfitReadinessTruthInput | None = None,
    config: OandaDemoToLiveProfitReadinessTruthConfig | None = None,
) -> OandaDemoToLiveProfitReadinessTruthResult:
    active_input = truth_input or build_sample_current_repo_live_profit_truth_input()
    active_config = config or OandaDemoToLiveProfitReadinessTruthConfig()
    evidence_map = _evidence_map(active_input)
    classification = _classify_live_truth(active_input)
    permissions = dict(PROTECTED_PERMISSION_DEFAULTS)

    return OandaDemoToLiveProfitReadinessTruthResult(
        version=VERSION,
        packet_id=active_config.packet_id,
        classification=classification,
        live_profit_distance_answer=REQUIRED_OPERATOR_SENTENCE,
        live_blockers=_live_blockers(active_input, active_config),
        evidence_present=_evidence_present(evidence_map),
        evidence_missing=_evidence_missing(evidence_map),
        evidence_map=evidence_map,
        exact_next_live_blocker_to_build=_next_live_blocker(active_input),
        source_files_read=tuple(active_input.source_files_read),
        source_files_missing=tuple(active_input.source_files_missing),
        permissions=permissions,
        **permissions,
    )


def oanda_demo_to_live_profit_readiness_truth_to_jsonable_dict(
    result: OandaDemoToLiveProfitReadinessTruthResult,
) -> dict[str, Any]:
    return {
        "version": result.version,
        "packet_id": result.packet_id,
        "classification": result.classification,
        "live_profit_distance_answer": result.live_profit_distance_answer,
        "live_blockers": list(result.live_blockers),
        "evidence_present": list(result.evidence_present),
        "evidence_missing": list(result.evidence_missing),
        "evidence_map": dict(result.evidence_map),
        "exact_next_live_blocker_to_build": result.exact_next_live_blocker_to_build,
        "source_files_read": list(result.source_files_read),
        "source_files_missing": list(result.source_files_missing),
        "permissions": dict(result.permissions),
        **dict(result.permissions),
        "no_trade_placed_by_this_packet": True,
        "no_broker_call_made_by_this_packet": True,
    }


def oanda_demo_to_live_profit_readiness_truth_to_operator_text(
    result: OandaDemoToLiveProfitReadinessTruthResult,
) -> str:
    return "\n".join(
        (
            REQUIRED_OPERATOR_SENTENCE,
            f"classification: {result.classification}",
            f"next_live_blocker: {result.exact_next_live_blocker_to_build}",
            "no_trade_placed_by_this_packet: true",
            "no_broker_call_made_by_this_packet: true",
        )
    )


def oanda_demo_to_live_profit_readiness_truth_to_markdown(
    result: OandaDemoToLiveProfitReadinessTruthResult,
) -> str:
    lines = [
        "# AIOS Forex OANDA Demo To Live Profit Readiness Truth V1",
        "",
        "## Plain English Answer",
        result.live_profit_distance_answer,
        "",
        "## Classification",
        f"- `{result.classification}`",
        "",
        "## Live Blockers",
        *[f"- {item}" for item in result.live_blockers],
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
    return "\n".join(lines) + "\n"


def _evidence_map(
    truth_input: OandaDemoToLiveProfitReadinessTruthInput,
) -> dict[str, bool]:
    return {field_name: bool(getattr(truth_input, field_name)) for field_name in EVIDENCE_LABELS}


def _evidence_present(evidence_map: Mapping[str, bool]) -> tuple[str, ...]:
    return tuple(EVIDENCE_LABELS[key] for key, value in evidence_map.items() if value)


def _evidence_missing(evidence_map: Mapping[str, bool]) -> tuple[str, ...]:
    return tuple(EVIDENCE_LABELS[key] for key, value in evidence_map.items() if not value)


def _classify_live_truth(truth_input: OandaDemoToLiveProfitReadinessTruthInput) -> str:
    if not truth_input.completed_live_evidence_bundle_present:
        return LIVE_PROFITABLE_EXECUTION_BLOCKED_NO_LIVE_EVIDENCE_BUNDLE
    if not truth_input.repeated_demo_profit_proof_present:
        return LIVE_PROFITABLE_EXECUTION_BLOCKED_NO_REPEATED_DEMO_PROFIT_PROOF
    if not truth_input.human_owner_live_exception_present:
        return LIVE_PROFITABLE_EXECUTION_BLOCKED_NO_LIVE_MICRO_EXCEPTION
    if truth_input.risk_policy_present:
        return LIVE_PROFITABLE_EXECUTION_REVIEW_READY_NOT_EXECUTION_READY
    return LIVE_PROFITABLE_EXECUTION_UNKNOWN


def _live_blockers(
    truth_input: OandaDemoToLiveProfitReadinessTruthInput,
    config: OandaDemoToLiveProfitReadinessTruthConfig,
) -> tuple[str, ...]:
    blockers = []
    if not truth_input.completed_live_evidence_bundle_present:
        blockers.append("completed_live_evidence_bundle_missing")
    if not truth_input.repeated_demo_profit_proof_present:
        blockers.append(
            "repeated_demo_profit_proof_missing:"
            f"minimum_{config.minimum_repeated_demo_profit_proof_count}_reconciled_results"
        )
    if not truth_input.human_owner_live_exception_present:
        blockers.append("human_owner_live_exception_missing")
    for field_name in (
        "external_credential_boundary_proof_present",
        "external_account_boundary_proof_present",
        "live_endpoint_denial_proof_present",
        "kill_switch_proof_present",
        "timeout_proof_present",
        "rollback_proof_present",
        "final_disarm_proof_present",
        "post_trade_journal_proof_present",
        "reconciliation_proof_present",
    ):
        if not getattr(truth_input, field_name):
            blockers.append(field_name.replace("_present", "_missing"))
    return tuple(blockers)


def _next_live_blocker(truth_input: OandaDemoToLiveProfitReadinessTruthInput) -> str:
    if not truth_input.completed_live_evidence_bundle_present:
        return (
            "Build a sanitized live evidence-bundle completeness review; do not "
            "request credentials, broker calls, account identifiers, or live order authority."
        )
    if not truth_input.repeated_demo_profit_proof_present:
        return "Complete repeated reconciled demo profit proof before live review."
    if not truth_input.human_owner_live_exception_present:
        return "Human Owner must explicitly approve a one-shot live micro exception before review."
    return "Review only; live execution remains blocked without a separate final arming packet."
