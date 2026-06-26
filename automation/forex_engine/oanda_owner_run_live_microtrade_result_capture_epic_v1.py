"""Top-level owner-run live microtrade result capture orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.oanda_owner_run_live_microtrade_reconciliation_gate_v1 import (
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_BLOCKED_UNSAFE,
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_READY_FOR_OWNER_REVIEW,
    evaluate_oanda_owner_run_live_microtrade_reconciliation_gate,
)
from automation.forex_engine.oanda_owner_run_live_microtrade_result_classifier_v1 import (
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BLOCKED_UNSAFE,
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LOSS,
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_PROFIT,
    classify_oanda_owner_run_live_microtrade_result,
)
from automation.forex_engine.oanda_owner_run_live_microtrade_result_contract_v1 import (
    EXACT_NEXT_CODEX_PACKET,
    EXACT_NEXT_OWNER_ACTION,
    EXACT_ONE_SENTENCE_ANSWER,
    EXACT_OWNER_WARNING,
    EXACT_RESULT_WARNING,
    PACKET_ID,
    build_sample_breakeven_result_input as contract_breakeven_input,
    build_sample_loss_result_input as contract_loss_input,
    build_sample_missing_owner_result_input as contract_missing_input,
    build_sample_profit_result_input as contract_profit_input,
    build_sample_unsafe_result_input as contract_unsafe_input,
    evaluate_oanda_owner_run_live_microtrade_result_contract,
    jsonable,
    markdown_safety_lines,
    protected_flags_false,
)
from automation.forex_engine.oanda_owner_run_live_microtrade_result_intake_v1 import (
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_ACCEPTED,
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_INCOMPLETE,
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_NO_OWNER_RESULT,
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_UNSAFE,
    intake_oanda_owner_run_live_microtrade_result,
)
from automation.forex_engine.oanda_owner_run_live_microtrade_result_ledger_bridge_v1 import (
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_BLOCKED_UNSAFE,
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_READY_FOR_OWNER_REVIEW,
    bridge_oanda_owner_run_live_microtrade_result_to_ledger,
)
from automation.forex_engine.oanda_owner_run_live_microtrade_result_quality_gate_v1 import (
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_BLOCKED_UNSAFE,
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_READY_FOR_OWNER_REVIEW,
    evaluate_oanda_owner_run_live_microtrade_result_quality_gate,
)


VERSION = "oanda_owner_run_live_microtrade_result_capture_epic_v1"

OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_READY_FOR_OWNER_REVIEW = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_READY_FOR_OWNER_REVIEW"
)
OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_REQUIRE_MORE_EVIDENCE = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_REQUIRE_MORE_EVIDENCE"
)
OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_BLOCKED_UNSAFE = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_BLOCKED_UNSAFE"
)
OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_BLOCKED_NO_OWNER_RESULT = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_BLOCKED_NO_OWNER_RESULT"
)


@dataclass(frozen=True)
class OandaOwnerRunLiveMicrotradeResultCaptureEpicInput:
    owner_result: Mapping[str, Any] | None
    unsafe_flags: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class OandaOwnerRunLiveMicrotradeResultCaptureEpicResult:
    version: str
    packet_id: str
    classification: str
    one_sentence_answer: str
    contract_status: str
    intake_status: str
    quality_gate_status: str
    classifier_status: str
    reconciliation_status: str
    ledger_bridge_status: str
    result_bucket: str
    realized_pl: Decimal | None
    realized_r: Decimal | None
    risk_breach: bool
    max_loss_respected: bool
    repeat_live_trade_allowed: bool
    vacation_profit_trial_allowed: bool
    live_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    autonomous_execution_allowed: bool
    codex_live_execution_authorized: bool
    ledger_preview: Mapping[str, Any]
    routing_targets: tuple[str, ...]
    exact_next_owner_action: str
    exact_next_codex_packet: str
    owner_warning: str
    result_warning: str
    result_capture_only: bool
    protected_flags: Mapping[str, bool]
    demo_execution_allowed: bool
    live_trading_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool
    scheduler_allowed: bool
    daemon_allowed: bool
    webhook_allowed: bool
    live_micro_trade_exception_allowed: bool
    owner_live_execution_approval_present: bool
    unattended_vacation_mode_allowed: bool


def build_sample_profit_result_input() -> OandaOwnerRunLiveMicrotradeResultCaptureEpicInput:
    return _from_contract_input(contract_profit_input())


def build_sample_loss_result_input() -> OandaOwnerRunLiveMicrotradeResultCaptureEpicInput:
    return _from_contract_input(contract_loss_input())


def build_sample_breakeven_result_input() -> OandaOwnerRunLiveMicrotradeResultCaptureEpicInput:
    return _from_contract_input(contract_breakeven_input())


def build_sample_missing_owner_result_input() -> OandaOwnerRunLiveMicrotradeResultCaptureEpicInput:
    return _from_contract_input(contract_missing_input())


def build_sample_unsafe_result_input() -> OandaOwnerRunLiveMicrotradeResultCaptureEpicInput:
    return _from_contract_input(contract_unsafe_input())


def run_oanda_owner_run_live_microtrade_result_capture_epic(
    epic_input: OandaOwnerRunLiveMicrotradeResultCaptureEpicInput | Mapping[str, Any] | None = None,
) -> OandaOwnerRunLiveMicrotradeResultCaptureEpicResult:
    active_input = _coerce_input(epic_input or build_sample_profit_result_input())
    base_input = {
        "owner_result": active_input.owner_result,
        "unsafe_flags": active_input.unsafe_flags,
    }
    intake_input = {"intake_input": base_input}
    quality_input = {"quality_gate_input": intake_input}
    classifier_input = {"classifier_input": quality_input}
    contract = evaluate_oanda_owner_run_live_microtrade_result_contract(base_input)
    intake = intake_oanda_owner_run_live_microtrade_result(base_input)
    quality = evaluate_oanda_owner_run_live_microtrade_result_quality_gate(intake_input)
    classifier = classify_oanda_owner_run_live_microtrade_result(quality_input)
    reconciliation = evaluate_oanda_owner_run_live_microtrade_reconciliation_gate(intake_input)
    ledger = bridge_oanda_owner_run_live_microtrade_result_to_ledger(classifier_input)
    classification = _epic_classification(
        contract_blocked_items=contract.blocked_items,
        intake_status=intake.classification,
        quality_status=quality.classification,
        classifier_status=classifier.classification,
        reconciliation_status=reconciliation.classification,
        ledger_status=ledger.classification,
    )
    protected_flags = protected_flags_false()
    return OandaOwnerRunLiveMicrotradeResultCaptureEpicResult(
        version=VERSION,
        packet_id=PACKET_ID,
        classification=classification,
        one_sentence_answer=EXACT_ONE_SENTENCE_ANSWER,
        contract_status=contract.classification,
        intake_status=intake.classification,
        quality_gate_status=quality.classification,
        classifier_status=classifier.classification,
        reconciliation_status=reconciliation.classification,
        ledger_bridge_status=ledger.classification,
        result_bucket=ledger.result_bucket,
        realized_pl=classifier.realized_pl,
        realized_r=classifier.realized_r,
        risk_breach=classifier.risk_breach,
        max_loss_respected=classifier.max_loss_respected,
        ledger_preview=ledger.ledger_preview,
        routing_targets=ledger.routing_targets,
        exact_next_owner_action=EXACT_NEXT_OWNER_ACTION,
        exact_next_codex_packet=EXACT_NEXT_CODEX_PACKET,
        owner_warning=EXACT_OWNER_WARNING,
        result_warning=EXACT_RESULT_WARNING,
        result_capture_only=True,
        protected_flags=protected_flags,
        **protected_flags,
    )


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return jsonable(result)


def to_operator_text(result: OandaOwnerRunLiveMicrotradeResultCaptureEpicResult) -> str:
    return "\n".join(
        (
            f"Result capture status: {result.classification}.",
            result.one_sentence_answer,
            f"Result bucket: {result.result_bucket}.",
            f"Exact next owner action: {result.exact_next_owner_action}",
            f"Exact next Codex packet: {result.exact_next_codex_packet}",
            result.owner_warning,
            result.result_warning,
        )
    )


def to_markdown(result: OandaOwnerRunLiveMicrotradeResultCaptureEpicResult) -> str:
    rows = [
        "# AIOS Forex OANDA Owner-Run Live Microtrade Result Capture Epic Report V1",
        "",
        f"- Packet ID: `{result.packet_id}`",
        f"- Classification: `{result.classification}`",
        f"- One sentence answer: {result.one_sentence_answer}",
        f"- Contract status: `{result.contract_status}`",
        f"- Intake status: `{result.intake_status}`",
        f"- Quality gate status: `{result.quality_gate_status}`",
        f"- Classifier status: `{result.classifier_status}`",
        f"- Reconciliation status: `{result.reconciliation_status}`",
        f"- Ledger bridge status: `{result.ledger_bridge_status}`",
        f"- Result bucket: `{result.result_bucket}`",
        f"- Realized P/L: `{jsonable(result.realized_pl)}`",
        f"- Realized R: `{jsonable(result.realized_r)}`",
        f"- Risk breach: `{str(result.risk_breach).lower()}`",
        f"- Max loss respected: `{str(result.max_loss_respected).lower()}`",
        "- Repeat live trade allowed: `false`",
        "- Vacation profit trial allowed: `false`",
        "- Live execution allowed: `false`",
        "- Broker action allowed: `false`",
        "- Real money allowed: `false`",
        "- Compounding allowed: `false`",
        "- Bank movement allowed: `false`",
        "- Autonomous execution allowed: `false`",
        "- Codex live execution authorized: `false`",
        "",
        "## Routing Targets",
    ]
    rows.extend(f"- `{item}`" for item in result.routing_targets)
    rows.extend(
        (
            "",
            "## Next Actions",
            f"- Owner: {result.exact_next_owner_action}",
            f"- Codex packet: `{result.exact_next_codex_packet}`",
        )
    )
    rows.extend(markdown_safety_lines())
    return "\n".join(rows) + "\n"


def _from_contract_input(value: Any) -> OandaOwnerRunLiveMicrotradeResultCaptureEpicInput:
    return OandaOwnerRunLiveMicrotradeResultCaptureEpicInput(
        owner_result=value.owner_result,
        unsafe_flags=value.unsafe_flags,
    )


def _coerce_input(
    value: OandaOwnerRunLiveMicrotradeResultCaptureEpicInput | Mapping[str, Any],
) -> OandaOwnerRunLiveMicrotradeResultCaptureEpicInput:
    if isinstance(value, OandaOwnerRunLiveMicrotradeResultCaptureEpicInput):
        return value
    raw = dict(value)
    return OandaOwnerRunLiveMicrotradeResultCaptureEpicInput(
        owner_result=raw.get("owner_result"),
        unsafe_flags=dict(raw.get("unsafe_flags", {})),
    )


def _epic_classification(
    *,
    contract_blocked_items: tuple[str, ...],
    intake_status: str,
    quality_status: str,
    classifier_status: str,
    reconciliation_status: str,
    ledger_status: str,
) -> str:
    if intake_status == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_NO_OWNER_RESULT:
        return OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_BLOCKED_NO_OWNER_RESULT
    if (
        contract_blocked_items
        or intake_status == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_UNSAFE
        or quality_status == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_BLOCKED_UNSAFE
        or classifier_status == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BLOCKED_UNSAFE
        or reconciliation_status == OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_BLOCKED_UNSAFE
        or ledger_status == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_BLOCKED_UNSAFE
    ):
        return OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_BLOCKED_UNSAFE
    if intake_status == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_INCOMPLETE:
        return OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_REQUIRE_MORE_EVIDENCE
    if (
        intake_status == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_ACCEPTED
        and quality_status == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_READY_FOR_OWNER_REVIEW
        and classifier_status
        in {
            OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_PROFIT,
            OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LOSS,
        }
        and reconciliation_status
        == OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_READY_FOR_OWNER_REVIEW
        and ledger_status
        == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_READY_FOR_OWNER_REVIEW
    ):
        return OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_READY_FOR_OWNER_REVIEW
    return OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_REQUIRE_MORE_EVIDENCE

