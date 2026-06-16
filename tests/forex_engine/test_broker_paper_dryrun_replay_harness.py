from __future__ import annotations

from pathlib import Path

from automation.forex_engine import broker_paper_adapter_stub_contract
from automation.forex_engine import broker_paper_dryrun_replay_harness


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "broker_paper_dryrun_replay_harness.py"
DEMO_PATH = REPO_ROOT / "automation" / "forex_engine" / "run_broker_paper_dryrun_replay_harness_demo.py"
ALLOWED_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "DRYRUN_REPLAY_HARNESS_READY"}


def test_module_exists() -> None:
    assert MODULE_PATH.exists()


def test_duplicate_prevention_reuses_existing_chain_contracts() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "broker_paper_presecurity_gate" in source
    assert "broker_paper_adapter_stub_contract" in source
    assert "broker_paper_dryrun_intent_ledger" in source
    assert "broker_paper_dryrun_risk_governor" in source
    assert "def build_presecurity_requirements" not in source
    assert "def build_broker_paper_adapter_stub_contract" not in source
    assert "def build_broker_paper_dryrun_intent_ledger_contract" not in source
    assert "def build_broker_paper_dryrun_risk_policy" not in source


def test_contract_blocks_all_protected_capabilities_and_uses_in_memory_replay() -> None:
    contract = broker_paper_dryrun_replay_harness.build_broker_paper_dryrun_replay_harness_contract()

    assert contract["mode"] == "PAPER_ONLY_DRYRUN_REPLAY_HARNESS"
    assert contract["replay_storage"] == "IN_MEMORY_ONLY"
    assert contract["file_writes_allowed"] is False
    assert contract["reports_writes_allowed"] is False
    for field in (
        "broker_sdk_allowed",
        "network_api_allowed",
        "credentials_allowed",
        "env_secret_read_allowed",
        "webhook_allowed",
        "scheduler_allowed",
        "daemon_allowed",
        "broker_paper_orders_allowed",
        "live_orders_allowed",
    ):
        assert contract[field] is False
    for field in (
        "manual_approval_required",
        "presecurity_gate_required",
        "stub_contract_required",
        "dryrun_ledger_required",
        "dryrun_risk_governor_required",
        "kill_switch_required",
        "kill_switch_armed",
        "max_loss_guard_required",
        "daily_stop_required",
        "audit_log_required",
        "deterministic_replay_required",
    ):
        assert contract[field] is True
    assert "replay_batch_schema" in contract
    assert "replay_result_schema" in contract
    assert "safety_invariants" in contract
    assert contract["next_safe_packet_if_ready"] == "PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-EVIDENCE-GATE-V1"


def test_default_batch_has_accepted_and_rejected_fake_examples() -> None:
    batch = broker_paper_dryrun_replay_harness.build_default_replay_batch()
    stub_results = [
        broker_paper_adapter_stub_contract.simulate_broker_paper_stub_adapter(intent)
        for intent in batch
    ]

    assert len(batch) >= 2
    assert any(item["accepted_for_simulation"] is True for item in stub_results)
    assert any(item["accepted_for_simulation"] is False for item in stub_results)
    assert all(str(intent["symbol"]).endswith("_FAKE") for intent in batch)
    assert all(intent["dry_run"] is True for intent in batch)


def test_replay_produces_stub_ledger_and_risk_counts_without_side_effects() -> None:
    result = broker_paper_dryrun_replay_harness.replay_dryrun_batch_through_safety_stack()
    summary = broker_paper_dryrun_replay_harness.summarize_dryrun_replay_harness(result)

    assert result["records_replayed"] == 2
    assert result["stub_accepted"] == 1
    assert result["stub_rejected"] == 1
    assert result["ledger_records"] == 2
    assert result["risk_accepted"] == 1
    assert result["risk_rejected"] == 1
    assert result["aggregate_max_loss_usd"] <= result["max_daily_loss_usd"]
    assert result["aggregate_max_loss_usd"] == 1.0
    assert result["kill_switch_armed"] is True
    assert result["would_place_order"] is False
    assert result["order_placed"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["credentials_used"] is False
    assert result["live_ready"] is False
    assert result["broker_paper_orders_allowed"] is False
    assert summary["classification"] == "DRYRUN_REPLAY_HARNESS_READY"
    assert summary["broker_paper_dryrun_replay_harness_ready"] is True
    assert summary["next_safe_packet"] == "PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-EVIDENCE-GATE-V1"


def test_classification_set_never_emits_broker_live_or_order_ready() -> None:
    result = broker_paper_dryrun_replay_harness.replay_dryrun_batch_through_safety_stack()
    summary = broker_paper_dryrun_replay_harness.summarize_dryrun_replay_harness(result)

    assert broker_paper_dryrun_replay_harness.classify_dryrun_replay_harness(summary) in ALLOWED_CLASSIFICATIONS
    assert summary["classification"] in ALLOWED_CLASSIFICATIONS
    assert summary["classification"] not in {"LIVE_READY", "BROKER_READY", "ORDER_READY"}


def test_boundary_summary_blocks_broker_network_credentials_orders_reports_and_files() -> None:
    summary = broker_paper_dryrun_replay_harness.broker_paper_dryrun_replay_harness_boundary_summary()

    assert summary["replay_harness_only"] is True
    assert summary["in_memory_only"] is True
    assert summary["file_writes_allowed"] is False
    assert summary["reports_writes_allowed"] is False
    assert summary["broker_sdk_allowed"] is False
    assert summary["network_api_allowed"] is False
    assert summary["credentials_allowed"] is False
    assert summary["env_secret_read_allowed"] is False
    assert summary["webhook_allowed"] is False
    assert summary["scheduler_allowed"] is False
    assert summary["daemon_allowed"] is False
    assert summary["broker_paper_orders_allowed"] is False
    assert summary["live_orders_allowed"] is False
    assert summary["would_place_order"] is False
    assert summary["order_placed"] is False


def test_demo_imports_and_prints_required_lines(capsys) -> None:
    from automation.forex_engine import run_broker_paper_dryrun_replay_harness_demo

    assert run_broker_paper_dryrun_replay_harness_demo.main([]) == 0
    output = capsys.readouterr().out

    assert "AIOS Broker-Paper Dry-Run Replay Harness Demo" in output
    assert "Mode: PAPER_ONLY_DRYRUN_REPLAY_HARNESS" in output
    assert "Classification: DRYRUN_REPLAY_HARNESS_READY" in output
    assert "Records replayed: 2" in output
    assert "Stub accepted: 1" in output
    assert "Stub rejected: 1" in output
    assert "Risk accepted: 1" in output
    assert "Risk rejected: 1" in output
    assert "Kill switch armed: true" in output
    assert "Broker SDK allowed: false" in output
    assert "Network/API allowed: false" in output
    assert "Credentials allowed: false" in output
    assert "Broker-paper orders allowed: false" in output
    assert "Live orders allowed: false" in output
    assert "Would place order: false" in output
    assert "Order placed: false" in output
    assert "Safety: dry-run replay harness only; no broker/API/network/orders/secrets/live execution." in output


def test_modules_have_no_forbidden_imports_or_calls() -> None:
    for path in (MODULE_PATH, DEMO_PATH):
        source = path.read_text(encoding="utf-8").lower()
        import_lines = "\n".join(
            line.strip()
            for line in source.splitlines()
            if line.startswith("import ") or line.startswith("from ")
        )

        for forbidden_import in ("requests", "socket", "urllib", "subprocess", "dotenv", "mt5", "ibkr"):
            assert forbidden_import not in import_lines
        for line in import_lines.splitlines():
            assert not line.startswith("import broker")
            assert not line.startswith("from broker")
            assert not line.startswith("import oanda")
            assert not line.startswith("from oanda")
        for forbidden_call in (
            "os.environ",
            "getenv",
            "open(",
            "write_text(",
            "write_bytes(",
            "start-process",
            "schedule.every",
            "daemon.daemoncontext",
        ):
            assert forbidden_call not in source
