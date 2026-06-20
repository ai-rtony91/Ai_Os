"""Tests for deterministic long-run paper supervisor."""
from __future__ import annotations

import inspect

from automation.forex_engine import (
    paper_account_state,
    paper_evidence_ledger,
    paper_long_run_supervisor,
    paper_position_sizing,
    paper_risk_governor,
    paper_session_replay,
    paper_trade_lifecycle,
)


def test_long_run_supervisor_completes_multi_cycle_session():
    result = paper_long_run_supervisor.run_long_run_paper_supervisor()
    assert result["cycles"] == 3
    assert result["candidate_count"] >= 9
    assert result["approved_trade_count"] >= 4
    assert result["rejected_trade_count"] >= 3
    assert result["win_count"] >= 1
    assert result["loss_count"] >= 1


def test_long_run_aggregate_balance_equals_starting_balance_plus_realized_pl():
    result = paper_long_run_supervisor.run_long_run_paper_supervisor()
    assert result["ending_balance"] == round(result["starting_balance"] + result["realized_pl"], 8)
    assert result["aggregate_replay"]["ending_balance"] == result["ending_balance"]


def test_long_run_safety_flags_remain_false_for_protected_behavior():
    safety = paper_long_run_supervisor.run_long_run_paper_supervisor()["safety"]
    assert safety["broker_request_sent"] is False
    assert safety["network_used"] is False
    assert safety["credentials_used"] is False
    assert safety["live_order_placed"] is False
    assert safety["paper_only"] is True


def test_new_source_files_have_no_forbidden_runtime_apis():
    modules = (
        paper_account_state,
        paper_position_sizing,
        paper_risk_governor,
        paper_trade_lifecycle,
        paper_evidence_ledger,
        paper_session_replay,
        paper_long_run_supervisor,
    )
    forbidden = (
        "import requests",
        "from requests",
        "import urllib",
        "from urllib",
        "import subprocess",
        "from subprocess",
        "import socket",
        "from socket",
        "os.environ",
        "getenv(",
        "write_text",
        "write_bytes",
        "broker_sdk",
        "oanda",
    )
    source = "\n".join(inspect.getsource(module) for module in modules)
    for token in forbidden:
        assert token not in source
