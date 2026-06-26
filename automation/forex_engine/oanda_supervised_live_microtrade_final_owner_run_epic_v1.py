"""Top-level final owner-run package for one supervised live microtrade review."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from automation.forex_engine.oanda_supervised_live_microtrade_disarm_recovery_v1 import (
    OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_BLOCKED_UNSAFE,
    OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_READY_FOR_OWNER_REVIEW,
    build_oanda_supervised_live_microtrade_disarm_recovery,
    build_sample_missing_input as build_disarm_missing_input,
    build_sample_ready_input as build_disarm_ready_input,
    build_sample_unsafe_input as build_disarm_unsafe_input,
    to_jsonable_dict as disarm_to_jsonable_dict,
)
from automation.forex_engine.oanda_supervised_live_microtrade_final_gate_v1 import (
    EXACT_LIVE_WARNING,
    EXACT_NEXT_CODEX_PACKET,
    EXACT_NEXT_OWNER_ACTION,
    EXACT_ONE_SENTENCE_ANSWER,
    EXACT_OWNER_WARNING,
    PACKET_ID,
    OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_BLOCKED_UNSAFE,
    OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_READY_FOR_OWNER_REVIEW,
    build_sample_missing_input as build_gate_missing_input,
    build_sample_ready_input as build_gate_ready_input,
    build_sample_unsafe_input as build_gate_unsafe_input,
    evaluate_oanda_supervised_live_microtrade_final_gate,
    jsonable,
    protected_flags_false,
    to_jsonable_dict as gate_to_jsonable_dict,
)
from automation.forex_engine.oanda_supervised_live_microtrade_owner_runbook_v1 import (
    OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_BLOCKED_UNSAFE,
    OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_READY_FOR_OWNER_REVIEW,
    build_oanda_supervised_live_microtrade_owner_runbook,
    build_sample_missing_input as build_runbook_missing_input,
    build_sample_ready_input as build_runbook_ready_input,
    build_sample_unsafe_input as build_runbook_unsafe_input,
    to_jsonable_dict as runbook_to_jsonable_dict,
)
from automation.forex_engine.oanda_supervised_live_microtrade_post_trade_capture_plan_v1 import (
    OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_BLOCKED_UNSAFE,
    OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_READY_FOR_OWNER_REVIEW,
    build_oanda_supervised_live_microtrade_post_trade_capture_plan,
    build_sample_missing_input as build_capture_missing_input,
    build_sample_ready_input as build_capture_ready_input,
    build_sample_unsafe_input as build_capture_unsafe_input,
    to_jsonable_dict as capture_to_jsonable_dict,
)
from automation.forex_engine.oanda_supervised_live_microtrade_ticket_preview_v1 import (
    OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_BLOCKED_UNSAFE,
    OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_READY_FOR_OWNER_REVIEW,
    build_oanda_supervised_live_microtrade_ticket_preview,
    build_sample_missing_input as build_ticket_missing_input,
    build_sample_ready_input as build_ticket_ready_input,
    build_sample_unsafe_input as build_ticket_unsafe_input,
    to_jsonable_dict as ticket_to_jsonable_dict,
)


VERSION = "oanda_supervised_live_microtrade_final_owner_run_epic_v1"

OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_READY_FOR_OWNER_REVIEW = (
    "OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_READY_FOR_OWNER_REVIEW"
)
OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_REQUIRE_MORE_EVIDENCE = (
    "OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_REQUIRE_MORE_EVIDENCE"
)
OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_BLOCKED = (
    "OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_BLOCKED"
)


@dataclass(frozen=True)
class OandaSupervisedLiveMicrotradeFinalOwnerRunEpicInput:
    final_gate_input: Mapping[str, Any] | Any
    ticket_preview_input: Mapping[str, Any] | Any
    disarm_recovery_input: Mapping[str, Any] | Any
    post_trade_capture_input: Mapping[str, Any] | Any
    owner_runbook_input: Mapping[str, Any] | Any
    unsafe_flags: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class OandaSupervisedLiveMicrotradeFinalOwnerRunEpicResult:
    version: str
    packet_id: str
    classification: str
    one_sentence_answer: str
    final_gate_status: str
    ticket_preview_status: str
    disarm_recovery_status: str
    post_trade_capture_status: str
    owner_runbook_status: str
    owner_final_review_allowed: bool
    risk_summary: Mapping[str, Any]
    ticket_preview: Mapping[str, Any]
    disarm_recovery_preview: Mapping[str, Any]
    owner_runbook_preview: Mapping[str, Any]
    post_trade_capture_preview: Mapping[str, Any]
    exact_next_owner_action: str
    exact_next_codex_packet: str
    owner_warning: str
    live_warning: str
    protected_flags: Mapping[str, bool]
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
    live_micro_trade_exception_allowed: bool
    owner_live_execution_approval_present: bool
    codex_live_execution_authorized: bool
    unattended_vacation_mode_allowed: bool
    vacation_profit_trial_allowed: bool


def build_sample_ready_input() -> OandaSupervisedLiveMicrotradeFinalOwnerRunEpicInput:
    return OandaSupervisedLiveMicrotradeFinalOwnerRunEpicInput(
        final_gate_input=build_gate_ready_input(),
        ticket_preview_input=build_ticket_ready_input(),
        disarm_recovery_input=build_disarm_ready_input(),
        post_trade_capture_input=build_capture_ready_input(),
        owner_runbook_input=build_runbook_ready_input(),
    )


def build_sample_missing_input() -> OandaSupervisedLiveMicrotradeFinalOwnerRunEpicInput:
    return OandaSupervisedLiveMicrotradeFinalOwnerRunEpicInput(
        final_gate_input=build_gate_missing_input(),
        ticket_preview_input=build_ticket_missing_input(),
        disarm_recovery_input=build_disarm_missing_input(),
        post_trade_capture_input=build_capture_missing_input(),
        owner_runbook_input=build_runbook_missing_input(),
    )


def build_sample_unsafe_input() -> OandaSupervisedLiveMicrotradeFinalOwnerRunEpicInput:
    return OandaSupervisedLiveMicrotradeFinalOwnerRunEpicInput(
        final_gate_input=build_gate_unsafe_input(),
        ticket_preview_input=build_ticket_unsafe_input(),
        disarm_recovery_input=build_disarm_unsafe_input(),
        post_trade_capture_input=build_capture_unsafe_input(),
        owner_runbook_input=build_runbook_unsafe_input(),
        unsafe_flags={"epic_unsafe": True},
    )


def run_oanda_supervised_live_microtrade_final_owner_run_epic(
    epic_input: OandaSupervisedLiveMicrotradeFinalOwnerRunEpicInput | Mapping[str, Any] | None = None,
) -> OandaSupervisedLiveMicrotradeFinalOwnerRunEpicResult:
    active_input = _coerce_input(epic_input or build_sample_ready_input())
    final_gate = evaluate_oanda_supervised_live_microtrade_final_gate(active_input.final_gate_input)
    ticket = build_oanda_supervised_live_microtrade_ticket_preview(active_input.ticket_preview_input)
    disarm = build_oanda_supervised_live_microtrade_disarm_recovery(
        active_input.disarm_recovery_input
    )
    capture = build_oanda_supervised_live_microtrade_post_trade_capture_plan(
        active_input.post_trade_capture_input
    )
    runbook = build_oanda_supervised_live_microtrade_owner_runbook(
        active_input.owner_runbook_input
    )
    statuses = (
        final_gate.classification,
        ticket.classification,
        disarm.classification,
        capture.classification,
        runbook.classification,
    )
    classification = _classify(statuses, active_input.unsafe_flags)
    protected_flags = protected_flags_false()
    return OandaSupervisedLiveMicrotradeFinalOwnerRunEpicResult(
        version=VERSION,
        packet_id=PACKET_ID,
        classification=classification,
        one_sentence_answer=EXACT_ONE_SENTENCE_ANSWER,
        final_gate_status=final_gate.classification,
        ticket_preview_status=ticket.classification,
        disarm_recovery_status=disarm.classification,
        post_trade_capture_status=capture.classification,
        owner_runbook_status=runbook.classification,
        owner_final_review_allowed=classification
        == OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_READY_FOR_OWNER_REVIEW,
        risk_summary={
            "one_shot_only": True,
            "owner_run_only": True,
            "profit_guaranteed": False,
            "live_execution_allowed": False,
            "real_money_allowed": False,
            "compounding_allowed": False,
            "bank_movement_allowed": False,
            "autonomous_execution_allowed": False,
            "vacation_profit_trial_allowed": False,
        },
        ticket_preview=ticket_to_jsonable_dict(ticket),
        disarm_recovery_preview=disarm_to_jsonable_dict(disarm),
        owner_runbook_preview=runbook_to_jsonable_dict(runbook),
        post_trade_capture_preview=capture_to_jsonable_dict(capture),
        exact_next_owner_action=EXACT_NEXT_OWNER_ACTION,
        exact_next_codex_packet=EXACT_NEXT_CODEX_PACKET,
        owner_warning=EXACT_OWNER_WARNING,
        live_warning=EXACT_LIVE_WARNING,
        protected_flags=protected_flags,
        **protected_flags,
    )


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return jsonable(result)


def to_operator_text(result: OandaSupervisedLiveMicrotradeFinalOwnerRunEpicResult) -> str:
    return "\n".join(
        (
            f"Final owner-run epic status: {result.classification}.",
            result.one_sentence_answer,
            f"Owner final review allowed: {str(result.owner_final_review_allowed).lower()}.",
            f"Exact next owner action: {result.exact_next_owner_action}",
            f"Exact next Codex packet: {result.exact_next_codex_packet}",
            result.owner_warning,
            result.live_warning,
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
        )
    )


def to_markdown(result: OandaSupervisedLiveMicrotradeFinalOwnerRunEpicResult) -> str:
    rows = [
        "# AIOS Forex OANDA Supervised Live Microtrade Final Owner-Run Epic V1",
        "",
        f"- Packet ID: `{result.packet_id}`",
        f"- Classification: `{result.classification}`",
        f"- One sentence answer: {result.one_sentence_answer}",
        f"- Final gate status: `{result.final_gate_status}`",
        f"- Ticket preview status: `{result.ticket_preview_status}`",
        f"- Disarm recovery status: `{result.disarm_recovery_status}`",
        f"- Post-trade capture status: `{result.post_trade_capture_status}`",
        f"- Owner runbook status: `{result.owner_runbook_status}`",
        f"- Owner final review allowed: `{str(result.owner_final_review_allowed).lower()}`",
        "- Live execution allowed: `false`",
        "- Broker action allowed: `false`",
        "- Real money allowed: `false`",
        "- Compounding allowed: `false`",
        "- Bank movement allowed: `false`",
        "- Autonomous execution allowed: `false`",
        "- Unattended vacation mode allowed: `false`",
        "- Vacation profit trial allowed: `false`",
        "- Codex live execution authorized: `false`",
        "",
        "## Next Actions",
        f"- Owner: {result.exact_next_owner_action}",
        f"- Codex packet: `{result.exact_next_codex_packet}`",
        "",
        "## Safety",
        "- No trade placed by this packet.",
        "- No broker call was made by this packet.",
        "- No live approval was granted.",
        "- No real money approval was granted.",
        "- No compounding approval was granted.",
        "- No bank movement approval was granted.",
        "- No autonomous execution was granted.",
        "- Unattended vacation mode remains blocked.",
        "- Vacation profit trial remains blocked unless Anthony separately approves.",
        "- Profit is not guaranteed.",
        "- All protected flags remain false.",
        "- Owner-run only.",
        "- One-shot only.",
    ]
    return "\n".join(rows) + "\n"


def _coerce_input(
    value: OandaSupervisedLiveMicrotradeFinalOwnerRunEpicInput | Mapping[str, Any],
) -> OandaSupervisedLiveMicrotradeFinalOwnerRunEpicInput:
    if isinstance(value, OandaSupervisedLiveMicrotradeFinalOwnerRunEpicInput):
        return value
    raw = dict(value)
    return OandaSupervisedLiveMicrotradeFinalOwnerRunEpicInput(
        final_gate_input=raw.get("final_gate_input", {}),
        ticket_preview_input=raw.get("ticket_preview_input", {}),
        disarm_recovery_input=raw.get("disarm_recovery_input", {}),
        post_trade_capture_input=raw.get("post_trade_capture_input", {}),
        owner_runbook_input=raw.get("owner_runbook_input", {}),
        unsafe_flags=dict(raw.get("unsafe_flags", {})),
    )


def _classify(statuses: tuple[str, ...], unsafe_flags: Mapping[str, bool]) -> str:
    unsafe_statuses = {
        OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_BLOCKED_UNSAFE,
        OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_BLOCKED_UNSAFE,
        OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_BLOCKED_UNSAFE,
        OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_BLOCKED_UNSAFE,
        OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_BLOCKED_UNSAFE,
    }
    ready_statuses = {
        OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_READY_FOR_OWNER_REVIEW,
        OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_READY_FOR_OWNER_REVIEW,
        OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_READY_FOR_OWNER_REVIEW,
        OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_READY_FOR_OWNER_REVIEW,
        OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_READY_FOR_OWNER_REVIEW,
    }
    if any(bool(value) for value in unsafe_flags.values()) or any(
        status in unsafe_statuses for status in statuses
    ):
        return OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_BLOCKED
    if set(statuses) == ready_statuses:
        return OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_READY_FOR_OWNER_REVIEW
    return OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_REQUIRE_MORE_EVIDENCE

