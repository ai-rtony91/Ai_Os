from __future__ import annotations

from pathlib import Path

import pytest

from automation.forex_engine import backtest_harness
from automation.forex_engine import paper_forward_simulator
from automation.forex_engine import schema_contracts as schemas


MODULE_PATH = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "paper_forward_simulator.py"


def intent(direction: str = "BUY") -> schemas.OrderIntent:
    return schemas.OrderIntent(
        intent_id=f"intent-{direction.lower()}",
        signal_id="signal-1",
        symbol="EURUSD",
        direction=direction,
        requested_units=1000,
        entry_reference_price=1.1000,
        stop_loss_reference_price=1.0950,
        take_profit_reference_price=1.1050,
    )


def test_simulate_order_intent_creates_simulated_ledger_entry_only() -> None:
    entry = paper_forward_simulator.simulate_order_intent(intent(), 1.1010)

    assert entry.status == "SIMULATED_ONLY"
    assert entry.broker_order_id is None
    assert entry.live_order is False
    assert entry.simulated_fill_price == 1.1010
    assert entry.simulated_pnl_usd == pytest.approx(1.0)


def test_run_paper_forward_simulation_never_creates_broker_order_ids_or_live_orders() -> None:
    fixture = backtest_harness.build_sample_backtest_fixture()

    entries = paper_forward_simulator.run_paper_forward_simulation(
        [intent("BUY"), intent("SELL")],
        fixture,
    )

    assert len(entries) == 2
    for entry in entries:
        assert entry.status == "SIMULATED_ONLY"
        assert entry.broker_order_id is None
        assert entry.live_order is False


def test_paper_forward_summary_blocks_execution_and_live_paths() -> None:
    entry = paper_forward_simulator.simulate_order_intent(intent(), 1.1010)
    summary = paper_forward_simulator.paper_forward_summary([entry])

    assert summary["status"] == "SIMULATED_ONLY"
    assert summary["broker_order_ids"] == []
    assert summary["live_orders"] is False
    assert summary["execution_allowed"] is False
    assert summary["local_simulation_only"] is True


def test_paper_forward_simulator_rejects_executable_intent() -> None:
    bad_intent = {**schemas.asdict(intent()), "execution_allowed": True}

    with pytest.raises(ValueError, match="execution_allowed"):
        paper_forward_simulator.simulate_order_intent(bad_intent, 1.1010)


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
