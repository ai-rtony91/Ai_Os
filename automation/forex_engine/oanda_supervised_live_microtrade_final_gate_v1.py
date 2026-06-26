"""Final owner-run review gate for one supervised live microtrade package."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Any, Mapping


VERSION = "oanda_supervised_live_microtrade_final_gate_v1"
PACKET_ID = "AIOS-FOREX-OANDA-SUPERVISED-LIVE-MICROTRADE-FINAL-OWNER-RUN-PATH-V1"

EXACT_OWNER_WARNING = "Do not execute unless Anthony explicitly approves."
EXACT_LIVE_WARNING = (
    "Supervised live microtrade final owner-run review only. Codex is not "
    "authorized to execute, call a broker, access credentials, place orders, "
    "approve live trading, compound profits, or move money."
)
EXACT_ONE_SENTENCE_ANSWER = (
    "AIOS can now prepare the final owner-run review package for one tiny "
    "supervised live microtrade, but live execution remains blocked until "
    "Anthony explicitly approves and performs the action outside Codex."
)
EXACT_NEXT_OWNER_ACTION = (
    "Review the owner-runbook, confirm every live boundary, and decide outside "
    "Codex whether to manually execute one tiny supervised live microtrade."
)
EXACT_NEXT_CODEX_PACKET = (
    "AIOS-FOREX-OANDA-OWNER-RUN-LIVE-MICROTRADE-RESULT-CAPTURE-V1"
)

OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_READY_FOR_OWNER_REVIEW = (
    "OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_READY_FOR_OWNER_REVIEW"
)
OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_REQUIRE_MORE_EVIDENCE = (
    "OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_REQUIRE_MORE_EVIDENCE"
)
OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_BLOCKED_UNSAFE = (
    "OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_BLOCKED_UNSAFE"
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

REQUIRED_READY_CHECKS = (
    "repeated_expectancy_proof_ready",
    "live_evidence_gap_bridge_ready",
    "vacation_profit_readiness_review_gate_present",
    "live_sample_status_accounted_for",
    "autonomy_controls_accounted_for",
    "compounding_permission_still_false",
    "owner_final_approval_still_required",
    "kill_switch_proof_present",
    "timeout_abort_proof_present",
    "rollback_plan_present",
    "final_disarm_proof_present",
    "duplicate_order_guard_present",
    "one_shot_scope_present",
    "no_compounding_scope_present",
    "no_bank_movement_scope_present",
    "no_autonomous_loop_scope_present",
    "post_trade_capture_plan_present",
    "codex_execution_authorization_false",
)


@dataclass(frozen=True)
class OandaSupervisedLiveMicrotradeFinalGateInput:
    checks: Mapping[str, bool]
    proof_label: str = "deterministic_final_owner_run_review_sample"
    unsafe_flags: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class OandaSupervisedLiveMicrotradeFinalGateResult:
    version: str
    packet_id: str
    classification: str
    owner_final_review_allowed: bool
    ready_checks: tuple[str, ...]
    missing_checks: tuple[str, ...]
    blocked_checks: tuple[str, ...]
    proof_summary: Mapping[str, Any]
    next_safe_action: str
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


def build_sample_ready_input() -> OandaSupervisedLiveMicrotradeFinalGateInput:
    return OandaSupervisedLiveMicrotradeFinalGateInput(
        checks={name: True for name in REQUIRED_READY_CHECKS}
    )


def build_sample_missing_input() -> OandaSupervisedLiveMicrotradeFinalGateInput:
    checks = {name: True for name in REQUIRED_READY_CHECKS}
    for name in (
        "live_sample_status_accounted_for",
        "post_trade_capture_plan_present",
        "rollback_plan_present",
    ):
        checks[name] = False
    return OandaSupervisedLiveMicrotradeFinalGateInput(checks=checks)


def build_sample_unsafe_input() -> OandaSupervisedLiveMicrotradeFinalGateInput:
    checks = {name: True for name in REQUIRED_READY_CHECKS}
    checks["codex_execution_authorization_false"] = False
    return OandaSupervisedLiveMicrotradeFinalGateInput(
        checks=checks,
        unsafe_flags={"codex_execution_authorization_not_false": True},
    )


def evaluate_oanda_supervised_live_microtrade_final_gate(
    gate_input: OandaSupervisedLiveMicrotradeFinalGateInput | Mapping[str, Any] | None = None,
) -> OandaSupervisedLiveMicrotradeFinalGateResult:
    active_input = _coerce_input(gate_input or build_sample_ready_input())
    ready_checks = tuple(
        check for check in REQUIRED_READY_CHECKS if bool(active_input.checks.get(check, False))
    )
    missing_checks = tuple(
        check for check in REQUIRED_READY_CHECKS if not bool(active_input.checks.get(check, False))
    )
    blocked_checks = _blocked_checks(active_input)
    if blocked_checks:
        classification = OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_BLOCKED_UNSAFE
        next_safe_action = "Stop and repair unsafe final owner-run gate conditions."
    elif missing_checks:
        classification = OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_REQUIRE_MORE_EVIDENCE
        next_safe_action = "Complete the missing proof checks before owner final review."
    else:
        classification = OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_READY_FOR_OWNER_REVIEW
        next_safe_action = (
            "Anthony may review the final package; this still is not live execution approval."
        )
    protected_flags = protected_flags_false()
    return OandaSupervisedLiveMicrotradeFinalGateResult(
        version=VERSION,
        packet_id=PACKET_ID,
        classification=classification,
        owner_final_review_allowed=classification
        == OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_READY_FOR_OWNER_REVIEW,
        ready_checks=ready_checks,
        missing_checks=missing_checks,
        blocked_checks=blocked_checks,
        proof_summary={
            "proof_label": active_input.proof_label,
            "required_check_count": len(REQUIRED_READY_CHECKS),
            "ready_check_count": len(ready_checks),
            "missing_check_count": len(missing_checks),
            "blocked_check_count": len(blocked_checks),
            "final_owner_approval_required": True,
            "live_execution_allowed": False,
        },
        next_safe_action=next_safe_action,
        owner_warning=EXACT_OWNER_WARNING,
        live_warning=EXACT_LIVE_WARNING,
        protected_flags=protected_flags,
        **protected_flags,
    )


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return _jsonable(result)


def to_operator_text(result: OandaSupervisedLiveMicrotradeFinalGateResult) -> str:
    return "\n".join(
        (
            f"Final owner-run gate status: {result.classification}.",
            f"Owner final review allowed: {str(result.owner_final_review_allowed).lower()}.",
            "Final review is not live execution approval.",
            result.owner_warning,
            result.live_warning,
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
        )
    )


def to_markdown(result: OandaSupervisedLiveMicrotradeFinalGateResult) -> str:
    rows = [
        "# AIOS Forex OANDA Supervised Live Microtrade Final Gate V1",
        "",
        f"- Classification: `{result.classification}`",
        f"- Owner final review allowed: `{str(result.owner_final_review_allowed).lower()}`",
        "- Final review is not live execution approval.",
        "",
        "## Ready Checks",
    ]
    rows.extend(f"- `{item}`" for item in result.ready_checks)
    rows.extend(("", "## Missing Checks"))
    rows.extend(f"- `{item}`" for item in result.missing_checks)
    rows.extend(("", "## Blocked Checks"))
    rows.extend(f"- `{item}`" for item in result.blocked_checks)
    rows.extend(_markdown_safety_lines())
    return "\n".join(rows) + "\n"


def protected_flags_false() -> dict[str, bool]:
    return dict(PROTECTED_FLAGS_FALSE)


def markdown_safety_lines() -> list[str]:
    return _markdown_safety_lines()


def jsonable(value: Any) -> Any:
    return _jsonable(value)


def _coerce_input(
    value: OandaSupervisedLiveMicrotradeFinalGateInput | Mapping[str, Any],
) -> OandaSupervisedLiveMicrotradeFinalGateInput:
    if isinstance(value, OandaSupervisedLiveMicrotradeFinalGateInput):
        return value
    raw = dict(value)
    return OandaSupervisedLiveMicrotradeFinalGateInput(
        checks=dict(raw.get("checks", {})),
        proof_label=str(raw.get("proof_label", "deterministic_final_owner_run_review_sample")),
        unsafe_flags=dict(raw.get("unsafe_flags", {})),
    )


def _blocked_checks(
    gate_input: OandaSupervisedLiveMicrotradeFinalGateInput,
) -> tuple[str, ...]:
    blocked = [name for name, value in gate_input.unsafe_flags.items() if bool(value)]
    for flag_name in PROTECTED_FLAG_NAMES:
        if flag_name in gate_input.checks and bool(gate_input.checks[flag_name]):
            blocked.append(flag_name)
    if not bool(gate_input.checks.get("compounding_permission_still_false", False)):
        blocked.append("compounding_permission_not_false")
    if not bool(gate_input.checks.get("codex_execution_authorization_false", False)):
        blocked.append("codex_execution_authorization_not_false")
    return tuple(dict.fromkeys(blocked))


def _markdown_safety_lines() -> list[str]:
    return [
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

