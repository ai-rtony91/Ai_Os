from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_approved_packet_executor_contract.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_approved_packet_executor_contract", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def selected_packet(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "packet_id": "PKT-AIOS-APPROVED-SAFE",
        "title": "Run approved safe self-build packet",
        "lane": "approved-safe-self-build",
        "priority": "high",
        "milestone_value": "high",
        "risk_level": "low",
        "status": "selected",
        "required_files": [
            "automation/orchestration/runtime/Invoke-AiOsRuntimeSelfRoute.ps1",
            "tests/orchestration/test_aios_persistent_runtime_supervisor.py",
        ],
        "blocked_files": [],
        "required_approvals": [],
        "validators": ["python -m pytest -p no:cacheprovider tests/orchestration/test_safe.py -q"],
        "dependencies": [],
        "conflicts": [],
        "safety_flags": [],
    }
    payload.update(overrides)
    return payload


def approval(packet_id: str = "PKT-AIOS-APPROVED-SAFE", **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "approved": True,
        "packet_id": packet_id,
        "approval_source": "Anthony Meza Human Owner",
        "approval_status": "approved",
        "human_owner": True,
    }
    payload.update(overrides)
    return payload


def build_result(**overrides: object) -> dict[str, object]:
    module = load_module()
    payload: dict[str, object] = {
        "selected_packet": selected_packet(),
        "approval_evidence": approval(),
    }
    payload.update(overrides)
    return module.build_approved_packet_executor_contract(payload)


def assert_preview_only(result: dict[str, object]) -> None:
    assert result["commands_executed"] == []
    assert result["workers_dispatched"] is False
    assert result["queues_mutated"] is False
    assert result["approvals_mutated"] is False
    assert result["files_written"] == []
    safety = result["safety"]
    assert isinstance(safety, dict)
    assert safety["preview_only"] is True
    assert safety["evidence_only"] is True
    assert safety["execution_contract_only"] is True
    assert safety["command_execution"] is False
    assert safety["codex_launch"] is False
    assert safety["filesystem_writes"] is False
    assert safety["reports_written"] is False
    assert safety["network_access"] is False


def test_no_selected_packet_returns_no_packet() -> None:
    module = load_module()

    result = module.build_approved_packet_executor_contract({})

    assert result["schema"] == "AIOS_APPROVED_PACKET_EXECUTOR_CONTRACT.v1"
    assert result["executor_status"] == "no_packet"
    assert result["selected_packet"] is None
    assert result["execution_allowed"] is False
    assert result["command_preview_allowed"] is False
    assert result["codex_launch_allowed"] is False
    assert_preview_only(result)


def test_selected_packet_without_approval_is_blocked() -> None:
    module = load_module()

    result = module.build_approved_packet_executor_contract({"selected_packet": selected_packet()})

    assert result["executor_status"] == "blocked"
    assert result["approval_status"] == "missing"
    assert result["execution_allowed"] is False
    assert "human_owner_approval_missing" in result["blocked_reasons"]


def test_matching_approval_allows_bounded_local_apply_preview_execution_contract() -> None:
    result = build_result()

    assert result["executor_status"] == "allowed"
    assert result["approval_required"] is True
    assert result["approval_status"] == "approved"
    assert result["approval_source"] == "Anthony Meza Human Owner"
    assert result["execution_allowed"] is True
    assert result["command_preview_allowed"] is True
    assert result["codex_launch_allowed"] is True
    assert result["allowed_execution_mode"] == "bounded_local_apply_preview"
    assert result["selected_packet"]["packet_id"] == "PKT-AIOS-APPROVED-SAFE"
    assert_preview_only(result)


def test_approval_for_wrong_packet_id_is_blocked() -> None:
    result = build_result(approval_evidence=approval("PKT-AIOS-WRONG"))

    assert result["executor_status"] == "blocked"
    assert result["approval_status"] == "packet_mismatch"
    assert result["execution_allowed"] is False
    assert "human_owner_approval_packet_mismatch" in result["blocked_reasons"]


def test_missing_validators_is_blocked() -> None:
    result = build_result(selected_packet=selected_packet(validators=[]))

    assert result["executor_status"] == "blocked"
    assert result["required_validators"] == []
    assert result["execution_allowed"] is False
    assert "validators_missing" in result["blocked_reasons"]


def test_unsafe_write_scope_is_blocked() -> None:
    result = build_result(
        selected_packet=selected_packet(required_files=["../outside_scope.py"])
    )

    assert result["executor_status"] == "blocked"
    assert result["execution_allowed"] is False
    assert any("unsafe_write_scope:path_traversal" in reason for reason in result["blocked_reasons"])


def test_broker_or_live_trading_path_is_rejected() -> None:
    broker = build_result(selected_packet=selected_packet(required_files=["broker/live_adapter.py"]))
    live = build_result(selected_packet=selected_packet(required_files=["apps/trading/live/execution.py"]))

    assert broker["executor_status"] == "rejected"
    assert live["executor_status"] == "rejected"
    assert any("unsafe_boundary_path" in reason for reason in broker["rejected_reasons"])
    assert any("unsafe_boundary_path" in reason for reason in live["rejected_reasons"])


def test_secrets_or_credential_path_is_rejected() -> None:
    secrets = build_result(selected_packet=selected_packet(required_files=["services/secret_loader.py"]))
    credentials = build_result(selected_packet=selected_packet(required_files=["apps/credentials/store.py"]))

    assert secrets["executor_status"] == "rejected"
    assert credentials["executor_status"] == "rejected"
    assert any("secret" in reason for reason in secrets["rejected_reasons"])
    assert any("credentials" in reason for reason in credentials["rejected_reasons"])


def test_order_or_webhook_path_is_rejected() -> None:
    order = build_result(selected_packet=selected_packet(required_files=["apps/trading/orders/router.py"]))
    webhook = build_result(selected_packet=selected_packet(required_files=["services/webhook_receiver.py"]))

    assert order["executor_status"] == "rejected"
    assert webhook["executor_status"] == "rejected"
    assert any("orders" in reason for reason in order["rejected_reasons"])
    assert any("webhook" in reason for reason in webhook["rejected_reasons"])


def test_scheduler_or_daemon_request_is_blocked_unless_separately_approved() -> None:
    scheduler = build_result(selected_packet=selected_packet(requested_actions=["start scheduler"]))
    daemon = build_result(selected_packet=selected_packet(requested_actions=["start daemon"]))
    approved = build_result(
        selected_packet=selected_packet(requested_actions=["start scheduler"]),
        separate_approvals={"scheduler": True},
    )

    assert scheduler["executor_status"] == "blocked"
    assert daemon["executor_status"] == "blocked"
    assert scheduler["protected_action_required"] is True
    assert daemon["protected_action_required"] is True
    assert any("scheduler" in reason for reason in scheduler["blocked_reasons"])
    assert any("daemon" in reason for reason in daemon["blocked_reasons"])
    assert approved["executor_status"] == "allowed"


def test_commit_push_merge_remain_blocked_unless_separately_approved() -> None:
    commit = build_result(selected_packet=selected_packet(requested_actions=["git commit"]))
    push = build_result(selected_packet=selected_packet(requested_actions=["git push"]))
    merge = build_result(selected_packet=selected_packet(requested_actions=["git merge"]))
    approved = build_result(
        selected_packet=selected_packet(requested_actions=["git commit"]),
        separate_approvals={"git_commit": True},
    )

    assert commit["executor_status"] == "blocked"
    assert push["executor_status"] == "blocked"
    assert merge["executor_status"] == "blocked"
    assert commit["protected_action_required"] is True
    assert push["protected_action_required"] is True
    assert merge["protected_action_required"] is True
    assert approved["executor_status"] == "allowed"


def test_execution_allowed_false_unless_explicit_approval_evidence_matches() -> None:
    no_approval = build_result(approval_evidence={})
    not_owner = build_result(approval_evidence=approval(approval_source="Night Supervisor", human_owner=False))
    not_approved = build_result(approval_evidence=approval(approved=False, approval_status="pending"))
    matched = build_result()

    assert no_approval["execution_allowed"] is False
    assert not_owner["execution_allowed"] is False
    assert not_approved["execution_allowed"] is False
    assert matched["execution_allowed"] is True


def test_commands_executed_is_empty() -> None:
    assert build_result()["commands_executed"] == []


def test_workers_dispatched_false() -> None:
    assert build_result()["workers_dispatched"] is False


def test_queues_mutated_false() -> None:
    assert build_result()["queues_mutated"] is False


def test_approvals_mutated_false() -> None:
    assert build_result()["approvals_mutated"] is False


def test_files_written_is_empty() -> None:
    assert build_result()["files_written"] == []


def test_safety_preview_only_true() -> None:
    assert build_result()["safety"]["preview_only"] is True


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
        "start-process",
    ]:
        assert forbidden not in source
