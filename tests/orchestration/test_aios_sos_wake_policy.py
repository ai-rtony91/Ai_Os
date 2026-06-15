from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_sos_wake_policy.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_sos_wake_policy", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_imports_and_normal_review_required_does_not_wake():
    module = load_module()
    result = module.evaluate_sos_wake_policy({"result": "REVIEW_REQUIRED"})
    assert result["schema"] == "AIOS_SOS_WAKE_POLICY.v1"
    assert result["sos_required"] is False
    assert result["wake_anthony"] is False


def test_sandbox_1312_is_blocker_not_sos():
    module = load_module()
    result = module.evaluate_sos_wake_policy({"stderr": "CreateProcessAsUserW failed: 1312"})
    assert result["sos_required"] is False
    assert result["wake_anthony"] is False
    assert result["reason_code"] == "sandbox_blocker"
    assert result["triggers"] == ["sandbox_1312_blocker"]


def test_protected_action_attempt_triggers_sos():
    module = load_module()
    result = module.evaluate_sos_wake_policy({"git_commit_attempted": True})
    assert result["sos_required"] is True
    assert result["wake_anthony"] is True
    assert "protected_action_attempt" in result["triggers"]


def test_live_broker_credential_or_real_order_triggers_sos():
    module = load_module()
    for key in ["live_execution", "broker_order", "credentials", "real_order", "webhook_url"]:
        result = module.evaluate_sos_wake_policy({key: True})
        assert result["sos_required"] is True
        assert result["wake_anthony"] is True


def test_repeated_validator_failures_trigger_sos():
    module = load_module()
    result = module.evaluate_sos_wake_policy({"repeated_validator_failures": 2})
    assert result["sos_required"] is True
    assert "repeated_validator_failures" in result["triggers"]


def test_blocked_approval_flags_do_not_trigger_sos():
    module = load_module()
    result = module.evaluate_sos_wake_policy({"protected_actions_blocked": {"git_commit": True}})
    assert result["sos_required"] is False
    assert result["wake_anthony"] is False
