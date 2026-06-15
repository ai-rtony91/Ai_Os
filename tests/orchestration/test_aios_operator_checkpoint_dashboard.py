from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_operator_checkpoint_dashboard.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_operator_checkpoint_dashboard", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def selected_report() -> dict[str, object]:
    return {
        "selected_packet": {"packet_id": "PKT-AIOS-FOREX-BUILDER-DATA-SCHEMAS"},
        "codex_ready_packet_preview": {"packet_ready": True},
        "approved_executor_status": "blocked",
        "approval_status": "missing",
        "execution_allowed": False,
        "command_validation_status": "NOT_RUN",
        "dashboard_contract": {"pr_status": "none", "checks_status": "not_run", "sos_required": False},
        "next_safe_action": "Review the selected packet preview.",
    }


def test_module_exists() -> None:
    assert MODULE_PATH.exists()


def test_panel_schema_is_operator_checkpoint_v1() -> None:
    module = load_module()
    panel = module.build_operator_checkpoint_panel(selected_report())

    assert panel["schema"] == "AIOS_OPERATOR_CHECKPOINT_PANEL.v1"
    assert panel["status"] == "ready"


def test_selected_packet_appears_in_panel() -> None:
    module = load_module()
    panel = module.build_operator_checkpoint_panel(selected_report())

    assert panel["current_packet"] == "PKT-AIOS-FOREX-BUILDER-DATA-SCHEMAS"
    assert "Packet: PKT-AIOS-FOREX-BUILDER-DATA-SCHEMAS" in panel["lines"]


def test_approval_missing_maps_to_waiting_for_approval() -> None:
    module = load_module()
    panel = module.build_operator_checkpoint_panel(selected_report())

    assert panel["state"] == "WAITING_FOR_APPROVAL"
    assert panel["next_action"] == "approve APPLY / skip packet / inspect details"


def test_sos_true_maps_to_sos_required() -> None:
    module = load_module()
    report = selected_report()
    report["sos_required"] = True
    panel = module.build_operator_checkpoint_panel(report)

    assert panel["state"] == "SOS_REQUIRED"
    assert panel["next_action"] == "wake Anthony / inspect blocker"


def test_no_selected_packet_maps_to_idle_safe_and_emits_bored_queue() -> None:
    module = load_module()
    panel = module.build_operator_checkpoint_panel({})

    assert panel["state"] == "IDLE_SAFE"
    assert panel["current_packet"] == "none"
    assert panel["bored_queue"]


def test_progress_line_includes_core_status_fields() -> None:
    module = load_module()
    panel = module.build_operator_checkpoint_panel(selected_report())
    progress = panel["progress_line"]

    assert "selected=yes" in progress
    assert "prompt=yes" in progress
    assert "tests=not_run" in progress
    assert "PR=none" in progress
    assert "SOS=no" in progress


def test_next_action_is_compact_and_non_empty() -> None:
    module = load_module()
    panel = module.build_operator_checkpoint_panel(selected_report())

    assert panel["next_action"]
    assert len(panel["next_action"]) < 80


def test_bored_queue_tasks_are_safe_and_explain_earned_green_box_reason() -> None:
    module = load_module()
    bored_queue = module.build_bored_work_queue({})

    assert bored_queue
    for task in bored_queue:
        assert task["earned_green_box_reason"]
        assert "not fake heatmap activity" in task["earned_green_box_reason"]
        write_scope_text = " ".join(task["write_scope"]).lower()
        assert "broker" not in write_scope_text
        assert "live" not in write_scope_text
        assert "secret" not in write_scope_text
        assert "order" not in write_scope_text
        assert "webhook" not in write_scope_text
        assert "scheduler" not in write_scope_text
        assert "daemon" not in write_scope_text
        for forbidden in ("broker", "live trading", "secrets", "orders", "webhooks", "scheduler", "daemon"):
            assert forbidden in task["forbidden_actions"]


def test_panel_lines_are_ten_lines_or_fewer_by_default() -> None:
    module = load_module()
    panel = module.build_operator_checkpoint_panel(selected_report())

    assert len(panel["lines"]) <= 10


def test_safety_line_includes_core_forbidden_boundaries() -> None:
    module = load_module()
    panel = module.build_operator_checkpoint_panel(selected_report())

    assert "no broker/live/secrets/orders/webhooks" in panel["safety_line"]


def test_formatter_returns_readable_text_without_full_json_dump() -> None:
    module = load_module()
    panel = module.build_operator_checkpoint_panel(selected_report())
    text = module.format_operator_checkpoint_panel(panel)

    assert text.startswith("AIOS STATUS")
    assert "Packet:" in text
    assert "State:" in text
    assert "Next:" in text
    assert "{" not in text
    assert "}" not in text


def test_pure_module_source_has_no_filesystem_writes_or_external_execution() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    import_lines = "\n".join(
        line.strip()
        for line in source.splitlines()
        if line.startswith("import ") or line.startswith("from ")
    )

    for forbidden_import in ("subprocess", "socket", "urllib", "requests", "http", "pathlib", "os", "shutil"):
        assert forbidden_import not in import_lines
    for forbidden_call in ("open(", "Path(", "write_text(", "write_bytes(", "subprocess.", "os."):
        assert forbidden_call not in source
