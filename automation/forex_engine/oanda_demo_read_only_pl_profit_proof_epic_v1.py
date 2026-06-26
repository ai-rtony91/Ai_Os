from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.oanda_demo_profit_proof_ledger_bridge_v1 import (
    OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_READY_FOR_ROUTING,
    build_oanda_demo_profit_proof_ledger_bridge,
    build_sample_breakeven_bridge_input,
    build_sample_incomplete_bridge_input,
    build_sample_loss_bridge_input,
    build_sample_profit_bridge_input,
    build_sample_unsafe_bridge_input,
    oanda_demo_profit_proof_ledger_bridge_to_jsonable_dict,
)
from automation.forex_engine.oanda_demo_read_only_pl_result_intake_v1 import (
    EXACT_OWNER_WARNING_TEXT,
    EXACT_READ_ONLY_WARNING_TEXT,
    PROTECTED_PERMISSION_DEFAULTS,
)

VERSION = "oanda_demo_read_only_pl_profit_proof_epic_v1"
OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_EPIC_VERSION = VERSION

OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_READY_FOR_OWNER_REVIEW = (
    "OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_READY_FOR_OWNER_REVIEW"
)
OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_BLOCKED = (
    "OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_BLOCKED"
)

EXACT_ONE_SENTENCE_ANSWER = (
    "AIOS can now intake one sanitized OANDA demo filled-trade P/L result for "
    "profit-proof routing, but repeated expectancy proof and live evidence remain "
    "separate gates."
)
EXACT_NEXT_OWNER_ACTION = (
    "Review sanitized read-only P/L result and approve routing into the local profit "
    "proof ledger review lane if the evidence is accurate."
)
EXACT_NEXT_CODEX_PACKET = (
    "AIOS-FOREX-OANDA-DEMO-REPEATED-EXPECTANCY-SAMPLE-ACCUMULATOR-V1"
)
LIVE_PROFIT_STATUS = (
    "LIVE_PROFITABLE_EXECUTION_STILL_BLOCKED_PENDING_REPEATED_DEMO_PROOF_AND_"
    "LIVE_EVIDENCE_BUNDLE"
)
REPEATED_EXPECTANCY_GATE = "REPEATED_EXPECTANCY_SAMPLE_STILL_REQUIRED"


@dataclass(frozen=True)
class OandaDemoReadOnlyPlProfitProofEpicConfig:
    packet_id: str = (
        "AIOS-FOREX-OANDA-DEMO-READ-ONLY-PL-CAPTURE-RESULT-INTAKE-AND-"
        "PROFIT-PROOF-LEDGER-BRIDGE-V1"
    )


@dataclass(frozen=True)
class OandaDemoReadOnlyPlProfitProofEpicInput:
    bridge_input: Mapping[str, Any]


@dataclass(frozen=True)
class OandaDemoReadOnlyPlProfitProofEpicResult:
    version: str
    packet_id: str
    classification: str
    one_sentence_answer: str
    intake_status: str
    quality_status: str
    bridge_status: str
    result_bucket: str
    realized_pl: Decimal | None
    planned_risk: Decimal | None
    realized_r_multiple: Decimal | None
    strategy_id: str
    candidate_id: str
    instrument: str
    direction: str
    ledger_entry_preview: Mapping[str, Any]
    expectancy_sample_preview: Mapping[str, Any]
    routing_targets: tuple[str, ...]
    bucket_recommendation: str
    next_allocation_hint: str
    profit_claim_status: str
    repeated_expectancy_gate: str
    live_profit_status: str
    exact_next_owner_action: str
    exact_next_codex_packet: str
    owner_warning: str
    read_only_warning: str
    bridge_result: Mapping[str, Any]
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


def build_sample_profit_epic_input() -> OandaDemoReadOnlyPlProfitProofEpicInput:
    return OandaDemoReadOnlyPlProfitProofEpicInput(
        bridge_input=_bridge_json(build_sample_profit_bridge_input())
    )


def build_sample_loss_epic_input() -> OandaDemoReadOnlyPlProfitProofEpicInput:
    return OandaDemoReadOnlyPlProfitProofEpicInput(
        bridge_input=_bridge_json(build_sample_loss_bridge_input())
    )


def build_sample_breakeven_epic_input() -> OandaDemoReadOnlyPlProfitProofEpicInput:
    return OandaDemoReadOnlyPlProfitProofEpicInput(
        bridge_input=_bridge_json(build_sample_breakeven_bridge_input())
    )


def build_sample_incomplete_epic_input() -> OandaDemoReadOnlyPlProfitProofEpicInput:
    return OandaDemoReadOnlyPlProfitProofEpicInput(
        bridge_input=_bridge_json(build_sample_incomplete_bridge_input())
    )


def build_sample_unsafe_epic_input() -> OandaDemoReadOnlyPlProfitProofEpicInput:
    return OandaDemoReadOnlyPlProfitProofEpicInput(
        bridge_input=_bridge_json(build_sample_unsafe_bridge_input())
    )


def run_oanda_demo_read_only_pl_profit_proof_epic(
    epic_input: OandaDemoReadOnlyPlProfitProofEpicInput | Mapping[str, Any] | None = None,
    config: OandaDemoReadOnlyPlProfitProofEpicConfig | None = None,
) -> OandaDemoReadOnlyPlProfitProofEpicResult:
    active_config = config or OandaDemoReadOnlyPlProfitProofEpicConfig()
    active_input = _coerce_input(epic_input or build_sample_profit_epic_input())
    bridge = dict(active_input.bridge_input)
    nested_intake = dict(bridge.get("ledger_entry_preview", {}))
    classification = (
        OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_READY_FOR_OWNER_REVIEW
        if bridge.get("classification")
        == OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_READY_FOR_ROUTING
        else OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_BLOCKED
    )
    permissions = dict(PROTECTED_PERMISSION_DEFAULTS)
    return OandaDemoReadOnlyPlProfitProofEpicResult(
        version=VERSION,
        packet_id=active_config.packet_id,
        classification=classification,
        one_sentence_answer=EXACT_ONE_SENTENCE_ANSWER,
        intake_status=str(nested_intake.get("intake_classification", "")),
        quality_status=str(nested_intake.get("quality_classification", "")),
        bridge_status=str(bridge.get("classification", "")),
        result_bucket=str(bridge.get("result_bucket", "INCOMPLETE")),
        realized_pl=_optional_decimal(bridge.get("realized_pl")),
        planned_risk=_planned_risk_from_bridge(bridge),
        realized_r_multiple=_optional_decimal(bridge.get("realized_r_multiple")),
        strategy_id=str(bridge.get("strategy_id", "")),
        candidate_id=str(bridge.get("candidate_id", "")),
        instrument=str(bridge.get("instrument", "")),
        direction=str(bridge.get("direction", "")),
        ledger_entry_preview=dict(bridge.get("ledger_entry_preview", {})),
        expectancy_sample_preview=dict(bridge.get("expectancy_sample_preview", {})),
        routing_targets=tuple(bridge.get("routing_targets", ())),
        bucket_recommendation=str(bridge.get("bucket_recommendation", "")),
        next_allocation_hint=str(bridge.get("next_allocation_hint", "")),
        profit_claim_status=_profit_claim_status(classification, bridge),
        repeated_expectancy_gate=REPEATED_EXPECTANCY_GATE,
        live_profit_status=LIVE_PROFIT_STATUS,
        exact_next_owner_action=EXACT_NEXT_OWNER_ACTION,
        exact_next_codex_packet=EXACT_NEXT_CODEX_PACKET,
        owner_warning=EXACT_OWNER_WARNING_TEXT,
        read_only_warning=EXACT_READ_ONLY_WARNING_TEXT,
        bridge_result=bridge,
        permissions=permissions,
        **permissions,
    )


def oanda_demo_read_only_pl_profit_proof_epic_to_jsonable_dict(
    result: OandaDemoReadOnlyPlProfitProofEpicResult,
) -> dict[str, Any]:
    return {
        "version": result.version,
        "packet_id": result.packet_id,
        "classification": result.classification,
        "one_sentence_answer": result.one_sentence_answer,
        "intake_status": result.intake_status,
        "quality_status": result.quality_status,
        "bridge_status": result.bridge_status,
        "result_bucket": result.result_bucket,
        "realized_pl": _json_value(result.realized_pl),
        "planned_risk": _json_value(result.planned_risk),
        "realized_r_multiple": _json_value(result.realized_r_multiple),
        "strategy_id": result.strategy_id,
        "candidate_id": result.candidate_id,
        "instrument": result.instrument,
        "direction": result.direction,
        "ledger_entry_preview": _json_value(result.ledger_entry_preview),
        "expectancy_sample_preview": _json_value(result.expectancy_sample_preview),
        "routing_targets": list(result.routing_targets),
        "bucket_recommendation": result.bucket_recommendation,
        "next_allocation_hint": result.next_allocation_hint,
        "profit_claim_status": result.profit_claim_status,
        "repeated_expectancy_gate": result.repeated_expectancy_gate,
        "live_profit_status": result.live_profit_status,
        "exact_next_owner_action": result.exact_next_owner_action,
        "exact_next_codex_packet": result.exact_next_codex_packet,
        "owner_warning": result.owner_warning,
        "read_only_warning": result.read_only_warning,
        "bridge_result": _json_value(result.bridge_result),
        "permissions": dict(result.permissions),
        **dict(result.permissions),
        "no_trade_placed_by_this_packet": True,
        "no_broker_call_made_by_this_packet": True,
    }


def oanda_demo_read_only_pl_profit_proof_epic_to_operator_text(
    result: OandaDemoReadOnlyPlProfitProofEpicResult,
) -> str:
    return "\n".join(
        (
            result.one_sentence_answer,
            f"epic_classification: {result.classification}",
            f"profit_claim_status: {result.profit_claim_status}",
            f"live_profit_status: {result.live_profit_status}",
            f"exact_next_owner_action: {result.exact_next_owner_action}",
            f"exact_next_codex_packet: {result.exact_next_codex_packet}",
            "no_trade_placed_by_this_packet: true",
            "no_broker_call_made_by_this_packet: true",
        )
    )


def oanda_demo_read_only_pl_profit_proof_epic_to_markdown(
    result: OandaDemoReadOnlyPlProfitProofEpicResult,
) -> str:
    lines = [
        "# AIOS Forex OANDA Demo Read Only P/L Profit Proof Epic V1",
        "",
        "## One Sentence Answer",
        result.one_sentence_answer,
        "",
        "## Status",
        f"- Classification: `{result.classification}`",
        f"- Result bucket: `{result.result_bucket}`",
        f"- Profit claim status: `{result.profit_claim_status}`",
        f"- Live profit status: `{result.live_profit_status}`",
        f"- Repeated expectancy gate: `{result.repeated_expectancy_gate}`",
        "",
        "## Next Actions",
        f"- Owner: {result.exact_next_owner_action}",
        f"- Codex packet: `{result.exact_next_codex_packet}`",
        "",
        "## Safety",
        "- No trade placed by this packet.",
        "- No broker call made by this packet.",
        "- All protected permission flags remain false.",
    ]
    return "\n".join(lines) + "\n"


def _bridge_json(bridge_input: Any) -> dict[str, Any]:
    return oanda_demo_profit_proof_ledger_bridge_to_jsonable_dict(
        build_oanda_demo_profit_proof_ledger_bridge(bridge_input)
    )


def _coerce_input(
    epic_input: OandaDemoReadOnlyPlProfitProofEpicInput | Mapping[str, Any],
) -> OandaDemoReadOnlyPlProfitProofEpicInput:
    if isinstance(epic_input, OandaDemoReadOnlyPlProfitProofEpicInput):
        return epic_input
    raw = dict(epic_input)
    return OandaDemoReadOnlyPlProfitProofEpicInput(
        bridge_input=raw.get("bridge_input", {})
    )


def _profit_claim_status(classification: str, bridge: Mapping[str, Any]) -> str:
    if classification == OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_READY_FOR_OWNER_REVIEW:
        return "FIRST_RESULT_READY_FOR_PROOF_REVIEW"
    if bridge.get("classification") == "OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_BLOCKED_UNSAFE":
        return "BLOCKED_UNSAFE"
    return "BLOCKED_RESULT_INCOMPLETE"


def _planned_risk_from_bridge(bridge: Mapping[str, Any]) -> Decimal | None:
    bridge_planned_risk = bridge.get("planned_risk")
    if bridge_planned_risk is not None:
        return _optional_decimal(bridge_planned_risk)
    ledger = bridge.get("ledger_entry_preview")
    if not isinstance(ledger, Mapping):
        return None
    planned_risk = ledger.get("planned_risk")
    if planned_risk is None:
        return None
    return _optional_decimal(planned_risk)


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
