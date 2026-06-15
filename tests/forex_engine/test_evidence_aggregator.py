from __future__ import annotations

from pathlib import Path

from automation.forex_engine import backtest_harness
from automation.forex_engine import evidence_aggregator
from automation.forex_engine import paper_forward_simulator
from automation.forex_engine import risk_contract
from automation.forex_engine import schema_contracts as schemas


MODULE_PATH = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "evidence_aggregator.py"


def walk_forward_summary(backtest: schemas.BacktestResult) -> schemas.WalkForwardSummary:
    window = schemas.WalkForwardWindow(
        window_id="window-1",
        train_start="2026-06-15T09:00:00Z",
        train_end="2026-06-15T09:10:00Z",
        test_start="2026-06-15T09:15:00Z",
        test_end="2026-06-15T09:25:00Z",
        result=backtest,
        classification="PAPER_FORWARD_READY",
    )
    return schemas.WalkForwardSummary(
        summary_id="summary-1",
        strategy_id=backtest.strategy_id,
        windows=[window],
        consistent_windows_pct=100.0,
        classification="PAPER_FORWARD_READY",
        blockers=[],
    )


def test_evidence_aggregator_combines_required_evidence_without_live_ready() -> None:
    backtest = backtest_harness.run_local_backtest_harness()
    walk = walk_forward_summary(backtest)
    gate = risk_contract.classify_risk_gate(backtest, walk, policy=risk_contract.EDGE_GATE_POLICY | {"minimum_trades": 1})
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

    bundle = evidence_aggregator.aggregate_forex_evidence(backtest, walk, gate, paper_summary)

    assert bundle["classification"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}
    assert bundle["classification"] != "LIVE_READY"
    assert bundle["live_ready"] is False
    assert bundle["backtest_result"]
    assert bundle["walk_forward_summary"]
    assert bundle["cost_model"]
    assert bundle["risk_gate"]
    assert bundle["paper_forward_summary"]
    assert bundle["next_safe_action"]


def test_evidence_aggregator_never_emits_live_ready_from_bad_input() -> None:
    bundle = {"classification": "LIVE_READY", "live_ready": True, "risk_gate": {}}

    assert evidence_aggregator.classify_evidence_bundle(bundle) == "FAIL"


def test_evidence_aggregator_marks_missing_paper_summary_watchlist() -> None:
    backtest = backtest_harness.run_local_backtest_harness()
    walk = walk_forward_summary(backtest)
    gate = risk_contract.classify_risk_gate(backtest, walk, policy={"minimum_trades": 1})

    bundle = evidence_aggregator.aggregate_forex_evidence(backtest, walk, gate)

    assert bundle["classification"] in {"FAIL", "WATCHLIST"}
    assert "paper_forward_summary_missing" in bundle["blockers"]


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
