"""Top-level vacation profit readiness proof gate epic."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.oanda_vacation_profit_autonomy_control_gate_v1 import (
    OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_BLOCKED_UNSAFE,
    OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_READY_FOR_OWNER_REVIEW,
    build_sample_missing_autonomy_controls_input as build_autonomy_missing_input,
    build_sample_ready_for_review_input as build_autonomy_ready_input,
    build_sample_unsafe_input as build_autonomy_unsafe_input,
    evaluate_oanda_vacation_profit_autonomy_control_gate,
    to_jsonable_dict as autonomy_to_jsonable_dict,
)
from automation.forex_engine.oanda_vacation_profit_compounding_permission_gate_v1 import (
    OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_BLOCKED_UNSAFE,
    OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_READY_FOR_FUTURE_OWNER_REVIEW,
    build_sample_compounding_blocked_input as build_compounding_blocked_gate_input,
    build_sample_ready_for_review_input as build_compounding_ready_input,
    build_sample_unsafe_input as build_compounding_unsafe_input,
    evaluate_oanda_vacation_profit_compounding_permission_gate,
    to_jsonable_dict as compounding_to_jsonable_dict,
)
from automation.forex_engine.oanda_vacation_profit_live_sample_gate_v1 import (
    OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_NO_LIVE_SAMPLE,
    OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_UNSAFE,
    OANDA_VACATION_PROFIT_LIVE_SAMPLE_READY_FOR_OWNER_REVIEW,
    build_sample_no_live_sample_input as build_live_no_sample_input,
    build_sample_ready_for_review_input as build_live_ready_input,
    build_sample_unsafe_input as build_live_unsafe_input,
    evaluate_oanda_vacation_profit_live_sample_gate,
    to_jsonable_dict as live_sample_to_jsonable_dict,
)
from automation.forex_engine.oanda_vacation_profit_readiness_contract_v1 import (
    EXACT_NEXT_CODEX_PACKET,
    EXACT_NEXT_OWNER_ACTION,
    EXACT_ONE_SENTENCE_ANSWER,
    EXACT_OWNER_WARNING,
    EXACT_VACATION_WARNING,
    PACKET_ID,
    PROFIT_CLAIM_STATUS,
    VACATION_PROFIT_STATUS,
    OANDA_VACATION_PROFIT_READINESS_CONTRACT_BLOCKED_UNSAFE,
    OANDA_VACATION_PROFIT_READINESS_CONTRACT_READY,
    build_sample_ready_for_review_input as build_contract_ready_input,
    build_sample_unsafe_input as build_contract_unsafe_input,
    evaluate_oanda_vacation_profit_readiness_contract,
    protected_flags_false,
    to_jsonable_dict as contract_to_jsonable_dict,
)
from automation.forex_engine.oanda_vacation_profit_trial_plan_v1 import (
    OANDA_VACATION_PROFIT_TRIAL_PLAN_BLOCKED_UNSAFE,
    build_oanda_vacation_profit_trial_plan,
    to_jsonable_dict as trial_plan_to_jsonable_dict,
)


VERSION = "oanda_vacation_profit_readiness_epic_v1"

AIOS_VACATION_PROFIT_READY_FOR_OWNER_REVIEW = (
    "AIOS_VACATION_PROFIT_READY_FOR_OWNER_REVIEW"
)
AIOS_VACATION_PROFIT_REQUIRE_MORE_LIVE_PROOF = (
    "AIOS_VACATION_PROFIT_REQUIRE_MORE_LIVE_PROOF"
)
AIOS_VACATION_PROFIT_BLOCKED_UNSAFE = "AIOS_VACATION_PROFIT_BLOCKED_UNSAFE"
AIOS_VACATION_PROFIT_BLOCKED_NO_LIVE_SAMPLE = (
    "AIOS_VACATION_PROFIT_BLOCKED_NO_LIVE_SAMPLE"
)
AIOS_VACATION_PROFIT_BLOCKED_NO_AUTONOMY_CONTROLS = (
    "AIOS_VACATION_PROFIT_BLOCKED_NO_AUTONOMY_CONTROLS"
)
AIOS_VACATION_PROFIT_BLOCKED_NO_COMPOUNDING_PERMISSION = (
    "AIOS_VACATION_PROFIT_BLOCKED_NO_COMPOUNDING_PERMISSION"
)


@dataclass(frozen=True)
class OandaVacationProfitReadinessEpicInput:
    contract_input: Mapping[str, Any] | Any
    live_sample_input: Mapping[str, Any] | Any
    autonomy_control_input: Mapping[str, Any] | Any
    compounding_permission_input: Mapping[str, Any] | Any
    unsafe_flags: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class OandaVacationProfitReadinessEpicResult:
    version: str
    packet_id: str
    classification: str
    one_sentence_answer: str
    contract_status: str
    live_sample_status: str
    autonomy_control_status: str
    compounding_permission_status: str
    trial_plan_status: str
    trial_capital: Decimal
    max_total_drawdown_percent: Decimal
    max_daily_loss_percent: Decimal
    max_trade_risk_percent: Decimal
    min_live_sample_trades: int
    profit_claim_status: str
    vacation_profit_status: str
    missing_proof_items: tuple[str, ...]
    blocked_items: tuple[str, ...]
    trial_plan_preview: Mapping[str, Any]
    contract_preview: Mapping[str, Any]
    live_sample_preview: Mapping[str, Any]
    autonomy_control_preview: Mapping[str, Any]
    compounding_permission_preview: Mapping[str, Any]
    exact_next_owner_action: str
    exact_next_codex_packet: str
    owner_warning: str
    vacation_warning: str
    owner_final_review_allowed: bool
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


def build_sample_ready_for_review_input() -> OandaVacationProfitReadinessEpicInput:
    return OandaVacationProfitReadinessEpicInput(
        contract_input=build_contract_ready_input(),
        live_sample_input=build_live_ready_input(),
        autonomy_control_input=build_autonomy_ready_input(),
        compounding_permission_input=build_compounding_ready_input(),
    )


def build_sample_no_live_sample_input() -> OandaVacationProfitReadinessEpicInput:
    return OandaVacationProfitReadinessEpicInput(
        contract_input=build_contract_ready_input(),
        live_sample_input=build_live_no_sample_input(),
        autonomy_control_input=build_autonomy_ready_input(),
        compounding_permission_input=build_compounding_ready_input(),
    )


def build_sample_missing_autonomy_controls_input() -> OandaVacationProfitReadinessEpicInput:
    return OandaVacationProfitReadinessEpicInput(
        contract_input=build_contract_ready_input(),
        live_sample_input=build_live_ready_input(),
        autonomy_control_input=build_autonomy_missing_input(),
        compounding_permission_input=build_compounding_ready_input(),
    )


def build_sample_compounding_blocked_input() -> OandaVacationProfitReadinessEpicInput:
    return OandaVacationProfitReadinessEpicInput(
        contract_input=build_contract_ready_input(),
        live_sample_input=build_live_ready_input(),
        autonomy_control_input=build_autonomy_ready_input(),
        compounding_permission_input=build_compounding_blocked_gate_input(),
    )


def build_sample_unsafe_input() -> OandaVacationProfitReadinessEpicInput:
    return OandaVacationProfitReadinessEpicInput(
        contract_input=build_contract_unsafe_input(),
        live_sample_input=build_live_unsafe_input(),
        autonomy_control_input=build_autonomy_unsafe_input(),
        compounding_permission_input=build_compounding_unsafe_input(),
        unsafe_flags={"epic_unsafe": True},
    )


def run_oanda_vacation_profit_readiness_epic(
    epic_input: OandaVacationProfitReadinessEpicInput | Mapping[str, Any] | None = None,
) -> OandaVacationProfitReadinessEpicResult:
    active_input = _coerce_input(epic_input or build_sample_ready_for_review_input())
    contract = evaluate_oanda_vacation_profit_readiness_contract(active_input.contract_input)
    live_sample = evaluate_oanda_vacation_profit_live_sample_gate(
        active_input.live_sample_input
    )
    autonomy = evaluate_oanda_vacation_profit_autonomy_control_gate(
        active_input.autonomy_control_input
    )
    compounding = evaluate_oanda_vacation_profit_compounding_permission_gate(
        active_input.compounding_permission_input
    )
    trial_plan = build_oanda_vacation_profit_trial_plan(
        {
            "contract_status": contract.classification,
            "live_sample_status": live_sample.classification,
            "autonomy_control_status": autonomy.classification,
            "compounding_permission_status": compounding.classification,
            "trial_capital": contract.trial_capital,
            "max_total_drawdown_percent": contract.max_total_drawdown_percent,
            "max_daily_loss_percent": contract.max_daily_loss_percent,
            "max_trade_risk_percent": contract.max_trade_risk_percent,
            "unsafe_flags": active_input.unsafe_flags,
        }
    )
    classification = _epic_classification(
        contract.classification,
        live_sample.classification,
        autonomy.classification,
        compounding.classification,
        trial_plan.classification,
        active_input.unsafe_flags,
    )
    missing_items = _missing_proof_items(live_sample, autonomy, compounding, trial_plan)
    blocked_items = _blocked_items(contract, live_sample, autonomy, compounding, trial_plan)
    protected_flags = protected_flags_false()
    return OandaVacationProfitReadinessEpicResult(
        version=VERSION,
        packet_id=PACKET_ID,
        classification=classification,
        one_sentence_answer=EXACT_ONE_SENTENCE_ANSWER,
        contract_status=contract.classification,
        live_sample_status=live_sample.classification,
        autonomy_control_status=autonomy.classification,
        compounding_permission_status=compounding.classification,
        trial_plan_status=trial_plan.classification,
        trial_capital=contract.trial_capital,
        max_total_drawdown_percent=contract.max_total_drawdown_percent,
        max_daily_loss_percent=contract.max_daily_loss_percent,
        max_trade_risk_percent=contract.max_trade_risk_percent,
        min_live_sample_trades=contract.min_live_sample_trades,
        profit_claim_status=PROFIT_CLAIM_STATUS,
        vacation_profit_status=VACATION_PROFIT_STATUS,
        missing_proof_items=missing_items,
        blocked_items=blocked_items,
        trial_plan_preview=trial_plan_to_jsonable_dict(trial_plan),
        contract_preview=contract_to_jsonable_dict(contract),
        live_sample_preview=live_sample_to_jsonable_dict(live_sample),
        autonomy_control_preview=autonomy_to_jsonable_dict(autonomy),
        compounding_permission_preview=compounding_to_jsonable_dict(compounding),
        exact_next_owner_action=EXACT_NEXT_OWNER_ACTION,
        exact_next_codex_packet=EXACT_NEXT_CODEX_PACKET,
        owner_warning=EXACT_OWNER_WARNING,
        vacation_warning=EXACT_VACATION_WARNING,
        owner_final_review_allowed=classification
        == AIOS_VACATION_PROFIT_READY_FOR_OWNER_REVIEW,
        protected_flags=protected_flags,
        **protected_flags,
    )


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return _jsonable(result)


def to_operator_text(result: OandaVacationProfitReadinessEpicResult) -> str:
    return "\n".join(
        (
            f"Vacation profit readiness epic status: {result.classification}.",
            result.one_sentence_answer,
            f"Profit claim status: {result.profit_claim_status}.",
            f"Vacation profit status: {result.vacation_profit_status}.",
            "READY_FOR_OWNER_REVIEW is not approval for unattended trading.",
            result.owner_warning,
            result.vacation_warning,
            f"Exact next owner action: {result.exact_next_owner_action}",
            f"Exact next Codex packet: {result.exact_next_codex_packet}",
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
        )
    )


def to_markdown(result: OandaVacationProfitReadinessEpicResult) -> str:
    rows = [
        "# AIOS Forex OANDA Vacation Profit Readiness Epic Report V1",
        "",
        f"- Packet ID: `{result.packet_id}`",
        f"- Classification: `{result.classification}`",
        f"- One sentence answer: {result.one_sentence_answer}",
        f"- Contract status: `{result.contract_status}`",
        f"- Live sample status: `{result.live_sample_status}`",
        f"- Autonomy control status: `{result.autonomy_control_status}`",
        f"- Compounding permission status: `{result.compounding_permission_status}`",
        f"- Trial plan status: `{result.trial_plan_status}`",
        f"- Profit claim status: `{result.profit_claim_status}`",
        f"- Vacation profit status: `{result.vacation_profit_status}`",
        "- Unattended vacation mode allowed: `false`",
        "- Vacation profit trial allowed: `false`",
        "- Live execution allowed: `false`",
        "- Broker action allowed: `false`",
        "- Real money allowed: `false`",
        "- Compounding allowed: `false`",
        "- Bank movement allowed: `false`",
        "- Autonomous execution allowed: `false`",
        "- Codex live execution authorized: `false`",
        "",
        "## Missing Proof Items",
    ]
    rows.extend(f"- `{item}`" for item in result.missing_proof_items)
    rows.extend(("", "## Blocked Items"))
    rows.extend(f"- `{item}`" for item in result.blocked_items)
    rows.extend(
        (
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
            "- Profit is not guaranteed.",
            "- All protected flags remain false.",
        )
    )
    return "\n".join(rows) + "\n"


def _coerce_input(
    value: OandaVacationProfitReadinessEpicInput | Mapping[str, Any],
) -> OandaVacationProfitReadinessEpicInput:
    if isinstance(value, OandaVacationProfitReadinessEpicInput):
        return value
    raw = dict(value)
    return OandaVacationProfitReadinessEpicInput(
        contract_input=raw.get("contract_input", {}),
        live_sample_input=raw.get("live_sample_input", {}),
        autonomy_control_input=raw.get("autonomy_control_input", {}),
        compounding_permission_input=raw.get("compounding_permission_input", {}),
        unsafe_flags=dict(raw.get("unsafe_flags", {})),
    )


def _epic_classification(
    contract_status: str,
    live_sample_status: str,
    autonomy_status: str,
    compounding_status: str,
    trial_plan_status: str,
    unsafe_flags: Mapping[str, bool],
) -> str:
    if (
        any(bool(value) for value in unsafe_flags.values())
        or contract_status == OANDA_VACATION_PROFIT_READINESS_CONTRACT_BLOCKED_UNSAFE
        or live_sample_status == OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_UNSAFE
        or autonomy_status == OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_BLOCKED_UNSAFE
        or compounding_status == OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_BLOCKED_UNSAFE
        or trial_plan_status == OANDA_VACATION_PROFIT_TRIAL_PLAN_BLOCKED_UNSAFE
    ):
        return AIOS_VACATION_PROFIT_BLOCKED_UNSAFE
    if live_sample_status == OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_NO_LIVE_SAMPLE:
        return AIOS_VACATION_PROFIT_BLOCKED_NO_LIVE_SAMPLE
    if live_sample_status != OANDA_VACATION_PROFIT_LIVE_SAMPLE_READY_FOR_OWNER_REVIEW:
        return AIOS_VACATION_PROFIT_REQUIRE_MORE_LIVE_PROOF
    if autonomy_status != OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_READY_FOR_OWNER_REVIEW:
        return AIOS_VACATION_PROFIT_BLOCKED_NO_AUTONOMY_CONTROLS
    if (
        compounding_status
        != OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_READY_FOR_FUTURE_OWNER_REVIEW
    ):
        return AIOS_VACATION_PROFIT_BLOCKED_NO_COMPOUNDING_PERMISSION
    if contract_status == OANDA_VACATION_PROFIT_READINESS_CONTRACT_READY:
        return AIOS_VACATION_PROFIT_READY_FOR_OWNER_REVIEW
    return AIOS_VACATION_PROFIT_BLOCKED_UNSAFE


def _missing_proof_items(
    live_sample: Any,
    autonomy: Any,
    compounding: Any,
    trial_plan: Any,
) -> tuple[str, ...]:
    missing: list[str] = []
    missing.extend(getattr(live_sample, "missing_proof_items", ()))
    missing.extend(getattr(autonomy, "missing_control_proofs", ()))
    if (
        compounding.classification
        != OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_READY_FOR_FUTURE_OWNER_REVIEW
    ):
        missing.append("compounding_permission_future_owner_review_ready")
    if trial_plan.classification != "OANDA_VACATION_PROFIT_TRIAL_PLAN_READY_FOR_OWNER_REVIEW":
        missing.extend(getattr(trial_plan, "evidence_required_before_trial", ()))
    return tuple(dict.fromkeys(str(item) for item in missing))


def _blocked_items(
    contract: Any,
    live_sample: Any,
    autonomy: Any,
    compounding: Any,
    trial_plan: Any,
) -> tuple[str, ...]:
    blocked: list[str] = []
    for result in (contract, live_sample, autonomy, compounding, trial_plan):
        blocked.extend(getattr(result, "blocked_items", ()))
    return tuple(dict.fromkeys(str(item) for item in blocked))


def _jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "__dataclass_fields__"):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value
