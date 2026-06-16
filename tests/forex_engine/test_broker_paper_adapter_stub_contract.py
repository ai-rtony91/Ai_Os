from __future__ import annotations

from pathlib import Path

from automation.forex_engine import broker_paper_adapter_stub_contract
from automation.forex_engine import run_broker_paper_adapter_stub_contract_demo


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "broker_paper_adapter_stub_contract.py"
DEMO_PATH = REPO_ROOT / "automation" / "forex_engine" / "run_broker_paper_adapter_stub_contract_demo.py"
ALLOWED_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "STUB_CONTRACT_READY"}
FORBIDDEN_CLASSIFICATIONS = {"LIVE_READY", "BROKER_READY", "ORDER_READY"}


def valid_fake_intent() -> dict[str, object]:
    return {
        "symbol": "EURUSD_FAKE",
        "side": "buy",
        "quantity_units": 1000,
        "order_type": "market_stub",
        "stop_loss_pips": 8.0,
        "take_profit_pips": 12.0,
        "max_loss_usd": 10.0,
        "dry_run": True,
        "approved_by_operator": True,
    }


def test_stub_contract_module_exists() -> None:
    assert MODULE_PATH.exists()


def test_contract_includes_blocked_capability_flags_and_intent_schema() -> None:
    contract = broker_paper_adapter_stub_contract.build_broker_paper_adapter_stub_contract()

    assert contract["mode"] == "PAPER_ONLY_STUB_CONTRACT"
    assert contract["broker_sdk_allowed"] is False
    assert contract["network_api_allowed"] is False
    assert contract["credentials_allowed"] is False
    assert contract["env_secret_read_allowed"] is False
    assert contract["webhook_allowed"] is False
    assert contract["scheduler_allowed"] is False
    assert contract["daemon_allowed"] is False
    assert contract["broker_paper_orders_allowed"] is False
    assert contract["live_orders_allowed"] is False
    assert contract["manual_approval_required"] is True
    assert contract["presecurity_gate_required"] is True
    assert contract["kill_switch_required"] is True
    assert contract["max_loss_guard_required"] is True
    assert contract["daily_stop_required"] is True
    assert contract["audit_log_required"] is True
    assert "intent_schema" in contract
    assert "normalized_intent_schema" in contract
    assert "rejection_reasons" in contract
    assert "safety_invariants" in contract


def test_invalid_intent_is_rejected_without_any_order_behavior() -> None:
    result = broker_paper_adapter_stub_contract.simulate_broker_paper_stub_adapter(
        {"symbol": "EURUSD", "side": "hold", "dry_run": False}
    )

    assert result["accepted_for_simulation"] is False
    assert result["classification"] == "WATCHLIST"
    assert result["rejection_reasons"]
    assert result["would_place_order"] is False
    assert result["order_placed"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["credentials_used"] is False
    assert result["live_ready"] is False
    assert result["broker_paper_orders_allowed"] is False


def test_valid_fake_dry_run_intent_is_simulated_only() -> None:
    result = broker_paper_adapter_stub_contract.simulate_broker_paper_stub_adapter(valid_fake_intent())
    summary = broker_paper_adapter_stub_contract.summarize_broker_paper_stub_contract(result)

    assert result["adapter_mode"] == "STUB_ONLY"
    assert result["accepted_for_simulation"] is True
    assert result["classification"] == "STUB_CONTRACT_READY"
    assert summary["broker_paper_stub_contract_ready"] is True
    assert summary["classification"] in ALLOWED_CLASSIFICATIONS
    assert summary["classification"] not in FORBIDDEN_CLASSIFICATIONS
    assert result["would_place_order"] is False
    assert result["order_placed"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["credentials_used"] is False
    assert result["live_ready"] is False
    assert result["broker_paper_orders_allowed"] is False
    assert "PKT-AIOS-BROKER-PAPER-DRYRUN-INTENT-LEDGER-V1" in result["next_safe_action"]


def test_boundary_summary_blocks_broker_network_credentials_orders_scheduler_and_daemon() -> None:
    boundary = broker_paper_adapter_stub_contract.broker_paper_stub_boundary_summary()

    assert boundary["stub_contract_only"] is True
    assert boundary["broker_sdk_allowed"] is False
    assert boundary["network_api_allowed"] is False
    assert boundary["credentials_allowed"] is False
    assert boundary["env_secret_read_allowed"] is False
    assert boundary["webhook_allowed"] is False
    assert boundary["scheduler_allowed"] is False
    assert boundary["daemon_allowed"] is False
    assert boundary["broker_paper_orders_allowed"] is False
    assert boundary["live_orders_allowed"] is False
    assert boundary["would_place_order"] is False
    assert boundary["order_placed"] is False
    assert boundary["broker_request_sent"] is False
    assert boundary["network_used"] is False


def test_demo_imports_and_prints_required_lines(capsys) -> None:
    assert run_broker_paper_adapter_stub_contract_demo.main([]) == 0
    output = capsys.readouterr().out

    assert "AIOS Broker-Paper Adapter Stub Contract Demo" in output
    assert "Mode: PAPER_ONLY_STUB_CONTRACT" in output
    assert "Classification: STUB_CONTRACT_READY" in output
    assert "Broker SDK allowed: false" in output
    assert "Network/API allowed: false" in output
    assert "Credentials allowed: false" in output
    assert "Env secret read allowed: false" in output
    assert "Webhook allowed: false" in output
    assert "Scheduler allowed: false" in output
    assert "Daemon allowed: false" in output
    assert "Broker-paper orders allowed: false" in output
    assert "Live orders allowed: false" in output
    assert "Would place order: false" in output
    assert "Order placed: false" in output
    assert "Safety: stub-only; no broker/API/network/orders/secrets/live execution." in output


def test_stub_modules_have_no_forbidden_imports_or_execution_calls() -> None:
    for path in (MODULE_PATH, DEMO_PATH):
        source = path.read_text(encoding="utf-8").lower()
        import_lines = "\n".join(
            line.strip()
            for line in source.splitlines()
            if line.startswith("import ") or line.startswith("from ")
        )

        for forbidden_import in ("requests", "socket", "urllib", "subprocess", "dotenv", "schedule", "daemon"):
            assert forbidden_import not in import_lines
        for line in import_lines.splitlines():
            assert not line.startswith("import broker")
            assert not line.startswith("from broker")
            assert not line.startswith("import oanda")
            assert not line.startswith("from oanda")
            assert not line.startswith("import mt5")
            assert not line.startswith("from mt5")
            assert not line.startswith("import ibkr")
            assert not line.startswith("from ibkr")
        for forbidden_call in (
            "os.environ",
            "getenv",
            "dotenv",
            "requests.",
            "socket.",
            "urllib.",
            "oanda",
            "mt5",
            "ibkr",
            "schedule.every",
            "daemon.daemoncontext",
            "open(",
            "write_text(",
            "write_bytes(",
            "start-process",
        ):
            assert forbidden_call not in source
