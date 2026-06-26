"""Local-only vacation profit readiness contract for owner review gates."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Any, Mapping


VERSION = "oanda_vacation_profit_readiness_contract_v1"
PACKET_ID = "AIOS-FOREX-OANDA-VACATION-PROFIT-READINESS-PROOF-GATE-V1"

EXACT_OWNER_WARNING = "Do not execute unless Anthony explicitly approves."
EXACT_VACATION_WARNING = (
    "Vacation profit readiness review only. Codex is not authorized to execute, "
    "call a broker, access credentials, place orders, approve unattended trading, "
    "compound profits, or move money."
)
EXACT_ONE_SENTENCE_ANSWER = (
    "AIOS can now measure whether the system is ready for a small-funded vacation "
    "profit trial, but unattended live trading and compounding remain blocked until "
    "live proof, autonomy controls, and Anthony's explicit approval are complete."
)
EXACT_NEXT_OWNER_ACTION = (
    "Review the vacation profit readiness proof gaps and decide whether to continue "
    "toward a controlled small-funded supervised trial; do not treat this as approval "
    "for unattended trading."
)
EXACT_NEXT_CODEX_PACKET = (
    "AIOS-FOREX-OANDA-SUPERVISED-LIVE-MICROTRADE-FINAL-OWNER-RUN-PATH-V1"
)

PROFIT_CLAIM_STATUS = "PROFIT_NOT_GUARANTEED_PROOF_REQUIRED"
VACATION_PROFIT_STATUS = "VACATION_PROFIT_BLOCKED_PENDING_LIVE_SAMPLE_AND_AUTONOMY_PROOF"

OANDA_VACATION_PROFIT_READINESS_CONTRACT_READY = (
    "OANDA_VACATION_PROFIT_READINESS_CONTRACT_READY"
)
OANDA_VACATION_PROFIT_READINESS_CONTRACT_BLOCKED_UNSAFE = (
    "OANDA_VACATION_PROFIT_READINESS_CONTRACT_BLOCKED_UNSAFE"
)

PROTECTED_FLAG_NAMES = (
    "demo_execution_allowed",
    "broker_action_allowed",
    "real_money_allowed",
    "compounding_allowed",
    "bank_movement_allowed",
    "live_trading_allowed",
    "credential_access_allowed",
    "account_id_persistence_allowed",
    "autonomous_execution_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
    "live_micro_trade_exception_allowed",
    "owner_live_execution_approval_present",
    "codex_live_execution_authorized",
    "unattended_vacation_mode_allowed",
    "vacation_profit_trial_allowed",
)
PROTECTED_FLAGS_FALSE = {name: False for name in PROTECTED_FLAG_NAMES}


@dataclass(frozen=True)
class OandaVacationProfitReadinessContractInput:
    trial_capital: Decimal = Decimal("200.00")
    target_profit_mode: str = "small_lump_sum_non_guaranteed"
    max_total_drawdown_percent: Decimal = Decimal("5.00")
    max_daily_loss_percent: Decimal = Decimal("2.00")
    max_trade_risk_percent: Decimal = Decimal("0.50")
    min_live_sample_trades: int = 20
    min_live_profit_factor: Decimal = Decimal("1.20")
    min_live_expectancy_per_trade: Decimal = Decimal("0.01")
    min_kill_switch_proof_count: int = 3
    min_disarm_proof_count: int = 3
    min_reconciliation_proof_count: int = 3
    unsafe_flags: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class OandaVacationProfitReadinessContractResult:
    version: str
    packet_id: str
    classification: str
    trial_capital: Decimal
    target_profit_mode: str
    max_total_drawdown_percent: Decimal
    max_daily_loss_percent: Decimal
    max_trade_risk_percent: Decimal
    min_live_sample_trades: int
    min_live_profit_factor: Decimal
    min_live_expectancy_per_trade: Decimal
    min_kill_switch_proof_count: int
    min_disarm_proof_count: int
    min_reconciliation_proof_count: int
    small_funded_account_goal: str
    capital_preservation_first: bool
    profit_is_not_guaranteed: bool
    no_compounding_without_later_gate: bool
    no_bank_movement: bool
    unattended_mode_blocked_until_proof_exists: bool
    owner_review_required: bool
    blocked_items: tuple[str, ...]
    owner_warning: str
    vacation_warning: str
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


def build_sample_ready_for_review_input() -> OandaVacationProfitReadinessContractInput:
    return OandaVacationProfitReadinessContractInput()


def build_sample_no_live_sample_input() -> OandaVacationProfitReadinessContractInput:
    return OandaVacationProfitReadinessContractInput()


def build_sample_missing_autonomy_controls_input() -> OandaVacationProfitReadinessContractInput:
    return OandaVacationProfitReadinessContractInput()


def build_sample_compounding_blocked_input() -> OandaVacationProfitReadinessContractInput:
    return OandaVacationProfitReadinessContractInput()


def build_sample_unsafe_input() -> OandaVacationProfitReadinessContractInput:
    return OandaVacationProfitReadinessContractInput(
        unsafe_flags={"unsafe_contract_boundary": True}
    )


def evaluate_oanda_vacation_profit_readiness_contract(
    contract_input: OandaVacationProfitReadinessContractInput | Mapping[str, Any] | None = None,
) -> OandaVacationProfitReadinessContractResult:
    active_input = _coerce_contract_input(
        contract_input or build_sample_ready_for_review_input()
    )
    blocked_items = _blocked_contract_items(active_input)
    classification = (
        OANDA_VACATION_PROFIT_READINESS_CONTRACT_BLOCKED_UNSAFE
        if blocked_items
        else OANDA_VACATION_PROFIT_READINESS_CONTRACT_READY
    )
    protected_flags = protected_flags_false()
    return OandaVacationProfitReadinessContractResult(
        version=VERSION,
        packet_id=PACKET_ID,
        classification=classification,
        trial_capital=active_input.trial_capital,
        target_profit_mode=active_input.target_profit_mode,
        max_total_drawdown_percent=active_input.max_total_drawdown_percent,
        max_daily_loss_percent=active_input.max_daily_loss_percent,
        max_trade_risk_percent=active_input.max_trade_risk_percent,
        min_live_sample_trades=active_input.min_live_sample_trades,
        min_live_profit_factor=active_input.min_live_profit_factor,
        min_live_expectancy_per_trade=active_input.min_live_expectancy_per_trade,
        min_kill_switch_proof_count=active_input.min_kill_switch_proof_count,
        min_disarm_proof_count=active_input.min_disarm_proof_count,
        min_reconciliation_proof_count=active_input.min_reconciliation_proof_count,
        small_funded_account_goal="small funded account review target",
        capital_preservation_first=True,
        profit_is_not_guaranteed=True,
        no_compounding_without_later_gate=True,
        no_bank_movement=True,
        unattended_mode_blocked_until_proof_exists=True,
        owner_review_required=True,
        blocked_items=blocked_items,
        owner_warning=EXACT_OWNER_WARNING,
        vacation_warning=EXACT_VACATION_WARNING,
        protected_flags=protected_flags,
        **protected_flags,
    )


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return _jsonable(result)


def to_operator_text(result: OandaVacationProfitReadinessContractResult) -> str:
    return "\n".join(
        (
            f"Vacation profit readiness contract status: {result.classification}.",
            "Profit is not guaranteed.",
            "Capital preservation is first.",
            "No compounding, bank movement, unattended trading, or live execution is approved.",
            result.owner_warning,
            result.vacation_warning,
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
        )
    )


def to_markdown(result: OandaVacationProfitReadinessContractResult) -> str:
    rows = [
        "# AIOS Forex OANDA Vacation Profit Readiness Contract V1",
        "",
        f"- Classification: `{result.classification}`",
        f"- Trial capital: `{_jsonable(result.trial_capital)}`",
        f"- Target profit mode: `{result.target_profit_mode}`",
        f"- Max total drawdown percent: `{_jsonable(result.max_total_drawdown_percent)}`",
        f"- Max daily loss percent: `{_jsonable(result.max_daily_loss_percent)}`",
        f"- Max trade risk percent: `{_jsonable(result.max_trade_risk_percent)}`",
        "- Profit is not guaranteed.",
        "- Capital preservation is first.",
        "- No compounding without explicit later gate.",
        "- No bank movement.",
        "- Unattended mode remains blocked until proof exists.",
        "- Owner review is required.",
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
    ]
    return "\n".join(rows) + "\n"


def protected_flags_false() -> dict[str, bool]:
    return dict(PROTECTED_FLAGS_FALSE)


def _coerce_contract_input(
    value: OandaVacationProfitReadinessContractInput | Mapping[str, Any],
) -> OandaVacationProfitReadinessContractInput:
    if isinstance(value, OandaVacationProfitReadinessContractInput):
        return value
    raw = dict(value)
    return OandaVacationProfitReadinessContractInput(
        trial_capital=_decimal(raw.get("trial_capital", "200.00")),
        target_profit_mode=str(
            raw.get("target_profit_mode", "small_lump_sum_non_guaranteed")
        ),
        max_total_drawdown_percent=_decimal(
            raw.get("max_total_drawdown_percent", "5.00")
        ),
        max_daily_loss_percent=_decimal(raw.get("max_daily_loss_percent", "2.00")),
        max_trade_risk_percent=_decimal(raw.get("max_trade_risk_percent", "0.50")),
        min_live_sample_trades=int(raw.get("min_live_sample_trades", 20)),
        min_live_profit_factor=_decimal(raw.get("min_live_profit_factor", "1.20")),
        min_live_expectancy_per_trade=_decimal(
            raw.get("min_live_expectancy_per_trade", "0.01")
        ),
        min_kill_switch_proof_count=int(raw.get("min_kill_switch_proof_count", 3)),
        min_disarm_proof_count=int(raw.get("min_disarm_proof_count", 3)),
        min_reconciliation_proof_count=int(
            raw.get("min_reconciliation_proof_count", 3)
        ),
        unsafe_flags=dict(raw.get("unsafe_flags", {})),
    )


def _blocked_contract_items(
    contract_input: OandaVacationProfitReadinessContractInput,
) -> tuple[str, ...]:
    blocked: list[str] = []
    if any(bool(value) for value in contract_input.unsafe_flags.values()):
        blocked.append("unsafe_contract_flag")
    if contract_input.trial_capital <= Decimal("0"):
        blocked.append("trial_capital_must_be_positive")
    if contract_input.max_total_drawdown_percent <= Decimal("0"):
        blocked.append("max_total_drawdown_percent_must_be_positive")
    if contract_input.max_daily_loss_percent <= Decimal("0"):
        blocked.append("max_daily_loss_percent_must_be_positive")
    if contract_input.max_trade_risk_percent <= Decimal("0"):
        blocked.append("max_trade_risk_percent_must_be_positive")
    if contract_input.min_live_sample_trades < 1:
        blocked.append("min_live_sample_trades_must_be_positive")
    if contract_input.min_live_profit_factor <= Decimal("1.00"):
        blocked.append("min_live_profit_factor_must_exceed_one")
    if contract_input.min_live_expectancy_per_trade <= Decimal("0"):
        blocked.append("min_live_expectancy_per_trade_must_be_positive")
    return tuple(blocked)


def _decimal(value: Any) -> Decimal:
    return Decimal(str(value))


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

