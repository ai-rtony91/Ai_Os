"""Proof-only autonomy control gate for vacation profit readiness review."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from automation.forex_engine.oanda_vacation_profit_readiness_contract_v1 import (
    EXACT_OWNER_WARNING,
    EXACT_VACATION_WARNING,
    protected_flags_false,
)


VERSION = "oanda_vacation_profit_autonomy_control_gate_v1"

OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_READY_FOR_OWNER_REVIEW = (
    "OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_READY_FOR_OWNER_REVIEW"
)
OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_REQUIRE_MORE_PROOF = (
    "OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_REQUIRE_MORE_PROOF"
)
OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_BLOCKED_UNSAFE = (
    "OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_BLOCKED_UNSAFE"
)

REQUIRED_CONTROL_FIELDS = (
    "kill_switch_proof",
    "timeout_abort_proof",
    "final_disarm_proof",
    "duplicate_order_guard_proof",
    "no_autonomous_loop_proof",
    "monitoring_proof",
    "alerting_proof",
    "owner_sos_escalation_proof",
    "read_only_reconciliation_proof",
    "post_trade_evidence_proof",
    "max_loss_hard_stop_proof",
    "daily_loss_hard_stop_proof",
    "stuck_order_handling_proof",
    "network_failure_handling_proof",
)


@dataclass(frozen=True)
class OandaVacationProfitAutonomyControlGateInput:
    kill_switch_proof_count: int = 3
    timeout_abort_proof_count: int = 3
    final_disarm_proof_count: int = 3
    duplicate_order_guard_proof_count: int = 3
    reconciliation_proof_count: int = 3
    min_kill_switch_proof_count: int = 3
    min_disarm_proof_count: int = 3
    min_reconciliation_proof_count: int = 3
    control_proofs: Mapping[str, bool] = field(
        default_factory=lambda: {name: True for name in REQUIRED_CONTROL_FIELDS}
    )
    unsafe_flags: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class OandaVacationProfitAutonomyControlGateResult:
    version: str
    classification: str
    kill_switch_proof_count: int
    timeout_abort_proof_count: int
    final_disarm_proof_count: int
    duplicate_order_guard_proof_count: int
    reconciliation_proof_count: int
    required_control_fields: tuple[str, ...]
    missing_control_proofs: tuple[str, ...]
    blocked_items: tuple[str, ...]
    owner_review_allowed: bool
    unattended_operation_approved: bool
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


def build_sample_ready_for_review_input() -> OandaVacationProfitAutonomyControlGateInput:
    return OandaVacationProfitAutonomyControlGateInput()


def build_sample_no_live_sample_input() -> OandaVacationProfitAutonomyControlGateInput:
    return OandaVacationProfitAutonomyControlGateInput()


def build_sample_missing_autonomy_controls_input() -> OandaVacationProfitAutonomyControlGateInput:
    proofs = {name: True for name in REQUIRED_CONTROL_FIELDS}
    for name in (
        "kill_switch_proof",
        "timeout_abort_proof",
        "monitoring_proof",
        "alerting_proof",
        "network_failure_handling_proof",
    ):
        proofs[name] = False
    return OandaVacationProfitAutonomyControlGateInput(
        kill_switch_proof_count=0,
        timeout_abort_proof_count=0,
        final_disarm_proof_count=1,
        duplicate_order_guard_proof_count=1,
        reconciliation_proof_count=1,
        control_proofs=proofs,
    )


def build_sample_compounding_blocked_input() -> OandaVacationProfitAutonomyControlGateInput:
    return OandaVacationProfitAutonomyControlGateInput()


def build_sample_unsafe_input() -> OandaVacationProfitAutonomyControlGateInput:
    return OandaVacationProfitAutonomyControlGateInput(
        unsafe_flags={"autonomy_control_unsafe": True}
    )


def evaluate_oanda_vacation_profit_autonomy_control_gate(
    gate_input: OandaVacationProfitAutonomyControlGateInput | Mapping[str, Any] | None = None,
) -> OandaVacationProfitAutonomyControlGateResult:
    active_input = _coerce_input(gate_input or build_sample_ready_for_review_input())
    missing = _missing_control_proofs(active_input)
    blocked = _blocked_items(active_input)
    if blocked:
        classification = OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_BLOCKED_UNSAFE
    elif missing:
        classification = OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_REQUIRE_MORE_PROOF
    else:
        classification = OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_READY_FOR_OWNER_REVIEW
    protected_flags = protected_flags_false()
    return OandaVacationProfitAutonomyControlGateResult(
        version=VERSION,
        classification=classification,
        kill_switch_proof_count=active_input.kill_switch_proof_count,
        timeout_abort_proof_count=active_input.timeout_abort_proof_count,
        final_disarm_proof_count=active_input.final_disarm_proof_count,
        duplicate_order_guard_proof_count=active_input.duplicate_order_guard_proof_count,
        reconciliation_proof_count=active_input.reconciliation_proof_count,
        required_control_fields=REQUIRED_CONTROL_FIELDS,
        missing_control_proofs=missing,
        blocked_items=blocked,
        owner_review_allowed=classification
        == OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_READY_FOR_OWNER_REVIEW,
        unattended_operation_approved=False,
        owner_warning=EXACT_OWNER_WARNING,
        vacation_warning=EXACT_VACATION_WARNING,
        protected_flags=protected_flags,
        **protected_flags,
    )


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return _jsonable(result)


def to_operator_text(result: OandaVacationProfitAutonomyControlGateResult) -> str:
    return "\n".join(
        (
            f"Vacation profit autonomy controls status: {result.classification}.",
            "Autonomy controls are proof for owner review only.",
            "Unattended operation remains blocked.",
            result.owner_warning,
            result.vacation_warning,
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
        )
    )


def to_markdown(result: OandaVacationProfitAutonomyControlGateResult) -> str:
    rows = [
        "# AIOS Forex OANDA Vacation Profit Autonomy Control Gate V1",
        "",
        f"- Classification: `{result.classification}`",
        f"- Owner review allowed: `{str(result.owner_review_allowed).lower()}`",
        "- Unattended operation approved: `false`",
        "",
        "## Required Controls",
    ]
    rows.extend(f"- `{name}`" for name in result.required_control_fields)
    rows.extend(("", "## Missing Control Proofs"))
    rows.extend(f"- `{name}`" for name in result.missing_control_proofs)
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
    value: OandaVacationProfitAutonomyControlGateInput | Mapping[str, Any],
) -> OandaVacationProfitAutonomyControlGateInput:
    if isinstance(value, OandaVacationProfitAutonomyControlGateInput):
        return value
    raw = dict(value)
    control_proofs = dict(raw.get("control_proofs", {}))
    return OandaVacationProfitAutonomyControlGateInput(
        kill_switch_proof_count=int(raw.get("kill_switch_proof_count", 0)),
        timeout_abort_proof_count=int(raw.get("timeout_abort_proof_count", 0)),
        final_disarm_proof_count=int(raw.get("final_disarm_proof_count", 0)),
        duplicate_order_guard_proof_count=int(
            raw.get("duplicate_order_guard_proof_count", 0)
        ),
        reconciliation_proof_count=int(raw.get("reconciliation_proof_count", 0)),
        min_kill_switch_proof_count=int(raw.get("min_kill_switch_proof_count", 3)),
        min_disarm_proof_count=int(raw.get("min_disarm_proof_count", 3)),
        min_reconciliation_proof_count=int(
            raw.get("min_reconciliation_proof_count", 3)
        ),
        control_proofs={
            name: bool(control_proofs.get(name, False))
            for name in REQUIRED_CONTROL_FIELDS
        },
        unsafe_flags=dict(raw.get("unsafe_flags", {})),
    )


def _missing_control_proofs(
    active_input: OandaVacationProfitAutonomyControlGateInput,
) -> tuple[str, ...]:
    missing = [
        name
        for name in REQUIRED_CONTROL_FIELDS
        if not bool(active_input.control_proofs.get(name, False))
    ]
    if active_input.kill_switch_proof_count < active_input.min_kill_switch_proof_count:
        missing.append("kill_switch_proof_count")
    if active_input.final_disarm_proof_count < active_input.min_disarm_proof_count:
        missing.append("final_disarm_proof_count")
    if active_input.reconciliation_proof_count < active_input.min_reconciliation_proof_count:
        missing.append("reconciliation_proof_count")
    if active_input.timeout_abort_proof_count < active_input.min_disarm_proof_count:
        missing.append("timeout_abort_proof_count")
    if active_input.duplicate_order_guard_proof_count < active_input.min_disarm_proof_count:
        missing.append("duplicate_order_guard_proof_count")
    return tuple(dict.fromkeys(missing))


def _blocked_items(
    active_input: OandaVacationProfitAutonomyControlGateInput,
) -> tuple[str, ...]:
    if any(bool(value) for value in active_input.unsafe_flags.values()):
        return ("unsafe_autonomy_control_flag",)
    return ()


def _jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value

