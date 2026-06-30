"""Governed paper-session controller for the long-cycle Forex workflow."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable, Iterable


SCHEMA = "AIOS_FOREX_PAPER_SESSION_CONTROLLER.v1"
STRICT_PHASES = ("evaluate", "enter", "monitor", "exit")
AUTO_PHASE = "auto"

STRICT_ENTER_ACTIONS = {"buy"}
STRICT_EXIT_ACTIONS = {"sell", "close"}
STRICT_MONITOR_ACTIONS = {"", None, "hold", "monitor"}

UNSAFE_FLAG_NAMES = {
    "live_execution",
    "broker_order",
    "credentials",
    "api_key",
    "real_order",
    "webhook_url",
    "network",
    "network_access",
}


def _load_sibling_function(module_name: str, function_name: str) -> Callable[..., dict[str, Any]]:
    try:
        module = __import__(f"trading_lab.{module_name}", fromlist=[function_name])
        return getattr(module, function_name)
    except ModuleNotFoundError:
        module_path = Path(__file__).with_name(f"{module_name}.py")
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            raise
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, function_name)


evaluate_risk_controls = _load_sibling_function("forex_risk_controls", "evaluate_risk_controls")
simulate_paper_execution = _load_sibling_function("forex_paper_execution_simulator", "simulate_paper_execution")
build_execution_ledger_record = _load_sibling_function(
    "forex_execution_ledger_integration",
    "build_execution_ledger_record",
)
build_portfolio_state = _load_sibling_function("forex_portfolio_state", "build_portfolio_state")


def _base_safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "real_webhooks": False,
        "network_access": False,
        "scheduler": False,
        "daemon": False,
        "worker_dispatch": False,
        "approval_mutation": False,
    }


def _unsafe_reason(flags: dict[str, Any]) -> str | None:
    for name in sorted(UNSAFE_FLAG_NAMES):
        if flags.get(name):
            return f"unsafe_flag_{name}"
    return None


def _blocked_summary(
    reason: str,
    account_snapshot: dict[str, Any] | None = None,
    *,
    cycle_reassessment_required: bool = False,
) -> dict[str, Any]:
    account = account_snapshot if isinstance(account_snapshot, dict) else {}
    return {
        "schema": SCHEMA,
        "allowed": False,
        "session_status": "blocked",
        "paper_only": True,
        "trades_attempted": 0,
        "trades_accepted": 0,
        "trades_blocked": 1,
        "final_cash": float(account.get("cash_balance", account.get("balance", 0.0)) or 0.0),
        "open_positions": {},
        "realized_pnl": 0.0,
        "realized_gain_bucket": 0.0,
        "realized_loss_bucket": 0.0,
        "daily_loss_used": 0.0,
        "cycle_reassessment_required": cycle_reassessment_required,
        "block_reasons": [reason],
        "ledger_records": [],
        "final_portfolio_state": {},
        "session_steps": [],
        "safety": _base_safety(),
        "next_safe_action": (
            "Hold operation and resolve the blocked reason before resuming paper long-cycle evaluation."
        ),
    }


def _account_for_risk(portfolio_state: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    return {
        "cash_balance": portfolio_state.get("cash_balance", fallback.get("cash_balance", fallback.get("balance", 0.0))),
        "balance": portfolio_state.get(
            "cash_balance",
            portfolio_state.get("balance", fallback.get("balance", fallback.get("cash_balance", 0.0))),
        ),
        "daily_loss": portfolio_state.get("daily_loss", fallback.get("daily_loss", 0.0)),
        "daily_pnl": portfolio_state.get("realized_pnl", fallback.get("daily_pnl", 0.0)),
        "daily_loss_used": portfolio_state.get("daily_loss_used", fallback.get("daily_loss_used", 0.0)),
        "trades_today": portfolio_state.get("trade_count", fallback.get("trades_today", 0)),
        "open_positions_count": portfolio_state.get("open_positions_count", fallback.get("open_positions_count", 0)),
        "consecutive_losses": portfolio_state.get("consecutive_losses", fallback.get("consecutive_losses", 0)),
        "portfolio_risk_percent": portfolio_state.get("portfolio_risk_percent", fallback.get("portfolio_risk_percent", 0.0)),
        "max_open_trades": fallback.get("max_open_trades", 0),
        "previous_position_size_units": fallback.get("previous_position_size_units", fallback.get("position_size_units", 0.0)),
    }


def _market_for_signal(signal: dict[str, Any], market: dict[str, Any]) -> dict[str, Any]:
    signal_market = signal.get("market")
    return signal_market if isinstance(signal_market, dict) else market


def _metadata_for_signal(signal: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    default_metadata = config.get("ledger_metadata")
    if isinstance(default_metadata, dict):
        metadata.update(default_metadata)
    signal_metadata = signal.get("metadata")
    if isinstance(signal_metadata, dict):
        metadata.update(signal_metadata)
    if "exit_price" in signal:
        metadata["exit_price"] = signal["exit_price"]
    return metadata


def _strict_cycle_enabled(signals: list[dict[str, Any]]) -> bool:
    return any(
        isinstance(signal, dict)
        and isinstance(signal.get("cycle_phase"), str)
        and signal.get("cycle_phase")
        for signal in signals
    )


def _normalize_cycle_phase(signal: dict[str, Any]) -> str:
    if not isinstance(signal, dict):
        return AUTO_PHASE
    phase = str(signal.get("cycle_phase", "")).strip().lower()
    if phase in {"", "auto", "evaluate", "enter", "monitor", "exit"}:
        if phase in {"", "auto"}:
            return AUTO_PHASE
        return phase
    aliases = {
        "entry": "enter",
        "open": "enter",
        "close": "exit",
        "monitoring": "monitor",
        "reassess": "evaluate",
        "review": "evaluate",
    }
    return aliases.get(phase, "invalid")


def _normalized_execution_action(phase: str, action: str) -> str:
    normalized = action.strip().lower()
    if normalized == "close":
        return "sell"
    if phase == "monitor" and normalized in {"hold", "monitor", ""}:
        return ""
    return normalized


def _safe_float(value: Any) -> float | None:
    if value is None or value is True or value is False:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if parsed != parsed or parsed in (float("inf"), float("-inf")):
        return None
    return parsed


def _has_any_float(signal: dict[str, Any], names: tuple[str, ...]) -> bool:
    return any(_safe_float(signal.get(name)) is not None for name in names)


def _required_reassessment_fields(signal: dict[str, Any], portfolio_state: dict[str, Any]) -> list[str]:
    reasons: list[str] = []

    ranked_pairs = signal.get("ranked_pairs")
    if not isinstance(ranked_pairs, list) or not ranked_pairs:
        reasons.append("reassessment_missing_ranked_pairs")

    for name in (
        ("confidence_score", "confidence"),
        ("spread_score", "spread_quality_score"),
        ("volatility_score", "volatility_quality_score"),
        ("liquidity_score", "liquidity"),
        ("expectancy_score", "expectancy"),
        ("drawdown_score", "drawdown_percent", "max_drawdown_percent", "max_drawdown"),
        ("risk_adjusted_score", "risk_score", "risk_adjusted"),
    ):
        if not _has_any_float(signal, name):
            reasons.append(f"reassessment_missing_{name[0]}")

    if _safe_float(portfolio_state.get("open_risk")) is None:
        reasons.append("reassessment_missing_open_exposure_snapshot")

    if _safe_float(portfolio_state.get("max_daily_loss")) is None and _safe_float(portfolio_state.get("available_risk")) is None:
        if (
            _safe_float(signal.get("max_daily_loss")) is None
            and _safe_float(signal.get("available_risk")) is None
            and _safe_float(signal.get("daily_risk_budget")) is None
        ):
            reasons.append("reassessment_missing_daily_risk_budget_snapshot")

    if _safe_float(portfolio_state.get("drawdown_percent")) is None:
        reasons.append("reassessment_missing_drawdown_snapshot")

    return reasons


def _append_step_failure(
    session_steps: list[dict[str, Any]],
    index: int,
    phase: str,
    reason: str,
    risk_result: dict[str, Any] | None = None,
    execution_result: dict[str, Any] | None = None,
    ledger_record: dict[str, Any] | None = None,
) -> None:
    step = {"index": index, "phase": phase, "status": "blocked", "blocked_reason": reason}
    if risk_result is not None:
        step["risk_result"] = risk_result
    if execution_result is not None:
        step["execution_result"] = execution_result
    if ledger_record is not None:
        step["ledger_record"] = ledger_record
    session_steps.append(step)


def _evaluate_transition(
    expected_phase: str,
    observed_phase: str,
    index: int,
    session_steps: list[dict[str, Any]],
) -> bool:
    if expected_phase == observed_phase:
        return True
    session_steps.append(
        {
            "index": index,
            "phase": observed_phase,
            "status": "blocked",
            "blocked_reason": "cycle_phase_mismatch",
            "expected_phase": expected_phase,
            "observed_phase": observed_phase,
        },
    )
    return False


def _append_monitor_step(index: int, portfolio_state: dict[str, Any], session_steps: list[dict[str, Any]]) -> None:
    session_steps.append(
        {
            "index": index,
            "phase": "monitor",
            "status": "passed",
            "open_positions": dict(portfolio_state.get("open_positions", {})),
            "portfolio_risk_percent": portfolio_state.get("portfolio_risk_percent", 0.0),
            "next_safe_action": "Hold the paper position under monitor and then provide an exit phase for controlled close.",
        },
    )


def _apply_exit_phase_gate(
    expected_phase: str,
    index: int,
    session_steps: list[dict[str, Any]],
    portfolio_state: dict[str, Any],
) -> bool:
    if portfolio_state.get("open_positions_count", 0) <= 0:
        _append_step_failure(
            session_steps,
            index=index,
            phase=expected_phase,
            reason="exit_without_open_position",
            risk_result={"allowed": False, "blocked_reason": "exit_without_open_position"},
        )
        return False
    return True


def _reassessment_step(
    signal: dict[str, Any],
    portfolio_state: dict[str, Any],
    account_snapshot: dict[str, Any],
    limits: dict[str, Any],
    index: int,
    session_steps: list[dict[str, Any]],
) -> tuple[bool, list[str]]:
    rejection_reasons = _required_reassessment_fields(signal, portfolio_state)
    if rejection_reasons:
        _append_step_failure(
            session_steps,
            index=index,
            phase="evaluate",
            reason=rejection_reasons[0],
        )
        return False, rejection_reasons

    evaluation_signal = dict(signal)
    evaluation_signal["action"] = str(signal.get("action", "hold") or "hold")
    evaluation_signal["position_size_units"] = 0.0
    evaluation_signal["risk_percent"] = 0.0

    account_for_risk = _account_for_risk(portfolio_state, account_snapshot)
    evaluation_result = evaluate_risk_controls(evaluation_signal, account_for_risk, limits)
    if not evaluation_result.get("allowed", False):
        reason = str(evaluation_result.get("blocked_reason", "risk_controls_blocked"))
        _append_step_failure(
            session_steps,
            index=index,
            phase="evaluate",
            reason=reason,
            risk_result=evaluation_result,
        )
        return False, [reason]

    session_steps.append(
        {
            "index": index,
            "phase": "evaluate",
            "status": "passed",
            "risk_result": evaluation_result,
            "rejection_reasons": [],
        },
    )
    return True, []


def _process_trade_signal(
    signal: dict[str, Any],
    portfolio_state: dict[str, Any],
    initial_account: dict[str, Any],
    limits: dict[str, Any],
    market: dict[str, Any],
    config: dict[str, Any],
    index: int,
    phase: str,
    ledger_records: list[dict[str, Any]],
    session_steps: list[dict[str, Any]],
    *,
    safety_flags: dict[str, Any],
) -> tuple[bool, str | None, dict[str, Any]]:
    account_for_risk = _account_for_risk(portfolio_state, initial_account)
    if phase in {"enter", "exit", "auto"}:
        action = _normalized_execution_action(phase, str(signal.get("action", "")))
        signal = dict(signal)
        signal["action"] = action
    risk_result = evaluate_risk_controls(signal, account_for_risk, limits, **safety_flags)
    if risk_result.get("allowed") is False:
        return False, str(risk_result.get("blocked_reason", "risk_controls_blocked")), {
            "index": index,
            "phase": phase,
            "risk_result": risk_result,
        }

    execution_result = simulate_paper_execution(
        signal,
        risk_result,
        _market_for_signal(signal, market),
        config,
        **safety_flags,
    )
    if execution_result.get("allowed") is not True:
        ledger_record = build_execution_ledger_record(
            execution_result,
            signal,
            account_snapshot=account_for_risk,
            metadata=_metadata_for_signal(signal, config),
            **safety_flags,
        )
        ledger_records.append(ledger_record)
        return False, str(execution_result.get("blocked_reason", "paper_execution_blocked")), {
            "index": index,
            "phase": phase,
            "risk_result": risk_result,
            "execution_result": execution_result,
            "ledger_record": ledger_record,
        }

    ledger_record = build_execution_ledger_record(
        execution_result,
        signal,
        account_snapshot=account_for_risk,
        metadata=_metadata_for_signal(signal, config),
        **safety_flags,
    )
    if ledger_record.get("allowed") is not True:
        return False, str(ledger_record.get("blocked_reason", "ledger_integration_blocked")), {
            "index": index,
            "phase": phase,
            "risk_result": risk_result,
            "execution_result": execution_result,
            "ledger_record": ledger_record,
        }

    ledger_records.append(ledger_record)
    return True, None, {
        "index": index,
        "phase": phase,
        "risk_result": risk_result,
        "execution_result": execution_result,
        "ledger_record": ledger_record,
    }


def _final_safe_action(strict_cycle: bool, expected_phase: str) -> str:
    if not strict_cycle:
        return "Review the completed paper session and refresh next intents."

    if expected_phase == "evaluate":
        return (
            "Reassess ranked pair inputs (confidence/spread/volatility/liquidity/expectancy/drawdown), "
            "open exposure, and daily risk budget before approving the next long entry."
        )
    if expected_phase == "monitor":
        return "Monitor the active long trade and send a controlled exit signal when TP/SL/owner gate closes it."
    if expected_phase == "enter":
        return "Provide a long entry signal with approved ranking and risk controls."
    if expected_phase == "exit":
        return "Exit the active long position before opening a fresh cycle."
    return "Review cycle integrity and refresh the long-cycle assessment."


def run_paper_session(
    signal_intents: Iterable[dict[str, Any]],
    account_snapshot: dict[str, Any] | None = None,
    limits: dict[str, Any] | None = None,
    market: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
    **safety_flags: Any,
) -> dict[str, Any]:
    unsafe = _unsafe_reason(safety_flags)
    initial_account = account_snapshot if isinstance(account_snapshot, dict) else {}
    if unsafe:
        return _blocked_summary(unsafe, initial_account, cycle_reassessment_required=False)

    limits = limits if isinstance(limits, dict) else {}
    market = market if isinstance(market, dict) else {}
    config = config if isinstance(config, dict) else {}
    signals = list(signal_intents or [])

    strict_cycle = _strict_cycle_enabled(signals)
    expected_phase = "evaluate" if strict_cycle else AUTO_PHASE

    ledger_records: list[dict[str, Any]] = []
    session_steps: list[dict[str, Any]] = []
    block_reasons: list[str] = []
    trades_attempted = 0
    trades_accepted = 0
    trades_blocked = 0

    portfolio_state = build_portfolio_state(ledger_records, initial_account, market, limits, **_base_safety())
    if portfolio_state.get("allowed") is False:
        return _blocked_summary(
            str(portfolio_state.get("blocked_reason", "portfolio_state_blocked")),
            initial_account,
            cycle_reassessment_required=(strict_cycle and expected_phase == "evaluate"),
        )

    for index, raw_signal in enumerate(signals):
        signal = raw_signal if isinstance(raw_signal, dict) else {}
        requested_phase = _normalize_cycle_phase(signal)

        if strict_cycle:
            if requested_phase == "invalid":
                trades_attempted += 1
                trades_blocked += 1
                reason = "invalid_cycle_phase"
                block_reasons.append(reason)
                _append_step_failure(session_steps, index, "cycle", reason)
                break

            if requested_phase == AUTO_PHASE:
                requested_phase = expected_phase

            if not _evaluate_transition(expected_phase, requested_phase, index, session_steps):
                trades_attempted += 1
                trades_blocked += 1
                block_reasons.append("cycle_phase_mismatch")
                break

            if expected_phase == "evaluate":
                if portfolio_state.get("next_trade_allowed") is False:
                    reason = str(portfolio_state.get("next_trade_blocked_reason", "portfolio_next_trade_blocked"))
                    block_reasons.append(reason)
                    _append_step_failure(
                        session_steps,
                        index=index,
                        phase="evaluate",
                        reason=reason,
                        risk_result={"allowed": False, "blocked_reason": reason},
                    )
                    break

                ok, reasons = _reassessment_step(
                    signal,
                    portfolio_state,
                    initial_account,
                    limits,
                    index,
                    session_steps,
                )
                if not ok:
                    trades_attempted += 1
                    trades_blocked += 1
                    block_reasons.extend(reasons)
                    break

                trades_attempted += 1
                session_steps.append({"index": index, "phase": "evaluate", "status": "accepted"})
                expected_phase = "enter"
                continue

            if expected_phase == "monitor":
                raw_action = signal.get("action")
                action = "" if raw_action is None else str(raw_action).strip().lower()
                if action and action not in STRICT_MONITOR_ACTIONS:
                    reason = "monitor_disallows_trade_action"
                    trades_attempted += 1
                    trades_blocked += 1
                    block_reasons.append(reason)
                    _append_step_failure(
                        session_steps,
                        index=index,
                        phase="monitor",
                        reason=reason,
                        risk_result={"allowed": False, "blocked_reason": reason},
                    )
                    break
                if portfolio_state.get("open_positions_count", 0) == 0:
                    reason = "monitor_without_open_positions"
                    trades_attempted += 1
                    trades_blocked += 1
                    block_reasons.append(reason)
                    _append_step_failure(session_steps, index=index, phase="monitor", reason=reason)
                    break
                _append_monitor_step(index, portfolio_state, session_steps)
                expected_phase = "exit"
                continue

            if expected_phase == "enter":
                action = str(signal.get("action", "")).lower()
                if action not in STRICT_ENTER_ACTIONS:
                    reason = "enter_requires_buy_action"
                    trades_attempted += 1
                    trades_blocked += 1
                    block_reasons.append(reason)
                    _append_step_failure(
                        session_steps,
                        index=index,
                        phase="enter",
                        reason=reason,
                        risk_result={"allowed": False, "blocked_reason": reason},
                    )
                    break
                allowed, reason, step = _process_trade_signal(
                    signal,
                    portfolio_state,
                    initial_account,
                    limits,
                    market,
                    config,
                    index,
                    "enter",
                    ledger_records,
                    session_steps,
                    safety_flags=safety_flags,
                )
                trades_attempted += 1
                if not allowed:
                    trades_blocked += 1
                    block_reasons.append(reason or "enter_blocked")
                    session_steps.append(step)
                    break

                trades_accepted += 1
                portfolio_state = build_portfolio_state(ledger_records, initial_account, market, limits, **_base_safety())
                if portfolio_state.get("allowed") is False:
                    reason = str(portfolio_state.get("blocked_reason", "portfolio_state_blocked"))
                    block_reasons.append(reason)
                    _append_step_failure(
                        session_steps,
                        index=index,
                        phase="enter",
                        reason=reason,
                        risk_result={"allowed": False, "blocked_reason": reason},
                    )
                    break
                session_steps.append({**step, "portfolio_state": portfolio_state})
                expected_phase = "monitor"
                continue

            if expected_phase == "exit":
                action = str(signal.get("action", "")).lower()
                if action not in STRICT_EXIT_ACTIONS:
                    reason = "exit_requires_sell_or_close_action"
                    trades_attempted += 1
                    trades_blocked += 1
                    block_reasons.append(reason)
                    _append_step_failure(
                        session_steps,
                        index=index,
                        phase="exit",
                        reason=reason,
                        risk_result={"allowed": False, "blocked_reason": reason},
                    )
                    break
                if not _apply_exit_phase_gate(expected_phase, index, session_steps, portfolio_state):
                    trades_attempted += 1
                    trades_blocked += 1
                    block_reasons.append("exit_without_open_position")
                    break

                allowed, reason, step = _process_trade_signal(
                    signal,
                    portfolio_state,
                    initial_account,
                    limits,
                    market,
                    config,
                    index,
                    "exit",
                    ledger_records,
                    session_steps,
                    safety_flags=safety_flags,
                )
                trades_attempted += 1
                if not allowed:
                    trades_blocked += 1
                    block_reasons.append(reason or "exit_blocked")
                    session_steps.append(step)
                    break

                trades_accepted += 1
                portfolio_state = build_portfolio_state(ledger_records, initial_account, market, limits, **_base_safety())
                if portfolio_state.get("allowed") is False:
                    reason = str(portfolio_state.get("blocked_reason", "portfolio_state_blocked"))
                    block_reasons.append(reason)
                    _append_step_failure(
                        session_steps,
                        index=index,
                        phase="exit",
                        reason=reason,
                        risk_result={"allowed": False, "blocked_reason": reason},
                    )
                    break
                session_steps.append({**step, "portfolio_state": portfolio_state})
                expected_phase = "evaluate"
                continue

        else:
            if requested_phase not in STRICT_PHASES:
                requested_phase = "enter"

            if portfolio_state.get("next_trade_allowed", True) is False:
                reason = str(portfolio_state.get("next_trade_blocked_reason", "portfolio_next_trade_blocked"))
                trades_attempted += 1
                trades_blocked += 1
                block_reasons.append(reason)
                _append_step_failure(session_steps, index=index, phase="portfolio_gate", reason=reason)
                break

            allowed, reason, step = _process_trade_signal(
                signal,
                portfolio_state,
                initial_account,
                limits,
                market,
                config,
                index,
                requested_phase,
                ledger_records,
                session_steps,
                safety_flags=safety_flags,
            )
            trades_attempted += 1
            if not allowed:
                trades_blocked += 1
                block_reasons.append(reason or "trade_blocked")
                session_steps.append(step)
                break

            trades_accepted += 1
            portfolio_state = build_portfolio_state(ledger_records, initial_account, market, limits, **_base_safety())
            if portfolio_state.get("allowed") is False:
                reason = str(portfolio_state.get("blocked_reason", "portfolio_state_blocked"))
                block_reasons.append(reason)
                _append_step_failure(
                    session_steps,
                    index=index,
                    phase=requested_phase,
                    reason=reason,
                    risk_result={"allowed": False, "blocked_reason": reason},
                )
                break

            session_steps.append({**step, "portfolio_state": portfolio_state})

    session_status = "completed" if not block_reasons else "stopped_blocked"
    final_next_safe_action = _final_safe_action(strict_cycle, expected_phase)

    return {
        "schema": SCHEMA,
        "allowed": not block_reasons,
        "session_status": session_status,
        "paper_only": True,
        "trades_attempted": trades_attempted,
        "trades_accepted": trades_accepted,
        "trades_blocked": trades_blocked,
        "final_cash": portfolio_state.get("cash_balance", 0.0),
        "open_positions": portfolio_state.get("open_positions", {}),
        "realized_pnl": portfolio_state.get("realized_pnl", 0.0),
        "realized_gain_bucket": portfolio_state.get("realized_gain_bucket", 0.0),
        "realized_loss_bucket": portfolio_state.get("realized_loss_bucket", 0.0),
        "daily_loss_used": portfolio_state.get("daily_loss_used", 0.0),
        "cycle_reassessment_required": expected_phase == "evaluate" and strict_cycle,
        "block_reasons": block_reasons,
        "ledger_records": ledger_records,
        "final_portfolio_state": portfolio_state,
        "session_steps": session_steps,
        "safety": _base_safety(),
        "next_safe_action": final_next_safe_action,
    }
