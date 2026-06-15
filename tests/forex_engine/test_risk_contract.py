from __future__ import annotations

from pathlib import Path

import pytest

from automation.forex_engine import backtest_harness
from automation.forex_engine import risk_contract


MODULE_PATH = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "risk_contract.py"


def ready_policy() -> dict[str, object]:
    return {
        "minimum_trades": 1,
        "minimum_expectancy_r": -1.0,
        "minimum_profit_factor": 0.1,
        "max_drawdown_pct": 50.0,
        "max_losing_streak": 10,
        "minimum_consistent_windows_pct": 0.0,
    }


def test_risk_contract_emits_only_allowed_classes() -> None:
    result = backtest_harness.run_local_backtest_harness()

    gate = risk_contract.classify_risk_gate(result, policy=ready_policy())

    assert gate.classification in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}
    assert risk_contract.assert_risk_contract_blocks_live(gate) is True


def test_risk_contract_blocks_live_ready() -> None:
    result = backtest_harness.run_local_backtest_harness()

    gate = risk_contract.classify_risk_gate(result, policy={"live_ready": True})

    assert gate.classification == "FAIL"
    assert "forbidden_boundary:live_ready" in gate.blockers
    assert gate.live_ready is False


def test_risk_contract_blocks_broker_network_orders_and_scheduler_flags() -> None:
    result = backtest_harness.run_local_backtest_harness()

    gate = risk_contract.classify_risk_gate(
        result,
        policy={
            "broker_allowed": True,
            "orders_allowed": True,
            "network_market_automation_allowed": True,
            "scheduler_allowed": True,
            "daemon_allowed": True,
            "webhooks_allowed": True,
            "credentials_allowed": True,
            "secrets_allowed": True,
        },
    )

    assert gate.classification == "FAIL"
    assert "forbidden_boundary:broker_allowed" in gate.blockers
    assert "forbidden_boundary:orders_allowed" in gate.blockers
    assert "forbidden_boundary:network_market_automation_allowed" in gate.blockers
    assert "forbidden_boundary:scheduler_allowed" in gate.blockers
    assert "forbidden_boundary:daemon_allowed" in gate.blockers


def test_risk_policy_summary_documents_edge_gate_relationship() -> None:
    summary = risk_contract.risk_policy_summary()

    assert summary["edge_gate_policy_module"] == "automation/forex_engine/edge_gate_policy.py"
    assert summary["automatic_live_ready"] is False
    assert "LIVE_READY" not in summary["allowed_classifications"]


def test_assert_risk_contract_rejects_live_ready_payload() -> None:
    with pytest.raises(ValueError, match="LIVE_READY"):
        risk_contract.assert_risk_contract_blocks_live(
            {
                "gate_id": "bad",
                "classification": "LIVE_READY",
                "blockers": [],
                "next_safe_action": "bad",
                "live_ready": False,
            }
        )


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
