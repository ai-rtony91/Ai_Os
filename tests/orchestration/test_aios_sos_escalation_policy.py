from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_sos_escalation_policy.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_sos_escalation_policy", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_imports():
    module = load_module()
    assert module.SCHEMA == "AIOS_SOS_ESCALATION_POLICY.v1"


def test_sos_triggers_for_hard_safety_flags():
    module = load_module()
    for key in [
        "broker",
        "live_trading",
        "credentials",
        "scheduler",
        "worker_dispatch",
        "queue_mutation",
        "destructive_action",
    ]:
        result = module.build_sos_escalation({"safety": {key: True}})
        assert result["sos_required"] is True
        assert result["triggers"]


def test_sos_triggers_for_tests_failed_after_repair():
    module = load_module()
    result = module.build_sos_escalation({"result": "failed", "repair_attempts": 1})
    assert result["sos_required"] is True
    assert "tests_failed_after_repair" in result["triggers"]


def test_sos_triggers_for_unsupported_mode_and_unbounded_path():
    module = load_module()
    result = module.build_sos_escalation(
        {"reason_code": "unsupported_mode", "blocked_reason": "unbounded_path"}
    )
    assert result["sos_required"] is True
    assert "unsupported_mode" in result["triggers"]
    assert "unbounded_path" in result["triggers"]


def test_sos_does_not_trigger_for_normal_review_required():
    module = load_module()
    result = module.build_sos_escalation({"result": "REVIEW_REQUIRED"})
    assert result["sos_required"] is False
    assert result["triggers"] == []


def test_sos_does_not_trigger_for_sandbox_1312_when_pytest_passed():
    module = load_module()
    result = module.build_sos_escalation(
        {
            "status": "SANDBOX_BLOCKED",
            "sandbox_blocked": True,
            "tests_passed_count": 12,
            "tests_failed_count": 0,
            "blockers": ["CreateProcessAsUserW failed: 1312"],
        }
    )
    assert result["sos_required"] is False


def test_source_has_no_command_or_external_call_imports():
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert "requests" not in source
