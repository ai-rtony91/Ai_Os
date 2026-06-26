"""Preview-only bridge from owner-run live result to proof-ledger routing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from automation.forex_engine.oanda_owner_run_live_microtrade_result_classifier_v1 import (
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BLOCKED_UNSAFE,
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BREAKEVEN,
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LOSS,
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_PROFIT,
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_REQUIRE_MORE_EVIDENCE,
    build_sample_breakeven_result_input as classifier_breakeven_input,
    build_sample_loss_result_input as classifier_loss_input,
    build_sample_missing_owner_result_input as classifier_missing_input,
    build_sample_profit_result_input as classifier_profit_input,
    build_sample_unsafe_result_input as classifier_unsafe_input,
    classify_oanda_owner_run_live_microtrade_result,
)
from automation.forex_engine.oanda_owner_run_live_microtrade_result_contract_v1 import (
    EXACT_OWNER_WARNING,
    EXACT_RESULT_WARNING,
    jsonable,
    markdown_safety_lines,
    protected_flags_false,
)
from automation.forex_engine.oanda_owner_run_live_microtrade_result_intake_v1 import (
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_NO_OWNER_RESULT,
)


VERSION = "oanda_owner_run_live_microtrade_result_ledger_bridge_v1"

OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_READY_FOR_OWNER_REVIEW = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_READY_FOR_OWNER_REVIEW"
)
OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_REQUIRE_MORE_EVIDENCE = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_REQUIRE_MORE_EVIDENCE"
)
OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_BLOCKED_UNSAFE = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_BLOCKED_UNSAFE"
)


@dataclass(frozen=True)
class OandaOwnerRunLiveMicrotradeResultLedgerBridgeInput:
    classifier_input: Mapping[str, Any] | Any


@dataclass(frozen=True)
class OandaOwnerRunLiveMicrotradeResultLedgerBridgeResult:
    version: str
    classification: str
    classifier_status: str
    intake_status: str
    result_bucket: str
    preview_only: bool
    ledger_preview: Mapping[str, Any]
    routing_targets: tuple[str, ...]
    next_safe_action: str
    result_capture_only: bool
    owner_warning: str
    result_warning: str
    protected_flags: Mapping[str, bool]
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    live_execution_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool
    autonomous_execution_allowed: bool
    scheduler_allowed: bool
    daemon_allowed: bool
    webhook_allowed: bool
    live_micro_trade_exception_allowed: bool
    owner_live_execution_approval_present: bool
    codex_live_execution_authorized: bool
    unattended_vacation_mode_allowed: bool
    vacation_profit_trial_allowed: bool
    repeat_live_trade_allowed: bool


def build_sample_profit_result_input() -> OandaOwnerRunLiveMicrotradeResultLedgerBridgeInput:
    return OandaOwnerRunLiveMicrotradeResultLedgerBridgeInput(
        classifier_input=classifier_profit_input()
    )


def build_sample_loss_result_input() -> OandaOwnerRunLiveMicrotradeResultLedgerBridgeInput:
    return OandaOwnerRunLiveMicrotradeResultLedgerBridgeInput(
        classifier_input=classifier_loss_input()
    )


def build_sample_breakeven_result_input() -> OandaOwnerRunLiveMicrotradeResultLedgerBridgeInput:
    return OandaOwnerRunLiveMicrotradeResultLedgerBridgeInput(
        classifier_input=classifier_breakeven_input()
    )


def build_sample_missing_owner_result_input() -> OandaOwnerRunLiveMicrotradeResultLedgerBridgeInput:
    return OandaOwnerRunLiveMicrotradeResultLedgerBridgeInput(
        classifier_input=classifier_missing_input()
    )


def build_sample_unsafe_result_input() -> OandaOwnerRunLiveMicrotradeResultLedgerBridgeInput:
    return OandaOwnerRunLiveMicrotradeResultLedgerBridgeInput(
        classifier_input=classifier_unsafe_input()
    )


def bridge_oanda_owner_run_live_microtrade_result_to_ledger(
    bridge_input: OandaOwnerRunLiveMicrotradeResultLedgerBridgeInput | Mapping[str, Any] | None = None,
) -> OandaOwnerRunLiveMicrotradeResultLedgerBridgeResult:
    active_input = _coerce_input(bridge_input or build_sample_profit_result_input())
    classifier = classify_oanda_owner_run_live_microtrade_result(active_input.classifier_input)
    routing_targets, next_safe_action = _routing(classifier)
    classification = _classification(classifier.classification)
    protected_flags = protected_flags_false()
    ledger_preview = {
        "preview_only": True,
        "result_capture_only": True,
        "classifier_status": classifier.classification,
        "intake_status": classifier.intake_status,
        "result_bucket": classifier.result_bucket,
        "realized_pl": classifier.realized_pl,
        "realized_r": classifier.realized_r,
        "risk_breach": classifier.risk_breach,
        "max_loss_respected": classifier.max_loss_respected,
        "routing_targets": routing_targets,
        "next_safe_action": next_safe_action,
        "repeat_live_trade_allowed": False,
        "vacation_profit_trial_allowed": False,
        "compounding_allowed": False,
        "bank_movement_allowed": False,
    }
    return OandaOwnerRunLiveMicrotradeResultLedgerBridgeResult(
        version=VERSION,
        classification=classification,
        classifier_status=classifier.classification,
        intake_status=classifier.intake_status,
        result_bucket=_bridge_bucket(classifier),
        preview_only=True,
        ledger_preview=jsonable(ledger_preview),
        routing_targets=routing_targets,
        next_safe_action=next_safe_action,
        result_capture_only=True,
        owner_warning=EXACT_OWNER_WARNING,
        result_warning=EXACT_RESULT_WARNING,
        protected_flags=protected_flags,
        **protected_flags,
    )


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return jsonable(result)


def to_operator_text(result: OandaOwnerRunLiveMicrotradeResultLedgerBridgeResult) -> str:
    return "\n".join(
        (
            f"Result ledger bridge status: {result.classification}.",
            f"Routing targets: {', '.join(result.routing_targets) or 'none'}.",
            f"Next safe action: {result.next_safe_action}",
            "Ledger bridge is preview-only.",
            result.owner_warning,
            result.result_warning,
        )
    )


def to_markdown(result: OandaOwnerRunLiveMicrotradeResultLedgerBridgeResult) -> str:
    rows = [
        "# AIOS Forex OANDA Owner-Run Live Microtrade Result Ledger Bridge V1",
        "",
        f"- Classification: `{result.classification}`",
        f"- Classifier status: `{result.classifier_status}`",
        f"- Intake status: `{result.intake_status}`",
        f"- Result bucket: `{result.result_bucket}`",
        f"- Preview only: `{str(result.preview_only).lower()}`",
        "",
        "## Routing Targets",
    ]
    rows.extend(f"- `{item}`" for item in result.routing_targets)
    rows.extend(("", f"Next safe action: {result.next_safe_action}"))
    rows.extend(markdown_safety_lines())
    return "\n".join(rows) + "\n"


def _coerce_input(
    value: OandaOwnerRunLiveMicrotradeResultLedgerBridgeInput | Mapping[str, Any],
) -> OandaOwnerRunLiveMicrotradeResultLedgerBridgeInput:
    if isinstance(value, OandaOwnerRunLiveMicrotradeResultLedgerBridgeInput):
        return value
    raw = dict(value)
    return OandaOwnerRunLiveMicrotradeResultLedgerBridgeInput(
        classifier_input=raw.get("classifier_input", raw)
    )


def _classification(classifier_status: str) -> str:
    if classifier_status == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BLOCKED_UNSAFE:
        return OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_BLOCKED_UNSAFE
    if classifier_status in {
        OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_PROFIT,
        OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LOSS,
    }:
        return OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_READY_FOR_OWNER_REVIEW
    return OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_REQUIRE_MORE_EVIDENCE


def _routing(classifier: Any) -> tuple[tuple[str, ...], str]:
    if classifier.intake_status == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_NO_OWNER_RESULT:
        return ("no_owner_result",), "Provide one sanitized owner-run result before review."
    if classifier.classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_PROFIT:
        return ("live_proof_candidate_review",), "Review profit result as a live proof candidate; do not repeat trade."
    if classifier.classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LOSS:
        return (
            "loss_review",
            "next_profit_candidate_gate",
        ), "Review loss result and repair candidate proof before any future owner decision."
    if classifier.classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BREAKEVEN:
        return ("more_evidence",), "Collect more evidence before routing this breakeven result."
    if classifier.classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_REQUIRE_MORE_EVIDENCE:
        return ("more_evidence",), "Complete missing sanitized result evidence before routing."
    return ("blocked_unsafe",), "Stop and remove unsafe result material before retry."


def _bridge_bucket(classifier: Any) -> str:
    if classifier.intake_status == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_NO_OWNER_RESULT:
        return "missing"
    if classifier.classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BLOCKED_UNSAFE:
        return "unsafe"
    if classifier.classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BREAKEVEN:
        return "breakeven"
    if classifier.classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_PROFIT:
        return "profit"
    if classifier.classification == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LOSS:
        return "loss"
    return "requires_more_evidence"

