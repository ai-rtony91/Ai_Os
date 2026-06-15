from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_github_pr_state.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_github_pr_state", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_github_pr_state_imports():
    module = load_module()
    assert module.SCHEMA == "AIOS_GITHUB_PR_STATE.v1"
    assert callable(module.build_github_pr_state)


def test_no_checks_reported_blocks_merge():
    module = load_module()
    state = module.build_github_pr_state("#42 branch: feature/test no checks reported")
    assert state["pr_number"] == 42
    assert state["branch"] == "feature/test"
    assert state["checks_attached"] is False
    assert state["merge_allowed"] is False
    assert state["merge_block_reason"] == "no_checks_reported"


def test_validate_pass_allows_merge_readiness_only():
    module = load_module()
    state = module.build_github_pr_state(
        {
            "number": 7,
            "headRefName": "autonomy-control-plane-substrate",
            "checks": [{"name": "validate", "conclusion": "SUCCESS", "status": "COMPLETED"}],
        }
    )
    assert state["checks_attached"] is True
    assert state["checks_passed"] == ["validate"]
    assert state["required_validate_present"] is True
    assert state["merge_allowed"] is True
    assert state["next_safe_action"].endswith("Anthony approval.")


def test_validate_fail_blocks_merge():
    module = load_module()
    state = module.build_github_pr_state("#8 branch: test validate failure")
    assert state["checks_failed"] == ["validate"]
    assert state["merge_allowed"] is False
    assert state["merge_block_reason"] == "validate_check_failed"


def test_required_validate_missing_blocks_merge():
    module = load_module()
    state = module.build_github_pr_state({"number": 9, "checks": [{"name": "lint", "conclusion": "SUCCESS"}]})
    assert state["merge_allowed"] is False
    assert state["merge_block_reason"] == "required_validate_missing"


def test_no_network_or_gh_execution_in_source():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["subprocess", "requests", "socket", "urllib", "http.client", ".run("]:
        assert forbidden not in source
