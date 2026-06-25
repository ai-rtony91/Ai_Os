from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from automation.forex_engine.oanda_demo_execution_truth_audit_v1 import (
    OandaDemoExecutionTruthAuditInput,
    OandaDemoExecutionTruthAuditResult,
    audit_oanda_demo_execution_truth,
    build_sample_blocked_missing_transport_input,
    build_sample_current_repo_execution_truth_input,
    oanda_demo_execution_truth_to_jsonable_dict,
    oanda_demo_execution_truth_to_operator_text,
)
from automation.forex_engine.oanda_demo_profit_proof_gap_bridge_v1 import (
    OandaDemoProfitProofGapBridgeInput,
    OandaDemoProfitProofGapBridgeResult,
    bridge_oanda_demo_profit_proof_gap,
    build_sample_blocked_no_result_input,
    build_sample_current_repo_profit_gap_input,
    oanda_demo_profit_proof_gap_to_jsonable_dict,
    oanda_demo_profit_proof_gap_to_operator_text,
)
from automation.forex_engine.oanda_demo_to_live_profit_readiness_truth_v1 import (
    OandaDemoToLiveProfitReadinessTruthInput,
    OandaDemoToLiveProfitReadinessTruthResult,
    build_sample_blocked_live_truth_input,
    build_sample_current_repo_live_profit_truth_input,
    evaluate_oanda_demo_to_live_profit_readiness_truth,
    oanda_demo_to_live_profit_readiness_truth_to_jsonable_dict,
    oanda_demo_to_live_profit_readiness_truth_to_operator_text,
)

VERSION = "oanda_demo_execution_truth_epic_v1"

EPIC_CLASSIFICATION = "OANDA_DEMO_EXECUTION_CLOSE_PROFIT_PROOF_AND_LIVE_BLOCKED"
REQUIRED_ONE_SENTENCE_ANSWER = (
    "AIOS is close to one owner-run OANDA demo order attempt, but live profitable "
    "execution is blocked until actual demo results, repeated profit proof, and "
    "the live evidence bundle are complete."
)
EXACT_NEXT_OWNER_ACTION = (
    "Review the existing filled demo result and, if Anthony chooses, run the "
    "read-only filled-trade P/L capture path manually; Codex must not call OANDA "
    "or place another order."
)
EXACT_NEXT_CODEX_PACKET = (
    "AIOS-FOREX-OANDA-DEMO-READ-ONLY-PL-CAPTURE-RESULT-INTAKE-AND-"
    "PROFIT-PROOF-LEDGER-BRIDGE-V1"
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


@dataclass(frozen=True)
class OandaDemoExecutionTruthEpicConfig:
    packet_id: str = (
        "AIOS-FOREX-OANDA-DEMO-EXECUTION-TRUTH-AUDIT-AND-"
        "PROFIT-PROOF-BRIDGE-EPIC-V1"
    )


@dataclass(frozen=True)
class OandaDemoExecutionTruthEpicInput:
    execution_truth_input: OandaDemoExecutionTruthAuditInput
    profit_gap_input: OandaDemoProfitProofGapBridgeInput
    live_profit_truth_input: OandaDemoToLiveProfitReadinessTruthInput


@dataclass(frozen=True)
class OandaDemoExecutionTruthEpicResult:
    version: str
    packet_id: str
    classification: str
    demo_execution_distance_classification: str
    profit_proof_classification: str
    live_profit_readiness_classification: str
    one_sentence_answer: str
    demo_execution_answer: str
    profit_proof_answer: str
    live_profit_answer: str
    exact_next_owner_action: str
    exact_next_codex_packet: str
    evidence_present: tuple[str, ...]
    evidence_missing: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    execution_truth: OandaDemoExecutionTruthAuditResult
    profit_gap: OandaDemoProfitProofGapBridgeResult
    live_truth: OandaDemoToLiveProfitReadinessTruthResult
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


def build_sample_oanda_demo_execution_truth_epic_current_repo_input() -> OandaDemoExecutionTruthEpicInput:
    return OandaDemoExecutionTruthEpicInput(
        execution_truth_input=build_sample_current_repo_execution_truth_input(),
        profit_gap_input=build_sample_current_repo_profit_gap_input(),
        live_profit_truth_input=build_sample_current_repo_live_profit_truth_input(),
    )


def build_sample_oanda_demo_execution_truth_epic_blocked_input() -> OandaDemoExecutionTruthEpicInput:
    return OandaDemoExecutionTruthEpicInput(
        execution_truth_input=build_sample_blocked_missing_transport_input(),
        profit_gap_input=build_sample_blocked_no_result_input(),
        live_profit_truth_input=build_sample_blocked_live_truth_input(),
    )


def run_oanda_demo_execution_truth_epic(
    epic_input: OandaDemoExecutionTruthEpicInput | None = None,
    config: OandaDemoExecutionTruthEpicConfig | None = None,
) -> OandaDemoExecutionTruthEpicResult:
    active_input = epic_input or build_sample_oanda_demo_execution_truth_epic_current_repo_input()
    active_config = config or OandaDemoExecutionTruthEpicConfig()

    execution_truth = audit_oanda_demo_execution_truth(active_input.execution_truth_input)
    profit_gap = bridge_oanda_demo_profit_proof_gap(active_input.profit_gap_input)
    live_truth = evaluate_oanda_demo_to_live_profit_readiness_truth(
        active_input.live_profit_truth_input
    )
    permissions = dict(PROTECTED_PERMISSION_DEFAULTS)

    return OandaDemoExecutionTruthEpicResult(
        version=VERSION,
        packet_id=active_config.packet_id,
        classification=EPIC_CLASSIFICATION,
        demo_execution_distance_classification=execution_truth.classification,
        profit_proof_classification=profit_gap.classification,
        live_profit_readiness_classification=live_truth.classification,
        one_sentence_answer=REQUIRED_ONE_SENTENCE_ANSWER,
        demo_execution_answer=oanda_demo_execution_truth_to_operator_text(execution_truth).splitlines()[0],
        profit_proof_answer=profit_gap.profit_proof_answer,
        live_profit_answer=live_truth.live_profit_distance_answer,
        exact_next_owner_action=EXACT_NEXT_OWNER_ACTION,
        exact_next_codex_packet=EXACT_NEXT_CODEX_PACKET,
        evidence_present=_merge_evidence_present(execution_truth, profit_gap, live_truth),
        evidence_missing=_merge_evidence_missing(execution_truth, profit_gap, live_truth),
        blocked_actions=_blocked_actions(),
        execution_truth=execution_truth,
        profit_gap=profit_gap,
        live_truth=live_truth,
        permissions=permissions,
        **permissions,
    )


def oanda_demo_execution_truth_epic_to_jsonable_dict(
    result: OandaDemoExecutionTruthEpicResult,
) -> dict[str, Any]:
    return {
        "version": result.version,
        "packet_id": result.packet_id,
        "classification": result.classification,
        "demo_execution_distance_classification": result.demo_execution_distance_classification,
        "profit_proof_classification": result.profit_proof_classification,
        "live_profit_readiness_classification": result.live_profit_readiness_classification,
        "one_sentence_answer": result.one_sentence_answer,
        "demo_execution_answer": result.demo_execution_answer,
        "profit_proof_answer": result.profit_proof_answer,
        "live_profit_answer": result.live_profit_answer,
        "exact_next_owner_action": result.exact_next_owner_action,
        "exact_next_codex_packet": result.exact_next_codex_packet,
        "evidence_present": list(result.evidence_present),
        "evidence_missing": list(result.evidence_missing),
        "blocked_actions": list(result.blocked_actions),
        "execution_truth": oanda_demo_execution_truth_to_jsonable_dict(result.execution_truth),
        "profit_gap": oanda_demo_profit_proof_gap_to_jsonable_dict(result.profit_gap),
        "live_truth": oanda_demo_to_live_profit_readiness_truth_to_jsonable_dict(
            result.live_truth
        ),
        "permissions": dict(result.permissions),
        **dict(result.permissions),
        "no_trade_placed_by_this_packet": True,
        "no_broker_call_made_by_this_packet": True,
    }


def oanda_demo_execution_truth_epic_to_operator_text(
    result: OandaDemoExecutionTruthEpicResult,
) -> str:
    return "\n".join(
        (
            result.one_sentence_answer,
            f"demo_execution_classification: {result.demo_execution_distance_classification}",
            f"profit_proof_classification: {result.profit_proof_classification}",
            f"live_profit_readiness_classification: {result.live_profit_readiness_classification}",
            f"exact_next_owner_action: {result.exact_next_owner_action}",
            f"exact_next_codex_packet: {result.exact_next_codex_packet}",
            "no_trade_placed_by_this_packet: true",
            "no_broker_call_made_by_this_packet: true",
        )
    )


def oanda_demo_execution_truth_epic_to_markdown(
    result: OandaDemoExecutionTruthEpicResult,
) -> str:
    lines = [
        "# AIOS Forex OANDA Demo Execution Truth Epic Report V1",
        "",
        "## One Sentence Answer",
        result.one_sentence_answer,
        "",
        "## Classifications",
        f"- Demo execution: `{result.demo_execution_distance_classification}`",
        f"- Profit proof: `{result.profit_proof_classification}`",
        f"- Live profit readiness: `{result.live_profit_readiness_classification}`",
        "",
        "## Answers",
        f"- Demo execution: {result.demo_execution_answer}",
        f"- Profit proof: {result.profit_proof_answer}",
        f"- Live profit: {result.live_profit_answer}",
        "",
        "## Exact Next Actions",
        f"- Owner: {result.exact_next_owner_action}",
        f"- Codex packet: `{result.exact_next_codex_packet}`",
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


def _merge_evidence_present(
    execution_truth: OandaDemoExecutionTruthAuditResult,
    profit_gap: OandaDemoProfitProofGapBridgeResult,
    live_truth: OandaDemoToLiveProfitReadinessTruthResult,
) -> tuple[str, ...]:
    return tuple(
        [f"execution: {item}" for item in execution_truth.evidence_present]
        + [f"profit: {item}" for item in profit_gap.evidence_present]
        + [f"live: {item}" for item in live_truth.evidence_present]
    )


def _merge_evidence_missing(
    execution_truth: OandaDemoExecutionTruthAuditResult,
    profit_gap: OandaDemoProfitProofGapBridgeResult,
    live_truth: OandaDemoToLiveProfitReadinessTruthResult,
) -> tuple[str, ...]:
    return tuple(
        [f"execution: {item}" for item in execution_truth.evidence_missing]
        + [f"profit: {item}" for item in profit_gap.evidence_missing]
        + [f"live: {item}" for item in live_truth.evidence_missing]
    )


def _blocked_actions() -> tuple[str, ...]:
    return (
        "codex_demo_order_execution",
        "broker_call_by_codex",
        "profit_claim_without_reconciled_demo_pl",
        "live_profitable_execution_claim",
        "live_trading",
        "real_money",
        "compounding",
        "bank_movement",
        "credential_or_account_identifier_access",
        "scheduler_or_daemon_or_webhook",
        "commit_push_pr_merge",
    )
