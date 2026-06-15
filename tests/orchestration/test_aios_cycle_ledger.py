from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_cycle_ledger.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_cycle_ledger", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def base_cycle(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "cycle_id": "CYCLE-001",
        "timestamp_utc": "2026-06-15T12:00:00Z",
        "repo_branch": "main",
        "repo_head": "abc1234",
        "selected_packet": {"packet_id": "PKT-AIOS-SAFE-NEXT", "title": "Build safe next packet"},
        "selected_reason": "highest safe packet",
        "codex_prompt_emitted": True,
        "validation_status": "passed",
        "validation_summary": "pytest passed",
        "pr_number": 723,
        "pr_status": "merged",
        "checks_status": "passed",
        "blocker_status": "none",
        "next_safe_action": "Review dashboard contract and stop before staging.",
        "tests_passed": 12,
        "tests_failed": 0,
    }
    payload.update(overrides)
    return payload


def assert_preview_only(result: dict[str, object]) -> None:
    assert result["commands_executed"] == []
    assert result["files_written"] == []
    assert result["workers_dispatched"] is False
    assert result["queues_mutated"] is False
    assert result["approvals_mutated"] is False
    safety = result["safety"]
    assert isinstance(safety, dict)
    assert safety["preview_only"] is True
    assert safety["evidence_only"] is True
    assert safety["command_execution"] is False
    assert safety["filesystem_writes"] is False
    assert safety["reports_written"] is False
    assert safety["network_access"] is False


def test_empty_evidence_produces_safe_reportable_dashboard_state() -> None:
    module = load_module()

    result = module.build_cycle_ledger_dashboard({})

    assert result["schema"] == "AIOS_CYCLE_LEDGER_DASHBOARD_SOS.v1"
    dashboard = result["dashboard_contract"]
    assert dashboard["current_mission"] == "AIOS self-building control-plane cycle memory"
    assert dashboard["current_cycle"] == "NO_CYCLE_EVIDENCE"
    assert dashboard["current_packet"] == ""
    assert dashboard["progress_status"] == "no_work"
    assert dashboard["sos_required"] is False
    assert "No SOS required" in dashboard["sos_reason"]
    assert_preview_only(result)


def test_successful_cycle_produces_sos_required_false() -> None:
    module = load_module()

    result = module.build_cycle_ledger_dashboard(base_cycle())

    assert result["cycle_ledger"]["sos_required"] is False
    assert result["dashboard_contract"]["sos_required"] is False
    assert result["dashboard_contract"]["progress_status"] == "cycle_recorded"


def test_validation_failure_produces_sos_required_true() -> None:
    module = load_module()

    result = module.build_cycle_ledger_dashboard(
        base_cycle(validation_status="failed", validation_summary="pytest failed", tests_failed=1)
    )

    assert result["cycle_ledger"]["sos_required"] is True
    assert result["dashboard_contract"]["sos_required"] is True
    assert result["dashboard_contract"]["sos_reason"] == "validation failure requiring owner decision"


def test_approval_required_protected_gate_produces_sos_required_true() -> None:
    module = load_module()

    result = module.build_cycle_ledger_dashboard(
        base_cycle(approval_required={"git_push": True}, protected_gate_blocked=True)
    )

    assert result["cycle_ledger"]["sos_required"] is True
    assert result["cycle_ledger"]["sos_reason"] == "blocked protected gate"


def test_broker_or_live_trading_boundary_produces_sos_required_true() -> None:
    module = load_module()

    broker = module.build_cycle_ledger_dashboard(base_cycle(safety={"broker": True}))
    live = module.build_cycle_ledger_dashboard(base_cycle(live_trading_boundary=True))

    assert broker["dashboard_contract"]["sos_required"] is True
    assert broker["dashboard_contract"]["sos_reason"] == "broker boundary"
    assert live["dashboard_contract"]["sos_required"] is True
    assert live["dashboard_contract"]["sos_reason"] == "live-trading boundary"


def test_secrets_or_credentials_boundary_produces_sos_required_true() -> None:
    module = load_module()

    secrets = module.build_cycle_ledger_dashboard(base_cycle(secrets_boundary=True))
    credentials = module.build_cycle_ledger_dashboard(base_cycle(safety={"credentials": True}))

    assert secrets["cycle_ledger"]["sos_required"] is True
    assert secrets["cycle_ledger"]["sos_reason"] == "secrets boundary"
    assert credentials["cycle_ledger"]["sos_required"] is True
    assert credentials["cycle_ledger"]["sos_reason"] == "credentials boundary"


def test_normal_stop_report_remains_sos_required_false() -> None:
    module = load_module()

    result = module.build_cycle_ledger_dashboard(
        base_cycle(stop_condition="report_only", validation_status="pending_safe_validation")
    )

    assert result["dashboard_contract"]["progress_status"] == "report_only_stop"
    assert result["dashboard_contract"]["sos_required"] is False


def test_dashboard_contract_includes_current_packet_progress_blocker_sos_and_next_action() -> None:
    module = load_module()

    dashboard = module.build_cycle_ledger_dashboard(base_cycle())["dashboard_contract"]

    assert dashboard["current_packet"] == "PKT-AIOS-SAFE-NEXT"
    assert dashboard["progress_status"] == "cycle_recorded"
    assert dashboard["blocker_status"] == "none"
    assert dashboard["sos_required"] is False
    assert dashboard["sos_reason"]
    assert dashboard["next_safe_action"] == "Review dashboard contract and stop before staging."


def test_ledger_includes_forex_builder_alignment() -> None:
    module = load_module()

    ledger = module.build_cycle_ledger_dashboard(base_cycle())["cycle_ledger"]
    alignment = ledger["forex_builder_alignment"]

    assert alignment["proof_target"] == "industrial-grade forex bot builder"
    assert alignment["aligned"] is True
    assert "no broker/live/secrets" in alignment["milestone"]
    assert alignment["requires_future_gates_before_execution"] is True


def test_commands_executed_is_empty() -> None:
    module = load_module()

    assert module.build_cycle_ledger_dashboard(base_cycle())["commands_executed"] == []


def test_files_written_is_empty() -> None:
    module = load_module()

    assert module.build_cycle_ledger_dashboard(base_cycle())["files_written"] == []


def test_workers_dispatched_false() -> None:
    module = load_module()

    assert module.build_cycle_ledger_dashboard(base_cycle())["workers_dispatched"] is False


def test_queues_mutated_false() -> None:
    module = load_module()

    assert module.build_cycle_ledger_dashboard(base_cycle())["queues_mutated"] is False


def test_approvals_mutated_false() -> None:
    module = load_module()

    assert module.build_cycle_ledger_dashboard(base_cycle())["approvals_mutated"] is False


def test_safety_preview_only_true() -> None:
    module = load_module()

    assert module.build_cycle_ledger_dashboard(base_cycle())["safety"]["preview_only"] is True


def test_source_does_not_import_subprocess_network_or_file_write_tools() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in [
        "import subprocess",
        "from subprocess",
        "import requests",
        "import socket",
        "import urllib",
        "http.client",
        "open(",
        "write_text",
        "write_bytes",
        "with open",
        "os.system",
        "system(",
    ]:
        assert forbidden not in source
