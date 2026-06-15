from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_resume_state.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_resume_state", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def wake_report(result: str = "DONE_FOR_CURRENT_GOAL", handoff_status: str = "ready") -> dict[str, object]:
    return {
        "schema": "AIOS_WAKE_CONTINUE.v1",
        "goal": "forex-paper-bot",
        "result": result,
        "selected_action": "validate_all_forex",
        "goal_decision": {
            "decision": "continue_build",
            "reason_code": "acceptable_report",
            "decision_reasons": ["acceptable_report"],
        },
        "next_build_plan": {
            "schema": "AIOS_NEXT_BUILD_PLAN.v1",
            "route": "build_next_paper_component",
            "next_component": "forex_risk_controls",
            "next_packet_id": "PKT-AIOS-FOREX-RISK-CONTROLS-CONTINUATION-APPLY",
        },
        "bounded_executor_handoff": {
            "schema": "AIOS_BOUNDED_EXECUTOR_HANDOFF.v1",
            "handoff_status": handoff_status,
            "allowed_action": "build_forex_risk_controls",
            "credentials": {"sample": "safe-placeholder"},
        },
        "validators_run": [
            {
                "name": "forex_tests",
                "command": "python -m pytest tests/trading_lab/test_forex_decision_policy.py",
                "returncode": 0,
                "passed": True,
                "stdout": "bulk stdout must be stripped",
                "stderr": "bulk stderr must be stripped",
            }
        ],
        "approval_required": {"commit": True, "push": True, "merge": True},
        "next_safe_action": "Prepare the bounded handoff for Anthony review.",
        "safety": {"queue_mutation": False},
    }


def test_resume_state_module_imports():
    module = load_module()
    assert module.SCHEMA == "AIOS_RESUME_STATE.v1"
    assert callable(module.build_resume_state)


def test_builds_valid_resume_state_from_wake_continue_fixture():
    module = load_module()
    resume = module.build_resume_state(wake_report())
    assert resume["schema"] == "AIOS_RESUME_STATE.v1"
    assert resume["goal"] == "forex-paper-bot"
    assert resume["last_decision"]["decision"] == "continue_build"
    assert resume["next_build_plan"]["next_component"] == "forex_risk_controls"
    assert resume["bounded_executor_handoff"]["allowed_action"] == "build_forex_risk_controls"


def test_strips_stdout_and_stderr_bulk_from_validators():
    module = load_module()
    resume = module.build_resume_state(wake_report())
    serialized = json.dumps(resume)
    assert "bulk stdout" not in serialized
    assert "bulk stderr" not in serialized
    assert resume["validators_summary"]["count"] == 1
    assert resume["validators_summary"]["passed_count"] == 1
    assert resume["validators_summary"]["failed_count"] == 0


def test_resume_ready_true_for_done_and_ready_handoff():
    module = load_module()
    resume = module.build_resume_state(wake_report())
    assert resume["resume_ready"] is True
    assert resume["resume_reason_code"] == "ready_for_resume"


def test_resume_ready_false_for_blocked_or_review_required():
    module = load_module()
    blocked = module.build_resume_state(wake_report(result="BLOCKED", handoff_status="blocked"))
    review = module.build_resume_state(wake_report(result="REVIEW_REQUIRED", handoff_status="stopped"))
    assert blocked["resume_ready"] is False
    assert blocked["resume_reason_code"] == "result_not_done_for_current_goal"
    assert review["resume_ready"] is False
    assert review["resume_reason_code"] == "result_not_done_for_current_goal"


def test_sensitive_payload_is_redacted():
    module = load_module()
    resume = module.build_resume_state(wake_report())
    assert resume["bounded_executor_handoff"]["credentials"] == "[redacted]"


def test_write_function_writes_timestamped_and_latest_files_under_resume_dir(tmp_path):
    module = load_module()
    resume = module.build_resume_state(wake_report())
    written = module.write_resume_state(
        tmp_path,
        resume,
        generated_at_utc=datetime(2026, 6, 14, 12, 30, 0, tzinfo=timezone.utc),
    )
    timestamped = tmp_path / written["resume_state_paths"]["timestamped"]
    latest = tmp_path / written["resume_state_paths"]["latest"]
    assert timestamped.exists()
    assert latest.exists()
    assert timestamped.name == "AIOS_RESUME_STATE_20260614_123000Z.json"
    assert latest.name == "AIOS_RESUME_STATE_latest.json"
    assert "Reports/aios_resume/" in written["resume_state_paths"]["timestamped"]


def test_write_function_rejects_path_traversal_or_outside_output(tmp_path):
    module = load_module()
    resume = module.build_resume_state(wake_report())
    for output_dir in [tmp_path / "outside", tmp_path / "Reports" / "aios_resume" / ".." / "other"]:
        try:
            module.write_resume_state(tmp_path, resume, output_dir=output_dir)
        except ValueError as exc:
            assert str(exc) == "resume_state_dir_outside_allowed_root"
        else:
            raise AssertionError("unsafe output dir was accepted")


def test_no_unsafe_flags_are_enabled():
    module = load_module()
    resume = module.build_resume_state(wake_report())
    assert all(value is False for value in resume["safety"].values())


def test_no_queue_approval_worker_scheduler_broker_or_live_paths_in_source():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in [
        "subprocess",
        "requests",
        "socket",
        "urllib",
        "http.client",
        "queue_mutation = true",
        "approval_mutation = true",
        "worker_dispatch = true",
        "scheduler = true",
        "daemon = true",
        "live_trading = true",
        "real_orders = true",
        "real_webhooks = true",
    ]:
        assert forbidden not in source
