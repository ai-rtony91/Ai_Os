"""Capital flow policy simulation V1.

This module builds deterministic treasury recommendations from sanitized
balances and policy limits. It never reads credentials, account identifiers, or
environment variables, never calls broker/bank/payment APIs, never mutates
balances as truth, and never claims a transfer completed.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


CAPITAL_FLOW_DISPLAY_ONLY = "CAPITAL_FLOW_DISPLAY_ONLY"
CAPITAL_FLOW_POLICY_READY = "CAPITAL_FLOW_POLICY_READY"
CAPITAL_FLOW_BLOCKED_BY_APPROVAL = "CAPITAL_FLOW_BLOCKED_BY_APPROVAL"
CAPITAL_FLOW_BLOCKED_BY_CONNECTOR_PROOF = "CAPITAL_FLOW_BLOCKED_BY_CONNECTOR_PROOF"
CAPITAL_FLOW_FROZEN_BY_RISK = "CAPITAL_FLOW_FROZEN_BY_RISK"
CAPITAL_FLOW_MAINTENANCE_ONLY = "CAPITAL_FLOW_MAINTENANCE_ONLY"

WITHDRAWAL_REQUEST_DRAFT_READY = "WITHDRAWAL_REQUEST_DRAFT_READY"
WITHDRAWAL_BLOCKED_BY_LIMIT = "WITHDRAWAL_BLOCKED_BY_LIMIT"
WITHDRAWAL_BLOCKED_BY_APPROVAL = "WITHDRAWAL_BLOCKED_BY_APPROVAL"
WITHDRAWAL_BLOCKED_BY_CONNECTOR_PROOF = "WITHDRAWAL_BLOCKED_BY_CONNECTOR_PROOF"

RESUPPLY_REQUEST_DRAFT_READY = "RESUPPLY_REQUEST_DRAFT_READY"
RESUPPLY_NOT_NEEDED = "RESUPPLY_NOT_NEEDED"
RESUPPLY_BLOCKED_BY_APPROVAL = "RESUPPLY_BLOCKED_BY_APPROVAL"
RESUPPLY_BLOCKED_BY_CONNECTOR_PROOF = "RESUPPLY_BLOCKED_BY_CONNECTOR_PROOF"

COMPOUND_IN_PLACE_DRAFT_READY = "COMPOUND_IN_PLACE_DRAFT_READY"
COMPOUND_TARGET_NOT_REACHED = "COMPOUND_TARGET_NOT_REACHED"
COMPOUND_BLOCKED_BY_RISK = "COMPOUND_BLOCKED_BY_RISK"
COMPOUND_BLOCKED_BY_APPROVAL = "COMPOUND_BLOCKED_BY_APPROVAL"

PROFIT_SWEEP_DRAFT_READY = "PROFIT_SWEEP_DRAFT_READY"
PROFIT_SWEEP_NOT_NEEDED = "PROFIT_SWEEP_NOT_NEEDED"
PROFIT_SWEEP_BLOCKED_BY_APPROVAL = "PROFIT_SWEEP_BLOCKED_BY_APPROVAL"
PROFIT_SWEEP_BLOCKED_BY_CONNECTOR_PROOF = "PROFIT_SWEEP_BLOCKED_BY_CONNECTOR_PROOF"

TREASURY_AUTOMATION_NOT_ACTIVE = "TREASURY_AUTOMATION_NOT_ACTIVE"
TREASURY_AUTOMATION_POLICY_ONLY = "TREASURY_AUTOMATION_POLICY_ONLY"
TREASURY_AUTOMATION_REQUIRES_FUTURE_CONNECTOR = "TREASURY_AUTOMATION_REQUIRES_FUTURE_CONNECTOR"
TREASURY_AUTOMATION_REQUIRES_HUMAN_APPROVAL = "TREASURY_AUTOMATION_REQUIRES_HUMAN_APPROVAL"

MONEY_RELEVANT_VISIBLE = "MONEY_RELEVANT_VISIBLE"
MONEY_RELEVANT_COLLAPSED = "MONEY_RELEVANT_COLLAPSED"
NOT_MONEY_RELEVANT_HIDDEN_UNLESS_BLOCKING = "NOT_MONEY_RELEVANT_HIDDEN_UNLESS_BLOCKING"
MONEY_LADDER_100K_GOAL_SIMULATION_ONLY = "MONEY_LADDER_100K_GOAL_SIMULATION_ONLY"

HOLD = "HOLD"
DRAFT_WITHDRAWAL_REQUEST = "DRAFT_WITHDRAWAL_REQUEST"
DRAFT_DEPOSIT_REQUEST = "DRAFT_DEPOSIT_REQUEST"
DRAFT_RESUPPLY_REQUEST = "DRAFT_RESUPPLY_REQUEST"
DRAFT_PROFIT_SWEEP_REQUEST = "DRAFT_PROFIT_SWEEP_REQUEST"
DRAFT_COMPOUND_IN_PLACE_REQUEST = "DRAFT_COMPOUND_IN_PLACE_REQUEST"
FREEZE_CAPITAL_FLOW = "FREEZE_CAPITAL_FLOW"
NEEDS_HUMAN_APPROVAL = "NEEDS_HUMAN_APPROVAL"
NEEDS_BROKER_OR_BANK_CONNECTOR_PROOF = "NEEDS_BROKER_OR_BANK_CONNECTOR_PROOF"
NEEDS_MAINTENANCE_WINDOW = "NEEDS_MAINTENANCE_WINDOW"

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / "Reports" / "forex_delivery"
REPORT_PATHS = {
    "money_goal_ladder": REPORTS_DIR / "AIOS_MONEY_COCKPIT_100K_GOAL_LADDER_V11.md",
    "simulation_range": REPORTS_DIR / "AIOS_CAPITAL_FLOW_POLICY_SIMULATION_RANGE_V11.md",
    "money_relevance": REPORTS_DIR / "AIOS_MONEY_RELEVANCE_DASHBOARD_RULE_V11.md",
}

ALLOWED_ACCOUNT_ALIASES = (
    "TRADING_FLOAT",
    "RESERVE_ACCOUNT",
    "PROFIT_VAULT",
    "TAX_BUCKET",
    "OPERATING_ACCOUNT",
    "WITHDRAWAL_TARGET",
    "RESUPPLY_SOURCE",
    "COMPOUND_BUCKET",
)

SCENARIO_BALANCES = (
    0.99,
    1.00,
    5.00,
    10.00,
    25.00,
    50.00,
    100.00,
    250.00,
    500.00,
    1_000.00,
    2_500.00,
    5_000.00,
    10_000.00,
    25_000.00,
    50_000.00,
    75_000.00,
    100_000.00,
)

DEFAULT_VISIBLE_MONEY_FIELDS = (
    "trading_float",
    "available_risk_budget",
    "daily_pl",
    "realized_pl",
    "equity",
    "drawdown",
    "daily_loss_left",
    "capital_cap",
    "sweep_amount",
    "resupply_need",
    "compounding_progress",
    "withdrawal_request_status",
    "broker_proof_status",
    "connector_proof_status",
    "transfer_approval_status",
    "next_money_action",
)

COLLAPSED_MONEY_FIELDS = (
    "raw_evidence_paths",
    "legal_governance_detail",
    "validator_logs",
    "repo_noise",
    "css_build_diagnostics",
    "stale_reports",
    "technical_detail",
)

SENSITIVE_KEYS = frozenset(
    {
        "token",
        "access_token",
        "refresh_token",
        "api_key",
        "apikey",
        "secret",
        "password",
        "credential",
        "credentials",
        "account_id",
        "account_identifier",
        "account_number",
        "bank_account",
        "routing_number",
        "card_number",
        "broker_account_id",
        "payment_secret",
        "raw_payload",
        "raw_request",
        "raw_response",
        "authorization",
    }
)

DEFAULT_INPUT_STATE: dict[str, Any] = {
    "trading_balance": 10_000.0,
    "reserve_balance": 5_000.0,
    "profit_vault_balance": 0.0,
    "tax_bucket_balance": 0.0,
    "operating_account_balance": 2_500.0,
    "equity": 10_000.0,
    "daily_pl": 0.0,
    "realized_pl": 0.0,
    "drawdown": 0.0,
    "daily_loss_limit": 250.0,
    "available_risk_budget": 100.0,
    "minimum_trading_float": 8_000.0,
    "maximum_trading_float": 12_000.0,
    "sweep_threshold": 1_000.0,
    "resupply_threshold": 8_000.0,
    "compounding_threshold": 2_000.0,
    "compounding_target": 15_000.0,
    "max_withdrawal_per_event": 2_500.0,
    "max_deposit_per_event": 2_500.0,
    "cooldown_minutes": 60,
    "maintenance_window": False,
    "emergency_freeze": False,
    "daily_loss_lockout": False,
    "broker_proof_status": "MISSING",
    "bank_proof_status": "MISSING",
    "payment_rail_proof_status": "MISSING",
    "live_trading_lock_status": "LIVE_LOCKED",
    "human_approval_status": "MISSING",
    "last_transfer_request_timestamp": "UNKNOWN",
    "account_aliases": ALLOWED_ACCOUNT_ALIASES,
}


def run_capital_flow_policy(
    input_state: dict[str, Any] | None = None,
    write_reports: bool = False,
) -> dict[str, Any]:
    """Build a deterministic, display-only treasury policy result."""

    state = _sanitize_state(input_state)
    explicit_input = input_state is not None
    sensitive_input_detected = _contains_sensitive_keys(input_state or {})
    scenarios = _build_scenarios(state)
    risk_frozen = state["emergency_freeze"] or state["daily_loss_lockout"] or sensitive_input_detected
    recommendations = _build_recommendations(state, scenarios, explicit_input, sensitive_input_detected)
    classifications = _classify(state, scenarios, explicit_input, sensitive_input_detected)
    requests = [] if risk_frozen else _build_request_previews(state, scenarios)
    simulation_ladder = _build_simulation_ladder(state)
    money_relevance_rule = _money_relevance_rule()
    result = {
        "schema": "AIOS_CAPITAL_FLOW_POLICY_V1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "input_was_supplied": explicit_input,
        "policy_inputs": state,
        "account_aliases": tuple(ALLOWED_ACCOUNT_ALIASES),
        "classifications": classifications,
        "money_ladder_status": MONEY_LADDER_100K_GOAL_SIMULATION_ONLY,
        "money_ladder_doctrine": {
            "goal_ceiling": "100000.00",
            "goal_ceiling_status": "SIMULATION_CEILING_NOT_GUARANTEE",
            "profit_guarantee": False,
            "return_guarantee": False,
            "custody_authority": False,
            "live_transfer_authority": False,
        },
        "range_simulation_status": "RANGE_SIMULATION_READY_0_99_TO_100000",
        "simulation_ladder": tuple(simulation_ladder),
        "money_relevance_rule": money_relevance_rule,
        "recommendations": tuple(recommendations),
        "request_previews": tuple(requests),
        "protected_gates": _protected_gates(state, sensitive_input_detected),
        "blocked_reasons": tuple(_blocked_reasons(state, classifications, sensitive_input_detected)),
        "safety_summary": _safety_summary(),
        "transfer_completion_claimed": False,
        "balance_mutation_performed": False,
        "next_safe_action": _next_safe_action(classifications),
        "reports": {
            "written": tuple(),
            "allowed_output_paths": tuple(_display_path(path) for path in REPORT_PATHS.values()),
        },
    }

    if write_reports:
        written = _write_reports(result)
        result["reports"] = {
            **result["reports"],
            "written": tuple(_display_path(path) for path in written),
        }

    return result


def _sanitize_state(input_state: Mapping[str, Any] | None) -> dict[str, Any]:
    state = dict(DEFAULT_INPUT_STATE)
    for key, value in (input_state or {}).items():
        if str(key).lower().strip() in SENSITIVE_KEYS:
            continue
        state[str(key)] = value

    aliases = tuple(str(alias).upper() for alias in state.get("account_aliases", ALLOWED_ACCOUNT_ALIASES))
    state["account_aliases"] = tuple(alias for alias in aliases if alias in ALLOWED_ACCOUNT_ALIASES)
    if not state["account_aliases"]:
        state["account_aliases"] = ALLOWED_ACCOUNT_ALIASES

    for key in (
        "trading_balance",
        "reserve_balance",
        "profit_vault_balance",
        "tax_bucket_balance",
        "operating_account_balance",
        "equity",
        "daily_pl",
        "realized_pl",
        "drawdown",
        "daily_loss_limit",
        "available_risk_budget",
        "minimum_trading_float",
        "maximum_trading_float",
        "sweep_threshold",
        "resupply_threshold",
        "compounding_threshold",
        "compounding_target",
        "max_withdrawal_per_event",
        "max_deposit_per_event",
    ):
        state[key] = _money(state.get(key))

    state["cooldown_minutes"] = max(0, int(_money(state.get("cooldown_minutes"))))
    state["maintenance_window"] = bool(state.get("maintenance_window", False))
    state["emergency_freeze"] = bool(state.get("emergency_freeze", False))
    state["daily_loss_lockout"] = bool(state.get("daily_loss_lockout", False))
    state["broker_proof_status"] = _upper(state.get("broker_proof_status"), "MISSING")
    state["bank_proof_status"] = _upper(state.get("bank_proof_status"), "MISSING")
    state["payment_rail_proof_status"] = _upper(state.get("payment_rail_proof_status"), "MISSING")
    state["live_trading_lock_status"] = _upper(state.get("live_trading_lock_status"), "LIVE_LOCKED")
    state["human_approval_status"] = _upper(state.get("human_approval_status"), "MISSING")
    state["last_transfer_request_timestamp"] = str(state.get("last_transfer_request_timestamp", "UNKNOWN"))
    return state


def _build_scenarios(state: Mapping[str, Any]) -> dict[str, Any]:
    trading_balance = state["trading_balance"]
    max_float = state["maximum_trading_float"]
    min_float = state["minimum_trading_float"]
    sweep_excess = max(0.0, trading_balance - max_float)
    resupply_gap = max(0.0, min_float - trading_balance)
    withdrawal_intent = max(0.0, _money(state.get("withdrawal_intent_amount", 0.0)))
    deposit_intent = max(0.0, _money(state.get("deposit_intent_amount", 0.0)))
    compound_gap = max(0.0, state["compounding_target"] - trading_balance)
    compound_ready = state["profit_vault_balance"] >= state["compounding_threshold"] and compound_gap > 0

    return {
        "sweep_needed": sweep_excess >= state["sweep_threshold"] or sweep_excess > 0,
        "sweep_amount": min(sweep_excess, state["max_withdrawal_per_event"]),
        "sweep_excess": sweep_excess,
        "resupply_needed": trading_balance <= state["resupply_threshold"] or resupply_gap > 0,
        "resupply_amount": min(max(resupply_gap, state["resupply_threshold"] - trading_balance), state["max_deposit_per_event"]),
        "withdrawal_intent": withdrawal_intent,
        "withdrawal_amount": min(withdrawal_intent, state["max_withdrawal_per_event"]),
        "withdrawal_over_limit": withdrawal_intent > state["max_withdrawal_per_event"],
        "deposit_intent": deposit_intent,
        "deposit_amount": min(deposit_intent, state["max_deposit_per_event"]),
        "compound_ready": compound_ready,
        "compound_amount": min(state["profit_vault_balance"], compound_gap, state["max_deposit_per_event"]),
    }


def _build_recommendations(
    state: Mapping[str, Any],
    scenarios: Mapping[str, Any],
    explicit_input: bool,
    sensitive_input_detected: bool,
) -> list[str]:
    recommendations: list[str] = []
    if state["emergency_freeze"] or state["daily_loss_lockout"] or sensitive_input_detected:
        return [FREEZE_CAPITAL_FLOW]

    if scenarios["withdrawal_intent"] > 0:
        recommendations.append(DRAFT_WITHDRAWAL_REQUEST)
    if scenarios["deposit_intent"] > 0:
        recommendations.append(DRAFT_DEPOSIT_REQUEST)
    if scenarios["resupply_needed"] and scenarios["resupply_amount"] > 0:
        recommendations.append(DRAFT_RESUPPLY_REQUEST)
    if scenarios["sweep_needed"] and scenarios["sweep_amount"] > 0:
        recommendations.append(DRAFT_PROFIT_SWEEP_REQUEST)
    if scenarios["compound_ready"] and scenarios["compound_amount"] > 0:
        recommendations.append(DRAFT_COMPOUND_IN_PLACE_REQUEST)

    if not recommendations:
        recommendations.append(HOLD)

    if any(item.startswith("DRAFT_") for item in recommendations):
        if not state["maintenance_window"]:
            recommendations.append(NEEDS_MAINTENANCE_WINDOW)
        if not _human_approved(state):
            recommendations.append(NEEDS_HUMAN_APPROVAL)
        if not _connector_current(state):
            recommendations.append(NEEDS_BROKER_OR_BANK_CONNECTOR_PROOF)

    if not explicit_input and HOLD not in recommendations:
        recommendations.append(HOLD)
    return _unique(recommendations)


def _classify(
    state: Mapping[str, Any],
    scenarios: Mapping[str, Any],
    explicit_input: bool,
    sensitive_input_detected: bool,
) -> dict[str, str]:
    risk_frozen = state["emergency_freeze"] or state["daily_loss_lockout"] or sensitive_input_detected
    has_transfer_preview = (
        scenarios["withdrawal_intent"] > 0
        or scenarios["deposit_intent"] > 0
        or scenarios["resupply_needed"]
        or scenarios["sweep_needed"]
        or scenarios["compound_ready"]
    )
    approval_ready = _human_approved(state)
    connector_ready = _connector_current(state)

    if not explicit_input:
        capital_status = CAPITAL_FLOW_DISPLAY_ONLY
    elif risk_frozen:
        capital_status = CAPITAL_FLOW_FROZEN_BY_RISK
    elif has_transfer_preview and not state["maintenance_window"]:
        capital_status = CAPITAL_FLOW_MAINTENANCE_ONLY
    elif has_transfer_preview and not approval_ready:
        capital_status = CAPITAL_FLOW_BLOCKED_BY_APPROVAL
    elif has_transfer_preview and not connector_ready:
        capital_status = CAPITAL_FLOW_BLOCKED_BY_CONNECTOR_PROOF
    else:
        capital_status = CAPITAL_FLOW_POLICY_READY

    return {
        "CAPITAL_FLOW_STATUS": capital_status,
        "WITHDRAWAL_STATUS": _withdrawal_status(state, scenarios, risk_frozen, approval_ready, connector_ready),
        "RESUPPLY_STATUS": _resupply_status(scenarios, risk_frozen, approval_ready, connector_ready),
        "COMPOUND_STATUS": _compound_status(scenarios, risk_frozen, approval_ready),
        "SWEEP_STATUS": _sweep_status(scenarios, risk_frozen, approval_ready, connector_ready),
        "TREASURY_AUTOMATION_STATUS": _treasury_automation_status(
            has_transfer_preview, approval_ready, connector_ready
        ),
        "MONEY_RELEVANCE_STATUS": MONEY_RELEVANT_VISIBLE,
    }


def _withdrawal_status(
    state: Mapping[str, Any],
    scenarios: Mapping[str, Any],
    risk_frozen: bool,
    approval_ready: bool,
    connector_ready: bool,
) -> str:
    if risk_frozen or scenarios["withdrawal_over_limit"]:
        return WITHDRAWAL_BLOCKED_BY_LIMIT
    if scenarios["withdrawal_intent"] <= 0 and not scenarios["sweep_needed"]:
        return WITHDRAWAL_BLOCKED_BY_APPROVAL
    if not approval_ready:
        return WITHDRAWAL_BLOCKED_BY_APPROVAL
    if not connector_ready:
        return WITHDRAWAL_BLOCKED_BY_CONNECTOR_PROOF
    return WITHDRAWAL_REQUEST_DRAFT_READY


def _resupply_status(
    scenarios: Mapping[str, Any],
    risk_frozen: bool,
    approval_ready: bool,
    connector_ready: bool,
) -> str:
    if not scenarios["resupply_needed"]:
        return RESUPPLY_NOT_NEEDED
    if risk_frozen or not approval_ready:
        return RESUPPLY_BLOCKED_BY_APPROVAL
    if not connector_ready:
        return RESUPPLY_BLOCKED_BY_CONNECTOR_PROOF
    return RESUPPLY_REQUEST_DRAFT_READY


def _compound_status(scenarios: Mapping[str, Any], risk_frozen: bool, approval_ready: bool) -> str:
    if not scenarios["compound_ready"]:
        return COMPOUND_TARGET_NOT_REACHED
    if risk_frozen:
        return COMPOUND_BLOCKED_BY_RISK
    if not approval_ready:
        return COMPOUND_BLOCKED_BY_APPROVAL
    return COMPOUND_IN_PLACE_DRAFT_READY


def _sweep_status(
    scenarios: Mapping[str, Any],
    risk_frozen: bool,
    approval_ready: bool,
    connector_ready: bool,
) -> str:
    if not scenarios["sweep_needed"]:
        return PROFIT_SWEEP_NOT_NEEDED
    if risk_frozen or not approval_ready:
        return PROFIT_SWEEP_BLOCKED_BY_APPROVAL
    if not connector_ready:
        return PROFIT_SWEEP_BLOCKED_BY_CONNECTOR_PROOF
    return PROFIT_SWEEP_DRAFT_READY


def _treasury_automation_status(
    has_transfer_preview: bool,
    approval_ready: bool,
    connector_ready: bool,
) -> str:
    if not has_transfer_preview:
        return TREASURY_AUTOMATION_POLICY_ONLY
    if not approval_ready:
        return TREASURY_AUTOMATION_REQUIRES_HUMAN_APPROVAL
    if not connector_ready:
        return TREASURY_AUTOMATION_REQUIRES_FUTURE_CONNECTOR
    return TREASURY_AUTOMATION_NOT_ACTIVE


def _build_request_previews(state: Mapping[str, Any], scenarios: Mapping[str, Any]) -> list[dict[str, Any]]:
    previews: list[dict[str, Any]] = []
    if scenarios["withdrawal_intent"] > 0:
        previews.append(_preview("WITHDRAWAL", scenarios["withdrawal_amount"], "TRADING_FLOAT", "OPERATING_ACCOUNT"))
    if scenarios["deposit_intent"] > 0:
        previews.append(_preview("DEPOSIT", scenarios["deposit_amount"], "OPERATING_ACCOUNT", "TRADING_FLOAT"))
    if scenarios["resupply_needed"] and scenarios["resupply_amount"] > 0:
        previews.append(_preview("RESUPPLY", scenarios["resupply_amount"], "RESERVE_ACCOUNT", "TRADING_FLOAT"))
    if scenarios["sweep_needed"] and scenarios["sweep_amount"] > 0:
        previews.append(_preview("PROFIT_SWEEP", scenarios["sweep_amount"], "TRADING_FLOAT", "PROFIT_VAULT"))
    if scenarios["compound_ready"] and scenarios["compound_amount"] > 0:
        previews.append(_preview("COMPOUND_IN_PLACE", scenarios["compound_amount"], "PROFIT_VAULT", "TRADING_FLOAT"))
    return previews


def _build_simulation_ladder(state: Mapping[str, Any]) -> list[dict[str, Any]]:
    ladder: list[dict[str, Any]] = []
    for balance in SCENARIO_BALANCES:
        tier = _balance_tier(balance)
        below_floor = balance < state["minimum_trading_float"]
        above_cap = balance > state["maximum_trading_float"]
        sweep_amount = min(max(0.0, balance - state["maximum_trading_float"]), state["max_withdrawal_per_event"])
        resupply_amount = min(max(0.0, state["minimum_trading_float"] - balance), state["max_deposit_per_event"])
        compound_ready = balance >= state["compounding_threshold"] and balance < state["compounding_target"]
        has_money_action = above_cap or below_floor or compound_ready
        risk_frozen = state["emergency_freeze"] or state["daily_loss_lockout"]
        withdrawal_gate = "STRICT_CAP_REQUIRED" if balance > state["max_withdrawal_per_event"] else "WITHIN_EVENT_LIMIT"
        connector_gate = "CONNECTOR_PROOF_CURRENT" if _connector_current(state) else NEEDS_BROKER_OR_BANK_CONNECTOR_PROOF
        approval_gate = "APPROVED_FOR_DRAFT" if _human_approved(state) else NEEDS_HUMAN_APPROVAL
        risk_cap = min(max(0.0, balance * 0.01), state["available_risk_budget"])
        goal_milestone_status = "SIMULATION_CEILING_NOT_GUARANTEE" if balance == 100_000.00 else "SIMULATION_STEP"

        if risk_frozen:
            next_action = "capital flow frozen by risk gate"
        elif balance == 100_000.00:
            next_action = "treat 100000 as simulation ceiling; enforce strict caps and human-approved sweep preview"
        elif above_cap:
            next_action = "draft capped profit sweep preview"
        elif below_floor:
            next_action = "draft capped resupply preview"
        elif compound_ready:
            next_action = "review compound-in-place preview"
        else:
            next_action = "hold trading float inside policy range"

        ladder.append(
            {
                "balance": f"{balance:.2f}",
                "capital_tier": tier,
                "balance_tier": tier,
                "trading_float_status": _trading_float_status(balance, state),
                "risk_cap": f"{risk_cap:.2f}",
                "risk_cap_status": "FROZEN" if risk_frozen else "SIMULATED_CAP_ONLY",
                "sweep_recommendation": DRAFT_PROFIT_SWEEP_REQUEST if above_cap and not risk_frozen else HOLD,
                "sweep_amount": f"{sweep_amount:.2f}",
                "resupply_recommendation": DRAFT_RESUPPLY_REQUEST if below_floor and not risk_frozen else RESUPPLY_NOT_NEEDED,
                "resupply_amount": f"{resupply_amount:.2f}",
                "compound_recommendation": DRAFT_COMPOUND_IN_PLACE_REQUEST if compound_ready and not risk_frozen else COMPOUND_TARGET_NOT_REACHED,
                "withdrawal_gate": withdrawal_gate,
                "withdrawal_limit_status": withdrawal_gate,
                "risk_freeze_status": "FROZEN" if risk_frozen else "CLEAR",
                "maintenance_window_action": NEEDS_MAINTENANCE_WINDOW if has_money_action and not state["maintenance_window"] else "MAINTENANCE_WINDOW_OK",
                "approval_gate": approval_gate,
                "approval_gate_status": approval_gate,
                "connector_proof_gate": connector_gate,
                "connector_proof_status": connector_gate,
                "goal_milestone_status": goal_milestone_status,
                "profit_guarantee": False,
                "transfer_authority": False,
                "next_money_action": next_action,
                "live_transfer_ready": False,
            }
        )
    return ladder


def _balance_tier(balance: float) -> str:
    if balance <= 10:
        return "MICRO_TEST"
    if balance <= 100:
        return "SMALL_TEST"
    if balance <= 1_000:
        return "STARTER_FLOAT"
    if balance <= 5_000:
        return "WORKING_FLOAT"
    if balance <= 25_000:
        return "SCALING_FLOAT"
    if balance <= 75_000:
        return "LARGE_FLOAT"
    return "HIGH_CONTROL_FLOAT"


def _trading_float_status(balance: float, state: Mapping[str, Any]) -> str:
    if balance < state["minimum_trading_float"]:
        return "BELOW_MINIMUM_FLOAT"
    if balance > state["maximum_trading_float"]:
        return "ABOVE_CAP_STRICT_CONTROL"
    return "INSIDE_FLOAT_POLICY"


def _money_relevance_rule() -> dict[str, Any]:
    samples = {
        "trading_float": _classify_money_field("trading_float"),
        "daily_pl": _classify_money_field("daily_pl"),
        "broker_proof_status": _classify_money_field("broker_proof_status"),
        "connector_proof_status": _classify_money_field("connector_proof_status"),
        "validator_logs": _classify_money_field("validator_logs"),
        "raw_evidence_paths": _classify_money_field("raw_evidence_paths"),
        "css_build_diagnostics": _classify_money_field("css_build_diagnostics"),
        "repo_noise": _classify_money_field("repo_noise"),
        "repo_noise_blocking_money_validation": _classify_money_field("repo_noise", blocking=True),
    }
    return {
        "status": MONEY_RELEVANT_VISIBLE,
        "default_visible_fields": DEFAULT_VISIBLE_MONEY_FIELDS,
        "collapsed_fields": COLLAPSED_MONEY_FIELDS,
        "hidden_unless_blocking_rule": "Technical detail stays hidden unless it blocks profit, loss, risk, capital flow, withdrawal, resupply, compounding, broker readiness, execution, uptime, or maintenance readiness.",
        "classification_samples": samples,
    }


def _classify_money_field(field_name: str, blocking: bool = False) -> str:
    normalized = field_name.lower().replace("-", "_").strip()
    if blocking and any(
        token in normalized
        for token in (
            "risk",
            "loss",
            "capital",
            "money",
            "profit",
            "broker",
            "connector",
            "transfer",
            "validation",
            "maintenance",
        )
    ):
        return MONEY_RELEVANT_VISIBLE
    if normalized in DEFAULT_VISIBLE_MONEY_FIELDS:
        return MONEY_RELEVANT_VISIBLE
    if any(
        token in normalized
        for token in (
            "profit",
            "loss",
            "risk",
            "capital",
            "withdrawal",
            "resupply",
            "compound",
            "sweep",
            "broker",
            "connector",
            "transfer",
            "equity",
            "drawdown",
            "float",
            "maintenance",
            "uptime",
            "pl",
        )
    ):
        return MONEY_RELEVANT_VISIBLE
    if normalized in COLLAPSED_MONEY_FIELDS or any(
        token in normalized for token in ("evidence", "legal", "governance", "validator", "repo", "css", "build")
    ):
        return MONEY_RELEVANT_COLLAPSED
    return NOT_MONEY_RELEVANT_HIDDEN_UNLESS_BLOCKING


def _preview(kind: str, amount: float, source_alias: str, destination_alias: str) -> dict[str, Any]:
    return {
        "request_id": f"AIOS-CAPITAL-{kind}-DRAFT",
        "request_type": kind,
        "amount": round(amount, 2),
        "source_alias": source_alias,
        "destination_alias": destination_alias,
        "status": "DRAFT_ONLY",
        "transfer_executed": False,
        "requires_human_approval": True,
        "requires_future_connector_proof": True,
    }


def _protected_gates(state: Mapping[str, Any], sensitive_input_detected: bool) -> dict[str, Any]:
    return {
        "human_approval_status": state["human_approval_status"],
        "broker_proof_status": state["broker_proof_status"],
        "bank_proof_status": state["bank_proof_status"],
        "payment_rail_proof_status": state["payment_rail_proof_status"],
        "maintenance_window": state["maintenance_window"],
        "emergency_freeze": state["emergency_freeze"],
        "daily_loss_lockout": state["daily_loss_lockout"],
        "sensitive_input_detected": sensitive_input_detected,
        "real_money_movement_allowed": False,
    }


def _blocked_reasons(
    state: Mapping[str, Any],
    classifications: Mapping[str, str],
    sensitive_input_detected: bool,
) -> list[str]:
    reasons: list[str] = []
    if sensitive_input_detected:
        reasons.append("sensitive_input_detected")
    if state["emergency_freeze"]:
        reasons.append("emergency_freeze")
    if state["daily_loss_lockout"]:
        reasons.append("daily_loss_lockout")
    if not state["maintenance_window"]:
        reasons.append("maintenance_window_required_for_treasury_action")
    if not _human_approved(state):
        reasons.append("human_approval_required")
    if not _connector_current(state):
        reasons.append("future_connector_proof_required")
    if classifications["CAPITAL_FLOW_STATUS"] == CAPITAL_FLOW_DISPLAY_ONLY:
        reasons.append("fixture_policy_display_only")
    return _unique(reasons)


def _next_safe_action(classifications: Mapping[str, str]) -> str:
    status = classifications["CAPITAL_FLOW_STATUS"]
    if status == CAPITAL_FLOW_POLICY_READY:
        return "review draft capital request preview; future real transfer still requires separate connector proof and human approval"
    if status == CAPITAL_FLOW_FROZEN_BY_RISK:
        return "keep capital flow frozen until risk lockout or emergency freeze is cleared by separate approval"
    if status == CAPITAL_FLOW_MAINTENANCE_ONLY:
        return "move treasury review into an approved maintenance window before drafting real connector actions"
    if status == CAPITAL_FLOW_BLOCKED_BY_CONNECTOR_PROOF:
        return "capture future sanitized broker/bank/payment connector proof without credentials or account identifiers"
    if status == CAPITAL_FLOW_BLOCKED_BY_APPROVAL:
        return "obtain separate human approval before any future transfer request leaves draft preview"
    return "review display-only treasury policy simulation"


def _write_reports(result: Mapping[str, Any]) -> list[Path]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    renders = {
        "money_goal_ladder": _render_money_goal_ladder_report(result),
        "simulation_range": _render_simulation_range_report(result),
        "money_relevance": _render_money_relevance_report(result),
    }
    written: list[Path] = []
    for key, text in renders.items():
        path = REPORT_PATHS[key]
        path.write_text(text, encoding="utf-8", newline="\n")
        written.append(path)
    return written


def _render_money_goal_ladder_report(result: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# AIOS Money Cockpit 100K Goal Ladder V11",
            "",
            "## Objective",
            "Keep and refine the 0.99-to-100000 Money Ladder as an aspirational simulation goal and capital-control test range without implying guaranteed growth, guaranteed return, live transfer authority, or automatic custody.",
            "",
            "## Money Cockpit Doctrine",
            "- Money-relevant fields stay visible by default.",
            "- Technical detail stays collapsed unless it blocks money, risk, broker readiness, uptime, or maintenance readiness.",
            "- The cockpit can feel like a semi-live trading HUD, but it remains policy and simulation only.",
            "- 100000 is a long-term goal, milestone, and simulation ceiling only.",
            "- 100000 is not a guaranteed profit target, guaranteed return, live-transfer threshold, or custody claim.",
            "",
            "## Capital Flow Doctrine",
            "- AIOS must not become a custodian of money.",
            "- AIOS does not move money from this policy engine or dashboard.",
            "- Account aliases only: TRADING_FLOAT, RESERVE_ACCOUNT, PROFIT_VAULT, TAX_BUCKET, OPERATING_ACCOUNT, WITHDRAWAL_TARGET, RESUPPLY_SOURCE, COMPOUND_BUCKET.",
            "- Real transfers require future connector proof and human approval.",
            "- Instant withdrawal/deposit depends on supported future broker, bank, or payment rails and is not claimed here.",
            "- This panel is policy and simulation only.",
            "",
            "## Money Ladder Status",
            f"`{result['money_ladder_status']}`",
            "",
            "## Money Ladder Doctrine",
            _table(result["money_ladder_doctrine"]),
            "",
            "## Money Relevance Rule",
            result["money_relevance_rule"]["hidden_unless_blocking_rule"],
            "",
            "## Classifications",
            _table(result["classifications"]),
            "",
            "## Policy Inputs",
            _table(result["policy_inputs"]),
            "",
            "## Recommendations",
            _bullets(result["recommendations"]),
            "",
            "## Protected Gates",
            _table(result["protected_gates"]),
            "",
            "## Dashboard Wiring",
            "Dashboard wiring is fixture-backed and display-only. It renders hot money facts, capital policy state, draft request previews, and collapsed ladder detail only.",
            "",
            "## Visible By Default",
            _bullets(result["money_relevance_rule"]["default_visible_fields"]),
            "",
            "## Collapsed By Default",
            _bullets(result["money_relevance_rule"]["collapsed_fields"]),
            "",
            "## Future Connector Proof Required",
            "- broker proof",
            "- bank proof",
            "- payment rail proof",
            "- transfer status proof",
            "",
            "## Human Approval Required",
            "Every future transfer must require explicit Human Owner approval before leaving draft preview.",
            "",
            "## Safety Status",
            "- broker status: not called",
            "- bank status: not called",
            "- payment processor status: not called",
            "- credential status: not read",
            "- account ID status: not read",
            "- transfer status: no transfer executed",
            "",
        ]
    )


def _render_simulation_range_report(result: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# AIOS Capital Flow Policy Simulation Range V11",
            "",
            "## 100000 Goal Boundary",
            "100000 is a long-term goal, milestone, and simulation ceiling only. It is not a guarantee of profit, return, settlement speed, custody, live transfer authority, or automated treasury activation.",
            "",
            "## Full 0.99-to-100000 Scenario Table",
            _ladder_table(result["simulation_ladder"]),
            "",
            "## Recommendation Output",
            _bullets(result["recommendations"]),
            "",
            "## Cap Scenario",
            "When trading float exceeds the maximum cap, the engine drafts a profit sweep preview capped by max withdrawal per event.",
            "",
            "## Resupply Scenario",
            "When trading float falls below the floor or resupply threshold, the engine drafts a resupply preview capped by max deposit per event.",
            "",
            "## Compound Scenario",
            "When profit vault reaches the compounding threshold and trading float is below target, the engine drafts a compound-in-place preview.",
            "",
            "## Sweep Scenario",
            "Profit sweep previews route from TRADING_FLOAT to PROFIT_VAULT by alias only.",
            "",
            "## Risk Freeze Scenario",
            "Emergency freeze or daily loss lockout produces FREEZE_CAPITAL_FLOW and blocks draft escalation.",
            "",
            "## Maintenance-Window Scenario",
            "Treasury actions outside a maintenance window are marked NEEDS_MAINTENANCE_WINDOW.",
            "",
            "## Approval-Blocked Scenario",
            "Missing human approval keeps recommendations in draft preview and blocks transfer execution.",
            "",
            "## Connector-Proof-Blocked Scenario",
            "Missing broker, bank, or payment connector proof keeps every transfer as draft-only display evidence.",
            "",
        ]
    )


def _render_connector_contract_report(result: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# AIOS Capital Flow Future Connector Contract V11",
            "",
            "## Future Broker/Bank/Payment Connector Requirements",
            "- runtime-only connector proof",
            "- no credential persistence",
            "- no account identifier persistence",
            "- explicit Human Owner approval",
            "- transfer request ID before any external action",
            "- sanitized audit log after any future approved action",
            "",
            "## Account Alias Model",
            _bullets(ALLOWED_ACCOUNT_ALIASES),
            "",
            "## Forbidden Credential Persistence",
            "Credentials, tokens, keys, card data, and payment secrets must not be stored, printed, logged, or written to repo fixtures/reports.",
            "",
            "## Forbidden Account ID Persistence",
            "Bank account numbers, broker account IDs, payment account IDs, broker order IDs, and raw payloads must not be stored.",
            "",
            "## Human Approval Model",
            "Each future real capital movement requires separate Human Owner approval for source alias, destination alias, amount, reason, rail, window, and stop condition.",
            "",
            "## Transfer Request ID Model",
            "`AIOS-CAPITAL-<TYPE>-<DATE>-<SEQUENCE>` sanitized request IDs may be used. They must not include bank, broker, or payment account identifiers.",
            "",
            "## Audit Log Model",
            "Future audit logs must contain request ID, aliases, amount, policy gate result, approval marker, status, timestamp, and sanitized failure reason.",
            "",
            "## Failure Handling",
            "Fail closed on connector mismatch, approval mismatch, account alias mismatch, stale proof, settlement uncertainty, or risk freeze.",
            "",
            "## Rollback/Reversal Note",
            "Rollback or reversal depends on external rail support and must not be guaranteed by AIOS.",
            "",
            "## Maintenance-Window Behavior",
            "Treasury actions should be reviewed during maintenance windows unless a future emergency policy explicitly says otherwise.",
            "",
            "## Daily/Weekly Capital Controls",
            "Future packets must define per-event, daily, weekly, and drawdown-aware capital controls before activation.",
            "",
            "## Regulatory/Compliance Review",
            "Regulatory, tax, broker, bank, and payment compliance review is required before activation.",
            "",
            "## Connector Activation Status",
            "Connector is not active.",
            "",
        ]
    )


def _render_money_relevance_report(result: Mapping[str, Any]) -> str:
    rule = result["money_relevance_rule"]
    return "\n".join(
        [
            "# AIOS Money Relevance Dashboard Rule V11",
            "",
            "## Default Visible Money Fields",
            _bullets(rule["default_visible_fields"]),
            "",
            "## Collapsed Fields",
            _bullets(rule["collapsed_fields"]),
            "",
            "## Hidden Unless Blocking Fields",
            "- CSS/build diagnostics",
            "- repo noise",
            "- stale reports",
            "- generic technical detail",
            "- raw evidence paths",
            "",
            "## Safety Fields That Remain Visible Because They Protect Money",
            "- broker proof status",
            "- connector proof status",
            "- transfer approval status",
            "- risk freeze status",
            "- daily loss left",
            "- maintenance window status",
            "",
            "## Dashboard UX Application",
            "The dashboard keeps hot money facts visible and pushes raw evidence, legal/governance detail, validator logs, repo noise, stale reports, and non-blocking technical detail into collapsed drawers.",
            "",
            "## Report Application",
            "Reports may retain full evidence detail, but summaries should lead with money, risk, connector, approval, uptime, and maintenance blockers.",
            "",
            "## Future 80 Percent Uptime Application",
            "An 80 percent uptime mode must keep capital, risk, connector, approval, maintenance, and incident-readiness signals visible while keeping non-money operational noise collapsed unless blocking.",
            "",
            "## Classification Samples",
            _table(rule["classification_samples"]),
            "",
        ]
    )


def _contains_sensitive_keys(payload: Any) -> bool:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if str(key).lower().strip() in SENSITIVE_KEYS:
                return True
            if _contains_sensitive_keys(value):
                return True
    elif isinstance(payload, list | tuple):
        return any(_contains_sensitive_keys(item) for item in payload)
    return False


def _connector_current(state: Mapping[str, Any]) -> bool:
    return (
        state["broker_proof_status"] == "CURRENT"
        and state["bank_proof_status"] == "CURRENT"
        and state["payment_rail_proof_status"] == "CURRENT"
    )


def _human_approved(state: Mapping[str, Any]) -> bool:
    return state["human_approval_status"] in {"APPROVED", "APPROVED_FOR_DRAFT"}


def _safety_summary() -> dict[str, bool]:
    return {
        "broker_api_called": False,
        "bank_api_called": False,
        "payment_api_called": False,
        "network_call_performed": False,
        "credentials_read": False,
        "account_identifiers_read": False,
        "env_read": False,
        "secret_files_read": False,
        "transfer_executed": False,
        "scheduler_started": False,
        "daemon_started": False,
        "webhook_started": False,
    }


def _money(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return 0.0


def _upper(value: Any, fallback: str) -> str:
    if value in (None, ""):
        return fallback
    return str(value).upper()


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            output.append(value)
    return output


def _bullets(values: Any) -> str:
    if isinstance(values, Mapping):
        values = values.items()
    lines = []
    for value in values:
        if isinstance(value, tuple) and len(value) == 2:
            lines.append(f"- `{value[0]}`: `{value[1]}`")
        else:
            lines.append(f"- `{value}`")
    return "\n".join(lines) if lines else "- `NONE`"


def _table(values: Mapping[str, Any]) -> str:
    lines = ["| Field | Value |", "|---|---|"]
    for key, value in values.items():
        lines.append(f"| {key} | `{value}` |")
    return "\n".join(lines)


def _ladder_table(rows: Any) -> str:
    columns = (
        "balance",
        "capital_tier",
        "trading_float_status",
        "risk_cap",
        "sweep_recommendation",
        "resupply_recommendation",
        "compound_recommendation",
        "withdrawal_gate",
        "connector_proof_gate",
        "approval_gate",
        "goal_milestone_status",
        "next_money_action",
    )
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(f"`{row.get(column, 'UNKNOWN')}`" for column in columns) + " |")
    return "\n".join(lines)
