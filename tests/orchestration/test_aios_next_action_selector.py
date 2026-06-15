from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_next_action_selector.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_next_action_selector", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def readiness(status: str = "ready") -> dict[str, object]:
    return {"readiness_status": status, "sos_required": False}


def queue_item(**overrides: object) -> dict[str, object]:
    item = {
        "priority": 10,
        "action_id": "build_platform_status_reader",
        "status": "ready",
        "allowed_paths": ["automation/orchestration/platform_status_reader.py"],
        "validators": ["python -m pytest tests/orchestration/test_platform_status_reader.py"],
        "protected_action_flags": {"git_commit": False},
    }
    item.update(overrides)
    return item


def test_imports_and_schema():
    module = load_module()
    assert module.SCHEMA == "AIOS_NEXT_ACTION_SELECTOR.v1"


def test_selects_ready_bounded_dry_run_item():
    module = load_module()
    result = module.select_next_action(readiness(), {"items": [queue_item()]})
    assert result["selector_status"] == "selected"
    assert result["selected_next_action"] == "build_platform_status_reader"
    assert result["reason_code"] == "selected_bounded_dry_run_action"


def test_stops_when_readiness_not_ready_or_review_required():
    module = load_module()
    assert module.select_next_action(readiness("not_ready"), {"items": [queue_item()]})["reason_code"] == "readiness_not_ready"
    assert (
        module.select_next_action(readiness("review_required"), {"items": [queue_item()]})["reason_code"]
        == "readiness_review_required"
    )


def test_stops_for_empty_queue_or_protected_action():
    module = load_module()
    assert module.select_next_action(readiness(), {"items": []})["reason_code"] == "queue_empty"
    protected = queue_item(protected_action_flags={"git_commit": True})
    assert module.select_next_action(readiness(), {"items": [protected]})["reason_code"] == "protected_action_required"


def test_sos_stops_selector():
    module = load_module()
    result = module.select_next_action({"readiness_status": "ready", "sos_required": True}, {"items": [queue_item()]})
    assert result["selector_status"] == "stopped"
    assert result["reason_code"] == "sos_required"
