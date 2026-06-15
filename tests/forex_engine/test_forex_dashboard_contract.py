from __future__ import annotations

from pathlib import Path

from automation.forex_engine import backtest_harness
from automation.forex_engine import forex_dashboard_contract
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
