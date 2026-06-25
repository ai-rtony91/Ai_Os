from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Mapping

VERSION = "oanda_demo_profit_proof_gap_bridge_v1"

OANDA_DEMO_PROFIT_PROOF_READY_FOR_FIRST_RESULT_CAPTURE = (
    "OANDA_DEMO_PROFIT_PROOF_READY_FOR_FIRST_RESULT_CAPTURE"
)
OANDA_DEMO_PROFIT_PROOF_BLOCKED_NO_ACTUAL_DEMO_RESULT = (
    "OANDA_DEMO_PROFIT_PROOF_BLOCKED_NO_ACTUAL_DEMO_RESULT"
)
OANDA_DEMO_PROFIT_PROOF_BLOCKED_NO_POST_TRADE_EVIDENCE = (
    "OANDA_DEMO_PROFIT_PROOF_BLOCKED_NO_POST_TRADE_EVIDENCE"
)
OANDA_DEMO_PROFIT_PROOF_BLOCKED_NO_EXPECTANCY_SAMPLE = (
    "OANDA_DEMO_PROFIT_PROOF_BLOCKED_NO_EXPECTANCY_SAMPLE"
)
OANDA_DEMO_PROFIT_PROOF_UNKNOWN = "OANDA_DEMO_PROFIT_PROOF_UNKNOWN"

REQUIRED_OPERATOR_SENTENCE = (
    "Profit cannot be claimed until an actual demo result is captured, "
    "reconciled, and added to proof/evidence depth."
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
    "automation/forex_engine/oanda_demo_post_trade_evidence_capture_v1.py",
    "automation/forex_engine/oanda_demo_micro_trade_owner_approval_evidence_capture_v1.py",
    "automation/forex_engine/oanda_demo_read_only_filled_trade_pl_capture_v1.py",
    "automation/forex_engine/profit_proof_ledger_v1.py",
    "automation/forex_engine/strategy_proof_engine_v1.py",
    "automation/forex_engine/expectancy_strength_router_v1.py",
    "automation/forex_engine/real_evidence_depth_engine_v1.py",
    "automation/forex_engine/profit_validation_loop_v1.py",
    "automation/forex_engine/oanda_demo_result_to_bucket_and_next_allocation_v1.py",
    "scripts/forex_delivery/run_oanda_demo_result_to_bucket_and_next_allocation_v1.py",
    "scripts/forex_delivery/run_oanda_demo_read_only_filled_trade_pl_capture_v1.py",
    "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_POST_TRADE_EVIDENCE_CAPTURE_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_POST_TRADE_EVIDENCE_CAPTURE_OWNER_RUN_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_MICRO_TRADE_OWNER_APPROVAL_EVIDENCE_CAPTURE_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_READ_ONLY_FILLED_TRADE_PL_CAPTURE_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_RESULT_TO_BUCKET_AND_NEXT_ALLOCATION_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_PROFIT_PROOF_LEDGER_V1_REPORT.md",
)

EVIDENCE_LABELS = {
    "post_trade_evidence_capture_present": "post-trade evidence capture tooling present",
    "owner_run_post_trade_capture_present": "owner-run post-trade capture report present",
    "filled_trade_pl_capture_present": "read-only filled-trade P/L capture tooling/report present",
    "result_to_bucket_allocation_present": "result-to-bucket allocation bridge present",
    "profit_proof_ledger_present": "profit proof ledger present",
    "strategy_proof_engine_present": "strategy proof engine present",
    "expectancy_strength_router_present": "expectancy strength router present",
    "real_evidence_depth_engine_present": "real evidence depth engine present",
    "actual_demo_trade_result_present": "actual filled demo result reference present",
    "reconciled_demo_pl_present": "reconciled demo P/L present",
    "repeated_profitable_sample_present": "repeated profitable demo sample present",
}


@dataclass(frozen=True)
class OandaDemoProfitProofGapBridgeConfig:
    packet_id: str = (
        "AIOS-FOREX-OANDA-DEMO-EXECUTION-TRUTH-AUDIT-AND-"
        "PROFIT-PROOF-BRIDGE-EPIC-V1"
    )
    minimum_repeated_sample_count: int = 3
    minimum_profit_factor: Decimal = Decimal("1.25")


@dataclass(frozen=True)
class OandaDemoProfitProofGapBridgeInput:
    post_trade_evidence_capture_present: bool
    owner_run_post_trade_capture_present: bool
    filled_trade_pl_capture_present: bool
    result_to_bucket_allocation_present: bool
    profit_proof_ledger_present: bool
    strategy_proof_engine_present: bool
    expectancy_strength_router_present: bool
    real_evidence_depth_engine_present: bool
    actual_demo_trade_result_present: bool
    reconciled_demo_pl_present: bool
    repeated_profitable_sample_present: bool
    source_files_read: tuple[str, ...] = field(default_factory=tuple)
    source_files_missing: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class OandaDemoProfitProofGapBridgeResult:
    version: str
    packet_id: str
    classification: str
    profit_proof_answer: str
    evidence_present: tuple[str, ...]
    evidence_missing: tuple[str, ...]
    evidence_map: Mapping[str, bool]
    minimum_next_profit_proof_step: str
    post_trade_evidence_required: tuple[str, ...]
    repeated_sample_required: str
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


def build_sample_current_repo_profit_gap_input() -> OandaDemoProfitProofGapBridgeInput:
    return OandaDemoProfitProofGapBridgeInput(
        post_trade_evidence_capture_present=True,
        owner_run_post_trade_capture_present=True,
        filled_trade_pl_capture_present=True,
        result_to_bucket_allocation_present=True,
        profit_proof_ledger_present=True,
        strategy_proof_engine_present=True,
        expectancy_strength_router_present=True,
        real_evidence_depth_engine_present=True,
        actual_demo_trade_result_present=True,
        reconciled_demo_pl_present=False,
        repeated_profitable_sample_present=False,
        source_files_read=CURRENT_REPO_SOURCE_FILES_PRESENT,
        source_files_missing=tuple(),
    )


def build_sample_blocked_no_result_input() -> OandaDemoProfitProofGapBridgeInput:
    return OandaDemoProfitProofGapBridgeInput(
        post_trade_evidence_capture_present=True,
        owner_run_post_trade_capture_present=True,
        filled_trade_pl_capture_present=True,
        result_to_bucket_allocation_present=True,
        profit_proof_ledger_present=True,
        strategy_proof_engine_present=True,
        expectancy_strength_router_present=True,
        real_evidence_depth_engine_present=True,
        actual_demo_trade_result_present=False,
        reconciled_demo_pl_present=False,
        repeated_profitable_sample_present=False,
        source_files_read=CURRENT_REPO_SOURCE_FILES_PRESENT,
        source_files_missing=tuple(),
    )


def bridge_oanda_demo_profit_proof_gap(
    proof_input: OandaDemoProfitProofGapBridgeInput | None = None,
    config: OandaDemoProfitProofGapBridgeConfig | None = None,
) -> OandaDemoProfitProofGapBridgeResult:
    active_input = proof_input or build_sample_current_repo_profit_gap_input()
    active_config = config or OandaDemoProfitProofGapBridgeConfig()
    evidence_map = _evidence_map(active_input)
    classification = _classify_profit_gap(active_input)
    permissions = dict(PROTECTED_PERMISSION_DEFAULTS)

    return OandaDemoProfitProofGapBridgeResult(
        version=VERSION,
        packet_id=active_config.packet_id,
        classification=classification,
        profit_proof_answer=REQUIRED_OPERATOR_SENTENCE,
        evidence_present=_evidence_present(evidence_map),
        evidence_missing=_evidence_missing(evidence_map),
        evidence_map=evidence_map,
        minimum_next_profit_proof_step=_minimum_next_step(active_input),
        post_trade_evidence_required=_post_trade_evidence_required(),
        repeated_sample_required=(
            f"At least {active_config.minimum_repeated_sample_count} reconciled demo "
            f"results with proof depth and profit-factor review; current repeated "
            "profitable sample evidence is absent."
        ),
        source_files_read=tuple(active_input.source_files_read),
        source_files_missing=tuple(active_input.source_files_missing),
        permissions=permissions,
        **permissions,
    )


def oanda_demo_profit_proof_gap_to_jsonable_dict(
    result: OandaDemoProfitProofGapBridgeResult,
) -> dict[str, Any]:
    return {
        "version": result.version,
        "packet_id": result.packet_id,
        "classification": result.classification,
        "profit_proof_answer": result.profit_proof_answer,
        "evidence_present": list(result.evidence_present),
        "evidence_missing": list(result.evidence_missing),
        "evidence_map": dict(result.evidence_map),
        "minimum_next_profit_proof_step": result.minimum_next_profit_proof_step,
        "post_trade_evidence_required": list(result.post_trade_evidence_required),
        "repeated_sample_required": result.repeated_sample_required,
        "source_files_read": list(result.source_files_read),
        "source_files_missing": list(result.source_files_missing),
        "permissions": dict(result.permissions),
        **dict(result.permissions),
        "no_trade_placed_by_this_packet": True,
        "no_broker_call_made_by_this_packet": True,
    }


def oanda_demo_profit_proof_gap_to_operator_text(
    result: OandaDemoProfitProofGapBridgeResult,
) -> str:
    return "\n".join(
        (
            REQUIRED_OPERATOR_SENTENCE,
            f"classification: {result.classification}",
            f"minimum_next_profit_proof_step: {result.minimum_next_profit_proof_step}",
            "no_trade_placed_by_this_packet: true",
            "no_broker_call_made_by_this_packet: true",
        )
    )


def oanda_demo_profit_proof_gap_to_markdown(
    result: OandaDemoProfitProofGapBridgeResult,
) -> str:
    lines = [
        "# AIOS Forex OANDA Demo Profit Proof Gap Bridge V1",
        "",
        "## Plain English Answer",
        result.profit_proof_answer,
        "",
        "## Classification",
        f"- `{result.classification}`",
        "",
        "## Minimum Next Profit Proof Step",
        result.minimum_next_profit_proof_step,
        "",
        "## Evidence Present",
        *[f"- {item}" for item in result.evidence_present],
        "",
        "## Evidence Missing",
        *([f"- {item}" for item in result.evidence_missing] or ["- none"]),
        "",
        "## Required Evidence Before Profit Claim",
        *[f"- {item}" for item in result.post_trade_evidence_required],
        "",
        "## Safety",
        "- No trade placed by this packet.",
        "- No broker call made by this packet.",
        "- All protected permission flags remain false.",
    ]
    return "\n".join(lines) + "\n"


def _evidence_map(
    proof_input: OandaDemoProfitProofGapBridgeInput,
) -> dict[str, bool]:
    return {field_name: bool(getattr(proof_input, field_name)) for field_name in EVIDENCE_LABELS}


def _evidence_present(evidence_map: Mapping[str, bool]) -> tuple[str, ...]:
    return tuple(EVIDENCE_LABELS[key] for key, value in evidence_map.items() if value)


def _evidence_missing(evidence_map: Mapping[str, bool]) -> tuple[str, ...]:
    return tuple(EVIDENCE_LABELS[key] for key, value in evidence_map.items() if not value)


def _classify_profit_gap(proof_input: OandaDemoProfitProofGapBridgeInput) -> str:
    post_trade_stack_present = (
        proof_input.post_trade_evidence_capture_present
        and proof_input.owner_run_post_trade_capture_present
        and proof_input.filled_trade_pl_capture_present
    )
    proof_stack_present = (
        proof_input.profit_proof_ledger_present
        and proof_input.strategy_proof_engine_present
        and proof_input.expectancy_strength_router_present
        and proof_input.real_evidence_depth_engine_present
    )
    if not proof_input.actual_demo_trade_result_present:
        return OANDA_DEMO_PROFIT_PROOF_BLOCKED_NO_ACTUAL_DEMO_RESULT
    if not post_trade_stack_present:
        return OANDA_DEMO_PROFIT_PROOF_BLOCKED_NO_POST_TRADE_EVIDENCE
    if (
        not proof_stack_present
        or not proof_input.reconciled_demo_pl_present
        or not proof_input.repeated_profitable_sample_present
    ):
        return OANDA_DEMO_PROFIT_PROOF_BLOCKED_NO_EXPECTANCY_SAMPLE
    if proof_stack_present and post_trade_stack_present:
        return OANDA_DEMO_PROFIT_PROOF_READY_FOR_FIRST_RESULT_CAPTURE
    return OANDA_DEMO_PROFIT_PROOF_UNKNOWN


def _minimum_next_step(proof_input: OandaDemoProfitProofGapBridgeInput) -> str:
    if not proof_input.actual_demo_trade_result_present:
        return (
            "Capture one sanitized actual OANDA demo result after an owner-run attempt; "
            "Codex must not call the broker."
        )
    if not proof_input.reconciled_demo_pl_present:
        return (
            "Anthony should review or run the read-only filled-trade P/L capture path "
            "for the existing filled demo result, then provide sanitized reconciled "
            "P/L evidence for ledger intake."
        )
    if not proof_input.repeated_profitable_sample_present:
        return (
            "Collect repeated reconciled demo results before any profitable execution "
            "or live-readiness claim."
        )
    return "Submit the reconciled result set for owner review; this still does not approve live trading."


def _post_trade_evidence_required() -> tuple[str, ...]:
    return (
        "sanitized actual demo order/result reference",
        "read-only filled-trade P/L capture output",
        "reconciled realized or open/unrealized P/L classification",
        "profit proof ledger entry",
        "real evidence depth entry",
        "repeated sample summary before any profit claim",
    )
