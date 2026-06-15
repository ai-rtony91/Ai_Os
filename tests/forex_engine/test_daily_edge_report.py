from automation.forex_engine.daily_edge_report import build_daily_edge_report, format_daily_edge_report


def test_daily_edge_report_contains_required_fields():
    report = build_daily_edge_report()
    assert report["mode"] == "PAPER_ONLY"
    assert report["strategy_name"] == "supertrend_pullback_v1"
    assert report["data_source_type"] in {"deterministic_sample", "local_fixture_csv"}
    assert "cost_assumptions" in report
    assert "expectancy_r" in report
    assert "max_drawdown_pct" in report
    assert "profit_factor" in report
    assert "no_trade_reasons" in report
    assert report["classification"] in {"REJECTED", "NEEDS_MORE_DATA", "CANDIDATE", "PAPER_FORWARD_READY"}
    assert report["live_ready"] is False


def test_daily_edge_report_formatter_is_human_readable_and_paper_only():
    text = format_daily_edge_report(build_daily_edge_report())
    assert "PAPER_ONLY" in text
    assert "Classification:" in text
    assert "no broker/API/network/live execution" in text
    assert "LIVE_READY" not in text
