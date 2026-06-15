from __future__ import annotations

import importlib.util
from pathlib import Path

from automation.orchestration.aios_next_action_selector import select_next_action


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_self_build_work_queue.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_self_build_work_queue", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_imports_and_schemas():
    module = load_module()
    assert module.QUEUE_SCHEMA == "AIOS_SELF_BUILD_WORK_QUEUE.v1"
    assert module.ITEM_SCHEMA == "AIOS_SELF_BUILD_WORK_QUEUE_ITEM.v1"


def test_build_queue_item_defaults_are_safe():
    module = load_module()
    item = module.build_queue_item(
        action_id="build_platform_status_reader",
        allowed_paths=["automation/orchestration/platform_status_reader.py"],
        validators=["python -m pytest tests/orchestration/test_platform_status_reader.py"],
    )
    assert item["schema"] == "AIOS_SELF_BUILD_WORK_QUEUE_ITEM.v1"
    assert item["status"] == "ready"
    assert item["protected_action_flags"]["git_commit"] is False
    assert item["safety"]["commands_executed"] is False


def test_queue_sorts_by_priority():
    module = load_module()
    queue = module.build_self_build_work_queue(
        [
            {"priority": 20, "action_id": "second", "allowed_paths": ["b.py"]},
            {"priority": 10, "action_id": "first", "allowed_paths": ["a.py"]},
        ]
    )
    assert queue["schema"] == "AIOS_SELF_BUILD_WORK_QUEUE.v1"
    assert [item["action_id"] for item in queue["items"]] == ["first", "second"]
    assert queue["mutation_performed"] is False


def test_queue_generically_marks_items_completed_when_allowed_paths_exist(tmp_path):
    module = load_module()
    allowed_paths = ["automation/orchestration/example_reader.py", "tests/orchestration/test_example_reader.py"]
    for relative_path in allowed_paths:
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("present", encoding="utf-8")

    queue = module.build_self_build_work_queue(
        [{"priority": 10, "action_id": "build_example_reader", "allowed_paths": allowed_paths}],
        repo_root=tmp_path,
    )

    item = queue["items"][0]
    assert item["status"] == "completed"
    assert item["reason_code"] == "completed_allowed_paths_exist"


def test_path_traversal_is_rejected_from_allowed_paths():
    module = load_module()
    item = module.build_queue_item(action_id="unsafe", allowed_paths=["../outside.py", "safe/path.py"])
    assert item["allowed_paths"] == ["safe/path.py"]
    assert item["reason_code"] == "bounded_dry_run_item"


def test_self_build_core_queue_marks_status_reader_completed_when_files_exist(tmp_path):
    module = load_module()
    for relative_path in module.CORE_STATUS_READER_PATHS:
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("present", encoding="utf-8")

    queue = module.build_self_build_core_preview_queue(tmp_path)
    items_by_action = {item["action_id"]: item for item in queue["items"]}

    assert items_by_action["build_self_build_core_status_reader"]["status"] == "completed"
    assert items_by_action["build_self_build_core_status_reader"]["reason_code"] == "completed_allowed_paths_exist"
    assert items_by_action["build_self_build_run_summary_view"]["status"] == "ready"
    assert items_by_action["build_self_build_run_summary_view"]["allowed_paths"] == module.RUN_SUMMARY_VIEW_PATHS


def test_queue_selects_run_summary_view_after_status_reader_completed(tmp_path):
    module = load_module()
    for relative_path in module.CORE_STATUS_READER_PATHS:
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("present", encoding="utf-8")

    queue = module.build_self_build_core_preview_queue(tmp_path)
    selected = select_next_action({"readiness_status": "ready"}, queue)

    assert selected["selector_status"] == "selected"
    assert selected["selected_next_action"] == "build_self_build_run_summary_view"
    assert selected["selected_queue_item"]["action_id"] == "build_self_build_run_summary_view"
    assert all(value is False for value in selected["selected_queue_item"]["protected_action_flags"].values())


def test_queue_skips_completed_status_reader_and_run_summary_view(tmp_path):
    module = load_module()
    for relative_path in module.CORE_STATUS_READER_PATHS + module.RUN_SUMMARY_VIEW_PATHS:
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("present", encoding="utf-8")

    queue = module.build_self_build_core_preview_queue(tmp_path)
    items_by_action = {item["action_id"]: item for item in queue["items"]}
    selected = select_next_action({"readiness_status": "ready"}, queue)

    assert items_by_action["build_self_build_core_status_reader"]["status"] == "completed"
    assert items_by_action["build_self_build_run_summary_view"]["status"] == "completed"
    assert items_by_action["build_self_build_apply_approval_gate"]["status"] == "ready"
    assert selected["selector_status"] == "selected"
    assert selected["selected_next_action"] == "build_self_build_apply_approval_gate"
    assert selected["selected_queue_item"]["allowed_paths"] == module.APPLY_APPROVAL_GATE_PATHS
    assert selected["selected_queue_item"]["validators"] == module.APPLY_APPROVAL_GATE_VALIDATORS
    assert all(value is False for value in selected["selected_queue_item"]["protected_action_flags"].values())


def test_queue_selects_apply_approval_gate_integration_before_bridge(tmp_path):
    module = load_module()
    completed_paths = (
        module.CORE_STATUS_READER_PATHS
        + module.RUN_SUMMARY_VIEW_PATHS
        + module.APPLY_APPROVAL_GATE_PATHS
    )
    for relative_path in completed_paths:
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("present", encoding="utf-8")

    queue = module.build_self_build_core_preview_queue(tmp_path)
    items_by_action = {item["action_id"]: item for item in queue["items"]}
    selected = select_next_action({"readiness_status": "ready"}, queue)

    assert items_by_action["build_self_build_apply_approval_gate"]["status"] == "completed"
    assert items_by_action["integrate_self_build_apply_approval_gate"]["status"] == "ready"
    assert items_by_action["build_self_build_local_apply_executor_bridge"]["status"] == "ready"
    assert selected["selected_next_action"] == "integrate_self_build_apply_approval_gate"
    assert selected["selected_queue_item"]["allowed_paths"] == module.INTEGRATE_APPLY_APPROVAL_GATE_PATHS
    assert selected["selected_queue_item"]["validators"] == module.INTEGRATE_APPLY_APPROVAL_GATE_VALIDATORS
    assert all(value is False for value in selected["selected_queue_item"]["protected_action_flags"].values())


def test_queue_selects_local_apply_executor_bridge_after_integration_completed(tmp_path):
    module = load_module()
    completed_paths = (
        module.CORE_STATUS_READER_PATHS
        + module.RUN_SUMMARY_VIEW_PATHS
        + module.APPLY_APPROVAL_GATE_PATHS
        + module.INTEGRATE_APPLY_APPROVAL_GATE_PATHS
    )
    for relative_path in completed_paths:
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("present", encoding="utf-8")

    queue = module.build_self_build_core_preview_queue(tmp_path)
    items_by_action = {item["action_id"]: item for item in queue["items"]}
    selected = select_next_action({"readiness_status": "ready"}, queue)

    assert items_by_action["integrate_self_build_apply_approval_gate"]["status"] == "completed"
    assert items_by_action["integrate_self_build_apply_approval_gate"]["reason_code"] == "completed_allowed_paths_exist"
    assert selected["selected_next_action"] == "build_self_build_local_apply_executor_bridge"
    assert selected["selected_queue_item"]["allowed_paths"] == module.LOCAL_APPLY_EXECUTOR_BRIDGE_PATHS
    assert selected["selected_queue_item"]["validators"] == module.LOCAL_APPLY_EXECUTOR_BRIDGE_VALIDATORS
    assert all(value is False for value in selected["selected_queue_item"]["protected_action_flags"].values())


def test_queue_selects_single_action_executor_after_bridge_completed(tmp_path):
    module = load_module()
    completed_paths = (
        module.CORE_STATUS_READER_PATHS
        + module.RUN_SUMMARY_VIEW_PATHS
        + module.APPLY_APPROVAL_GATE_PATHS
        + module.INTEGRATE_APPLY_APPROVAL_GATE_PATHS
        + module.LOCAL_APPLY_EXECUTOR_BRIDGE_PATHS
    )
    for relative_path in completed_paths:
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("present", encoding="utf-8")

    queue = module.build_self_build_core_preview_queue(tmp_path)
    items_by_action = {item["action_id"]: item for item in queue["items"]}
    selected = select_next_action({"readiness_status": "ready"}, queue)

    assert items_by_action["build_self_build_local_apply_executor_bridge"]["status"] == "completed"
    assert items_by_action["build_self_build_single_action_executor"]["status"] == "ready"
    assert selected["selected_next_action"] == "build_self_build_single_action_executor"
    assert selected["selected_queue_item"]["allowed_paths"] == module.SINGLE_ACTION_EXECUTOR_PATHS
    assert selected["selected_queue_item"]["validators"] == module.SINGLE_ACTION_EXECUTOR_VALIDATORS
    assert all(value is False for value in selected["selected_queue_item"]["protected_action_flags"].values())


def test_queue_selects_apply_result_verifier_after_single_action_executor_completed(tmp_path):
    module = load_module()
    completed_paths = (
        module.CORE_STATUS_READER_PATHS
        + module.RUN_SUMMARY_VIEW_PATHS
        + module.APPLY_APPROVAL_GATE_PATHS
        + module.INTEGRATE_APPLY_APPROVAL_GATE_PATHS
        + module.LOCAL_APPLY_EXECUTOR_BRIDGE_PATHS
        + module.SINGLE_ACTION_EXECUTOR_PATHS
    )
    for relative_path in completed_paths:
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("present", encoding="utf-8")

    queue = module.build_self_build_core_preview_queue(tmp_path)
    items_by_action = {item["action_id"]: item for item in queue["items"]}
    selected = select_next_action({"readiness_status": "ready"}, queue)

    assert items_by_action["build_self_build_single_action_executor"]["status"] == "completed"
    assert items_by_action["build_self_build_apply_result_verifier"]["status"] == "ready"
    assert selected["selected_next_action"] == "build_self_build_apply_result_verifier"
    assert selected["selected_queue_item"]["allowed_paths"] == module.APPLY_RESULT_VERIFIER_PATHS
    assert selected["selected_queue_item"]["validators"] == module.APPLY_RESULT_VERIFIER_VALIDATORS
    assert all(value is False for value in selected["selected_queue_item"]["protected_action_flags"].values())


def test_queue_skips_apply_result_verifier_and_selects_one_action_execution_controller(tmp_path):
    module = load_module()
    completed_paths = (
        module.CORE_STATUS_READER_PATHS
        + module.RUN_SUMMARY_VIEW_PATHS
        + module.APPLY_APPROVAL_GATE_PATHS
        + module.INTEGRATE_APPLY_APPROVAL_GATE_PATHS
        + module.LOCAL_APPLY_EXECUTOR_BRIDGE_PATHS
        + module.SINGLE_ACTION_EXECUTOR_PATHS
        + module.APPLY_RESULT_VERIFIER_PATHS
    )
    for relative_path in completed_paths:
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("present", encoding="utf-8")

    queue = module.build_self_build_core_preview_queue(tmp_path)
    items_by_action = {item["action_id"]: item for item in queue["items"]}
    selected = select_next_action({"readiness_status": "ready"}, queue)

    assert items_by_action["build_self_build_apply_result_verifier"]["status"] == "completed"
    assert items_by_action["build_self_build_apply_result_verifier"]["reason_code"] == "completed_allowed_paths_exist"
    assert items_by_action["build_self_build_one_action_execution_controller"]["status"] == "ready"
    assert selected["selected_next_action"] == "build_self_build_one_action_execution_controller"
    assert selected["selected_queue_item"]["allowed_paths"] == module.ONE_ACTION_EXECUTION_CONTROLLER_PATHS
    assert selected["selected_queue_item"]["validators"] == module.ONE_ACTION_EXECUTION_CONTROLLER_VALIDATORS
    assert all(value is False for value in selected["selected_queue_item"]["protected_action_flags"].values())


def test_queue_skips_completed_one_action_controller_and_selects_apply_runner(tmp_path):
    module = load_module()
    completed_paths = (
        module.CORE_STATUS_READER_PATHS
        + module.RUN_SUMMARY_VIEW_PATHS
        + module.APPLY_APPROVAL_GATE_PATHS
        + module.INTEGRATE_APPLY_APPROVAL_GATE_PATHS
        + module.LOCAL_APPLY_EXECUTOR_BRIDGE_PATHS
        + module.SINGLE_ACTION_EXECUTOR_PATHS
        + module.APPLY_RESULT_VERIFIER_PATHS
        + module.ONE_ACTION_EXECUTION_CONTROLLER_PATHS
    )
    for relative_path in completed_paths:
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("present", encoding="utf-8")

    queue = module.build_self_build_core_preview_queue(tmp_path)
    items_by_action = {item["action_id"]: item for item in queue["items"]}
    selected = select_next_action({"readiness_status": "ready"}, queue)

    assert items_by_action["build_self_build_one_action_execution_controller"]["status"] == "completed"
    assert items_by_action["build_self_build_one_action_apply_runner"]["status"] == "ready"
    assert selected["selected_next_action"] == "build_self_build_one_action_apply_runner"
    assert selected["selected_queue_item"]["allowed_paths"] == module.ONE_ACTION_APPLY_RUNNER_PATHS
    assert selected["selected_queue_item"]["validators"] == module.ONE_ACTION_APPLY_RUNNER_VALIDATORS
    assert all(value is False for value in selected["selected_queue_item"]["protected_action_flags"].values())


def test_queue_skips_completed_one_action_apply_runner_and_selects_execute_gate(tmp_path):
    module = load_module()
    completed_paths = (
        module.CORE_STATUS_READER_PATHS
        + module.RUN_SUMMARY_VIEW_PATHS
        + module.APPLY_APPROVAL_GATE_PATHS
        + module.INTEGRATE_APPLY_APPROVAL_GATE_PATHS
        + module.LOCAL_APPLY_EXECUTOR_BRIDGE_PATHS
        + module.SINGLE_ACTION_EXECUTOR_PATHS
        + module.APPLY_RESULT_VERIFIER_PATHS
        + module.ONE_ACTION_EXECUTION_CONTROLLER_PATHS
        + module.ONE_ACTION_APPLY_RUNNER_PATHS
    )
    for relative_path in completed_paths:
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("present", encoding="utf-8")

    queue = module.build_self_build_core_preview_queue(tmp_path)
    items_by_action = {item["action_id"]: item for item in queue["items"]}
    selected = select_next_action({"readiness_status": "ready"}, queue)

    assert items_by_action["build_self_build_one_action_apply_runner"]["status"] == "completed"
    assert items_by_action["build_self_build_one_action_execute_gate"]["status"] == "ready"
    assert selected["selected_next_action"] == "build_self_build_one_action_execute_gate"
    assert selected["selected_queue_item"]["allowed_paths"] == module.ONE_ACTION_EXECUTE_GATE_PATHS
    assert selected["selected_queue_item"]["validators"] == module.ONE_ACTION_EXECUTE_GATE_VALIDATORS
    assert all(value is False for value in selected["selected_queue_item"]["protected_action_flags"].values())


def test_queue_skips_completed_one_action_execute_gate_and_selects_local_apply_executor(tmp_path):
    module = load_module()
    completed_paths = (
        module.CORE_STATUS_READER_PATHS
        + module.RUN_SUMMARY_VIEW_PATHS
        + module.APPLY_APPROVAL_GATE_PATHS
        + module.INTEGRATE_APPLY_APPROVAL_GATE_PATHS
        + module.LOCAL_APPLY_EXECUTOR_BRIDGE_PATHS
        + module.SINGLE_ACTION_EXECUTOR_PATHS
        + module.APPLY_RESULT_VERIFIER_PATHS
        + module.ONE_ACTION_EXECUTION_CONTROLLER_PATHS
        + module.ONE_ACTION_APPLY_RUNNER_PATHS
        + module.ONE_ACTION_EXECUTE_GATE_PATHS
    )
    for relative_path in completed_paths:
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("present", encoding="utf-8")

    queue = module.build_self_build_core_preview_queue(tmp_path)
    items_by_action = {item["action_id"]: item for item in queue["items"]}
    selected = select_next_action({"readiness_status": "ready"}, queue)

    assert items_by_action["build_self_build_one_action_execute_gate"]["status"] == "completed"
    assert items_by_action["build_self_build_one_action_local_apply_executor"]["status"] == "ready"
    assert selected["selected_next_action"] == "build_self_build_one_action_local_apply_executor"
    assert selected["selected_queue_item"]["allowed_paths"] == module.ONE_ACTION_LOCAL_APPLY_EXECUTOR_PATHS
    assert selected["selected_queue_item"]["validators"] == module.ONE_ACTION_LOCAL_APPLY_EXECUTOR_VALIDATORS
    assert all(value is False for value in selected["selected_queue_item"]["protected_action_flags"].values())


def test_no_network_subprocess_or_file_write_usage():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["subprocess", "requests", "socket", "urllib", ".write_text", "open("]:
        assert forbidden not in source
