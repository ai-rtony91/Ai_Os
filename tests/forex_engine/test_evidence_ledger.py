from pathlib import Path

from automation.forex_engine import evidence_ledger


def _base_payload():
    return {"value": 1}


def test_module_import():
    assert evidence_ledger.EVIDENCE_LEDGER_MODE == "PAPER_ONLY"


def test_build_event_allowed_and_shape():
    event = evidence_ledger.build_ledger_event(
        event_type="market_data_accepted",
        payload=_base_payload(),
        session_id="s1",
        timestamp=1.23,
    )
    assert event["allowed"] is True
    assert event["event_type"] == "market_data_accepted"
    assert event["session_id"] == "s1"
    assert event["sequence"] == 0
    assert event["paper_only"] is True
    assert event["mode"] == "PAPER_ONLY"
    assert event["safety"]["broker"] is False


def test_build_event_deterministic_event_id():
    e1 = evidence_ledger.build_ledger_event("preview_created", {"a": 1}, "s1", timestamp=10.0)
    e2 = evidence_ledger.build_ledger_event("preview_created", {"a": 1}, "s1", timestamp=10.0)
    assert e1["event_id"] == e2["event_id"]


def test_build_rejects_invalid_event_type():
    event = evidence_ledger.build_ledger_event("bad_type", {}, "s1", timestamp=1.0)
    assert event["allowed"] is False
    assert event["blocked_reason"] == "invalid_event_type"


def test_build_rejects_missing_session_and_timestamp():
    event = evidence_ledger.build_ledger_event("preview_created", {"a": 1}, None, timestamp=None)
    assert event["allowed"] is False
    reasons = event["blocked_reasons"]
    assert "missing_session_id" in reasons
    assert "missing_timestamp" in reasons


def test_append_event_without_mutating_input():
    events = [
        evidence_ledger.build_ledger_event("market_data_accepted", {"value": 1}, "s1", timestamp=1.0),
    ]
    out = evidence_ledger.append_ledger_event(
        events,
        evidence_ledger.build_ledger_event("strategy_candidate_created", {"candidate_id": "c1"}, "s1", timestamp=2.0),
    )
    assert out["allowed"] is True
    assert len(out["ledger"]) == 2
    assert len(events) == 1


def test_append_rejects_duplicate_event_id():
    base = evidence_ledger.build_ledger_event("market_data_accepted", {"x": 1}, "s1", event_id="dup", timestamp=1.0)
    events = [base]
    second = evidence_ledger.build_ledger_event("market_data_rejected", {"x": 2}, "s1", event_id="dup", timestamp=2.0)
    out = evidence_ledger.append_ledger_event(events, second)
    assert out["allowed"] is False
    assert "duplicate_event_id" in out["blocked_reasons"]
    assert len(out["ledger"]) == 1


def test_append_respects_parent_chain():
    first = evidence_ledger.build_ledger_event("market_data_accepted", {"x": 1}, "s1", timestamp=1.0)
    second = evidence_ledger.build_ledger_event("market_data_accepted", {"x": 2}, "s1", parent_event_id=first["event_id"], timestamp=2.0)
    out = evidence_ledger.append_ledger_event([first], second)
    assert out["allowed"] is True


def test_validate_detects_missing_parent():
    first = evidence_ledger.build_ledger_event("market_data_accepted", {"x": 1}, "s1", timestamp=1.0)
    orphan = evidence_ledger.build_ledger_event("market_data_rejected", {"x": 2}, "s1", parent_event_id="missing", timestamp=2.0)
    report = evidence_ledger.validate_ledger([first, orphan], session_id="s1")
    assert report["valid"] is False
    assert "evidence_chain_broken" in report["errors"]


def test_validate_allows_valid_ordering():
    events = [
        evidence_ledger.build_ledger_event("market_data_accepted", {"x": 1}, "s1", timestamp=1.0),
        evidence_ledger.build_ledger_event("strategy_candidate_created", {"x": 2}, "s1", timestamp=2.0),
    ]
    report = evidence_ledger.validate_ledger(events, session_id="s1")
    assert report["valid"] is True
    assert report["errors"] == []


def test_replay_counts_events():
    events = [
        evidence_ledger.build_ledger_event("market_data_accepted", {"x": 1}, "s1", timestamp=1.0),
        evidence_ledger.build_ledger_event("market_data_rejected", {"x": 1}, "s1", timestamp=2.0),
        evidence_ledger.build_ledger_event("strategy_candidate_created", {"x": 3}, "s1", timestamp=3.0),
        evidence_ledger.build_ledger_event("risk_accepted", {"x": 4}, "s1", timestamp=4.0),
        evidence_ledger.build_ledger_event("paper_trade_opened", {"trade_id": "t1"}, "s1", timestamp=5.0),
        evidence_ledger.build_ledger_event("paper_trade_closed", {"trade_id": "t1"}, "s1", timestamp=6.0),
        evidence_ledger.build_ledger_event("balance_updated", {"delta": 100}, "s1", timestamp=7.0),
        evidence_ledger.build_ledger_event("kill_switch_triggered", {"reason": "manual"}, "s1", timestamp=8.0),
        evidence_ledger.build_ledger_event("session_summary_generated", {"session": 1}, "s1", timestamp=9.0),
    ]
    replay = evidence_ledger.replay_ledger(events, session_id="s1")
    assert replay["valid"] is True
    assert replay["counts_by_event_type"]["strategy_candidate_created"] == 1
    assert replay["accepted_market_data"] == 1
    assert replay["rejected_market_data"] == 1
    assert replay["trades_opened"] == 1
    assert replay["trades_closed"] == 1
    assert replay["balance_updates"] == 1
    assert replay["kill_switch_events"] == 1
    assert replay["session_summaries"] == 1


def test_replay_summary_for_missing_parent_and_invalid():
    events = [
        evidence_ledger.build_ledger_event("market_data_accepted", {"x": 1}, "s1", timestamp=1.0),
    ]
    orphan = evidence_ledger.build_ledger_event("strategy_candidate_created", {"x": 1}, "s1", parent_event_id="missing", timestamp=2.0)
    replay = evidence_ledger.replay_ledger(events + [orphan], session_id="s1")
    assert replay["missing_parent_events"] >= 1


def test_invalid_session_blocked():
    events = [evidence_ledger.build_ledger_event("market_data_accepted", {"x": 1}, "s1", timestamp=1.0)]
    replay = evidence_ledger.replay_ledger(events, session_id="missing")
    assert replay["total_events"] == 0


def test_live_mode_or_non_paper_blocks():
    event = evidence_ledger.build_ledger_event("market_data_accepted", {"x": 1}, "s1", timestamp=1.0)
    event["paper_only"] = False
    out = evidence_ledger.append_ledger_event([], event)
    assert out["allowed"] is False
    assert "non_paper_mode" in out["blocked_reasons"]

    event2 = evidence_ledger.build_ledger_event("market_data_accepted", {"x": 1}, "s1", timestamp=1.0)
    event2["mode"] = "live"
    out2 = evidence_ledger.append_ledger_event([], event2)
    assert out2["allowed"] is False
    assert "live_trading_blocked" in out2["blocked_reasons"]


def test_invalid_evidence_path_blocks_build():
    event = evidence_ledger.build_ledger_event("market_data_accepted", {"x": 1}, "s1", timestamp=1.0, evidence_path="C:\\tmp\\ledger.json")
    assert event["allowed"] is False
    assert event["blocked_reason"] == "evidence_path_invalid"


def test_append_rejects_invalid_event_type():
    out = evidence_ledger.append_ledger_event([], {"event_type": "bad", "session_id": "s1", "event_id": "x", "timestamp": 1.0, "payload": {}})
    assert out["allowed"] is False
    assert "invalid_event_type" in out["blocked_reasons"]


def test_validation_reports_duplicate_ids():
    first = evidence_ledger.build_ledger_event("market_data_accepted", {"x": 1}, "s1", event_id="same", timestamp=1.0)
    second = evidence_ledger.build_ledger_event("market_data_accepted", {"x": 2}, "s1", event_id="same", timestamp=2.0)
    out = evidence_ledger.validate_ledger([first, second], session_id="s1")
    assert out["valid"] is False
    assert "duplicate_event_id" in out["errors"]


def test_source_scan_no_forbidden_runtime_or_secret_terms():
    source = Path("automation/forex_engine/evidence_ledger.py").read_text(encoding="utf-8")
    forbidden = [
        "import subprocess",
        "from subprocess",
        "import requests",
        "from requests",
        "import socket",
        "from socket",
        "import urllib",
        "from urllib",
        "open(",
        ".write_text",
        ".write_bytes",
        "import pathlib",
        "from pathlib",
        "os.system",
        "os.getenv",
        "os.environ",
        "getenv(",
        "environ[",
        "api_key",
        "access_token",
        "refresh_token",
        "private_key",
        "password",
        "bearer ",
    ]
    for token in forbidden:
        assert token not in source
