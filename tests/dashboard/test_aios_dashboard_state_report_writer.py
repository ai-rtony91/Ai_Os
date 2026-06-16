from __future__ import annotations

import copy
import importlib.util
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
WRITER_MODULE_PATH = (
    REPO_ROOT / "automation" / "orchestration" / "dashboard" / "aios_dashboard_state_report_writer.py"
)
PROJECTOR_MODULE_PATH = (
    REPO_ROOT / "automation" / "orchestration" / "dashboard" / "aios_dashboard_state_projector.py"
)
FIXED_NOW = "2026-06-16T00:00:00Z"


def load_writer_module() -> Any:
    spec = importlib.util.spec_from_file_location("aios_dashboard_state_report_writer", WRITER_MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_projector_module() -> Any:
    spec = importlib.util.spec_from_file_location("aios_dashboard_state_projector", PROJECTOR_MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def temp_output_root(tmp_path: Path) -> Path:
    return tmp_path / "Reports" / "dashboard_state"


def evidence_ref(payload: dict[str, Any], section: str) -> dict[str, Any]:
    return {
        "payload": payload,
        "source_path": f"tests/fixtures/dashboard/aios_dashboard_state_projector/{section}.json",
        "source_schema": payload.get("schema"),
        "source_type": "fixture",
    }


def full_evidence() -> dict[str, Any]:
    return {
        "security_state": evidence_ref(
            {
                "schema": "AIOS_PREEMPTIVE_SECURITY_STATE.v1",
                "generated_utc": FIXED_NOW,
                "overall_state": "CLEAR",
                "security_status": "clear",
                "shield_state": "GREEN",
                "vault_lock_state": "LOCKED",
                "blocked_actions": ["broker execution"],
                "next_safe_action": "Continue display-only security review.",
            },
            "security_state",
        ),
        "continuation_state": evidence_ref(
            {
                "schema": "AIOS_AUTONOMOUS_JOB_CONTINUATION_STATE.v1",
                "generated_at_utc": FIXED_NOW,
                "state": "CONTINUE",
                "selected_task": {"task_id": "fixture-task", "mode": "DRY_RUN"},
                "repair_count": 0,
                "next_safe_action": "Continue to the next safe READ_ONLY/DRY_RUN cycle.",
            },
            "continuation_state",
        ),
        "watchtower_state": evidence_ref(
            {
                "schema": "AIOS_TRADING_WATCHTOWER_RESULT.v1",
                "generated_at_utc": FIXED_NOW,
                "watchtower_status": "CANDIDATE_FOUND",
                "market_regime": "TREND_UP",
                "market_radar": [{"symbol": "EURUSD", "direction": "LONG"}],
                "next_safe_action": "Review paper-only watchtower candidate.",
            },
            "watchtower_state",
        ),
    }


def projected_state() -> dict[str, Any]:
    projector = load_projector_module()
    return projector.project_dashboard_state(full_evidence(), now_utc=FIXED_NOW)


def test_successful_projected_state_write(tmp_path: Path) -> None:
    module = load_writer_module()
    root = temp_output_root(tmp_path)

    result = module.write_dashboard_state_report(
        projected_state=projected_state(),
        now_utc=FIXED_NOW,
        output_root=root,
    )

    output_path = Path(result["output_path"])
    assert result["status"] == "WROTE"
    assert output_path.parent == root
    assert output_path.read_text(encoding="utf-8").startswith("# AIOS Dashboard State Report")
    assert result["bytes_written"] == len(output_path.read_bytes())


def test_successful_evidence_through_renderer_write(tmp_path: Path) -> None:
    module = load_writer_module()

    result = module.write_dashboard_state_report(
        evidence=full_evidence(),
        now_utc=FIXED_NOW,
        output_root=temp_output_root(tmp_path),
        filename="evidence_report.md",
    )

    assert result["status"] == "WROTE"
    assert "CANDIDATE_FOUND" in Path(result["output_path"]).read_text(encoding="utf-8")


def test_empty_input_fail_closed_report_write(tmp_path: Path) -> None:
    module = load_writer_module()

    result = module.write_dashboard_state_report(now_utc=FIXED_NOW, output_root=temp_output_root(tmp_path))

    assert result["status"] == "WROTE"
    content = Path(result["output_path"]).read_text(encoding="utf-8")
    assert "NEEDS_REVIEW" in content
    assert "MISSING" in content


def test_default_filename_format(tmp_path: Path) -> None:
    module = load_writer_module()

    result = module.write_dashboard_state_report(now_utc=FIXED_NOW, output_root=temp_output_root(tmp_path))

    assert Path(result["output_path"]).name == "dashboard_state_report_20260616_000000Z.md"
    assert re.fullmatch(r"dashboard_state_report_\d{8}_\d{6}Z\.md", Path(result["output_path"]).name)


def test_metadata_fields_and_safety_flags(tmp_path: Path) -> None:
    module = load_writer_module()

    result = module.write_dashboard_state_report(
        projected_state=projected_state(),
        now_utc=FIXED_NOW,
        output_root=temp_output_root(tmp_path),
    )

    for field in ("status", "output_path", "bytes_written", "mode", "safety_flags", "reason"):
        assert field in result
    assert result["mode"] == "GATED_MARKDOWN_REPORT_OUTPUT"
    assert result["safety_flags"]["approved_output_root"] is True
    assert result["safety_flags"]["safe_filename"] is True
    assert result["safety_flags"]["path_confined"] is True
    assert result["safety_flags"]["non_empty_markdown"] is True
    assert result["safety_flags"]["control_authority"] is False
    assert result["safety_flags"]["execution_allowed"] is False
    assert result["safety_flags"]["mutation_allowed"] is False


def test_unsafe_filename_is_blocked(tmp_path: Path) -> None:
    module = load_writer_module()
    root = temp_output_root(tmp_path)

    result = module.write_dashboard_state_report(
        evidence=full_evidence(),
        now_utc=FIXED_NOW,
        output_root=root,
        filename="../outside.md",
    )

    assert result["status"] == "BLOCKED"
    assert result["reason"] == "unsafe_filename"
    assert not (tmp_path / "outside.md").exists()
    assert not root.exists()


def test_path_escape_and_unapproved_root_are_blocked(tmp_path: Path) -> None:
    module = load_writer_module()

    result = module.write_dashboard_state_report(
        evidence=full_evidence(),
        now_utc=FIXED_NOW,
        output_root=tmp_path / "Reports",
        filename="report.md",
    )

    assert result["status"] == "BLOCKED"
    assert result["reason"] == "unapproved_output_root"
    assert not (tmp_path / "Reports" / "report.md").exists()


def test_existing_file_is_not_overwritten_by_default(tmp_path: Path) -> None:
    module = load_writer_module()
    root = temp_output_root(tmp_path)
    root.mkdir(parents=True)
    target = root / "existing.md"
    target.write_text("original", encoding="utf-8")

    result = module.write_dashboard_state_report(
        evidence=full_evidence(),
        now_utc=FIXED_NOW,
        output_root=root,
        filename=target.name,
    )

    assert result["status"] == "BLOCKED"
    assert result["reason"] == "target_exists"
    assert target.read_text(encoding="utf-8") == "original"


def test_explicit_overwrite_true_works(tmp_path: Path) -> None:
    module = load_writer_module()
    root = temp_output_root(tmp_path)
    root.mkdir(parents=True)
    target = root / "existing.md"
    target.write_text("original", encoding="utf-8")

    result = module.write_dashboard_state_report(
        evidence=full_evidence(),
        now_utc=FIXED_NOW,
        output_root=root,
        filename=target.name,
        overwrite=True,
    )

    assert result["status"] == "WROTE"
    assert "AIOS Dashboard State Report" in target.read_text(encoding="utf-8")


def test_empty_rendered_content_is_blocked(tmp_path: Path) -> None:
    module = load_writer_module()
    module.render_dashboard_state_report = lambda **_: "   "
    root = temp_output_root(tmp_path)

    result = module.write_dashboard_state_report(
        evidence=full_evidence(),
        now_utc=FIXED_NOW,
        output_root=root,
    )

    assert result["status"] == "BLOCKED"
    assert result["reason"] == "empty_content"
    assert not root.exists()


def test_evidence_input_is_not_mutated(tmp_path: Path) -> None:
    module = load_writer_module()
    evidence = full_evidence()
    before = copy.deepcopy(evidence)

    result = module.write_dashboard_state_report(
        evidence=evidence,
        now_utc=FIXED_NOW,
        output_root=temp_output_root(tmp_path),
    )

    assert result["status"] == "WROTE"
    assert evidence == before


def test_writer_source_has_no_forbidden_process_terms() -> None:
    source = WRITER_MODULE_PATH.read_text(encoding="utf-8").lower()

    assert "subprocess" not in source
    for term in ("scheduler", "daemon", "worker", "launch"):
        assert term not in source


def test_writer_does_not_write_outside_approved_root(tmp_path: Path) -> None:
    module = load_writer_module()
    root = temp_output_root(tmp_path)

    result = module.write_dashboard_state_report(
        evidence=full_evidence(),
        now_utc=FIXED_NOW,
        output_root=root,
        filename="..\\escaped.md",
    )

    assert result["status"] == "BLOCKED"
    assert not (tmp_path / "escaped.md").exists()
    assert not root.exists()
