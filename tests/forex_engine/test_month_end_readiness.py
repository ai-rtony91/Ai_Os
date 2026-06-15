from __future__ import annotations

from pathlib import Path

from automation.forex_engine import backtest_harness
from automation.forex_engine import evidence_aggregator
from automation.forex_engine import forex_dashboard_contract
from automation.forex_engine import month_end_readiness
from automation.forex_engine import paper_forward_simulator
from automation.forex_engine import risk_contract
from automation.forex_engine import schema_contracts as schemas


MODULE_PATH = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "month_end_readiness.py"


def evidence_bundle() -> dict[str, object]:
    backtest = backtest_harness.run_local_backtest_harness()
    walk = schemas.WalkForwardSummary(
        summary_id="summary-1",
        strategy_id=backtest.strategy_id,
        windows=[
            schemas.WalkForwardWindow(
                window_id="window-1",
                train_start="2026-06-15T09:00:00Z",
                train_end="2026-06-15T09:10:00Z",
                test_start="2026-06-15T09:15:00Z",
                test_end="2026-06-15T09:25:00Z",
                result=backtest,
                classification="PAPER_FORWARD_READY",
            )
        ],
        consistent_windows_pct=100.0,
        classification="PAPER_FORWARD_READY",
        blockers=[],
    )
    gate = risk_contract.classify_risk_gate(backtest, walk, policy={"minimum_trades": 1})
    intent = schemas.OrderIntent(
        intent_id="intent-1",
        signal_id="signal-1",
        symbol="EURUSD",
        direction="BUY",
        requested_units=1000,
        entry_reference_price=1.1000,
    )
    paper_entry = paper_forward_simulator.simulate_order_intent(intent, 1.1010)
    paper_summary = paper_forward_simulator.paper_forward_summary([paper_entry])
    return evidence_aggregator.aggregate_forex_evidence(backtest, walk, gate, paper_summary)


def test_month_end_readiness_blocks_live_trading_without_protected_approval() -> None:
    bundle = evidence_bundle()
    dashboard = forex_dashboard_contract.build_forex_dashboard_state(
        backtest_result=bundle["backtest_result"],
        risk_gate=bundle["risk_gate"],
        paper_forward_summary=bundle["paper_forward_summary"],
    )

    review = month_end_readiness.build_month_end_readiness_review(bundle, dashboard)

    assert review["paper_forward_ready"] in {True, False}
    assert review["live_trade_ready"] is False
    assert review["protected_gate_required"] is True
    assert review["live_trade_blockers"]
    assert "broker integration is not approved" in review["live_trade_blockers"]
    assert review["next_safe_action"]


def test_month_end_readiness_reports_complete_and_blocked_sections() -> None:
    review = month_end_readiness.build_month_end_readiness_review(evidence_bundle())

    assert "backtest result" in review["complete"]
    assert "cost model" in review["complete"]
    assert review["evidence_exists"]["backtest"] is True
    assert review["evidence_exists"]["risk_gate"] is True
    assert review["blocked"]


def test_module_has_no_network_broker_env_or_file_write_behavior() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    import_lines = "\n".join(
        line.strip()
        for line in source.splitlines()
        if line.startswith("import ") or line.startswith("from ")
    )

    for forbidden_import in ("subprocess", "socket", "urllib", "requests", "http", "os", "dotenv"):
        assert forbidden_import not in import_lines
    for forbidden_call in ("open(", "write_text(", "write_bytes(", "getenv", "environ", "start-process"):
        assert forbidden_call not in source
