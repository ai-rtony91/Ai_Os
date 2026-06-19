"""Aggregate PAPER_SIMULATION forex signal execution loop read-model.

The loop proves signal, risk, exit, paper entry, paper close/reconcile, and
history writeback behavior without secrets, broker calls, live orders, or live
close actions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from automation.forex_engine.paper_execution_simulator import (
    DEFAULT_ENTRY_TIME_UTC,
    DEFAULT_EXIT_TIME_UTC,
    DEFAULT_SELECTED_PAIR,
    DEFAULT_STRATEGY_NAME,
    SAFE_EVIDENCE_PATH,
    PAPER_SIMULATION_LABEL,
    PaperExecutionSimulator,
    PaperExitPlanner,
    PaperReconciler,
    PaperRiskGate,
    PaperSignalEngine,
    TradingHistoryWriteback,
)


SCHEMA = "AIOS_FOREX_PAPER_SIGNAL_EXECUTION_LOOP.v1"
REPORT_TITLE = "AIOS Forex Paper Signal Execution Loop Dry Run V1"

FORBIDDEN_OUTPUT_MARKERS = (
    "OANDA_API_TOKEN",
    "OANDA_ACCOUNT_ID",
    "Authorization",
    "Bearer ",
    "transactionID",
    "orderID",
    "accountID",
    "rawBroker",
)


def build_paper_signal_execution_loop_result(
    *,
    selected_pair: str = DEFAULT_SELECTED_PAIR,
    strategy_name: str = DEFAULT_STRATEGY_NAME,
    requested_units: int = 1000,
    read_model: Mapping[str, Any] | None = None,
    explicit_paper_fixture_mode: bool = True,
    entry_time_utc: str = DEFAULT_ENTRY_TIME_UTC,
    exit_time_utc: str = DEFAULT_EXIT_TIME_UTC,
) -> dict[str, Any]:
    signal = PaperSignalEngine(
        selected_pair=selected_pair,
        strategy_name=strategy_name,
        explicit_paper_fixture_mode=explicit_paper_fixture_mode,
    ).evaluate(read_model=read_model)
    risk = PaperRiskGate().evaluate(signal, requested_units=requested_units)
    exit_plan = PaperExitPlanner().plan(signal)
    paper_entry = PaperExecutionSimulator().create_entry(
        signal,
        risk,
        exit_plan,
        now_utc=entry_time_utc,
    )
    reconciliation = PaperReconciler().close_and_reconcile(
        paper_entry,
        exit_plan,
        now_utc=exit_time_utc,
    )
    history = TradingHistoryWriteback().build(reconciliation)

    result = {
        "schema": SCHEMA,
        "mode": PAPER_SIMULATION_LABEL,
        "selected_pair": signal["selected_pair"],
        "signal_side": signal["signal_side"],
        "strategy_name": signal["strategy_name"],
        "confidence": signal["confidence"],
        "signal_reason": signal["signal_reason"],
        "spread_slippage_status": signal["spread_slippage_status"],
        "risk_approval": risk["risk_approval"],
        "paper_entry_created": paper_entry["paper_entry_created"],
        "paper_entry_price": paper_entry.get("entry_price", "UNAVAILABLE"),
        "paper_units": paper_entry.get("units", requested_units),
        "exit_plan_status": exit_plan["exit_plan_status"],
        "stop_loss_policy": exit_plan["stop_loss_policy"],
        "take_profit_policy": exit_plan["take_profit_policy"],
        "trailing_stop_policy": exit_plan["trailing_stop_policy"],
        "max_time_policy": exit_plan["max_time_policy"],
        "auto_exit_readiness": exit_plan["auto_exit_readiness"],
        "manual_close_fallback": exit_plan["manual_close_fallback"],
        "paper_close_reconcile": reconciliation["paper_close_reconcile"],
        "realized_paper_pl": reconciliation.get("realized_paper_pl", "UNAVAILABLE"),
        "exit_reason": reconciliation.get("exit_reason", "UNAVAILABLE"),
        "trading_history_row_written": history["trading_history_row_written"],
        "evidence_path": history["evidence_path"],
        "live_execution_allowed": False,
        "broker_write_calls_allowed": False,
        "order_placement_allowed": False,
        "close_trade_allowed": False,
        "secret_values_printed": False,
        "private_identifiers_recorded": False,
        "raw_broker_payload_recorded": False,
        "next_safe_action": _next_safe_action(history["trading_history_row_written"]),
        "signal": signal,
        "risk": risk,
        "exit_plan": exit_plan,
        "paper_execution": paper_entry,
        "reconciliation": reconciliation,
        "trading_history": history,
        "dashboard_status": _dashboard_status(signal, paper_entry, reconciliation, history),
    }
    assert_paper_loop_sanitized(result)
    return result


def build_sanitized_report(result: Mapping[str, Any]) -> str:
    assert_paper_loop_sanitized(result)
    summary = {
        "selected_pair": result.get("selected_pair"),
        "signal_side": result.get("signal_side"),
        "strategy_name": result.get("strategy_name"),
        "confidence": result.get("confidence"),
        "risk_approval": result.get("risk_approval"),
        "paper_entry_created": result.get("paper_entry_created"),
        "paper_close_reconcile": result.get("paper_close_reconcile"),
        "realized_paper_pl": result.get("realized_paper_pl"),
        "trading_history_row_written": result.get("trading_history_row_written"),
        "evidence_path": result.get("evidence_path"),
        "live_execution_allowed": False,
        "next_safe_action": result.get("next_safe_action"),
    }
    return (
        f"# {REPORT_TITLE}\n\n"
        "Status: PAPER_SIMULATION_SANITIZED\n\n"
        "This evidence is paper-only. It records no live trade, live order, broker write call, "
        "secret value, account identifier, real order identifier, transaction identifier, "
        "or raw broker payload.\n\n"
        "## Summary\n\n"
        f"```json\n{json.dumps(summary, indent=2, sort_keys=True)}\n```\n\n"
        "## Sanitized Aggregate Result\n\n"
        f"```json\n{json.dumps(dict(result), indent=2, sort_keys=True)}\n```\n"
    )


def write_paper_signal_execution_loop_report(
    result: Mapping[str, Any],
    *,
    repo_root: Path,
    relative_path: str = SAFE_EVIDENCE_PATH,
) -> Path:
    assert_paper_loop_sanitized(result)
    report_path = repo_root / relative_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_sanitized_report(result), encoding="utf-8")
    return report_path


def cli_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_PAPER_SIGNAL_EXECUTION_LOOP_CLI_SUMMARY.v1",
        "mode": result.get("mode"),
        "selected_pair": result.get("selected_pair"),
        "signal_side": result.get("signal_side"),
        "strategy_name": result.get("strategy_name"),
        "risk_approval": result.get("risk_approval"),
        "paper_entry_created": result.get("paper_entry_created"),
        "paper_close_reconcile": result.get("paper_close_reconcile"),
        "realized_paper_pl": result.get("realized_paper_pl"),
        "trading_history_row_written": result.get("trading_history_row_written"),
        "evidence_path": result.get("evidence_path"),
        "live_execution_allowed": False,
        "next_safe_action": result.get("next_safe_action"),
    }


def assert_paper_loop_sanitized(payload: Mapping[str, Any]) -> None:
    serialized = json.dumps(payload, sort_keys=True)
    for marker in FORBIDDEN_OUTPUT_MARKERS:
        if marker in serialized:
            raise ValueError(f"forbidden_paper_loop_output_marker:{marker}")
    if '"live_execution_allowed": true' in serialized.lower():
        raise ValueError("paper_loop_must_not_allow_live_execution")


def _dashboard_status(
    signal: Mapping[str, Any],
    paper_entry: Mapping[str, Any],
    reconciliation: Mapping[str, Any],
    history: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "PAPER_LOOP_AVAILABLE": history.get("trading_history_row_written") is True,
        "last_paper_signal": signal.get("signal_side"),
        "last_paper_trade_status": reconciliation.get(
            "paper_trade_status",
            paper_entry.get("paper_trade_status", "UNAVAILABLE"),
        ),
        "last_paper_realized_pl": reconciliation.get("realized_paper_pl", "UNAVAILABLE"),
        "history_writeback_status": (
            "PAPER_HISTORY_WRITTEN"
            if history.get("trading_history_row_written") is True
            else "PAPER_HISTORY_UNAVAILABLE"
        ),
        "live_execution_allowed": False,
        "next_safe_action": _next_safe_action(history.get("trading_history_row_written") is True),
    }


def _next_safe_action(history_written: bool) -> str:
    if history_written:
        return (
            "Review paper loop evidence for risk-adjusted expectancy; live execution remains "
            "blocked until AIOS-FOREX-LIVE-MICRO-TRADE-ARMING-GATE-V1."
        )
    return "Repair paper loop writeback before any live arming gate."
