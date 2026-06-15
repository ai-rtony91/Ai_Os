from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable, Iterable


SCHEMA = "AIOS_FOREX_PAPER_SESSION_CONTROLLER.v1"
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
        "queue_mutation": False,
        "approval_mutation": False,
    }


def _unsafe_reason(flags: dict[str, Any]) -> str | None:
    for name in sorted(UNSAFE_FLAG_NAMES):
        if flags.get(name):
            return f"unsafe_flag_{name}"
    return None


def _blocked_summary(reason: str, account_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
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
        "daily_loss_used": 0.0,
        "block_reasons": [reason],
        "ledger_records": [],
        "final_portfolio_state": {},
        "session_steps": [],
        "safety": _base_safety(),
        "next_safe_action": "Stop the paper session and inspect the blocked reason.",
    }


def _account_for_risk(portfolio_state: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    return {
        "cash_balance": portfolio_state.get("cash_balance", fallback.get("cash_balance", fallback.get("balance", 0.0))),
        "balance": portfolio_state.get("cash_balance", fallback.get("balance", fallback.get("cash_balance", 0.0))),
        "daily_loss": portfolio_state.get("daily_loss_used", fallback.get("daily_loss", 0.0)),
        "daily_pnl": portfolio_state.get("realized_pnl", fallback.get("daily_pnl", 0.0)),
        "trades_today": portfolio_state.get("trade_count", fallback.get("trades_today", 0)),
    }


def _market_for_signal(signal: dict[str, Any], market: dict[str, Any]) -> dict[str, Any]:
    signal_market = signal.get("market")
    return signal_market if isinstance(signal_market, dict) else market


def _metadata_for_signal(signal: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    metadata = {}
    default_metadata = config.get("ledger_metadata")
    if isinstance(default_metadata, dict):
        metadata.update(default_metadata)
    signal_metadata = signal.get("metadata")
    if isinstance(signal_metadata, dict):
        metadata.update(signal_metadata)
    if "exit_price" in signal:
        metadata["exit_price"] = signal["exit_price"]
    return metadata


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
        return _blocked_summary(unsafe, initial_account)

    limits = limits if isinstance(limits, dict) else {}
    market = market if isinstance(market, dict) else {}
    config = config if isinstance(config, dict) else {}
    signals = list(signal_intents or [])

    ledger_records: list[dict[str, Any]] = []
    session_steps: list[dict[str, Any]] = []
    block_reasons: list[str] = []
    trades_attempted = 0
    trades_accepted = 0
    trades_blocked = 0
    portfolio_state = build_portfolio_state(ledger_records, initial_account, market, limits)

    for index, raw_signal in enumerate(signals):
        signal = raw_signal if isinstance(raw_signal, dict) else {}
        if portfolio_state.get("next_trade_allowed") is False:
            reason = str(portfolio_state.get("next_trade_blocked_reason", "portfolio_next_trade_blocked"))
            trades_attempted += 1
            trades_blocked += 1
            block_reasons.append(reason)
            session_steps.append({"index": index, "phase": "portfolio_gate", "blocked_reason": reason})
            break

        trades_attempted += 1
        account_for_risk = _account_for_risk(portfolio_state, initial_account)
        risk_result = evaluate_risk_controls(signal, account_for_risk, limits, **safety_flags)
        if risk_result.get("allowed") is not True:
            reason = str(risk_result.get("blocked_reason", "risk_controls_blocked"))
            trades_blocked += 1
            block_reasons.append(reason)
            session_steps.append({"index": index, "phase": "risk_controls", "risk_result": risk_result})
            break

        execution_result = simulate_paper_execution(
            signal,
            risk_result,
            _market_for_signal(signal, market),
            config,
            **safety_flags,
        )
        ledger_record = build_execution_ledger_record(
            execution_result,
            signal,
            account_snapshot=account_for_risk,
            metadata=_metadata_for_signal(signal, config),
            **safety_flags,
        )
        ledger_records.append(ledger_record)

        if execution_result.get("allowed") is not True:
            reason = str(execution_result.get("blocked_reason", "paper_execution_blocked"))
            trades_blocked += 1
            block_reasons.append(reason)
            session_steps.append(
                {
                    "index": index,
                    "phase": "paper_execution",
                    "risk_result": risk_result,
                    "execution_result": execution_result,
                    "ledger_record": ledger_record,
                }
            )
            break
        if ledger_record.get("allowed") is not True:
            reason = str(ledger_record.get("blocked_reason", "ledger_integration_blocked"))
            trades_blocked += 1
            block_reasons.append(reason)
            session_steps.append(
                {
                    "index": index,
                    "phase": "ledger_integration",
                    "risk_result": risk_result,
                    "execution_result": execution_result,
                    "ledger_record": ledger_record,
                }
            )
            break

        trades_accepted += 1
        portfolio_state = build_portfolio_state(ledger_records, initial_account, market, limits)
        session_steps.append(
            {
                "index": index,
                "phase": "accepted",
                "risk_result": risk_result,
                "execution_result": execution_result,
                "ledger_record": ledger_record,
                "portfolio_state": portfolio_state,
            }
        )

    session_status = "completed" if not block_reasons else "stopped_blocked"
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
        "daily_loss_used": portfolio_state.get("daily_loss_used", 0.0),
        "block_reasons": block_reasons,
        "ledger_records": ledger_records,
        "final_portfolio_state": portfolio_state,
        "session_steps": session_steps,
        "safety": _base_safety(),
        "next_safe_action": (
            "Review the completed paper session summary."
            if not block_reasons
            else "Stop the paper session and review the first blocking gate."
        ),
    }
