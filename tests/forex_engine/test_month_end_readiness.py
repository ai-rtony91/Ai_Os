from __future__ import annotations

from pathlib import Path

from automation.forex_engine import backtest_harness
from automation.forex_engine import evidence_bundle_runner
from automation.forex_engine import evidence_aggregator
from automation.forex_engine import forex_dashboard_contract
from automation.forex_engine import month_end_readiness
from automation.forex_engine import paper_forward_evidence_v2
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


def test_month_end_readiness_accepts_local_evidence_bundle_runner_output() -> None:
    bundle = evidence_bundle_runner.build_local_evidence_bundle()
    review = bundle["month_end_readiness_review"]

    assert review["classification"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}
    assert review["evidence_exists"]["backtest"] is True
    assert review["evidence_exists"]["paper_forward"] is True
    assert review["live_trade_ready"] is False
    assert review["protected_gate_required"] is True
    assert "broker integration is not approved" in review["live_trade_blockers"]


def test_month_end_readiness_accepts_v2_evidence_and_blocks_live_trading() -> None:
    bundle = paper_forward_evidence_v2.build_paper_forward_evidence_v2()
    review = month_end_readiness.build_month_end_readiness_v2_review(bundle)

    assert review["classification"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}
    assert review["paper_forward_ready"] in {True, False}
    assert review["v2_evidence_ready"] in {True, False}
    assert review["stress_oos_ready"] in {True, False}
    assert review["broker_paper_sandbox_ready"] is False
    assert review["stress_repair_status"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY", "not_run"}
    assert review["repaired_stress_classification"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY", "not_run"}
    assert review["broker_paper_contract_ready"] in {True, False}
    assert review["broker_paper_sandbox_readiness_status"] in {
        "NOT_READY",
        "WATCHLIST",
        "CONTRACT_READY_FOR_PROTECTED_BROKER_PAPER_SANDBOX_PACKET",
    }
    assert review["broker_paper_sandbox_contract_ready"] in {True, False}
    assert review["live_trade_ready"] is False
    assert review["protected_gate_required"] is True
    assert review["broker_integration_active"] is False
    assert review["credentials_required_now"] is False
    assert review["evidence_summary"]["fixture_count"] == 9
    assert review["evidence_summary"]["starting_balance"] == 500.0
    assert review["evidence_summary"]["ending_balance"] >= 500.0
    assert review["evidence_summary"]["return_pct"] >= 0.0
    assert review["evidence_summary"]["capture_rate_pct"] >= 0.0
    assert review["evidence_summary"]["missed_signal_count"] >= 0
    assert review["evidence_summary"]["missed_pnl_estimate"] >= 0.0
    assert review["evidence_summary"]["risk_adjusted_return"] >= 0.0
    assert review["evidence_summary"]["opportunity_quality_score"] >= 0.0
    assert review["evidence_summary"]["risk_governor_classification"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}
    assert review["evidence_summary"]["stress_scenario_count"] >= 1
    assert review["evidence_summary"]["paper_forward_stress_scenario_count"] >= 1
    assert review["evidence_summary"]["stress_classification"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY", "not_run"}
    assert review["evidence_summary"]["oos_classification"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY", "not_run"}
    assert review["evidence_summary"]["combined_stress_oos_classification"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY", "not_run"}
    assert review["evidence_summary"]["heldout_consistency_pct"] >= 0.0
    assert review["evidence_summary"]["degradation_pct"] >= 0.0
    assert review["evidence_summary"]["stress_repair_status"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY", "not_run"}
    assert review["evidence_summary"]["repaired_stress_classification"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY", "not_run"}
    assert "repaired_worst_stress_pnl" in review["evidence_summary"]
    assert review["evidence_summary"]["broker_paper_contract_ready"] in {True, False}
    assert review["evidence_summary"]["broker_paper_sandbox_ready"] is False
    assert review["evidence_summary"]["broker_paper_sandbox_readiness_status"] in {
        "NOT_READY",
        "WATCHLIST",
        "CONTRACT_READY_FOR_PROTECTED_BROKER_PAPER_SANDBOX_PACKET",
    }
    assert review["evidence_summary"]["broker_paper_sandbox_contract_ready"] in {True, False}
    assert review["evidence_summary"]["broker_integration_active"] is False
    assert review["evidence_summary"]["credentials_required_now"] is False
    assert "broker integration is not approved" in review["live_trade_blockers"]
    assert "live readiness requires separate future approval" in review["next_safe_action"]


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
