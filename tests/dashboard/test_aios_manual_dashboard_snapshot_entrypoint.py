from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "dashboard"
    / "aios_manual_dashboard_snapshot_entrypoint.py"
)
AIOS_SCRIPT_PATH = REPO_ROOT / "aios.ps1"
FIXED_NOW = "2026-06-16T00:00:00Z"


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("aios_manual_dashboard_snapshot_entrypoint", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def temp_output_root(tmp_path: Path) -> Path:
    return tmp_path / "Reports" / "dashboard_state"


def run_main(module: Any, args: list[str], capsys: pytest.CaptureFixture[str]) -> tuple[int, dict[str, Any]]:
    exit_code = module.main(args)
    captured = capsys.readouterr()
    assert captured.err == ""
    return exit_code, json.loads(captured.out)


def test_main_writes_json_metadata_for_temp_output_root(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    module = load_module()
    root = temp_output_root(tmp_path)

    exit_code, metadata = run_main(
        module,
        ["--output-root", str(root), "--now-utc", FIXED_NOW],
        capsys,
    )

    output_path = Path(metadata["output_path"])
    assert exit_code == 0
    assert metadata["status"] == "WROTE"
    assert metadata["writer_status"] == "WROTE"
    assert metadata["mode"] == "MANUAL_DASHBOARD_SNAPSHOT"
    assert metadata["bytes_written"] == len(output_path.read_bytes())
    assert output_path.parent == root


def test_default_empty_fail_closed_snapshot_path_works_through_m9_m8(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = load_module()

    exit_code, metadata = run_main(
        module,
        ["--output-root", str(temp_output_root(tmp_path)), "--now-utc", FIXED_NOW],
        capsys,
    )

    content = Path(metadata["output_path"]).read_text(encoding="utf-8")
    assert exit_code == 0
    assert "NEEDS_REVIEW" in content
    assert "MISSING" in content


def test_explicit_filename_is_passed_through_safely(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    module = load_module()
    root = temp_output_root(tmp_path)

    exit_code, metadata = run_main(
        module,
        [
            "--output-root",
            str(root),
            "--filename",
            "manual_entrypoint.md",
            "--now-utc",
            FIXED_NOW,
        ],
        capsys,
    )

    assert exit_code == 0
    assert Path(metadata["output_path"]).name == "manual_entrypoint.md"
    assert Path(metadata["output_path"]).parent == root


def test_overwrite_flag_is_passed_through_safely(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    module = load_module()
    root = temp_output_root(tmp_path)
    root.mkdir(parents=True)
    target = root / "manual_entrypoint.md"
    target.write_text("original", encoding="utf-8")

    exit_code, metadata = run_main(
        module,
        [
            "--output-root",
            str(root),
            "--filename",
            target.name,
            "--now-utc",
            FIXED_NOW,
            "--overwrite",
        ],
        capsys,
    )

    assert exit_code == 0
    assert metadata["status"] == "WROTE"
    assert "AIOS Dashboard State Report" in target.read_text(encoding="utf-8")


def test_now_utc_controls_deterministic_filename_timestamp(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = load_module()

    exit_code, metadata = run_main(
        module,
        ["--output-root", str(temp_output_root(tmp_path)), "--now-utc", FIXED_NOW],
        capsys,
    )

    assert exit_code == 0
    assert Path(metadata["output_path"]).name == "dashboard_state_report_20260616_000000Z.md"


def test_main_returns_zero_on_wrote(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    module = load_module()
    calls: list[dict[str, Any]] = []

    def fake_snapshot(**kwargs: Any) -> dict[str, Any]:
        calls.append(kwargs)
        return {
            "status": "WROTE",
            "output_path": "C:/tmp/Reports/dashboard_state/report.md",
            "bytes_written": 12,
            "mode": "MANUAL_DASHBOARD_SNAPSHOT",
            "safety_flags": {"output_written": True},
            "reason": "written",
            "writer_status": "WROTE",
        }

    monkeypatch.setattr(module, "create_manual_dashboard_snapshot", fake_snapshot)

    exit_code, metadata = run_main(module, ["--now-utc", FIXED_NOW], capsys)

    assert exit_code == 0
    assert metadata["status"] == "WROTE"
    assert calls == [
        {
            "evidence": {},
            "now_utc": FIXED_NOW,
            "output_root": None,
            "filename": None,
            "overwrite": False,
            "manual_trigger": True,
        }
    ]


@pytest.mark.parametrize("status", ["BLOCKED", "NEEDS_REVIEW", "ERROR"])
def test_main_returns_nonzero_for_non_success_statuses(
    status: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = load_module()

    def fake_snapshot(**_: Any) -> dict[str, Any]:
        return {
            "status": status,
            "output_path": "",
            "bytes_written": 0,
            "mode": "MANUAL_DASHBOARD_SNAPSHOT",
            "safety_flags": {"output_written": False},
            "reason": "blocked",
            "writer_status": status,
        }

    monkeypatch.setattr(module, "create_manual_dashboard_snapshot", fake_snapshot)

    exit_code, metadata = run_main(module, ["--now-utc", FIXED_NOW], capsys)

    assert exit_code != 0
    assert metadata["status"] == status


def test_no_real_reports_output_is_required(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    module = load_module()
    root = temp_output_root(tmp_path)

    exit_code, metadata = run_main(
        module,
        ["--output-root", str(root), "--now-utc", FIXED_NOW],
        capsys,
    )

    assert exit_code == 0
    assert Path(metadata["output_path"]).parent == root
    assert not str(metadata["output_path"]).startswith(str(REPO_ROOT / "Reports"))


def test_source_contains_no_subprocess_usage() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "subprocess" not in source


def test_source_contains_no_background_start_terms() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()

    for term in ("scheduler", "daemon", "worker", "launch"):
        assert term not in source


def test_source_does_not_reference_aios_script() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()

    assert "aios.ps1" not in source


def test_aios_script_remains_untouched(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    module = load_module()
    before = AIOS_SCRIPT_PATH.read_text(encoding="utf-8")

    exit_code, metadata = run_main(
        module,
        ["--output-root", str(temp_output_root(tmp_path)), "--now-utc", FIXED_NOW],
        capsys,
    )

    after = AIOS_SCRIPT_PATH.read_text(encoding="utf-8")
    assert exit_code == 0
    assert metadata["status"] == "WROTE"
    assert after == before
