from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from automation.forex_engine.forex_demo_run_day_recorder_v1 import (  # noqa: E402
    LEDGER_NEVER_LIVE_FLAGS,
    RECORD_TYPE_REAL_DEMO_DAY,
    build_demo_verdict_snapshot,
    load_demo_ledger_entries,
    record_forex_demo_run_day,
    summarize_demo_ledger,
)
from forex_delivery.paper_signal_execution_loop import build_paper_signal_execution_loop_result  # noqa: E402


def _seed_mock_ledger(repo_root: Path) -> Path:
    ledger_path = repo_root / "telemetry" / "forex" / "demo_proof_ledger.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(
        (ROOT / "telemetry" / "forex" / "demo_proof_ledger.jsonl").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    return ledger_path


def test_summary_ignores_mock_rows_before_any_real_demo_day(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _seed_mock_ledger(repo_root)

    summary = build_demo_verdict_snapshot(repo_root)

    assert summary["real_demo_day_count"] == 0
    assert summary["mock_entry_count"] == 3
    assert summary["mock_entries_superseded_by_real_run"] == 3
    assert summary["days_recorded_toward_verdict"] == 0
    assert summary["trades_accumulated"] == 0
    assert summary["windows"] == 0
    assert summary["verdict_status"] == "EARNING"


def test_record_real_demo_day_appends_and_keeps_never_live_flags_false(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _seed_mock_ledger(repo_root)

    session_result = build_paper_signal_execution_loop_result()
    receipt = record_forex_demo_run_day(
        repo_root,
        session_result,
        apply=True,
        recorded_at_utc="2026-07-02T09:30:00Z",
        session_date="2026-07-02",
        baseline_equity_usd=1000.0,
    )

    ledger_entries = load_demo_ledger_entries(repo_root)
    summary = summarize_demo_ledger(ledger_entries, baseline_equity_usd=1000.0)
    new_entry = ledger_entries[-1]

    assert len(ledger_entries) == 4
    assert summary["real_demo_day_count"] == 1
    assert summary["mock_entries_superseded_by_real_run"] == 3
    assert summary["days_recorded_toward_verdict"] == 1
    assert summary["trades_accumulated"] == 1
    assert summary["windows"] == 1
    assert receipt["appended"] is True
    assert receipt["session_summary"]["fills"] == 1
    assert receipt["session_summary"]["wins"] == 1
    assert receipt["session_summary"]["losses"] == 0
    assert receipt["days_recorded_toward_verdict"] == 1
    assert receipt["trades_accumulated_toward_verdict"] == 1
    assert receipt["windows_toward_verdict"] == 1
    assert new_entry["schema"] == "aios.forex.demo_proof_ledger.v1"
    assert new_entry["record_type"] == RECORD_TYPE_REAL_DEMO_DAY
    assert new_entry["date"] == "2026-07-02"
    assert new_entry["trade_rows"]
    assert all(not bool(new_entry[field]) for field in LEDGER_NEVER_LIVE_FLAGS)
    assert all(not bool(receipt[field]) for field in LEDGER_NEVER_LIVE_FLAGS)


def test_duplicate_real_demo_day_same_date_is_rejected(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _seed_mock_ledger(repo_root)

    session_result = build_paper_signal_execution_loop_result()
    record_forex_demo_run_day(
        repo_root,
        session_result,
        apply=True,
        recorded_at_utc="2026-07-02T09:30:00Z",
        session_date="2026-07-02",
        baseline_equity_usd=1000.0,
    )

    with pytest.raises(ValueError, match="duplicate_real_demo_day_entry:2026-07-02"):
        record_forex_demo_run_day(
            repo_root,
            session_result,
            apply=True,
            recorded_at_utc="2026-07-02T15:45:00Z",
            session_date="2026-07-02",
            baseline_equity_usd=1000.0,
        )

