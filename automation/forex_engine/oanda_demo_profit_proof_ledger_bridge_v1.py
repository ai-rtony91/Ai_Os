from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.oanda_demo_pl_result_quality_gate_v1 import (
    OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_INCOMPLETE,
    OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_LOW_SIGNAL,
    OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_UNSAFE,
    OANDA_DEMO_PL_RESULT_QUALITY_PROOF_READY,
    OANDA_DEMO_PL_RESULT_QUALITY_REVIEW_READY,
    build_sample_breakeven_quality_input,
    build_sample_incomplete_quality_input,
    build_sample_loss_quality_input,
    build_sample_profit_quality_input,
    evaluate_oanda_demo_pl_result_quality,
    oanda_demo_pl_result_quality_to_jsonable_dict,
)
from automation.forex_engine.oanda_demo_read_only_pl_result_intake_v1 import (
    EXACT_OWNER_WARNING_TEXT,
    EXACT_READ_ONLY_WARNING_TEXT,
    PROTECTED_PERMISSION_DEFAULTS,
    RESULT_BUCKET_BREAKEVEN,
    RESULT_BUCKET_LOSS,
    RESULT_BUCKET_PROFIT,
    build_sample_unsafe_pl_evidence,
    intake_oanda_demo_read_only_pl_result,
    oanda_demo_read_only_pl_result_intake_to_jsonable_dict,
)

VERSION = "oanda_demo_profit_proof_ledger_bridge_v1"
OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_VERSION = VERSION

OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_READY_FOR_ROUTING = (
    "OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_READY_FOR_ROUTING"
)
OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_BLOCKED_RESULT_INCOMPLETE = (
    "OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_BLOCKED_RESULT_INCOMPLETE"
)
OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_BLOCKED_QUALITY = (
    "OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_BLOCKED_QUALITY"
)
OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_BLOCKED_UNSAFE = (
    "OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_BLOCKED_UNSAFE"
)
OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_ROUTING_TARGETS_MISSING = (
    "OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_ROUTING_TARGETS_MISSING"
)

BASE_ROUTING_TARGETS = (
    "Profit Proof Ledger",
    "Strategy Proof Engine",
    "Expectancy Strength Router",
    "Demo Review Engine",
    "Strategy Promotion Router",
    "Real Evidence Depth Engine",
    "Result To Bucket And Next Allocation",
)


@dataclass(frozen=True)
class OandaDemoProfitProofLedgerBridgeConfig:
    require_routing_targets: bool = True


@dataclass(frozen=True)
class OandaDemoProfitProofLedgerBridgeInput:
    intake_result: Mapping[str, Any]
    quality_result: Mapping[str, Any]
    routing_targets_present: bool = True


@dataclass(frozen=True)
class OandaDemoProfitProofLedgerBridgeResult:
    version: str
    classification: str
    bridge_review_allowed: bool
    proof_routing_allowed: bool
    result_bucket: str
    realized_pl: Decimal | None
    planned_risk: Decimal | None
    realized_r_multiple: Decimal | None
    strategy_id: str
    candidate_id: str
    instrument: str
    direction: str
    routing_targets: tuple[str, ...]
    ledger_entry_preview: Mapping[str, Any]
    expectancy_sample_preview: Mapping[str, Any]
    evidence_depth_preview: Mapping[str, Any]
    bucket_recommendation: str
    next_allocation_hint: str
    blockers: tuple[str, ...]
    next_safe_action: str
    owner_warning: str
    read_only_warning: str
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


def build_sample_profit_bridge_input() -> OandaDemoProfitProofLedgerBridgeInput:
    return _bridge_input(build_sample_profit_quality_input())


def build_sample_loss_bridge_input() -> OandaDemoProfitProofLedgerBridgeInput:
    return _bridge_input(build_sample_loss_quality_input())


def build_sample_breakeven_bridge_input() -> OandaDemoProfitProofLedgerBridgeInput:
    return _bridge_input(build_sample_breakeven_quality_input())


def build_sample_incomplete_bridge_input() -> OandaDemoProfitProofLedgerBridgeInput:
    return _bridge_input(build_sample_incomplete_quality_input())


def build_sample_unsafe_bridge_input() -> OandaDemoProfitProofLedgerBridgeInput:
    intake = oanda_demo_read_only_pl_result_intake_to_jsonable_dict(
        intake_oanda_demo_read_only_pl_result(build_sample_unsafe_pl_evidence())
    )
    quality = oanda_demo_pl_result_quality_to_jsonable_dict(
        evaluate_oanda_demo_pl_result_quality({"intake_result": intake})
    )
    return OandaDemoProfitProofLedgerBridgeInput(
        intake_result=intake,
        quality_result=quality,
        routing_targets_present=True,
    )


def build_oanda_demo_profit_proof_ledger_bridge(
    bridge_input: OandaDemoProfitProofLedgerBridgeInput | Mapping[str, Any] | None = None,
    config: OandaDemoProfitProofLedgerBridgeConfig | None = None,
) -> OandaDemoProfitProofLedgerBridgeResult:
    active_config = config or OandaDemoProfitProofLedgerBridgeConfig()
    active_input = _coerce_input(bridge_input or build_sample_profit_bridge_input())
    intake = dict(active_input.intake_result)
    quality = dict(active_input.quality_result)
    result_bucket = str(intake.get("result_bucket", "INCOMPLETE"))
    routing_targets = _routing_targets(result_bucket, active_input.routing_targets_present)
    classification, blockers = _classification(
        quality, active_input.routing_targets_present, active_config
    )
    sanitized = dict(intake.get("sanitized_evidence", {}))
    permissions = dict(PROTECTED_PERMISSION_DEFAULTS)
    return OandaDemoProfitProofLedgerBridgeResult(
        version=VERSION,
        classification=classification,
        bridge_review_allowed=classification
        == OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_READY_FOR_ROUTING,
        proof_routing_allowed=quality.get("proof_routing_allowed") is True
        and classification == OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_READY_FOR_ROUTING,
        result_bucket=result_bucket,
        realized_pl=_optional_decimal(intake.get("realized_pl")),
        planned_risk=_optional_decimal(intake.get("planned_risk")),
        realized_r_multiple=_optional_decimal(intake.get("realized_r_multiple")),
        strategy_id=str(sanitized.get("strategy_id", "")),
        candidate_id=str(sanitized.get("candidate_id", "")),
        instrument=str(sanitized.get("instrument", "")),
        direction=str(sanitized.get("direction", "")),
        routing_targets=routing_targets,
        ledger_entry_preview=_ledger_preview(intake, quality),
        expectancy_sample_preview=_expectancy_preview(intake, quality),
        evidence_depth_preview=_evidence_depth_preview(intake, quality),
        bucket_recommendation=_bucket_recommendation(result_bucket, classification),
        next_allocation_hint=_next_allocation_hint(result_bucket, classification),
        blockers=tuple(blockers),
        next_safe_action=_next_safe_action(classification, result_bucket),
        owner_warning=EXACT_OWNER_WARNING_TEXT,
        read_only_warning=EXACT_READ_ONLY_WARNING_TEXT,
        permissions=permissions,
        **permissions,
    )


def oanda_demo_profit_proof_ledger_bridge_to_jsonable_dict(
    result: OandaDemoProfitProofLedgerBridgeResult,
) -> dict[str, Any]:
    return {
        "version": result.version,
        "classification": result.classification,
        "bridge_review_allowed": result.bridge_review_allowed,
        "proof_routing_allowed": result.proof_routing_allowed,
        "result_bucket": result.result_bucket,
        "realized_pl": _json_value(result.realized_pl),
        "planned_risk": _json_value(result.planned_risk),
        "realized_r_multiple": _json_value(result.realized_r_multiple),
        "strategy_id": result.strategy_id,
        "candidate_id": result.candidate_id,
        "instrument": result.instrument,
        "direction": result.direction,
        "routing_targets": list(result.routing_targets),
        "ledger_entry_preview": _json_value(result.ledger_entry_preview),
        "expectancy_sample_preview": _json_value(result.expectancy_sample_preview),
        "evidence_depth_preview": _json_value(result.evidence_depth_preview),
        "bucket_recommendation": result.bucket_recommendation,
        "next_allocation_hint": result.next_allocation_hint,
        "blockers": list(result.blockers),
        "next_safe_action": result.next_safe_action,
        "owner_warning": result.owner_warning,
        "read_only_warning": result.read_only_warning,
        "permissions": dict(result.permissions),
        **dict(result.permissions),
        "no_trade_placed_by_this_packet": True,
        "no_broker_call_made_by_this_packet": True,
        "mutates_existing_ledger_file": False,
        "preview_only": True,
    }


def oanda_demo_profit_proof_ledger_bridge_to_operator_text(
    result: OandaDemoProfitProofLedgerBridgeResult,
) -> str:
    return "\n".join(
        (
            f"Profit proof ledger bridge status: {result.classification}.",
            f"Result bucket: {result.result_bucket}.",
            f"Bucket recommendation: {result.bucket_recommendation}.",
            "Preview only; no existing ledger file is mutated.",
            "No trade placed by this packet.",
            "No broker call made by this packet.",
        )
    )


def oanda_demo_profit_proof_ledger_bridge_to_markdown(
    result: OandaDemoProfitProofLedgerBridgeResult,
) -> str:
    lines = [
        "# AIOS Forex OANDA Demo Profit Proof Ledger Bridge V1",
        "",
        "## Status",
        f"- Classification: `{result.classification}`",
        f"- Result bucket: `{result.result_bucket}`",
        f"- Bucket recommendation: `{result.bucket_recommendation}`",
        f"- Next allocation hint: {result.next_allocation_hint}",
        "",
        "## Routing Targets",
    ]
    lines.extend(f"- {target}" for target in result.routing_targets)
    lines.extend(
        [
            "",
            "## Preview Policy",
            "- Produces preview objects only.",
            "- Does not mutate existing ledger files.",
            "",
            "## Safety",
            "- No trade placed by this packet.",
            "- No broker call made by this packet.",
            "- All protected permission flags remain false.",
        ]
    )
    return "\n".join(lines) + "\n"


def _bridge_input(quality_input: Any) -> OandaDemoProfitProofLedgerBridgeInput:
    quality = oanda_demo_pl_result_quality_to_jsonable_dict(
        evaluate_oanda_demo_pl_result_quality(quality_input)
    )
    intake = quality_input.intake_result
    return OandaDemoProfitProofLedgerBridgeInput(
        intake_result=intake,
        quality_result=quality,
        routing_targets_present=True,
    )


def _coerce_input(
    bridge_input: OandaDemoProfitProofLedgerBridgeInput | Mapping[str, Any],
) -> OandaDemoProfitProofLedgerBridgeInput:
    if isinstance(bridge_input, OandaDemoProfitProofLedgerBridgeInput):
        return bridge_input
    raw = dict(bridge_input)
    return OandaDemoProfitProofLedgerBridgeInput(
        intake_result=raw.get("intake_result", {}),
        quality_result=raw.get("quality_result", {}),
        routing_targets_present=bool(raw.get("routing_targets_present", True)),
    )


def _classification(
    quality: Mapping[str, Any],
    targets_present: bool,
    config: OandaDemoProfitProofLedgerBridgeConfig,
) -> tuple[str, list[str]]:
    quality_classification = str(quality.get("classification", ""))
    if quality_classification == OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_UNSAFE:
        return OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_BLOCKED_UNSAFE, ["quality_unsafe"]
    if quality_classification == OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_INCOMPLETE:
        return (
            OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_BLOCKED_RESULT_INCOMPLETE,
            ["quality_incomplete"],
        )
    if quality_classification == OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_LOW_SIGNAL:
        return OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_BLOCKED_QUALITY, ["quality_low_signal"]
    if config.require_routing_targets and not targets_present:
        return (
            OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_ROUTING_TARGETS_MISSING,
            ["routing_targets_missing"],
        )
    if quality_classification in {
        OANDA_DEMO_PL_RESULT_QUALITY_PROOF_READY,
        OANDA_DEMO_PL_RESULT_QUALITY_REVIEW_READY,
    }:
        return OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_READY_FOR_ROUTING, []
    return OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_BLOCKED_QUALITY, ["quality_not_ready"]


def _routing_targets(result_bucket: str, targets_present: bool) -> tuple[str, ...]:
    if not targets_present:
        return tuple()
    targets = list(BASE_ROUTING_TARGETS)
    if result_bucket == RESULT_BUCKET_LOSS:
        targets.append("Loss To Next Profit Candidate Gate")
    return tuple(targets)


def _ledger_preview(intake: Mapping[str, Any], quality: Mapping[str, Any]) -> dict[str, Any]:
    sanitized = dict(intake.get("sanitized_evidence", {}))
    return {
        "preview_only": True,
        "strategy_id": sanitized.get("strategy_id"),
        "candidate_id": sanitized.get("candidate_id"),
        "instrument": sanitized.get("instrument"),
        "direction": sanitized.get("direction"),
        "result_bucket": intake.get("result_bucket"),
        "intake_classification": intake.get("classification"),
        "realized_pl": intake.get("realized_pl"),
        "planned_risk": intake.get("planned_risk"),
        "realized_r_multiple": intake.get("realized_r_multiple"),
        "quality_classification": quality.get("classification"),
        "repeated_sample_complete": False,
    }


def _expectancy_preview(intake: Mapping[str, Any], quality: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "preview_only": True,
        "single_result_only": True,
        "result_bucket": intake.get("result_bucket"),
        "realized_r_multiple": intake.get("realized_r_multiple"),
        "can_claim_repeated_expectancy": False,
        "quality_classification": quality.get("classification"),
    }


def _evidence_depth_preview(intake: Mapping[str, Any], quality: Mapping[str, Any]) -> dict[str, Any]:
    sanitized = dict(intake.get("sanitized_evidence", {}))
    return {
        "preview_only": True,
        "evidence_type": "sanitized_read_only_pl_result",
        "trade_reference": sanitized.get("trade_reference"),
        "broker_reconciled": sanitized.get("broker_reconciled"),
        "read_only_capture": sanitized.get("read_only_capture"),
        "quality_classification": quality.get("classification"),
    }


def _bucket_recommendation(result_bucket: str, classification: str) -> str:
    if classification != OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_READY_FOR_ROUTING:
        return "NO_BUCKET_RECOMMENDATION_BLOCKED"
    if result_bucket == RESULT_BUCKET_PROFIT:
        return "PROFIT_SAMPLE_ACCEPTED_FOR_REVIEW"
    if result_bucket == RESULT_BUCKET_LOSS:
        return "LOSS_SAMPLE_ACCEPTED_FOR_REVIEW"
    if result_bucket == RESULT_BUCKET_BREAKEVEN:
        return "BREAKEVEN_SAMPLE_ACCEPTED_FOR_REVIEW"
    return "NO_BUCKET_RECOMMENDATION_BLOCKED"


def _next_allocation_hint(result_bucket: str, classification: str) -> str:
    if classification != OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_READY_FOR_ROUTING:
        return "do not allocate; repair result evidence first"
    if result_bucket == RESULT_BUCKET_PROFIT:
        return "add to repeated expectancy sample before any live review"
    if result_bucket == RESULT_BUCKET_LOSS:
        return "route to loss review / next profit candidate gate"
    if result_bucket == RESULT_BUCKET_BREAKEVEN:
        return "add to evidence depth but do not strengthen expectancy alone"
    return "do not allocate; unsupported result bucket"


def _next_safe_action(classification: str, result_bucket: str) -> str:
    if classification == OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_READY_FOR_ROUTING:
        return (
            f"Owner review may route this {result_bucket} preview into local proof evidence; "
            "one result still does not prove expectancy."
        )
    return "Resolve blocked intake or quality evidence before ledger bridge review."


def _optional_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _json_value(child) for key, child in value.items()}
    if isinstance(value, tuple):
        return [_json_value(child) for child in value]
    if isinstance(value, list):
        return [_json_value(child) for child in value]
    return value
