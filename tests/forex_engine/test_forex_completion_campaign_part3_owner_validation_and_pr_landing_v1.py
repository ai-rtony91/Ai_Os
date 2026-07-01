from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_completion_campaign_part3_owner_validation_and_pr_landing_v1 import (  # noqa: E402
    BLOCKED_BY_MISSING_PART1_FILES,
    BLOCKED_BY_MISSING_PART2_FILES,
    BLOCKED_BY_SAFETY_BOUNDARY,
    BLOCKED_BY_SENSITIVE_DATA,
    BLOCKED_BY_UNRELATED_DIRTY_FILES,
    BLOCKED_BY_VALIDATION_FAILURE,
    HARD_FALSE_FIELDS,
    INCOMPLETE_INPUTS,
    NEXT_PACKET_PART4,
    PART1_FILES,
    PART2_FILES,
    PART3_FILES,
    PART3_OWNER_VALIDATION_READY,
    PART3_READY_FOR_COMMIT_APPROVAL,
    PART3_READY_FOR_PR_LANDING_APPROVAL,
    SAFETY_FALSE_FIELDS,
    SCHEMA,
    evaluate_forex_completion_campaign_part3_owner_validation_and_pr_landing_v1,
)
from scripts.forex_delivery.run_forex_completion_campaign_part3_owner_validation_v1 import (  # noqa: E402
    main as runner_main,
)


MODULE_PATH = (
    ROOT
    / "automation"
    / "forex_engine"
    / "forex_completion_campaign_part3_owner_validation_and_pr_landing_v1.py"
)
SCRIPT_PATH = (
    ROOT
    / "scripts"
    / "forex_delivery"
    / "run_forex_completion_campaign_part3_owner_validation_v1.py"
)


def _manifest(paths: tuple[str, ...], value: bool = True) -> dict[str, bool]:
    return {path: value for path in paths}


def _validation(value: str = "PASS") -> dict[str, str]:
    return {
        "part3_module_py_compile": value,
        "part3_runner_py_compile": value,
        "part3_focused_tests": value,
        "part1_focused_tests": value,
        "part2_focused_tests": value,
        "part2_runner": value,
        "part3_runner": value,
        "existing_regressions": value,
        "forbidden_marker_scan": value,
        "diff_whitespace_validation": value,
    }


def _payload() -> dict:
    return {
        "part1_files": _manifest(PART1_FILES),
        "part2_files": _manifest(PART2_FILES),
        "part3_files": _manifest(PART3_FILES),
        "validation_results": _validation(),
        "dirty_state": {
            "branch": "main",
            "same_mission_untracked_only": True,
            "unrelated_dirty_files_present": False,
            "staged_files_present": False,
        },
        "safety_boundary": {field: False for field in HARD_FALSE_FIELDS},
        "owner_validation": {
            "owner_review_required": True,
            "commit_approval_required": True,
            "push_approval_required": True,
            "pr_approval_required": True,
            "merge_approval_required": True,
            "owner_has_not_approved_commit_yet": True,
        },
    }


def _run(payload: dict | None = None) -> dict:
    return (
        evaluate_forex_completion_campaign_part3_owner_validation_and_pr_landing_v1(
            payload
        )
    )


def test_empty_payload_incomplete() -> None:
    result = _run({})
    assert result["schema"] == SCHEMA
    assert result["landing_status"] == INCOMPLETE_INPUTS
    assert result["landing_ready"] is False


def test_sensitive_data_blocked_and_value_not_echoed() -> None:
    payload = _payload()
    payload["nested"] = {"password": "DO-NOT-ECHO"}
    result = _run(payload)
    assert result["landing_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert result["sensitive_data_detected"] is True
    assert "DO-NOT-ECHO" not in repr(result)


def test_validation_result_secret_like_value_blocked_without_echo() -> None:
    payload = _payload()
    payload["validation_results"]["validator"] = "bearer SECRET"
    result = _run(payload)
    assert result["landing_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert result["sensitive_data_detected"] is True
    assert "SECRET" not in repr(result)


def test_unknown_not_run_validation_status_is_not_sensitive() -> None:
    payload = _payload()
    payload["validation_results"]["validator"] = "UNKNOWN_NOT_RUN_BY_SCRIPT"
    result = _run(payload)
    assert result["landing_status"] == PART3_OWNER_VALIDATION_READY
    assert result["sensitive_data_detected"] is False
    assert (
        result["validation_summary"]["results"]["validator"]
        == "UNKNOWN_NOT_RUN_BY_SCRIPT"
    )


def test_missing_part1_file_blocks() -> None:
    payload = _payload()
    payload["part1_files"][PART1_FILES[0]] = False
    result = _run(payload)
    assert result["landing_status"] == BLOCKED_BY_MISSING_PART1_FILES
    assert PART1_FILES[0] in result["part1_file_manifest"]["missing_paths"]


def test_missing_part2_file_blocks() -> None:
    payload = _payload()
    payload["part2_files"][PART2_FILES[0]] = False
    result = _run(payload)
    assert result["landing_status"] == BLOCKED_BY_MISSING_PART2_FILES
    assert PART2_FILES[0] in result["part2_file_manifest"]["missing_paths"]


def test_missing_part3_file_incomplete() -> None:
    payload = _payload()
    payload["part3_files"][PART3_FILES[0]] = False
    result = _run(payload)
    assert result["landing_status"] == INCOMPLETE_INPUTS
    assert PART3_FILES[0] in result["part3_file_manifest"]["missing_paths"]


def test_validation_failure_blocks() -> None:
    payload = _payload()
    payload["validation_results"]["part3_focused_tests"] = "FAIL"
    result = _run(payload)
    assert result["landing_status"] == BLOCKED_BY_VALIDATION_FAILURE
    assert "part3_focused_tests" in result["validation_summary"]["failed_validators"]


def test_unrelated_dirty_files_block() -> None:
    payload = _payload()
    payload["dirty_state"]["unrelated_dirty_files_present"] = True
    assert _run(payload)["landing_status"] == BLOCKED_BY_UNRELATED_DIRTY_FILES


def test_staged_files_block() -> None:
    payload = _payload()
    payload["dirty_state"]["staged_files_present"] = True
    assert _run(payload)["landing_status"] == BLOCKED_BY_UNRELATED_DIRTY_FILES


def test_safety_hard_false_true_blocks() -> None:
    payload = _payload()
    payload["safety_boundary"]["broker_api_called"] = True
    result = _run(payload)
    assert result["landing_status"] == BLOCKED_BY_SAFETY_BOUNDARY
    assert "broker_api_called_true" in result["landing_blockers"]


def test_all_files_present_and_validators_pass_routes_to_commit_approval() -> None:
    result = _run(_payload())
    assert result["landing_status"] == PART3_READY_FOR_COMMIT_APPROVAL
    assert result["landing_ready"] is True
    assert result["next_best_packet"] == NEXT_PACKET_PART4


def test_owner_commit_approval_recorded_routes_to_pr_landing_approval() -> None:
    payload = _payload()
    payload["owner_validation"].pop("owner_has_not_approved_commit_yet")
    payload["owner_validation"]["owner_commit_approval_recorded"] = True
    payload["owner_validation"]["push_approval_recorded"] = False
    payload["owner_validation"]["pr_approval_recorded"] = False
    result = _run(payload)
    assert result["landing_status"] == PART3_READY_FOR_PR_LANDING_APPROVAL
    assert result["landing_ready"] is True


def test_landing_command_preview_is_text_only() -> None:
    result = _run(_payload())
    preview = result["landing_command_preview"]
    commands = preview["commands"]
    assert preview["text_only"] is True
    assert preview["inert_preview_only"] is True
    assert all(command != "git push -u origin main" for command in commands)
    assert (
        "git switch -c feature/forex-completion-campaign-owner-validation-v1"
        in commands
    )
    assert any(command.startswith("git add ") for command in commands)
    assert (
        'git commit -m "feat: add forex completion campaign owner validation"'
        in commands
    )
    assert (
        "git push -u origin feature/forex-completion-campaign-owner-validation-v1"
        in commands
    )
    assert any(
        command.startswith(
            "gh pr create --base main --head "
            "feature/forex-completion-campaign-owner-validation-v1"
        )
        for command in commands
    )


def test_blocked_commands_show_no_protected_action_occurred() -> None:
    blocked = _run(_payload())["blocked_commands"]
    for phrase in (
        "not executed by this packet",
        "requires Anthony approval",
        "no staging occurred",
        "no commit occurred",
        "no push occurred",
        "no PR occurred",
        "no merge occurred",
    ):
        assert phrase in blocked


def test_all_hard_false_and_safety_false_fields_remain_false() -> None:
    result = _run(_payload())
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False
    for field in SAFETY_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False


def test_next_best_packet_routes_correctly() -> None:
    ready = _run(_payload())
    assert ready["next_best_packet"] == NEXT_PACKET_PART4

    owner_ready_payload = _payload()
    owner_ready_payload["validation_results"]["part3_runner"] = "UNKNOWN_NOT_RUN_BY_SCRIPT"
    owner_ready = _run(owner_ready_payload)
    assert owner_ready["landing_status"] == PART3_OWNER_VALIDATION_READY
    assert owner_ready["next_best_packet"] == NEXT_PACKET_PART4

    blocked_payload = _payload()
    blocked_payload["part1_files"][PART1_FILES[0]] = False
    blocked = _run(blocked_payload)
    assert blocked["next_best_packet"] == SCHEMA


def test_runner_script_emits_deterministic_json() -> None:
    first = io.StringIO()
    second = io.StringIO()
    with redirect_stdout(first):
        assert runner_main() == 0
    with redirect_stdout(second):
        assert runner_main() == 0
    left = json.loads(first.getvalue())
    right = json.loads(second.getvalue())
    assert left == right
    assert left["schema"] == SCHEMA
    assert left["landing_status"]


def test_production_source_has_no_forbidden_runtime_markers() -> None:
    forbidden = (
        "re" + "quests",
        "so" + "cket",
        "ur" + "llib",
        "sub" + "process",
        "os." + "environ",
        "broker" + "_sdk",
        "schedule" + ".every",
        "start" + "-process",
    )
    for path in (MODULE_PATH, SCRIPT_PATH):
        source = path.read_text(encoding="utf-8").lower()
        hits = [marker for marker in forbidden if marker in source]
        assert not hits, {str(path): hits}
