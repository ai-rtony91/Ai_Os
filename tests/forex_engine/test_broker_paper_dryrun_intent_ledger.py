from __future__ import annotations

from pathlib import Path

from automation.forex_engine import broker_paper_dryrun_intent_ledger
from automation.forex_engine import run_broker_paper_dryrun_intent_ledger_demo


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "broker_paper_dryrun_intent_ledger.py"
DEMO_PATH = REPO_ROOT / "automation" / "forex_engine" / "run_broker_paper_dryrun_intent_ledger_demo.py"
ALLOWED_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "DRYRUN_LEDGER_READY"}
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


def invalid_fake_intent() -> dict[str, object]:
    return {
        "symbol": "EURUSD",
        "side": "hold",
        "quantity_units": 0,
        "order_type": "market",
        "max_loss_usd": 1000.0,
        "dry_run": False,
        "approved_by_operator": False,
    }


def test_dryrun_ledger_module_exists() -> None:
    assert MODULE_PATH.exists()


def test_contract_includes_all_blocked_capability_flags_and_schemas() -> None:
    contract = broker_paper_dryrun_intent_ledger.build_broker_paper_dryrun_intent_ledger_contract()

    assert contract["mode"] == "PAPER_ONLY_DRYRUN_INTENT_LEDGER"
    assert contract["ledger_storage"] == "IN_MEMORY_ONLY"
    assert contract["file_writes_allowed"] is False
    assert contract["reports_writes_allowed"] is False
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
    assert contract["stub_contract_required"] is True
    assert contract["kill_switch_required"] is True
    assert contract["max_loss_guard_required"] is True
    assert contract["daily_stop_required"] is True
    assert contract["audit_log_required"] is True
    assert contract["deterministic_record_required"] is True
    assert "intent_schema" in contract
    assert "stub_result_schema" in contract
    assert "ledger_record_schema" in contract
    assert "ledger_summary_schema" in contract
    assert "safety_invariants" in contract


def test_accepted_fake_dryrun_intent_creates_simulated_audit_record_only() -> None:
    record = broker_paper_dryrun_intent_ledger.create_dryrun_intent_record(valid_fake_intent())

    assert record["accepted_for_simulation"] is True
    assert record["classification"] == "DRYRUN_LEDGER_READY"
    assert record["record_id"].startswith("DRYRUN-")
    assert record["packet_id"] == "PKT-AIOS-BROKER-PAPER-DRYRUN-INTENT-LEDGER-V1"
    assert record["audit_notes"]
    assert record["would_place_order"] is False
    assert record["order_placed"] is False
    assert record["broker_request_sent"] is False
    assert record["network_used"] is False
    assert record["credentials_used"] is False
    assert record["live_ready"] is False
    assert record["broker_paper_orders_allowed"] is False


def test_rejected_fake_intent_creates_rejection_record() -> None:
    record = broker_paper_dryrun_intent_ledger.create_dryrun_intent_record(invalid_fake_intent())

    assert record["accepted_for_simulation"] is False
    assert record["classification"] == "WATCHLIST"
    assert record["rejection_reasons"]
    assert record["would_place_order"] is False
    assert record["order_placed"] is False
    assert record["broker_request_sent"] is False
    assert record["network_used"] is False
    assert record["credentials_used"] is False
    assert record["live_ready"] is False
    assert record["broker_paper_orders_allowed"] is False


def test_ledger_append_returns_new_dict_and_counts_accepted_and_rejected_records() -> None:
    ledger = broker_paper_dryrun_intent_ledger.build_empty_dryrun_intent_ledger()
    accepted = broker_paper_dryrun_intent_ledger.create_dryrun_intent_record(valid_fake_intent())
    rejected = broker_paper_dryrun_intent_ledger.create_dryrun_intent_record(invalid_fake_intent())

    next_ledger = broker_paper_dryrun_intent_ledger.append_dryrun_intent_record(ledger, accepted)
    final_ledger = broker_paper_dryrun_intent_ledger.append_dryrun_intent_record(next_ledger, rejected)
    summary = broker_paper_dryrun_intent_ledger.summarize_dryrun_intent_ledger(final_ledger)

    assert ledger["records_count"] == 0
    assert next_ledger is not ledger
    assert final_ledger["records_count"] == 2
    assert summary["records_count"] == 2
    assert summary["accepted_count"] == 1
    assert summary["rejected_count"] == 1
    assert summary["classification"] == "DRYRUN_LEDGER_READY"
    assert summary["broker_paper_dryrun_ledger_ready"] is True
    assert summary["next_safe_packet"] == "PKT-AIOS-BROKER-PAPER-DRYRUN-RISK-GOVERNOR-V1"
    assert summary["would_place_order"] is False
    assert summary["order_placed"] is False
    assert summary["broker_request_sent"] is False
    assert summary["network_used"] is False
    assert summary["credentials_used"] is False
    assert summary["live_ready"] is False
    assert summary["broker_paper_orders_allowed"] is False


def test_replay_batch_produces_in_memory_ledger_with_accept_and_reject_audit() -> None:
    ledger = broker_paper_dryrun_intent_ledger.replay_dryrun_intent_batch()
    summary = broker_paper_dryrun_intent_ledger.summarize_dryrun_intent_ledger(ledger)

    assert ledger["ledger_storage"] == "IN_MEMORY_ONLY"
    assert summary["records_count"] >= 2
    assert summary["accepted_count"] >= 1
    assert summary["rejected_count"] >= 1
    assert summary["classification"] in ALLOWED_CLASSIFICATIONS
    assert summary["classification"] not in FORBIDDEN_CLASSIFICATIONS
    assert summary["classification"] == "DRYRUN_LEDGER_READY"


def test_boundary_summary_blocks_file_reports_broker_network_credentials_orders_scheduler_and_daemon() -> None:
    boundary = broker_paper_dryrun_intent_ledger.broker_paper_dryrun_intent_ledger_boundary_summary()

    assert boundary["ledger_only"] is True
    assert boundary["in_memory_only"] is True
    assert boundary["file_writes_allowed"] is False
    assert boundary["reports_writes_allowed"] is False
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
    assert run_broker_paper_dryrun_intent_ledger_demo.main([]) == 0
    output = capsys.readouterr().out

    assert "AIOS Broker-Paper Dry-Run Intent Ledger Demo" in output
    assert "Mode: PAPER_ONLY_DRYRUN_INTENT_LEDGER" in output
    assert "Classification: DRYRUN_LEDGER_READY" in output
    assert "Ledger storage: IN_MEMORY_ONLY" in output
    assert "Records: 2" in output
    assert "Accepted: 1" in output
    assert "Rejected: 1" in output
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
    assert "Safety: dry-run ledger only; no broker/API/network/orders/secrets/live execution." in output


def test_classification_is_limited_and_never_emits_forbidden_ready_states() -> None:
    for classification in ALLOWED_CLASSIFICATIONS:
        payload = {"classification": classification}
        assert broker_paper_dryrun_intent_ledger.classify_dryrun_intent_ledger(payload) in ALLOWED_CLASSIFICATIONS

    for classification in FORBIDDEN_CLASSIFICATIONS:
        payload = {"classification": classification}
        assert broker_paper_dryrun_intent_ledger.classify_dryrun_intent_ledger(payload) == "FAIL"


def test_ledger_modules_have_no_forbidden_imports_or_execution_calls() -> None:
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
            "path.write_text",
            "path.write_bytes",
            "start-process",
        ):
            assert forbidden_call not in source
