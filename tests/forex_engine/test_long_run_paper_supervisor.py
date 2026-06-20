from __future__ import annotations

import inspect
from typing import Any, Dict, List

import pytest

from automation.forex_engine import long_run_paper_supervisor as supervisor


def _mock_snapshot_allowed(*_args, **kwargs) -> Dict[str, Any]:
    pair = (kwargs.get("raw_market_data") or {}).get("pair", "EURUSD")
    return {
        "allowed": True,
        "decision": supervisor.LONG_RUN_ALLOWED,
        "blocked_reason": supervisor._RejectionReason.NONE,
        "paper_only": True,
        "mode": supervisor.LONG_RUN_PAPER_MODE,
        "pair": pair,
        "normalized_for_strategy": {"pair": pair},
        "normalized_for_preview": {"pair": pair},
    }


def _mock_snapshot_stale(*_args, **kwargs) -> Dict[str, Any]:
    pair = (kwargs.get("raw_market_data") or {}).get("pair", "EURUSD")
    return {
        "allowed": False,
        "decision": supervisor.LONG_RUN_BLOCKED,
        "blocked_reason": supervisor._RejectionReason.STALE_MARKET_DATA,
        "paper_only": True,
        "mode": supervisor.LONG_RUN_PAPER_MODE,
        "pair": pair,
        "warnings": [],
    }


def _mock_strategy_result(*_args, **kwargs) -> Dict[str, Any]:
    normalized = _args[0] if _args else {}
    pair = normalized.get("pair", "EURUSD")
    candidate = {
        "candidate_id": f"{pair}-candidate",
        "pair": pair,
        "direction": "buy",
        "entry_price": 1.09,
        "stop_loss": 1.08,
        "take_profit": 1.1,
        "risk_percent": 1.0,
    }
    return {
        "allowed": True,
        "decision": supervisor.LONG_RUN_ALLOWED,
        "candidates": [candidate],
        "selected_count": 1,
        "rejected_count": 0,
        "strategy_count": 1,
        "strategy_name": "moving_average_trend",
        "pair": pair,
        "safety": {"paper_only": True, "broker": False},
    }


def _mock_queue_result(*_args, **kwargs) -> Dict[str, Any]:
    strategy_result = _args[0]
    selected = strategy_result.get("candidates", [])
    return {
        "allowed": True,
        "decision": supervisor.LONG_RUN_ALLOWED,
        "selected_candidates": selected,
        "rejected_candidates": [],
        "selected_count": len(selected),
        "rejected_count": 0,
        "strategy_count": 1,
        "total_candidates": len(selected),
        "safety": {"paper_only": True, "broker": False},
    }


def _mock_preview_allowed(*_args, **kwargs) -> Dict[str, Any]:
    candidate = _args[0]
    return {
        "allowed": True,
        "decision": supervisor.LONG_RUN_ALLOWED,
        "approval_state": "paper_preview_ready",
        "pair": candidate.get("pair"),
        "direction": candidate.get("direction"),
        "entry_type": "market",
        "entry_price": candidate.get("entry_price"),
        "units": 1000.0,
        "dollar_risk": 10.0,
        "percent_risk": 1.0,
        "paper_only": True,
        "mode": supervisor.LONG_RUN_PAPER_MODE,
        "safety": {"paper_only": True, "broker": False},
    }


def _mock_fill_result(*_args, **kwargs) -> Dict[str, Any]:
    return {
        "allowed": True,
        "decision": supervisor.LONG_RUN_ALLOWED,
        "trade": {
            "pair": "EURUSD",
            "direction": "buy",
            "entry_type": "market",
            "entry_price": 1.09,
            "stop_loss": 1.08,
            "take_profit": 1.10,
            "units": 1000.0,
            "status": "active",
            "opened_timestamp": kwargs.get("timestamp", 0.0),
            "paper_only": True,
            "mode": supervisor.LONG_RUN_PAPER_MODE,
        },
        "safety": {"paper_only": True, "broker": False},
    }


def _mock_process_trade_update(*_args, **kwargs) -> Dict[str, Any]:
    trade = _args[0]
    return {
        "allowed": True,
        "decision": supervisor.LONG_RUN_ALLOWED,
        "closed": False,
        "status": trade.get("status"),
        "previous_status": trade.get("status"),
        "trade": trade,
        "closed_timestamp": None,
        "realized_pnl": 0.0,
        "paper_only": True,
        "mode": supervisor.LONG_RUN_PAPER_MODE,
    }


def _mock_close_trade_update(*_args, **kwargs) -> Dict[str, Any]:
    trade = _args[0]
    closed = dict(trade)
    closed["status"] = "closed"
    closed["closed_timestamp"] = kwargs.get("timestamp", 0.0)
    return {
        "allowed": True,
        "decision": supervisor.LONG_RUN_ALLOWED,
        "closed": True,
        "status": "closed",
        "previous_status": trade.get("status"),
        "close_reason": "take_profit",
        "entry_price": trade.get("entry_price"),
        "exit_price": trade.get("take_profit"),
        "realized_pnl": 12.0,
        "trade": closed,
        "closed_timestamp": kwargs.get("timestamp", 0.0),
        "paper_only": True,
        "mode": supervisor.LONG_RUN_PAPER_MODE,
    }


def _mock_close_balance(*_args, **kwargs) -> Dict[str, Any]:
    account = _as = _args[0] if _args else {}
    before = dict(account) if isinstance(account, dict) else {}
    before.setdefault("starting_balance", 1000.0)
    before.setdefault("current_balance", 1000.0)
    before.setdefault("cash_balance", 1000.0)
    before.setdefault("equity", 1000.0)
    before.setdefault("realized_pnl", 0.0)
    before.setdefault("trade_count", 0)
    before.setdefault("session_count", 0)
    return {
        "allowed": True,
        "decision": supervisor.LONG_RUN_ALLOWED,
        "account_state_before": before,
        "account_state_after": {**before, "current_balance": before["current_balance"] + 12.0, "realized_pnl_total": 12.0},
        "realized_pnl_delta": 12.0,
        "warnings": [],
        "safe_to_continue": True,
        "paper_only": True,
        "mode": supervisor.LONG_RUN_PAPER_MODE,
    }


def _mock_balance_no_change(*_args, **kwargs) -> Dict[str, Any]:
    account = _args[0] if _args else {}
    before = dict(account) if isinstance(account, dict) else {}
    before.setdefault("starting_balance", 1000.0)
    before.setdefault("current_balance", 1000.0)
    before.setdefault("cash_balance", 1000.0)
    before.setdefault("equity", 1000.0)
    return {
        "allowed": True,
        "decision": supervisor.LONG_RUN_ALLOWED,
        "account_state_before": before,
        "account_state_after": before,
        "realized_pnl_delta": 0.0,
        "warnings": [],
        "paper_only": True,
        "mode": supervisor.LONG_RUN_PAPER_MODE,
    }


def _mock_replay(*_args, **kwargs):
    events = _args[0] if _args else []
    return {
        "allowed": True,
        "decision": supervisor.LONG_RUN_ALLOWED,
        "session_id": kwargs.get("session_id"),
        "event_count": len(events),
        "counts_by_event_type": {},
        "trades_opened": 0,
        "trades_closed": 0,
        "balance_change": 0.0,
        "warnings": [],
        "paper_only": True,
        "mode": supervisor.LONG_RUN_PAPER_MODE,
    }


def test_supervisor_module_imports():
    assert supervisor.LONG_RUN_PAPER_MODE == "PAPER_ONLY"
    assert callable(supervisor.run_paper_supervisor_cycle)
    assert callable(supervisor.summarize_paper_supervisor_session)


def test_valid_single_cycle_runs_until_summary(monkeypatch):
    monkeypatch.setattr(supervisor, "normalize_market_snapshot", _mock_snapshot_allowed)
    monkeypatch.setattr(supervisor, "generate_strategy_candidates", _mock_strategy_result)
    monkeypatch.setattr(supervisor, "build_multi_trade_queue", _mock_queue_result)
    monkeypatch.setattr(supervisor, "build_order_preview", _mock_preview_allowed)
    monkeypatch.setattr(supervisor, "simulate_paper_fill", _mock_fill_result)
    monkeypatch.setattr(supervisor, "process_trade_update", _mock_process_trade_update)
    monkeypatch.setattr(supervisor, "apply_closed_trade_to_balance", _mock_balance_no_change)
    monkeypatch.setattr(supervisor, "build_session_replay", _mock_replay)

    result = supervisor.run_paper_supervisor_cycle(
        [{"pair": "EURUSD", "bid": 1.11, "ask": 1.12, "timestamp": 10}],
        account_state={"starting_balance": 1000.0, "current_balance": 1000.0, "cash_balance": 1000.0, "equity": 1000.0},
        session_state={"session_id": "session-1", "cycle_number": 1},
        timestamp=10.0,
    )

    assert result["allowed"] is True
    assert result["normalized_market_count"] == 1
    assert result["previews_created"] == 1
    assert result["fills_created"] == 1
    assert result["trades_opened"] == 1
    assert result["account_state_after"]["current_balance"] == 1000.0
    assert result["decision"] == supervisor.LONG_RUN_ALLOWED
    assert isinstance(result["heartbeat"], dict)
    assert result["heartbeat"]["paper_only"] is True
    assert result["safety"]["paper_only"] is True
    assert result["replay_summary"]["event_count"] == 2


def test_stale_market_data_stops_cycle(monkeypatch):
    monkeypatch.setattr(supervisor, "normalize_market_snapshot", _mock_snapshot_stale)
    result = supervisor.run_paper_supervisor_cycle(
        [{"pair": "EURUSD", "bid": 1.1, "ask": 1.2}],
        account_state={"starting_balance": 1000.0, "current_balance": 1000.0, "cash_balance": 1000.0, "equity": 1000.0},
        session_state={"session_id": "session-1", "cycle_number": 1},
        limits={"stale_market_data_seconds": 0},
        timestamp=10.0,
    )
    assert result["allowed"] is False
    assert result["decision"] == supervisor.LONG_RUN_BLOCKED
    assert result["blocked_reason"] == supervisor._RejectionReason.STALE_MARKET_DATA
    assert supervisor._RejectionReason.STALE_MARKET_DATA in result["blocked_reasons"]


def test_risk_halt_blocking_preview(monkeypatch):
    def preview_risk_blocked(*_args, **_kwargs):
        out = _mock_preview_allowed(*_args, **_kwargs)
        out["allowed"] = False
        out["blocked_reason"] = supervisor._RejectionReason.VALIDATION_FAILURE
        return out

    monkeypatch.setattr(supervisor, "normalize_market_snapshot", _mock_snapshot_allowed)
    monkeypatch.setattr(supervisor, "generate_strategy_candidates", _mock_strategy_result)
    monkeypatch.setattr(supervisor, "build_multi_trade_queue", _mock_queue_result)
    monkeypatch.setattr(supervisor, "build_order_preview", preview_risk_blocked)
    monkeypatch.setattr(supervisor, "build_session_replay", _mock_replay)

    result = supervisor.run_paper_supervisor_cycle(
        [{"pair": "EURUSD", "bid": 1.1, "ask": 1.2}],
        account_state={"starting_balance": 1000.0, "current_balance": 1000.0, "cash_balance": 1000.0, "equity": 1000.0},
        session_state={"session_id": "session-1", "cycle_number": 1},
    )

    assert result["allowed"] is False
    assert supervisor._RejectionReason.RISK_HALT in result["stop_conditions"] or result["blocked_reason"] == supervisor._RejectionReason.RISK_HALT


def test_kill_switch_block(monkeypatch):
    monkeypatch.setattr(supervisor, "normalize_market_snapshot", _mock_snapshot_allowed)
    result = supervisor.run_paper_supervisor_cycle(
        [{"pair": "EURUSD", "bid": 1.1, "ask": 1.2}],
        account_state={"starting_balance": 1000.0, "current_balance": 1000.0, "cash_balance": 1000.0, "equity": 1000.0},
        session_state={"session_id": "session-1", "cycle_number": 1},
        limits={"kill_switch_active": True},
    )
    assert result["decision"] == supervisor.LONG_RUN_BLOCKED
    assert "kill_switch_active" in result["stop_conditions"]


def test_max_session_trades_limit_blocks(monkeypatch):
    monkeypatch.setattr(supervisor, "normalize_market_snapshot", _mock_snapshot_allowed)
    monkeypatch.setattr(supervisor, "generate_strategy_candidates", _mock_strategy_result)
    monkeypatch.setattr(supervisor, "build_multi_trade_queue", _mock_queue_result)
    monkeypatch.setattr(supervisor, "build_order_preview", _mock_preview_allowed)
    monkeypatch.setattr(supervisor, "simulate_paper_fill", _mock_fill_result)
    monkeypatch.setattr(supervisor, "process_trade_update", _mock_process_trade_update)
    monkeypatch.setattr(supervisor, "apply_closed_trade_to_balance", _mock_balance_no_change)
    monkeypatch.setattr(supervisor, "build_session_replay", _mock_replay)

    result = supervisor.run_paper_supervisor_cycle(
        [{"pair": "EURUSD", "bid": 1.1, "ask": 1.2}],
        account_state={"starting_balance": 1000.0, "current_balance": 1000.0, "cash_balance": 1000.0, "equity": 1000.0},
        session_state={"session_id": "session-1", "cycle_number": 1},
        limits={"max_session_trades": 0},
    )
    assert result["decision"] == supervisor.LONG_RUN_BLOCKED
    assert supervisor._RejectionReason.MAX_SESSION_TRADES_HIT in result["stop_conditions"]


def test_max_session_loss_limit_blocks(monkeypatch):
    def _loss_balance(*_args, **_kwargs):
        account = _args[0] if _args else {}
        before = dict(account) if isinstance(account, dict) else {}
        before.setdefault("starting_balance", 1000.0)
        before.setdefault("current_balance", 1000.0)
        return {
            "allowed": True,
            "decision": supervisor.LONG_RUN_ALLOWED,
            "account_state_before": before,
            "account_state_after": {**before, "current_balance": 10.0},
            "realized_pnl_delta": -990.0,
            "warnings": [],
            "paper_only": True,
            "mode": supervisor.LONG_RUN_PAPER_MODE,
        }

    monkeypatch.setattr(supervisor, "normalize_market_snapshot", _mock_snapshot_allowed)
    monkeypatch.setattr(supervisor, "generate_strategy_candidates", _mock_strategy_result)
    monkeypatch.setattr(supervisor, "build_multi_trade_queue", _mock_queue_result)
    monkeypatch.setattr(supervisor, "build_order_preview", _mock_preview_allowed)
    monkeypatch.setattr(supervisor, "simulate_paper_fill", _mock_fill_result)
    monkeypatch.setattr(supervisor, "process_trade_update", _mock_close_trade_update)
    monkeypatch.setattr(supervisor, "apply_closed_trade_to_balance", _loss_balance)
    monkeypatch.setattr(supervisor, "build_session_replay", _mock_replay)

    result = supervisor.run_paper_supervisor_cycle(
        [{"pair": "EURUSD", "bid": 1.1, "ask": 1.2}],
        account_state={"starting_balance": 1000.0, "current_balance": 1000.0, "cash_balance": 1000.0, "equity": 1000.0},
        session_state={"session_id": "session-1", "cycle_number": 1},
        limits={"max_session_loss": 50.0},
    )
    assert result["decision"] == supervisor.LONG_RUN_BLOCKED
    assert supervisor._RejectionReason.MAX_SESSION_LOSS_HIT in result["stop_conditions"]


def test_invalid_evidence_path_blocks():
    result = supervisor.run_paper_supervisor_cycle(
        [{"pair": "EURUSD", "bid": 1.1, "ask": 1.2}],
        account_state={"starting_balance": 1000.0, "current_balance": 1000.0, "cash_balance": 1000.0, "equity": 1000.0},
        evidence_path="C:/absolute/path/ledger.json",
    )
    assert result["decision"] == supervisor.LONG_RUN_BLOCKED
    assert result["blocked_reason"] == supervisor._RejectionReason.EVIDENCE_PATH_INVALID


def test_summarize_paper_supervisor_session(monkeypatch):
    cycle_results = [
        {
            "session_id": "session-1",
            "cycle_id": "c1",
            "normalized_market_count": 2,
            "candidate_count": 1,
            "selected_count": 1,
            "rejected_count": 0,
            "previews_created": 1,
            "fills_created": 1,
            "trades_opened": 1,
            "trades_closed": 0,
            "balance_updates": 1,
            "ledger_events": [{"event_type": "paper_trade_opened"}],
        },
        {
            "session_id": "session-1",
            "cycle_id": "c2",
            "normalized_market_count": 1,
            "candidate_count": 2,
            "selected_count": 0,
            "rejected_count": 1,
            "previews_created": 0,
            "fills_created": 0,
            "trades_opened": 0,
            "trades_closed": 1,
            "balance_updates": 1,
            "ledger_events": [{"event_type": "paper_trade_closed"}],
        },
    ]
    monkeypatch.setattr(supervisor, "build_session_replay", _mock_replay)
    summary = supervisor.summarize_paper_supervisor_session(cycle_results, session_id="session-1")
    assert summary["cycle_count"] == 2
    assert summary["total_candidates"] == 3
    assert summary["total_selected"] == 1
    assert summary["total_rejected"] == 1
    assert summary["total_previews"] == 1
    assert summary["total_fills"] == 1
    assert summary["total_opened"] == 1
    assert summary["total_closed"] == 1
    assert summary["safety"]["broker"] is False
    assert summary["replay_summary"]["event_count"] == 2


def test_module_source_has_no_forbidden_apis():
    source = inspect.getsource(supervisor)
    forbidden = [
        "subprocess",
        "requests.",
        "socket",
        "urllib",
        "open(",
        ".write_text",
        ".write_bytes",
        "pathlib",
        "os.system",
        "broker_sdk",
        "credential",
        "account_id",
        "getenv",
        "environ",
    ]
    for token in forbidden:
        assert token not in source


def test_invalid_account_state_blocks(monkeypatch):
    result = supervisor.run_paper_supervisor_cycle(
        [{"pair": "EURUSD", "bid": 1.1, "ask": 1.2}],
        account_state={"starting_balance": -100.0, "current_balance": -100.0, "cash_balance": -100.0, "equity": -100.0},
    )
    assert result["decision"] == supervisor.LONG_RUN_BLOCKED
    assert result["blocked_reason"] == supervisor._RejectionReason.VALIDATION_FAILURE
