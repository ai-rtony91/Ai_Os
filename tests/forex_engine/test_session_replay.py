from pathlib import Path

from automation.forex_engine import evidence_ledger, session_replay


def _market_data_event(event_type="market_data_accepted", **kwargs):
    return evidence_ledger.build_ledger_event(event_type, payload={"pair": "EURUSD"}, session_id="session-1", timestamp=1.0, **kwargs)


def _candidate_event(event_type="strategy_candidate_created", candidate_id="c1", **kwargs):
    return evidence_ledger.build_ledger_event(event_type, payload={"candidate_id": candidate_id}, session_id="session-1", timestamp=2.0, **kwargs)


def _preview_event(event_type="preview_created", candidate_id="c1", **kwargs):
    return evidence_ledger.build_ledger_event(event_type, payload={"candidate_id": candidate_id}, session_id="session-1", timestamp=3.0, **kwargs)


def _risk_event(event_type="risk_accepted", candidate_id="c1", **kwargs):
    return evidence_ledger.build_ledger_event(event_type, payload={"candidate_id": candidate_id, "dollar_risk": 120.0}, session_id="session-1", timestamp=4.0, **kwargs)


def _trade_event(event_type, trade_id="t1", realized=None, **kwargs):
    payload = {"trade_id": trade_id}
    if realized is not None:
        payload["realized_pnl"] = realized
    return evidence_ledger.build_ledger_event(event_type, payload=payload, session_id="session-1", timestamp=5.0, **kwargs)


def _balance_event(value):
    return evidence_ledger.build_ledger_event("balance_updated", payload={"current_balance": value}, session_id="session-1", timestamp=6.0)


def _build_valid_ledger():
    return [
        _market_data_event("market_data_accepted"),
        _market_data_event("market_data_rejected"),
        _candidate_event("strategy_candidate_created", candidate_id="c1"),
        _candidate_event("candidate_rejected", candidate_id="c2"),
        _preview_event("preview_created", candidate_id="c1"),
        _risk_event("risk_accepted", candidate_id="c1"),
        _trade_event("paper_trade_opened", trade_id="t1"),
        _trade_event("paper_trade_closed", trade_id="t1", realized=40.0),
        _trade_event("paper_trade_closed", trade_id="t2", realized=-20.0),
        _balance_event(1000.0),
        _balance_event(1030.0),
    ]


def test_module_import():
    assert session_replay.SESSION_REPLAY_MODE == "PAPER_ONLY"


def test_empty_ledger_returns_warnings_not_crash():
    result = session_replay.build_session_replay([])
    assert result["allowed"] is False
    assert result["event_count"] == 0
    assert result["warnings"] is not None


def test_valid_session_replay_counts():
    ledger = _build_valid_ledger()
    result = session_replay.build_session_replay(ledger, session_id="session-1")
    assert result["event_count"] == 11
    assert result["total_candidates"] == 2
    assert result["accepted_candidates"] == 1
    assert result["rejected_candidates"] == 1
    assert result["previews_created"] == 1
    assert result["risk_accepted"] == 1
    assert result["trades_opened"] == 1
    assert result["trades_closed"] == 2


def test_pnl_metrics_deterministic():
    ledger = _build_valid_ledger()
    result = session_replay.build_session_replay(ledger, session_id="session-1")
    assert result["wins"] == 1
    assert result["losses"] == 1
    assert result["breakeven"] == 0
    assert result["gross_profit"] == 40.0
    assert result["gross_loss"] == 20.0
    assert result["net_pnl"] == 20.0
    assert result["profit_factor"] == 2.0


def test_balance_metrics_from_events():
    ledger = _build_valid_ledger()
    result = session_replay.build_session_replay(ledger, session_id="session-1")
    assert result["balance_start"] == 1000.0
    assert result["balance_end"] == 1030.0
    assert result["balance_change"] == 30.0


def test_close_without_open_warning():
    e_open = _trade_event("paper_trade_opened", trade_id="t1")
    e_close = _trade_event("paper_trade_closed", trade_id="t2", realized=10.0)
    result = session_replay.build_session_replay([e_open, e_close], session_id="session-1")
    assert "missing_trade_open_evidence" in result["missing_evidence_warnings"]


def test_preview_without_candidate_warning():
    e_preview = _preview_event("preview_created", candidate_id="unknown")
    result = session_replay.build_session_replay([_market_data_event(), _candidate_event(candidate_id="c1"), e_preview], session_id="session-1")
    assert "missing_candidate_evidence" in result["missing_evidence_warnings"]


def test_risk_without_preview_warning():
    e_risk = _risk_event("risk_accepted", candidate_id="missing")
    result = session_replay.build_session_replay([_market_data_event(), _candidate_event(candidate_id="c1"), e_risk], session_id="session-1")
    assert "missing_risk_evidence" in result["missing_evidence_warnings"]


def test_session_filter_works():
    e1 = _market_data_event(session_id="session-1")
    e2 = _market_data_event(session_id="session-2")
    result = session_replay.build_session_replay([e1, e2], session_id="session-2")
    assert result["event_count"] == 1
    assert result["event_count"] == 1


def test_live_mode_and_paper_only_validation():
    live = _market_data_event()
    live["mode"] = "live"
    out = session_replay.build_session_replay([live], session_id="session-1")
    assert "live_trading_blocked" in out["blocked_reasons"]

    non = _market_data_event()
    non["paper_only"] = False
    out2 = session_replay.build_session_replay([non], session_id="session-1")
    assert "non_paper_mode" in out2["blocked_reasons"]


def test_invalid_ledger_type_blocks():
    out = session_replay.build_session_replay("invalid")
    assert out["allowed"] is False
    assert out["blocked_reason"] == "invalid_ledger"


def test_invalid_evidence_path_blocks():
    out = session_replay.build_session_replay([], evidence_path="C:\\tmp\\session.json")
    assert out["allowed"] is False
    assert out["blocked_reason"] == "evidence_path_invalid"


def test_replay_source_event_ids_deterministic():
    ledger = _build_valid_ledger()
    result = session_replay.build_session_replay(ledger, session_id="session-1")
    expected = [e["event_id"] for e in ledger]
    assert result["source_event_ids"] == expected


def test_safety_dict_present():
    result = session_replay.build_session_replay(_build_valid_ledger(), session_id="session-1")
    assert result["safety"]["paper_only"] is True
    assert result["safety"]["broker"] is False
    assert result["safety"]["live_trading"] is False


def test_source_scan_forbidden_operations():
    source = Path("automation/forex_engine/session_replay.py").read_text(encoding="utf-8")
    forbidden = [
        "subprocess",
        "requests",
        "socket",
        "urllib",
        "open(",
        ".write_text",
        ".write_bytes",
        "pathlib",
        "os.system",
        "getenv",
        "environ",
    ]
    for token in forbidden:
        assert token not in source
