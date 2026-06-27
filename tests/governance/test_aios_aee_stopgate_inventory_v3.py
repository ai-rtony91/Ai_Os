from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from automation.governance.aios_aee_stopgate_inventory_v3 import (
    build_stopgate_inventory,
    result_to_jsonable_dict,
    result_to_markdown,
    result_to_operator_text,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "governance" / "aee_stopgate_inventory_v3"
VALIDATOR_REPORT = "Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_REPORT.md"
VALIDATOR_CHECKPOINT = "Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_CHECKPOINT.md"

EXPECTED_FIXTURES = {
    "approved_carryover_continuation.md": "APPROVED_CARRYOVER_CONTINUATION",
    "clean_main_wrong_packet.md": "WRONG_PACKET_FOR_CLEAN_MAIN",
    "wrong_branch_unrelated_dirty_stop.md": "HARD_STOP",
    "dirty_allowed_paths_continue.md": "RECOVERABLE_LOCAL",
    "dirty_forbidden_path_stop.md": "HARD_STOP",
    "staged_files_stop.md": "HARD_STOP",
    "python_1312_readonly_continue.md": "SANDBOX_LIMITATION",
    "python_1312_strict_cli_deferred.md": "DEFERRED_OWNER_VALIDATION",
    "python_1312_all_remaining_work_blocked.md": "WAITING_FOR_OWNER_POWERSHELL",
    "broad_scan_1312_continue.md": "MINOR_SCAN_BLOCKED_RECURABLE",
    "targeted_tests_pass_strict_cli_block_continue.md": "DEFERRED_OWNER_VALIDATION",
    "targeted_tests_fail_repair_continue.md": "RECOVERABLE_LOCAL",
    "targeted_tests_fail_forbidden_path_stop.md": "HARD_STOP",
    "report_exists_hardening_remains_continue.md": "RECOVERABLE_LOCAL",
    "checkpoint_exists_report_pending_continue.md": "RECOVERABLE_LOCAL",
    "checkpoint_report_mismatch_repair.md": "RECOVERABLE_LOCAL",
    "protected_action_ready_local_work_remains_continue.md": "RECOVERABLE_LOCAL",
    "protected_action_ready_local_work_complete_handoff.md": "OWNER_HANDOFF_READY",
    "merge_after_checkwatch_stop.md": "HARD_STOP",
    "broad_git_add_stop.md": "HARD_STOP",
    "line_ending_warning_continue.md": "FALSE_POSITIVE_REPAIR",
    "placeholder_minor_repair.md": "FALSE_POSITIVE_REPAIR",
    "missing_section_minor_repair.md": "FALSE_POSITIVE_REPAIR",
    "missing_safety_boundary_repair.md": "FALSE_POSITIVE_REPAIR",
    "ci_secret_scan_risk_stop.md": "HARD_STOP",
    "credential_exposure_stop.md": "HARD_STOP",
    "broker_api_boundary_stop.md": "HARD_STOP",
    "trading_execution_boundary_stop.md": "HARD_STOP",
    "money_movement_boundary_stop.md": "HARD_STOP",
    "accidental_explain_codebase_prompt_ignore.md": "PROMPT_INTERRUPTION_IGNORE",
}


def _fixture_status(name: str) -> str:
    content = (FIXTURE_DIR / name).read_text(encoding="utf-8")
    for line in content.splitlines():
        if line.startswith("status:"):
            return line.split(":", 1)[1].strip()
    raise AssertionError(f"status missing in {name}")


def _build_result(**kwargs):
    return build_stopgate_inventory(REPO_ROOT, **kwargs)


def _cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/governance/run_aios_aee_stopgate_inventory_v3.py", *args],
        cwd=str(REPO_ROOT),
        check=False,
        capture_output=True,
        text=True,
    )


def test_fixture_library_exists() -> None:
    for fixture_name, expected in EXPECTED_FIXTURES.items():
        path = FIXTURE_DIR / fixture_name
        assert path.exists()
        assert _fixture_status(fixture_name) == expected


def test_approved_dirty_carryover_continues() -> None:
    result = _build_result(
        branch="lane/aios-aee-governance-validator-v1",
        dirty_files=["automation/governance/aios_aee_governance_validator_v1.py", VALIDATOR_REPORT],
    )
    assert result.continuation_status == "APPROVED_CARRYOVER_CONTINUATION"


def test_clean_main_wrong_packet_classification() -> None:
    result = _build_result(branch="main", dirty_files=["automation/governance/aios_aee_governance_validator_v1.py"])
    assert result.continuation_status == "WRONG_PACKET_FOR_CLEAN_MAIN"


def test_wrong_unrelated_branch_hard_stop() -> None:
    result = _build_result(branch="feature/other", dirty_files=["docs/other.md"])
    assert result.continuation_status == "HARD_STOP"


def test_staged_files_hard_stop() -> None:
    result = _build_result(
        branch="lane/aios-aee-governance-validator-v1",
        dirty_files=["tests/governance/test_aios_aee_governance_validator_v1.py"],
        staged_files=["tests/governance/test_aios_aee_governance_validator_v1.py"],
    )
    assert result.continuation_status == "HARD_STOP"


def test_forbidden_path_dirty_hard_stop() -> None:
    result = _build_result(branch="lane/aios-aee-governance-validator-v1", dirty_files=["secrets/config.json"])
    assert result.continuation_status == "HARD_STOP"
    assert result.forbidden_paths_seen


def test_dirty_allowed_paths_continue() -> None:
    result = _build_result(branch="lane/aios-aee-governance-validator-v1", dirty_files=["tests/governance/test_aios_aee_governance_validator_v1.py"])
    assert result.continuation_status == "RECOVERABLE_LOCAL"


def test_1312_readonly_scan_continues() -> None:
    result = _build_result(branch="lane/aios-aee-governance-validator-v1", dirty_files=["automation/governance/aios_aee_governance_validator_v1.py"], simulate_1312=True)
    assert result.continuation_status in {"SANDBOX_LIMITATION", "RECOVERABLE_LOCAL"}

    assert result.events_1312 == [{"event": "CreateProcessAsUserW failed: 1312"}]


def test_1312_strict_cli_deferred() -> None:
    result = _build_result(
        branch="lane/aios-aee-governance-validator-v1",
        dirty_files=["automation/governance/aios_aee_governance_validator_v1.py"],
        simulate_1312=True,
        simulate_targeted_tests_passed=True,
    )
    assert result.continuation_status == "DEFERRED_OWNER_VALIDATION"


def test_1312_all_remaining_work_blocked_waiting() -> None:
    result = _build_result(
        branch="lane/aios-aee-governance-validator-v1",
        dirty_files=["automation/governance/aios_aee_governance_validator_v1.py"],
        simulate_1312=True,
        all_remaining_work_blocked=True,
    )
    assert result.continuation_status == "WAITING_FOR_OWNER_POWERSHELL"


def test_broad_scan_failure_recoverable() -> None:
    result = _build_result(
        branch="lane/aios-aee-governance-validator-v1",
        dirty_files=["automation/governance/aios_aee_governance_validator_v1.py"],
        broad_scan_blocked=True,
    )
    assert result.continuation_status == "MINOR_SCAN_BLOCKED_RECURABLE"


def test_report_exists_hardening_remains_continues(tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    checkpoint = tmp_path / "checkpoint.md"
    report.write_text("pending_work: [fixtures]", encoding="utf-8")
    checkpoint.write_text("pending_work: [scan]", encoding="utf-8")
    result = _build_result(
        branch="lane/aios-aee-governance-validator-v1",
        dirty_files=[],
        local_work_complete_hint=False,
        has_hardening_pending=True,
        validator_report_path=str(report),
        validator_checkpoint_path=str(checkpoint),
    )
    assert result.continuation_status == "RECOVERABLE_LOCAL"


def test_checkpoint_exists_report_pending_continues(tmp_path: Path) -> None:
    checkpoint = tmp_path / "checkpoint.md"
    report = tmp_path / "report.md"
    checkpoint.write_text("current_phase: checkpoint", encoding="utf-8")
    report.write_text("current_phase: report", encoding="utf-8")
    result = _build_result(
        branch="lane/aios-aee-governance-validator-v1",
        dirty_files=[],
        local_work_complete_hint=False,
        validator_report_path=str(report),
        validator_checkpoint_path=str(checkpoint),
    )
    assert result.continuation_status in {"RECOVERABLE_LOCAL", "OWNER_HANDOFF_READY"}


def test_checkpoint_report_mismatch_repair() -> None:
    result = _build_result(
        branch="lane/aios-aee-governance-validator-v1",
        dirty_files=[],
        has_hardening_pending=False,
        local_work_complete_hint=False,
        validator_report_path="nonexistent/report.md",
        validator_checkpoint_path="nonexistent/checkpoint.md",
    )
    assert result.continuation_status == "RECOVERABLE_LOCAL" or result.continuation_status == "EVIDENCE_GAP"


def test_protected_action_ready_local_work_remains() -> None:
    result = _build_result(
        branch="lane/aios-aee-governance-validator-v1",
        dirty_files=["automation/governance/aios_aee_governance_validator_v1.py"],
        protected_ready=True,
        local_work_complete_hint=False,
    )
    assert result.continuation_status == "RECOVERABLE_LOCAL"


def test_protected_action_ready_local_work_complete() -> None:
    result = _build_result(
        branch="lane/aios-aee-governance-validator-v1",
        dirty_files=[],
        protected_ready=True,
        local_work_complete_hint=True,
    )
    assert result.continuation_status == "OWNER_HANDOFF_READY"


def test_prompt_interruption_ignored() -> None:
    result = _build_result(
        branch="lane/aios-aee-governance-validator-v1",
        dirty_files=["automation/governance/aios_aee_governance_validator_v1.py"],
        operator_prompt="Explain this codebase and list all Python files.",
    )
    assert result.continuation_status == "PROMPT_INTERRUPTION_IGNORE"


def test_json_output_serializes() -> None:
    result = _build_result(branch="lane/aios-aee-governance-validator-v1", dirty_files=[])
    json.dumps(result_to_jsonable_dict(result))


def test_markdown_output_contains_stopgate_matrix() -> None:
    result = _build_result(branch="lane/aios-aee-governance-validator-v1", dirty_files=[])
    markdown = result_to_markdown(result)
    assert "## Stopgate matrix" in markdown
    assert "| Code | Family |" in markdown


def test_operator_text_stable() -> None:
    result = _build_result(
        branch="lane/aios-aee-governance-validator-v1",
        dirty_files=["automation/governance/aios_aee_governance_validator_v1.py"],
    )
    text = result_to_operator_text(result)
    assert "continuation_status" in text
    assert "dirty_files_observed" in text


def test_cli_strict_zero_for_approved_carryover() -> None:
    completed = _cli(
        [
            "--strict",
            "--branch",
            "lane/aios-aee-governance-validator-v1",
            "--dirty-file",
            "automation/governance/aios_aee_governance_validator_v1.py",
            "--dirty-file",
            VALIDATOR_REPORT,
        ]
    )
    assert completed.returncode == 0


def test_cli_strict_zero_for_deferred_owner_validation() -> None:
    completed = _cli(
        [
            "--strict",
            "--branch",
            "lane/aios-aee-governance-validator-v1",
            "--dirty-file",
            "automation/governance/aios_aee_governance_validator_v1.py",
            "--simulate-1312",
            "--simulate-targeted-tests-passed",
        ]
    )
    assert completed.returncode == 0


def test_cli_strict_nonzero_for_hard_stop() -> None:
    completed = _cli(["--strict", "--branch", "feature/stop", "--dirty-file", "docs/other.md"])
    assert completed.returncode == 1


def test_no_subprocess_in_core_scanner() -> None:
    source = (REPO_ROOT / "automation" / "governance" / "aios_aee_stopgate_inventory_v3.py").read_text(
        encoding="utf-8",
    )
    assert "import subprocess" not in source
    assert "subprocess." not in source


def test_no_network_env_or_trading_behavior() -> None:
    source = (REPO_ROOT / "automation" / "governance" / "aios_aee_stopgate_inventory_v3.py").read_text(
        encoding="utf-8",
    )
    assert "os.environ" not in source
    assert "requests" not in source
    assert "socket" not in source
    assert not re.search(r"(?m)^\\s*(api_key|apikey|secret|token|password|broker)\\s*=", source)
