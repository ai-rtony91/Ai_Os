from __future__ import annotations

from pathlib import Path

from automation.forex_engine import broker_paper_dryrun_replay_evidence_gate
from automation.forex_engine import broker_paper_dryrun_replay_harness


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "broker_paper_dryrun_replay_evidence_gate.py"
DEMO_PATH = REPO_ROOT / "automation" / "forex_engine" / "run_broker_paper_dryrun_replay_evidence_gate_demo.py"
ALLOWED_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "DRYRUN_REPLAY_EVIDENCE_READY"}


def test_module_exists() -> None:
    assert MODULE_PATH.exists()


def test_duplicate_prevention_reuses_replay_harness_without_recreating_prior_safety_modules() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "broker_paper_dryrun_replay_harness" in source
    assert "def build_presecurity_requirements" not in source
    assert "def build_broker_paper_adapter_stub_contract" not in source
    assert "def build_broker_paper_dryrun_intent_ledger_contract" not in source
    assert "def build_broker_paper_dryrun_risk_policy" not in source
    assert "def replay_dryrun_batch_through_safety_stack" not in source


def test_contract_blocks_capabilities_and_uses_in_memory_evidence() -> None:
    contract = broker_paper_dryrun_replay_evidence_gate.build_broker_paper_dryrun_replay_evidence_gate_contract()

    assert contract["mode"] == "PAPER_ONLY_DRYRUN_REPLAY_EVIDENCE_GATE"
    assert contract["evidence_storage"] == "IN_MEMORY_ONLY"
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
    assert contract["replay_harness_required"] is True
    assert contract["kill_switch_armed_required"] is True
    assert contract["deterministic_evidence_required"] is True
    assert "eom_milestone_alignment" in contract
    assert contract["next_safe_packet_if_ready"] == "PKT-AIOS-BROKER-PAPER-ADAPTER-PLAN-APPROVAL-GATE-V1"


def test_default_evidence_result_is_ready_without_side_effects() -> None:
    result = broker_paper_dryrun_replay_evidence_gate.build_default_replay_evidence_gate_result()
    summary = broker_paper_dryrun_replay_evidence_gate.summarize_replay_evidence_gate(result)

    assert result["classification"] == "DRYRUN_REPLAY_EVIDENCE_READY"
    assert result["evidence_ready"] is True
    assert result["records_replayed"] == 2
    assert result["stub_accepted"] == 1
    assert result["stub_rejected"] == 1
    assert result["risk_accepted"] == 1
    assert result["risk_rejected"] == 1
    assert result["aggregate_max_loss_usd"] <= result["max_daily_loss_usd"]
    assert result["kill_switch_armed"] is True
    assert result["all_unsafe_flags_false"] is True
    assert result["broker_sdk_allowed"] is False
    assert result["network_api_allowed"] is False
    assert result["credentials_allowed"] is False
    assert result["broker_paper_orders_allowed"] is False
    assert result["live_ready"] is False
    assert result["live_orders_allowed"] is False
    assert summary["next_safe_packet"] == "PKT-AIOS-BROKER-PAPER-ADAPTER-PLAN-APPROVAL-GATE-V1"


def test_evidence_requires_replay_harness_ready() -> None:
    replay = broker_paper_dryrun_replay_harness.replay_dryrun_batch_through_safety_stack()
    replay["classification"] = "WATCHLIST"
    replay["broker_paper_dryrun_replay_harness_classification"] = "WATCHLIST"

    result = broker_paper_dryrun_replay_evidence_gate.validate_replay_harness_evidence(replay)

    assert result["classification"] == "WATCHLIST"
    assert "replay_harness_must_be_ready" in result["blockers"]


def test_evidence_requires_minimum_replay_records() -> None:
    replay = broker_paper_dryrun_replay_harness.replay_dryrun_batch_through_safety_stack()
    replay["records_replayed"] = 1

    result = broker_paper_dryrun_replay_evidence_gate.validate_replay_harness_evidence(replay)

    assert result["classification"] == "WATCHLIST"
    assert "minimum_replay_records_not_met" in result["blockers"]


def test_evidence_requires_accepted_and_rejected_stub_counts() -> None:
    replay = broker_paper_dryrun_replay_harness.replay_dryrun_batch_through_safety_stack()
    replay["stub_accepted"] = 0
    replay["stub_rejected"] = 0

    result = broker_paper_dryrun_replay_evidence_gate.validate_replay_harness_evidence(replay)

    assert result["classification"] == "WATCHLIST"
    assert "minimum_stub_accepted_not_met" in result["blockers"]
    assert "minimum_stub_rejected_not_met" in result["blockers"]


def test_evidence_requires_accepted_and_rejected_risk_counts() -> None:
    replay = broker_paper_dryrun_replay_harness.replay_dryrun_batch_through_safety_stack()
    replay["risk_accepted"] = 0
    replay["risk_rejected"] = 0

    result = broker_paper_dryrun_replay_evidence_gate.validate_replay_harness_evidence(replay)

    assert result["classification"] == "WATCHLIST"
    assert "minimum_risk_accepted_not_met" in result["blockers"]
    assert "minimum_risk_rejected_not_met" in result["blockers"]


def test_evidence_rejects_max_loss_over_daily_cap() -> None:
    replay = broker_paper_dryrun_replay_harness.replay_dryrun_batch_through_safety_stack()
    replay["aggregate_max_loss_usd"] = replay["max_daily_loss_usd"] + 1.0

    result = broker_paper_dryrun_replay_evidence_gate.validate_replay_harness_evidence(replay)

    assert result["classification"] == "WATCHLIST"
    assert "aggregate_max_loss_exceeds_daily_cap" in result["blockers"]


def test_evidence_rejects_kill_switch_off() -> None:
    replay = broker_paper_dryrun_replay_harness.replay_dryrun_batch_through_safety_stack()
    replay["kill_switch_armed"] = False

    result = broker_paper_dryrun_replay_evidence_gate.validate_replay_harness_evidence(replay)

    assert result["classification"] == "WATCHLIST"
    assert "kill_switch_must_remain_armed" in result["blockers"]


def test_evidence_rejects_any_unsafe_flag_true() -> None:
    for field in (
        "would_place_order",
        "order_placed",
        "broker_request_sent",
        "network_used",
        "credentials_used",
        "live_ready",
        "broker_paper_orders_allowed",
        "broker_sdk_allowed",
        "network_api_allowed",
        "credentials_allowed",
    ):
        replay = broker_paper_dryrun_replay_harness.replay_dryrun_batch_through_safety_stack()
        replay[field] = True

        result = broker_paper_dryrun_replay_evidence_gate.validate_replay_harness_evidence(replay)

        assert result["classification"] == "FAIL"
        assert "unsafe_flag_detected" in result["blockers"]


def test_classification_set_never_emits_broker_live_or_order_ready() -> None:
    result = broker_paper_dryrun_replay_evidence_gate.build_default_replay_evidence_gate_result()
    summary = broker_paper_dryrun_replay_evidence_gate.summarize_replay_evidence_gate(result)

    assert broker_paper_dryrun_replay_evidence_gate.classify_replay_evidence_gate(summary) in ALLOWED_CLASSIFICATIONS
    assert summary["classification"] in ALLOWED_CLASSIFICATIONS
    assert summary["classification"] not in {"LIVE_READY", "BROKER_READY", "ORDER_READY"}


def test_boundary_summary_blocks_broker_network_credentials_orders_reports_and_files() -> None:
    summary = broker_paper_dryrun_replay_evidence_gate.broker_paper_dryrun_replay_evidence_gate_boundary_summary()

    assert summary["evidence_gate_only"] is True
    assert summary["in_memory_only"] is True
    assert summary["file_writes_allowed"] is False
    assert summary["reports_writes_allowed"] is False
    assert summary["broker_sdk_allowed"] is False
    assert summary["network_api_allowed"] is False
    assert summary["credentials_allowed"] is False
    assert summary["broker_paper_orders_allowed"] is False
    assert summary["live_orders_allowed"] is False
    assert summary["next_safe_packet_if_ready"] == "PKT-AIOS-BROKER-PAPER-ADAPTER-PLAN-APPROVAL-GATE-V1"


def test_demo_imports_and_prints_required_lines(capsys) -> None:
    from automation.forex_engine import run_broker_paper_dryrun_replay_evidence_gate_demo

    assert run_broker_paper_dryrun_replay_evidence_gate_demo.main([]) == 0
    output = capsys.readouterr().out

    assert "AIOS Broker-Paper Dry-Run Replay Evidence Gate Demo" in output
    assert "Mode: PAPER_ONLY_DRYRUN_REPLAY_EVIDENCE_GATE" in output
    assert "Classification: DRYRUN_REPLAY_EVIDENCE_READY" in output
    assert "Evidence ready: true" in output
    assert "Records replayed: 2" in output
    assert "Stub accepted/rejected: 1/1" in output
    assert "Risk accepted/rejected: 1/1" in output
    assert "Kill switch armed: true" in output
    assert "All unsafe flags false: true" in output
    assert "Broker SDK allowed: false" in output
    assert "Network/API allowed: false" in output
    assert "Credentials allowed: false" in output
    assert "Broker-paper orders allowed: false" in output
    assert "Live orders allowed: false" in output
    assert "Safety: evidence gate only; no broker/API/network/orders/secrets/live execution." in output


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
