from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_overnight_build_controller.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_overnight_build_controller", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def ready_status() -> dict[str, object]:
    return {
        "self_build_loop_readiness": {
            "readiness_status": "ready",
            "current_goal": "forex-paper-bot",
            "latest_validated_chain": "forex_paper_session_controller",
            "sos_required": False,
        }
    }


def queue() -> dict[str, object]:
    return {
        "items": [
            {
                "priority": 10,
                "action_id": "build_platform_status_reader",
                "status": "ready",
                "protected_action_flags": {"git_commit": False},
            }
        ]
    }


def test_imports_and_schema():
    module = load_module()
    assert module.SCHEMA == "AIOS_OVERNIGHT_BUILD_CONTROLLER.v1"


def test_ready_status_selects_queue_item_in_dry_run():
    module = load_module()
    report = module.build_overnight_build_controller(ready_status(), queue(), cycle_budget=2)
    assert report["schema"] == "AIOS_OVERNIGHT_BUILD_CONTROLLER.v1"
    assert report["controller_mode"] == "DRY_RUN"
    assert report["allowed_to_continue"] is True
    assert report["selected_next_action"] == "build_platform_status_reader"
    assert report["cycle_budget"] == 2
    assert report["approval_required"]["git_commit"] is True
    assert report["safety"]["commands_executed"] is False


def test_review_required_stops_without_queue_item():
    module = load_module()
    report = module.build_overnight_build_controller(
        {"self_build_loop_readiness": {"readiness_status": "review_required", "current_goal": "forex-paper-bot"}},
        queue(),
    )
    assert report["allowed_to_continue"] is False
    assert report["selected_next_action"] == "self_build_loop_readiness_review"
    assert report["stop_reason"] == "self_build_readiness_review_required"


def test_cli_outputs_json(capsys):
    module = load_module()
    exit_code = module.main(["--status", json.dumps(ready_status()), "--queue", json.dumps(queue())])
    captured = capsys.readouterr()
    assert exit_code == 0
    report = json.loads(captured.out)
    assert report["controller_mode"] == "DRY_RUN"


def test_no_subprocess_network_or_file_write_usage():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["subprocess", "requests", "socket", "urllib", ".write_text", "open("]:
        assert forbidden not in source
