from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "dashboard" / "aios_manual_dashboard_snapshot.py"
PROJECTOR_MODULE_PATH = (
    REPO_ROOT / "automation" / "orchestration" / "dashboard" / "aios_dashboard_state_projector.py"
)
AIOS_SCRIPT_PATH = REPO_ROOT / "aios.ps1"
FIXED_NOW = "2026-06-16T00:00:00Z"


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("aios_manual_dashboard_snapshot", MODULE_PATH)
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


def test_projected_state_manual_snapshot_succeeds(tmp_path: Path) -> None:
    module = load_module()

    result = module.create_manual_dashboard_snapshot(
        projected_state=projected_state(),
        now_utc=FIXED_NOW,
        output_root=temp_output_root(tmp_path),
    )

    output_path = Path(result["output_path"])
    assert result["status"] == "WROTE"
    assert result["writer_status"] == "WROTE"
    assert output_path.parent == temp_output_root(tmp_path)
    assert output_path.read_text(encoding="utf-8").startswith("# AIOS Dashboard State Report")


def test_evidence_manual_snapshot_succeeds(tmp_path: Path) -> None:
    module = load_module()

    result = module.create_manual_dashboard_snapshot(
        evidence=full_evidence(),
        now_utc=FIXED_NOW,
        output_root=temp_output_root(tmp_path),
        filename="manual_evidence.md",
    )

    assert result["status"] == "WROTE"
    assert "CANDIDATE_FOUND" in Path(result["output_path"]).read_text(encoding="utf-8")


def test_empty_fail_closed_evidence_produces_report_through_writer(tmp_path: Path) -> None:
    module = load_module()

    result = module.create_manual_dashboard_snapshot(now_utc=FIXED_NOW, output_root=temp_output_root(tmp_path))

    content = Path(result["output_path"]).read_text(encoding="utf-8")
    assert result["status"] == "WROTE"
    assert "NEEDS_REVIEW" in content
    assert "MISSING" in content


def test_manual_trigger_false_blocks_before_writer_call() -> None:
    module = load_module()
    calls: list[dict[str, Any]] = []

    def fake_writer(**kwargs: Any) -> dict[str, Any]:
        calls.append(kwargs)
        return {"status": "WROTE"}

    module.write_dashboard_state_report = fake_writer

    result = module.create_manual_dashboard_snapshot(manual_trigger=False)

    assert result["status"] == "BLOCKED"
    assert result["writer_status"] == "NOT_CALLED"
    assert result["reason"] == "manual_trigger_required"
    assert calls == []


def test_writer_blocked_status_propagates_safely() -> None:
    module = load_module()

    def fake_writer(**_: Any) -> dict[str, Any]:
        return {
            "status": "BLOCKED",
            "output_path": "",
            "bytes_written": 0,
            "mode": "GATED_MARKDOWN_REPORT_OUTPUT",
            "safety_flags": {"approved_output_root": False},
            "reason": "unsafe_filename",
        }

    module.write_dashboard_state_report = fake_writer

    result = module.create_manual_dashboard_snapshot(evidence=full_evidence())

    assert result["status"] == "BLOCKED"
    assert result["writer_status"] == "BLOCKED"
    assert result["reason"] == "unsafe_filename"
    assert result["bytes_written"] == 0


def test_metadata_contains_required_fields(tmp_path: Path) -> None:
    module = load_module()

    result = module.create_manual_dashboard_snapshot(
        evidence=full_evidence(),
        now_utc=FIXED_NOW,
        output_root=temp_output_root(tmp_path),
    )

    for field in ("status", "output_path", "bytes_written", "mode", "safety_flags", "reason", "writer_status"):
        assert field in result
    assert result["mode"] == "MANUAL_DASHBOARD_SNAPSHOT"
    assert result["safety_flags"]["manual_trigger"] is True
    assert result["safety_flags"]["writer_called"] is True
    assert result["safety_flags"]["output_written"] is True
    assert result["safety_flags"]["control_authority"] is False
    assert result["safety_flags"]["execution_allowed"] is False
    assert result["safety_flags"]["mutation_allowed"] is False


def test_evidence_input_is_not_mutated(tmp_path: Path) -> None:
    module = load_module()
    evidence = full_evidence()
    before = copy.deepcopy(evidence)

    result = module.create_manual_dashboard_snapshot(
        evidence=evidence,
        now_utc=FIXED_NOW,
        output_root=temp_output_root(tmp_path),
    )

    assert result["status"] == "WROTE"
    assert evidence == before


def test_source_has_no_subprocess_usage() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "subprocess" not in source


def test_source_has_no_background_start_terms() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()

    for term in ("scheduler", "daemon", "worker", "launch"):
        assert term not in source


def test_source_does_not_reference_aios_script() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()

    assert AIOS_SCRIPT_PATH.exists()
    assert "aios.ps1" not in source
