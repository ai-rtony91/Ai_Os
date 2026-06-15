from __future__ import annotations

import importlib.util
from pathlib import Path


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


def test_path_traversal_is_rejected_from_allowed_paths():
    module = load_module()
    item = module.build_queue_item(action_id="unsafe", allowed_paths=["../outside.py", "safe/path.py"])
    assert item["allowed_paths"] == ["safe/path.py"]
    assert item["reason_code"] == "bounded_dry_run_item"


def test_no_network_subprocess_or_file_write_usage():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["subprocess", "requests", "socket", "urllib", ".write_text", "open("]:
        assert forbidden not in source
