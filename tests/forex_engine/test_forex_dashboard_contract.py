from __future__ import annotations

from pathlib import Path

from automation.forex_engine import backtest_harness
from automation.forex_engine import forex_dashboard_contract
from automation.forex_engine import paper_forward_evidence_v2
from automation.forex_engine import risk_contract


MODULE_PATH = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "forex_dashboard_contract.py"


def test_dashboard_contract_produces_compact_state() -> None:
    fixture = backtest_harness.build_sample_backtest_fixture()
    backtest = backtest_harness.run_local_backtest_harness(fixture)
    gate = risk_contract.classify_risk_gate(backtest, policy={"minimum_trades": 1})

    state = forex_dashboard_contract.build_forex_dashboard_state(
        fixture=fixture,
        backtest_result=backtest,
        risk_gate=gate,
        paper_forward_summary={"total_entries": 1},
    )
    lines = forex_dashboard_contract.format_forex_dashboard_lines(state)

    assert state.live_permission_state == "blocked"
    assert state.sos_required is False
    assert lines[0] == "FOREX BUILDER STATUS"
    assert len(lines) <= 10
    assert any("Risk gate:" in line for line in lines)
    assert any("Paper-forward:" in line for line in lines)
    assert lines[-1] == "Safety: no broker/live/secrets/orders/webhooks"


def test_dashboard_contract_summary_is_reportless_by_default() -> None:
    summary = forex_dashboard_contract.dashboard_contract_summary()

    assert summary["compact_default"] is True
    assert summary["max_default_lines"] == 10
    assert summary["reports_written_by_default"] is False
    assert summary["live_permission_state"] == "blocked"


def test_dashboard_state_accepts_blockers_and_next_safe_action() -> None:
    state = forex_dashboard_contract.build_forex_dashboard_state(
        blockers=["walk_forward_missing"],
        next_safe_action="Collect local evidence.",
    )

    assert state.current_blocker == "walk_forward_missing"
    assert state.next_safe_action == "Collect local evidence."


def test_dashboard_v2_summary_is_compact_and_live_blocked() -> None:
    bundle = paper_forward_evidence_v2.build_paper_forward_evidence_v2()
    summary = paper_forward_evidence_v2.summarize_paper_forward_evidence_v2(bundle)
    dashboard = forex_dashboard_contract.build_forex_dashboard_v2_summary(summary)
    lines = forex_dashboard_contract.format_forex_dashboard_v2_lines(dashboard)

    assert dashboard["fixture_count"] == 9
    assert dashboard["paper_forward_classification"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}
    assert dashboard["aggregate_paper_pnl"] >= 0.0
    assert dashboard["return_pct"] >= 0.0
    assert dashboard["capture_rate_pct"] >= 0.0
    assert dashboard["risk_governor_classification"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}
    assert dashboard["opportunity_quality_score"] >= 0.0
    assert dashboard["stress_classification"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY", "not_run"}
    assert dashboard["oos_classification"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY", "not_run"}
    assert dashboard["combined_stress_oos_classification"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY", "not_run"}
    assert dashboard["heldout_consistency_pct"] >= 0.0
    assert dashboard["degradation_pct"] >= 0.0
    assert dashboard["stress_oos_ready"] in {True, False}
    assert dashboard["broker_paper_sandbox_readiness_status"] in {
        "NOT_READY",
        "WATCHLIST",
        "CONTRACT_READY_FOR_PROTECTED_BROKER_PAPER_SANDBOX_PACKET",
        "not_run",
    }
    assert dashboard["broker_paper_sandbox_contract_ready"] in {True, False}
    assert dashboard["live_ready"] is False
    assert dashboard["protected_gate_required"] is True
    assert len(lines) <= 10
    assert any("PnL:" in line for line in lines)
    assert any("Capture:" in line for line in lines)
    assert any("Stress/OOS:" in line for line in lines)
    assert any("Sandbox contract:" in line for line in lines)
    assert any("Live ready: false" in line for line in lines)
    assert any("Protected gate required: true" in line for line in lines)
    assert lines[-1] == "Safety: no broker/live/secrets/orders/webhooks"


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
