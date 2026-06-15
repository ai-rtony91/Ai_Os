from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_bounded_worker_routing_preview.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_bounded_worker_routing_preview", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def recommendation(command: str | None = None, **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "mode": "READ_ONLY",
        "recommended_command": command
        or "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/campaign_registry/Get-AiOsCampaignNoReadyStageDiscovery.DRY_RUN.ps1 -OutputJson",
        "reason": "Campaign registry reports NO_READY_STAGE; run read-only discovery.",
        "orchestration_result_contract": {
            "status": "READY",
            "worker_identity": "UNKNOWN",
            "approval_required": False,
            "next_safe_action": "Preview routing only.",
        },
    }
    payload.update(overrides)
    return payload


def assert_preview_only(preview: dict[str, object]) -> None:
    assert preview["workers_dispatched"] is False
    assert preview["queues_mutated"] is False
    assert preview["approvals_mutated"] is False
    assert preview["commands_executed"] == []
    assert preview["files_written"] == []
    safety = preview["safety"]
    assert isinstance(safety, dict)
    assert safety["preview_only"] is True
    for key, value in safety.items():
        if key in {"preview_only", "runtime_supervisor_consumable_status"}:
            assert value is True
        else:
            assert value is False


def test_safe_validated_recommendation_returns_route_ready() -> None:
    module = load_module()

    preview = module.build_bounded_worker_routing_preview(recommendation(), {"status": "PASS"})

    assert preview["schema"] == "AIOS_BOUNDED_WORKER_ROUTING_PREVIEW.v1"
    assert preview["routing_status"] == "route_ready"
    assert preview["validated_command"]["validated"] is True
    assert preview["proposed_worker_identity"] == "route_dispatch"
    assert preview["proposed_lane"] == "bounded-routing-preview"
    assert preview["required_approvals"]["worker_dispatch"] is True
    assert_preview_only(preview)


def test_missing_recommendation_returns_no_route() -> None:
    module = load_module()

    preview = module.build_bounded_worker_routing_preview(None)

    assert preview["routing_status"] == "no_route"
    assert preview["proposed_worker_identity"] is None
    assert preview["validated_command"]["validated"] is False
    assert "missing_recommendation" in preview["blocked_actions"]
    assert_preview_only(preview)


def test_no_action_recommendation_returns_no_route() -> None:
    module = load_module()

    preview = module.build_bounded_worker_routing_preview(
        recommendation("No command recommended. Review campaign registry statuses."),
        {"status": "PASS"},
    )

    assert preview["routing_status"] == "no_route"
    assert preview["proposed_lane"] is None
    assert_preview_only(preview)


def test_unvalidated_command_returns_blocked() -> None:
    module = load_module()

    preview = module.build_bounded_worker_routing_preview(recommendation())

    assert preview["routing_status"] == "blocked"
    assert preview["validated_command"]["validation_status"] == "NOT_RUN"
    assert "recommended_command_not_validated" in preview["blocked_actions"]
    assert_preview_only(preview)


def test_failed_validation_returns_rejected() -> None:
    module = load_module()

    preview = module.build_bounded_worker_routing_preview(recommendation(), {"status": "BLOCKED"})

    assert preview["routing_status"] == "rejected"
    assert "recommended_command_failed_validation" in preview["blocked_actions"]
    assert_preview_only(preview)


def test_protected_action_returns_blocked() -> None:
    module = load_module()

    preview = module.build_bounded_worker_routing_preview(
        recommendation("git push origin main"),
        {"status": "PASS"},
    )

    assert preview["routing_status"] == "blocked"
    assert any(str(action).startswith("protected_command_term:") for action in preview["blocked_actions"])
    assert_preview_only(preview)


def test_contract_approval_required_returns_blocked() -> None:
    module = load_module()
    payload = recommendation()
    payload["orchestration_result_contract"] = {
        "status": "READY",
        "worker_identity": "UNKNOWN",
        "approval_required": True,
    }

    preview = module.build_bounded_worker_routing_preview(payload, {"status": "PASS"})

    assert preview["routing_status"] == "blocked"
    assert "recommendation_requires_approval" in preview["blocked_actions"]
    assert_preview_only(preview)


def test_preview_contains_required_contract_fields() -> None:
    module = load_module()

    preview = module.build_bounded_worker_routing_preview(recommendation(), {"status": "PASS"})

    assert set(preview) >= {
        "schema",
        "routing_status",
        "source_recommendation",
        "validated_command",
        "proposed_worker_identity",
        "proposed_lane",
        "proposed_task_summary",
        "proposed_write_scope",
        "required_approvals",
        "blocked_actions",
        "commands_executed",
        "queues_mutated",
        "approvals_mutated",
        "workers_dispatched",
        "files_written",
        "safety",
        "next_safe_action",
    }


def test_runtime_supervisor_can_consume_blocker_status_if_connected() -> None:
    module = load_module()
    runtime_self_route_report = {
        "schema": "AIOS_RUNTIME_SELF_ROUTE_REPORT.v1",
        "route_status": "rejected",
        "recommended_command": "git add unsafe",
        "command_validation_status": "PASS",
        "command_execution_allowed": False,
        "command_executed": False,
        "safety": {
            "queue_mutation": False,
            "approval_mutation": False,
            "live_worker_dispatch": False,
        },
    }

    preview = module.build_bounded_worker_routing_preview(runtime_self_route_report)

    assert preview["routing_status"] == "blocked"
    assert preview["runtime_supervisor_blocker"]
    assert preview["safety"]["runtime_supervisor_consumable_status"] is True
    assert_preview_only(preview)


def test_preview_source_does_not_import_execution_or_file_write_tools() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in [
        "subprocess",
        "requests",
        "socket",
        "urllib",
        "http.client",
        "open(",
        "write_text",
        "write_bytes",
        "with open",
        "os.",
        "pathlib",
    ]:
        assert forbidden not in source
