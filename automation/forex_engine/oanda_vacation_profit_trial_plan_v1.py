"""Non-executing vacation profit trial plan preview."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.oanda_vacation_profit_autonomy_control_gate_v1 import (
    OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_READY_FOR_OWNER_REVIEW,
)
from automation.forex_engine.oanda_vacation_profit_compounding_permission_gate_v1 import (
    OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_READY_FOR_FUTURE_OWNER_REVIEW,
)
from automation.forex_engine.oanda_vacation_profit_live_sample_gate_v1 import (
    OANDA_VACATION_PROFIT_LIVE_SAMPLE_READY_FOR_OWNER_REVIEW,
)
from automation.forex_engine.oanda_vacation_profit_readiness_contract_v1 import (
    EXACT_OWNER_WARNING,
    EXACT_VACATION_WARNING,
    OANDA_VACATION_PROFIT_READINESS_CONTRACT_READY,
    protected_flags_false,
)


VERSION = "oanda_vacation_profit_trial_plan_v1"

OANDA_VACATION_PROFIT_TRIAL_PLAN_READY_FOR_OWNER_REVIEW = (
    "OANDA_VACATION_PROFIT_TRIAL_PLAN_READY_FOR_OWNER_REVIEW"
)
OANDA_VACATION_PROFIT_TRIAL_PLAN_REQUIRE_MORE_PROOF = (
    "OANDA_VACATION_PROFIT_TRIAL_PLAN_REQUIRE_MORE_PROOF"
)
OANDA_VACATION_PROFIT_TRIAL_PLAN_BLOCKED_UNSAFE = (
    "OANDA_VACATION_PROFIT_TRIAL_PLAN_BLOCKED_UNSAFE"
)

TRIAL_CAPITAL_PLACEHOLDER = "OWNER_RUNTIME_TRIAL_CAPITAL_VALUE"
TRIAL_DURATION_PLACEHOLDER = "OWNER_RUNTIME_TRIAL_DURATION_VALUE"


@dataclass(frozen=True)
class OandaVacationProfitTrialPlanInput:
    contract_status: str
    live_sample_status: str
    autonomy_control_status: str
    compounding_permission_status: str
    trial_capital: Decimal = Decimal("200.00")
    max_total_drawdown_percent: Decimal = Decimal("5.00")
    max_daily_loss_percent: Decimal = Decimal("2.00")
    max_trade_risk_percent: Decimal = Decimal("0.50")
    unsafe_flags: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class OandaVacationProfitTrialPlanResult:
    version: str
    classification: str
    trial_capital_placeholder: str
    trial_duration_placeholder: str
    trial_capital: Decimal
    max_total_drawdown_percent: Decimal
    max_daily_loss_percent: Decimal
    max_trade_risk_percent: Decimal
    no_compounding: bool
    no_withdrawals: bool
    no_deposits: bool
    no_unattended_approval_yet: bool
    owner_review_required: bool
    evidence_required_before_trial: tuple[str, ...]
    abort_rules: tuple[str, ...]
    post_trial_review_requirements: tuple[str, ...]
    blocked_items: tuple[str, ...]
    plan_preview: Mapping[str, Any]
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


def build_sample_ready_for_review_input() -> OandaVacationProfitTrialPlanInput:
    return OandaVacationProfitTrialPlanInput(
        contract_status=OANDA_VACATION_PROFIT_READINESS_CONTRACT_READY,
        live_sample_status=OANDA_VACATION_PROFIT_LIVE_SAMPLE_READY_FOR_OWNER_REVIEW,
        autonomy_control_status=OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_READY_FOR_OWNER_REVIEW,
        compounding_permission_status=(
            OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_READY_FOR_FUTURE_OWNER_REVIEW
        ),
    )


def build_sample_no_live_sample_input() -> OandaVacationProfitTrialPlanInput:
    return OandaVacationProfitTrialPlanInput(
        contract_status=OANDA_VACATION_PROFIT_READINESS_CONTRACT_READY,
        live_sample_status="OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_NO_LIVE_SAMPLE",
        autonomy_control_status=OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_READY_FOR_OWNER_REVIEW,
        compounding_permission_status=(
            OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_READY_FOR_FUTURE_OWNER_REVIEW
        ),
    )


def build_sample_missing_autonomy_controls_input() -> OandaVacationProfitTrialPlanInput:
    return OandaVacationProfitTrialPlanInput(
        contract_status=OANDA_VACATION_PROFIT_READINESS_CONTRACT_READY,
        live_sample_status=OANDA_VACATION_PROFIT_LIVE_SAMPLE_READY_FOR_OWNER_REVIEW,
        autonomy_control_status="OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_REQUIRE_MORE_PROOF",
        compounding_permission_status=(
            OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_READY_FOR_FUTURE_OWNER_REVIEW
        ),
    )


def build_sample_compounding_blocked_input() -> OandaVacationProfitTrialPlanInput:
    return OandaVacationProfitTrialPlanInput(
        contract_status=OANDA_VACATION_PROFIT_READINESS_CONTRACT_READY,
        live_sample_status=OANDA_VACATION_PROFIT_LIVE_SAMPLE_READY_FOR_OWNER_REVIEW,
        autonomy_control_status=OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_READY_FOR_OWNER_REVIEW,
        compounding_permission_status=(
            "OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_BLOCKED_BY_DEFAULT"
        ),
    )


def build_sample_unsafe_input() -> OandaVacationProfitTrialPlanInput:
    return OandaVacationProfitTrialPlanInput(
        contract_status=OANDA_VACATION_PROFIT_READINESS_CONTRACT_READY,
        live_sample_status=OANDA_VACATION_PROFIT_LIVE_SAMPLE_READY_FOR_OWNER_REVIEW,
        autonomy_control_status=OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_READY_FOR_OWNER_REVIEW,
        compounding_permission_status=(
            OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_READY_FOR_FUTURE_OWNER_REVIEW
        ),
        unsafe_flags={"trial_plan_unsafe": True},
    )


def build_oanda_vacation_profit_trial_plan(
    plan_input: OandaVacationProfitTrialPlanInput | Mapping[str, Any] | None = None,
) -> OandaVacationProfitTrialPlanResult:
    active_input = _coerce_input(plan_input or build_sample_ready_for_review_input())
    blocked_items = _blocked_items(active_input)
    missing_items = _missing_items(active_input)
    if blocked_items:
        classification = OANDA_VACATION_PROFIT_TRIAL_PLAN_BLOCKED_UNSAFE
    elif missing_items:
        classification = OANDA_VACATION_PROFIT_TRIAL_PLAN_REQUIRE_MORE_PROOF
    else:
        classification = OANDA_VACATION_PROFIT_TRIAL_PLAN_READY_FOR_OWNER_REVIEW
    evidence_required = (
        "live_sample_gate_ready_for_owner_review",
        "autonomy_control_gate_ready_for_owner_review",
        "compounding_permission_future_owner_review_ready",
        "owner_manual_review_before_any_trial",
    )
    abort_rules = (
        "abort_if_drawdown_limit_reached",
        "abort_if_daily_stop_reached",
        "abort_if_trade_risk_exceeds_contract",
        "abort_if_account_boundary_unclear",
        "abort_if_credential_boundary_unclear",
        "abort_if_monitoring_or_alerting_not_confirmed",
        "abort_if_owner_sos_escalation_not_confirmed",
    )
    post_trial_requirements = (
        "capture_realized_pl_summary",
        "capture_drawdown_summary",
        "capture_trade_count_summary",
        "capture_reconciliation_summary",
        "capture_journal_summary",
        "route_result_back_to_evidence_ledger",
    )
    preview = {
        "preview_only": True,
        "trial_capital_placeholder": TRIAL_CAPITAL_PLACEHOLDER,
        "trial_duration_placeholder": TRIAL_DURATION_PLACEHOLDER,
        "maximum_allowed_drawdown": active_input.max_total_drawdown_percent,
        "daily_stop": active_input.max_daily_loss_percent,
        "max_trade_risk": active_input.max_trade_risk_percent,
        "no_compounding": True,
        "no_withdrawals": True,
        "no_deposits": True,
        "no_unattended_approval_yet": True,
        "owner_review_required": True,
    }
    protected_flags = protected_flags_false()
    return OandaVacationProfitTrialPlanResult(
        version=VERSION,
        classification=classification,
        trial_capital_placeholder=TRIAL_CAPITAL_PLACEHOLDER,
        trial_duration_placeholder=TRIAL_DURATION_PLACEHOLDER,
        trial_capital=active_input.trial_capital,
        max_total_drawdown_percent=active_input.max_total_drawdown_percent,
        max_daily_loss_percent=active_input.max_daily_loss_percent,
        max_trade_risk_percent=active_input.max_trade_risk_percent,
        no_compounding=True,
        no_withdrawals=True,
        no_deposits=True,
        no_unattended_approval_yet=True,
        owner_review_required=True,
        evidence_required_before_trial=evidence_required + missing_items,
        abort_rules=abort_rules,
        post_trial_review_requirements=post_trial_requirements,
        blocked_items=blocked_items,
        plan_preview=_jsonable(preview),
        owner_warning=EXACT_OWNER_WARNING,
        vacation_warning=EXACT_VACATION_WARNING,
        protected_flags=protected_flags,
        **protected_flags,
    )


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return _jsonable(result)


def to_operator_text(result: OandaVacationProfitTrialPlanResult) -> str:
    return "\n".join(
        (
            f"Vacation profit trial plan status: {result.classification}.",
            f"Trial capital placeholder: {result.trial_capital_placeholder}.",
            f"Trial duration placeholder: {result.trial_duration_placeholder}.",
            "This is a non-executing owner-review trial plan.",
            result.owner_warning,
            result.vacation_warning,
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
        )
    )


def to_markdown(result: OandaVacationProfitTrialPlanResult) -> str:
    rows = [
        "# AIOS Forex OANDA Vacation Profit Trial Plan V1",
        "",
        f"- Classification: `{result.classification}`",
        f"- Trial capital placeholder: `{result.trial_capital_placeholder}`",
        f"- Trial duration placeholder: `{result.trial_duration_placeholder}`",
        f"- Maximum allowed drawdown: `{_jsonable(result.max_total_drawdown_percent)}`",
        f"- Daily stop: `{_jsonable(result.max_daily_loss_percent)}`",
        f"- Max trade risk: `{_jsonable(result.max_trade_risk_percent)}`",
        "- No compounding.",
        "- No withdrawals.",
        "- No deposits.",
        "- No unattended approval yet.",
        "- Owner review required.",
        "",
        "## Evidence Required Before Trial",
    ]
    rows.extend(f"- `{item}`" for item in result.evidence_required_before_trial)
    rows.extend(("", "## Abort Rules"))
    rows.extend(f"- `{item}`" for item in result.abort_rules)
    rows.extend(("", "## Post-Trial Review Requirements"))
    rows.extend(f"- `{item}`" for item in result.post_trial_review_requirements)
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
    value: OandaVacationProfitTrialPlanInput | Mapping[str, Any],
) -> OandaVacationProfitTrialPlanInput:
    if isinstance(value, OandaVacationProfitTrialPlanInput):
        return value
    raw = dict(value)
    return OandaVacationProfitTrialPlanInput(
        contract_status=str(raw.get("contract_status", "")),
        live_sample_status=str(raw.get("live_sample_status", "")),
        autonomy_control_status=str(raw.get("autonomy_control_status", "")),
        compounding_permission_status=str(raw.get("compounding_permission_status", "")),
        trial_capital=_decimal(raw.get("trial_capital", "200.00")),
        max_total_drawdown_percent=_decimal(
            raw.get("max_total_drawdown_percent", "5.00")
        ),
        max_daily_loss_percent=_decimal(raw.get("max_daily_loss_percent", "2.00")),
        max_trade_risk_percent=_decimal(raw.get("max_trade_risk_percent", "0.50")),
        unsafe_flags=dict(raw.get("unsafe_flags", {})),
    )


def _missing_items(active_input: OandaVacationProfitTrialPlanInput) -> tuple[str, ...]:
    missing: list[str] = []
    if active_input.contract_status != OANDA_VACATION_PROFIT_READINESS_CONTRACT_READY:
        missing.append("contract_ready")
    if (
        active_input.live_sample_status
        != OANDA_VACATION_PROFIT_LIVE_SAMPLE_READY_FOR_OWNER_REVIEW
    ):
        missing.append("live_sample_ready_for_owner_review")
    if (
        active_input.autonomy_control_status
        != OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_READY_FOR_OWNER_REVIEW
    ):
        missing.append("autonomy_controls_ready_for_owner_review")
    if (
        active_input.compounding_permission_status
        != OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_READY_FOR_FUTURE_OWNER_REVIEW
    ):
        missing.append("compounding_permission_future_owner_review_ready")
    return tuple(missing)


def _blocked_items(active_input: OandaVacationProfitTrialPlanInput) -> tuple[str, ...]:
    if any(bool(value) for value in active_input.unsafe_flags.values()):
        return ("unsafe_trial_plan_flag",)
    return ()


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

