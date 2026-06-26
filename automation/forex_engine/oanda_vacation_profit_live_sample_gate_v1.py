"""Gate live-sample proof before vacation profit readiness can be reviewed."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.oanda_vacation_profit_readiness_contract_v1 import (
    EXACT_OWNER_WARNING,
    EXACT_VACATION_WARNING,
    PROTECTED_FLAG_NAMES,
    protected_flags_false,
)


VERSION = "oanda_vacation_profit_live_sample_gate_v1"

OANDA_VACATION_PROFIT_LIVE_SAMPLE_READY_FOR_OWNER_REVIEW = (
    "OANDA_VACATION_PROFIT_LIVE_SAMPLE_READY_FOR_OWNER_REVIEW"
)
OANDA_VACATION_PROFIT_LIVE_SAMPLE_REQUIRE_MORE_PROOF = (
    "OANDA_VACATION_PROFIT_LIVE_SAMPLE_REQUIRE_MORE_PROOF"
)
OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_NO_LIVE_SAMPLE = (
    "OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_NO_LIVE_SAMPLE"
)
OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_NEGATIVE_EXPECTANCY = (
    "OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_NEGATIVE_EXPECTANCY"
)
OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_UNSAFE = (
    "OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_UNSAFE"
)


@dataclass(frozen=True)
class OandaVacationProfitLiveSampleGateInput:
    repeated_demo_expectancy_ready: bool
    live_evidence_gap_bridge_ready: bool
    live_microtrade_result_sample_exists: bool
    live_sample_trade_count: int
    live_profit_factor: Decimal
    live_expectancy_per_trade: Decimal
    max_total_drawdown_percent_observed: Decimal
    max_total_drawdown_percent_limit: Decimal = Decimal("5.00")
    min_live_sample_trades: int = 20
    min_live_profit_factor: Decimal = Decimal("1.20")
    min_live_expectancy_per_trade: Decimal = Decimal("0.01")
    unresolved_loss_spike_present: bool = False
    reconciliation_complete: bool = True
    post_trade_capture_complete: bool = True
    unsafe_flags: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class OandaVacationProfitLiveSampleGateResult:
    version: str
    classification: str
    repeated_demo_expectancy_ready: bool
    live_evidence_gap_bridge_ready: bool
    live_microtrade_result_sample_exists: bool
    live_sample_trade_count: int
    live_profit_factor: Decimal
    live_expectancy_per_trade: Decimal
    max_total_drawdown_percent_observed: Decimal
    min_live_sample_trades: int
    min_live_profit_factor: Decimal
    min_live_expectancy_per_trade: Decimal
    reconciliation_complete: bool
    post_trade_capture_complete: bool
    requires_more_proof: bool
    blocked: bool
    missing_proof_items: tuple[str, ...]
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


def build_sample_ready_for_review_input() -> OandaVacationProfitLiveSampleGateInput:
    return OandaVacationProfitLiveSampleGateInput(
        repeated_demo_expectancy_ready=True,
        live_evidence_gap_bridge_ready=True,
        live_microtrade_result_sample_exists=True,
        live_sample_trade_count=24,
        live_profit_factor=Decimal("1.35"),
        live_expectancy_per_trade=Decimal("0.03"),
        max_total_drawdown_percent_observed=Decimal("3.20"),
    )


def build_sample_no_live_sample_input() -> OandaVacationProfitLiveSampleGateInput:
    return OandaVacationProfitLiveSampleGateInput(
        repeated_demo_expectancy_ready=True,
        live_evidence_gap_bridge_ready=True,
        live_microtrade_result_sample_exists=False,
        live_sample_trade_count=0,
        live_profit_factor=Decimal("0"),
        live_expectancy_per_trade=Decimal("0"),
        max_total_drawdown_percent_observed=Decimal("0"),
        reconciliation_complete=False,
        post_trade_capture_complete=False,
    )


def build_sample_missing_autonomy_controls_input() -> OandaVacationProfitLiveSampleGateInput:
    return build_sample_ready_for_review_input()


def build_sample_compounding_blocked_input() -> OandaVacationProfitLiveSampleGateInput:
    return build_sample_ready_for_review_input()


def build_sample_unsafe_input() -> OandaVacationProfitLiveSampleGateInput:
    return OandaVacationProfitLiveSampleGateInput(
        repeated_demo_expectancy_ready=True,
        live_evidence_gap_bridge_ready=True,
        live_microtrade_result_sample_exists=True,
        live_sample_trade_count=24,
        live_profit_factor=Decimal("1.35"),
        live_expectancy_per_trade=Decimal("0.03"),
        max_total_drawdown_percent_observed=Decimal("3.20"),
        unresolved_loss_spike_present=True,
        unsafe_flags={"unresolved_loss_spike": True},
    )


def evaluate_oanda_vacation_profit_live_sample_gate(
    gate_input: OandaVacationProfitLiveSampleGateInput | Mapping[str, Any] | None = None,
) -> OandaVacationProfitLiveSampleGateResult:
    active_input = _coerce_input(gate_input or build_sample_ready_for_review_input())
    missing_items = _missing_items(active_input)
    blocked_items = _blocked_items(active_input)
    if blocked_items:
        classification = OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_UNSAFE
    elif not active_input.live_microtrade_result_sample_exists:
        classification = OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_NO_LIVE_SAMPLE
    elif active_input.live_expectancy_per_trade < active_input.min_live_expectancy_per_trade:
        classification = OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_NEGATIVE_EXPECTANCY
    elif missing_items:
        classification = OANDA_VACATION_PROFIT_LIVE_SAMPLE_REQUIRE_MORE_PROOF
    else:
        classification = OANDA_VACATION_PROFIT_LIVE_SAMPLE_READY_FOR_OWNER_REVIEW
    protected_flags = protected_flags_false()
    return OandaVacationProfitLiveSampleGateResult(
        version=VERSION,
        classification=classification,
        repeated_demo_expectancy_ready=active_input.repeated_demo_expectancy_ready,
        live_evidence_gap_bridge_ready=active_input.live_evidence_gap_bridge_ready,
        live_microtrade_result_sample_exists=active_input.live_microtrade_result_sample_exists,
        live_sample_trade_count=active_input.live_sample_trade_count,
        live_profit_factor=active_input.live_profit_factor,
        live_expectancy_per_trade=active_input.live_expectancy_per_trade,
        max_total_drawdown_percent_observed=active_input.max_total_drawdown_percent_observed,
        min_live_sample_trades=active_input.min_live_sample_trades,
        min_live_profit_factor=active_input.min_live_profit_factor,
        min_live_expectancy_per_trade=active_input.min_live_expectancy_per_trade,
        reconciliation_complete=active_input.reconciliation_complete,
        post_trade_capture_complete=active_input.post_trade_capture_complete,
        requires_more_proof=classification
        == OANDA_VACATION_PROFIT_LIVE_SAMPLE_REQUIRE_MORE_PROOF,
        blocked=classification
        in {
            OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_NO_LIVE_SAMPLE,
            OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_NEGATIVE_EXPECTANCY,
            OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_UNSAFE,
        },
        missing_proof_items=missing_items,
        blocked_items=blocked_items,
        owner_warning=EXACT_OWNER_WARNING,
        vacation_warning=EXACT_VACATION_WARNING,
        protected_flags=protected_flags,
        **protected_flags,
    )


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return _jsonable(result)


def to_operator_text(result: OandaVacationProfitLiveSampleGateResult) -> str:
    return "\n".join(
        (
            f"Vacation profit live sample gate status: {result.classification}.",
            f"Live sample trades: {result.live_sample_trade_count}.",
            f"Live profit factor: {_jsonable(result.live_profit_factor)}.",
            f"Live expectancy per trade: {_jsonable(result.live_expectancy_per_trade)}.",
            "Live proof review is not live execution approval.",
            result.owner_warning,
            result.vacation_warning,
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
        )
    )


def to_markdown(result: OandaVacationProfitLiveSampleGateResult) -> str:
    rows = [
        "# AIOS Forex OANDA Vacation Profit Live Sample Gate V1",
        "",
        f"- Classification: `{result.classification}`",
        f"- Repeated demo expectancy ready: `{str(result.repeated_demo_expectancy_ready).lower()}`",
        f"- Live evidence gap bridge ready: `{str(result.live_evidence_gap_bridge_ready).lower()}`",
        f"- Live result sample exists: `{str(result.live_microtrade_result_sample_exists).lower()}`",
        f"- Live sample trade count: `{result.live_sample_trade_count}`",
        f"- Live profit factor: `{_jsonable(result.live_profit_factor)}`",
        f"- Live expectancy per trade: `{_jsonable(result.live_expectancy_per_trade)}`",
        f"- Observed max drawdown percent: `{_jsonable(result.max_total_drawdown_percent_observed)}`",
        "",
        "## Missing Proof Items",
    ]
    rows.extend(f"- `{item}`" for item in result.missing_proof_items)
    rows.extend(
        (
            "",
            "## Blocked Items",
        )
    )
    rows.extend(f"- `{item}`" for item in result.blocked_items)
    rows.extend(
        (
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
    value: OandaVacationProfitLiveSampleGateInput | Mapping[str, Any],
) -> OandaVacationProfitLiveSampleGateInput:
    if isinstance(value, OandaVacationProfitLiveSampleGateInput):
        return value
    raw = dict(value)
    return OandaVacationProfitLiveSampleGateInput(
        repeated_demo_expectancy_ready=bool(raw.get("repeated_demo_expectancy_ready", False)),
        live_evidence_gap_bridge_ready=bool(raw.get("live_evidence_gap_bridge_ready", False)),
        live_microtrade_result_sample_exists=bool(
            raw.get("live_microtrade_result_sample_exists", False)
        ),
        live_sample_trade_count=int(raw.get("live_sample_trade_count", 0)),
        live_profit_factor=_decimal(raw.get("live_profit_factor", "0")),
        live_expectancy_per_trade=_decimal(raw.get("live_expectancy_per_trade", "0")),
        max_total_drawdown_percent_observed=_decimal(
            raw.get("max_total_drawdown_percent_observed", "0")
        ),
        max_total_drawdown_percent_limit=_decimal(
            raw.get("max_total_drawdown_percent_limit", "5.00")
        ),
        min_live_sample_trades=int(raw.get("min_live_sample_trades", 20)),
        min_live_profit_factor=_decimal(raw.get("min_live_profit_factor", "1.20")),
        min_live_expectancy_per_trade=_decimal(
            raw.get("min_live_expectancy_per_trade", "0.01")
        ),
        unresolved_loss_spike_present=bool(raw.get("unresolved_loss_spike_present", False)),
        reconciliation_complete=bool(raw.get("reconciliation_complete", False)),
        post_trade_capture_complete=bool(raw.get("post_trade_capture_complete", False)),
        unsafe_flags=dict(raw.get("unsafe_flags", {})),
    )


def _missing_items(active_input: OandaVacationProfitLiveSampleGateInput) -> tuple[str, ...]:
    missing: list[str] = []
    if not active_input.repeated_demo_expectancy_ready:
        missing.append("repeated_demo_expectancy_ready")
    if not active_input.live_evidence_gap_bridge_ready:
        missing.append("live_evidence_gap_bridge_ready")
    if (
        active_input.live_microtrade_result_sample_exists
        and active_input.live_sample_trade_count < active_input.min_live_sample_trades
    ):
        missing.append("live_sample_size_threshold")
    if (
        active_input.live_microtrade_result_sample_exists
        and active_input.live_profit_factor < active_input.min_live_profit_factor
    ):
        missing.append("live_profit_factor_threshold")
    if (
        active_input.live_microtrade_result_sample_exists
        and active_input.max_total_drawdown_percent_observed
        > active_input.max_total_drawdown_percent_limit
    ):
        missing.append("max_drawdown_under_threshold")
    if not active_input.reconciliation_complete:
        missing.append("reconciliation_complete")
    if not active_input.post_trade_capture_complete:
        missing.append("post_trade_capture_complete")
    return tuple(missing)


def _blocked_items(active_input: OandaVacationProfitLiveSampleGateInput) -> tuple[str, ...]:
    blocked: list[str] = []
    if any(bool(value) for value in active_input.unsafe_flags.values()):
        blocked.append("unsafe_live_sample_flag")
    if active_input.unresolved_loss_spike_present:
        blocked.append("unresolved_loss_spike_present")
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


assert tuple(PROTECTED_FLAG_NAMES)

