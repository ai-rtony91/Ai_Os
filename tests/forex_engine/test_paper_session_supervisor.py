"""Tests for deterministic forex paper-session supervisor."""
from __future__ import annotations

import inspect

from automation.forex_engine import paper_session_supervisor as supervisor


def test_default_session_completes():
    result = supervisor.run_paper_session_supervisor()
    assert result["mode"] == supervisor.SESSION_MODE
    assert result["candidate_count"] == 5
    assert result["approved_trade_count"] == 3
    assert result["rejected_trade_count"] == 2
    assert result["closed_trade_count"] == 3


def test_output_is_deterministic():
    first = supervisor.run_paper_session_supervisor()
    second = supervisor.run_paper_session_supervisor()
    assert first == second


def test_required_top_level_sections_exist():
    result = supervisor.run_paper_session_supervisor()
    required = {
        "session_id",
        "mode",
        "starting_balance",
        "ending_balance",
        "realized_pl",
        "win_count",
        "loss_count",
        "candidate_count",
        "approved_trade_count",
        "rejected_trade_count",
        "open_trade_count",
        "closed_trade_count",
        "risk_rejections",
        "events",
        "watchlist",
        "replay",
        "safety",
    }
    assert required.issubset(result)


def test_approved_and_rejected_trades_exist():
    result = supervisor.run_paper_session_supervisor()
    assert len(result["approved_trades"]) == 3
    assert len(result["risk_rejections"]) == 2
    assert {item["reason"] for item in result["risk_rejections"]} == {
        "spread_too_high",
        "risk_percent_too_high",
    }


def test_profit_and_loss_trades_exist():
    result = supervisor.run_paper_session_supervisor()
    realized = [trade["realized_pl"] for trade in result["closed_trades"]]
    assert any(value > 0 for value in realized)
    assert any(value < 0 for value in realized)
    assert result["win_count"] >= 1
    assert result["loss_count"] >= 1


def test_ending_balance_equals_starting_balance_plus_realized_pl():
    result = supervisor.run_paper_session_supervisor()
    assert result["ending_balance"] == round(result["starting_balance"] + result["realized_pl"], 8)


def test_replay_matches_event_totals():
    result = supervisor.run_paper_session_supervisor()
    replay = result["replay"]
    assert replay["event_count"] == len(result["events"])
    assert replay["candidate_events"] == result["candidate_count"]
    assert replay["rejection_events"] == result["rejected_trade_count"]
    assert replay["approval_events"] == result["approved_trade_count"]
    assert replay["execution_events"] == result["approved_trade_count"]
    assert replay["balance_events"] == result["closed_trade_count"]
    assert replay["realized_pl"] == result["realized_pl"]


def test_watchlist_has_selected_and_blocked_rows():
    result = supervisor.run_paper_session_supervisor()
    statuses = {row["status"] for row in result["watchlist"]}
    assert "selected" in statuses
    assert "blocked" in statuses
    assert all("risk_reward" in row for row in result["watchlist"])


def test_source_has_no_forbidden_runtime_apis():
    source = inspect.getsource(supervisor)
    forbidden = (
        "import requests",
        "from requests",
        "import urllib",
        "from urllib",
        "import subprocess",
        "from subprocess",
        "import socket",
        "from socket",
        "open(",
        "write_text",
        "write_bytes",
        "os.environ",
        "getenv(",
        "broker_sdk",
        "oanda",
    )
    for token in forbidden:
        assert token not in source


def test_safety_flags_remain_false_for_protected_behavior():
    result = supervisor.run_paper_session_supervisor()
    safety = result["safety"]
    assert safety["broker_request_sent"] is False
    assert safety["network_used"] is False
    assert safety["credentials_used"] is False
    assert safety["live_order_placed"] is False
    assert safety["paper_only"] is True

