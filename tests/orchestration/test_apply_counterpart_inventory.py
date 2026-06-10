"""Tests for the APPLY-counterpart inventory (observe-only scan)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INVENTORY = (
    REPO_ROOT / "automation" / "orchestration" / "autonomy_reports"
    / "aios_apply_counterpart_inventory.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("aios_apply_counterpart_inventory", INVENTORY)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _touch(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("# script\n", encoding="utf-8")


def test_mutation_without_twin_is_high_priority(tmp_path):
    m = _load()
    _touch(tmp_path / "automation" / "Invoke-AiOsRelayRunner.DRY_RUN.ps1")
    inv = m.build_inventory(tmp_path)
    assert inv["total_dry_run_scripts"] == 1
    item = inv["items"][0]
    assert item["kind"] == "MUTATION"
    assert item["has_apply_twin"] is False
    assert item["priority"] == "HIGH"
    assert inv["counts"]["mutation_without_apply"] == 1


def test_mutation_with_apply_twin_is_covered(tmp_path):
    m = _load()
    _touch(tmp_path / "Update-AiOsCycleMarker.DRY_RUN.ps1")
    _touch(tmp_path / "Update-AiOsCycleMarker.APPLY.ps1")
    inv = m.build_inventory(tmp_path)
    item = next(i for i in inv["items"] if "DRY_RUN" in i["path"])
    assert item["has_apply_twin"] is True
    assert item["apply_twin"].endswith("Update-AiOsCycleMarker.APPLY.ps1")
    assert item["priority"] == "NONE"
    assert inv["counts"]["mutation_with_apply"] == 1


def test_read_only_needs_no_apply(tmp_path):
    m = _load()
    _touch(tmp_path / "Get-AiOsApprovalInboxSummary.DRY_RUN.ps1")
    inv = m.build_inventory(tmp_path)
    item = inv["items"][0]
    assert item["kind"] == "READ_ONLY"
    assert item["priority"] == "NONE"
    assert inv["counts"]["read_only"] == 1


def test_ranking_puts_high_first(tmp_path):
    m = _load()
    _touch(tmp_path / "Get-AiOsView.DRY_RUN.ps1")            # read-only -> not ranked
    _touch(tmp_path / "Invoke-AiOsThing.DRY_RUN.ps1")        # mutation no twin -> HIGH
    _touch(tmp_path / "Frobnicate-AiOs.DRY_RUN.ps1")         # unknown verb no twin -> MEDIUM
    inv = m.build_inventory(tmp_path)
    ranked = inv["ranked_needs_apply"]
    assert ranked[0]["priority"] == "HIGH"
    assert all(r["priority"] in {"HIGH", "MEDIUM"} for r in ranked)
    # read-only excluded from ranking
    assert all("Get-AiOsView" not in r["path"] for r in ranked)


def test_archive_dirs_skipped_by_default(tmp_path):
    m = _load()
    _touch(tmp_path / "archive" / "Invoke-AiOsOld.DRY_RUN.ps1")
    _touch(tmp_path / "automation" / "Invoke-AiOsLive.DRY_RUN.ps1")
    inv = m.build_inventory(tmp_path)
    assert inv["total_dry_run_scripts"] == 1  # archive skipped
    inv2 = m.build_inventory(tmp_path, include_skipped=True)
    assert inv2["total_dry_run_scripts"] == 2


def test_creates_no_files(tmp_path):
    m = _load()
    _touch(tmp_path / "Invoke-AiOsThing.DRY_RUN.ps1")
    before = sorted(p.name for p in tmp_path.rglob("*"))
    m.build_inventory(tmp_path)
    after = sorted(p.name for p in tmp_path.rglob("*"))
    assert before == after  # observe-only: scan created nothing
