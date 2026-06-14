from __future__ import annotations

import json
from pathlib import Path

import pytest

from automation.orchestration.self_development.aios_autonomy_run_ledger import (
    SCHEMA,
    LedgerPathError,
    build_ledger_record,
    resolve_ledger_output_root,
    write_ledger_record,
)


def _record(**overrides: object) -> dict:
    record = build_ledger_record(
        run_id="run_001",
        mode="APPLY",
        task_type="FOREX_BACKTEST_STUB",
        status="PASS",
        generated_utc="2026-06-13T00:00:00Z",
        stop_reason="",
        next_safe_action="Review local run ledger.",
        result_summary={"ok": True},
    )
    record.update(overrides)
    return record


def test_ledger_writes_only_to_approved_output_root(tmp_path: Path) -> None:
    output_root = tmp_path / "approved_ledger"
    receipt = write_ledger_record(output_root, _record())

    target = Path(receipt["path"])
    assert receipt["written"] is True
    assert target.exists()
    assert output_root.resolve() in target.resolve().parents
    assert json.loads(target.read_text(encoding="utf-8"))["schema"] == SCHEMA


def test_path_traversal_blocked(tmp_path: Path) -> None:
    with pytest.raises(LedgerPathError):
        resolve_ledger_output_root(tmp_path / ".." / "outside")


def test_secrets_and_live_trading_paths_blocked(tmp_path: Path) -> None:
    for unsafe in ("secrets", ".env", "broker", "live_trading", "oanda", "webhook", "orders"):
        with pytest.raises(LedgerPathError):
            resolve_ledger_output_root(tmp_path / unsafe / "ledger")


def test_record_schema_emitted() -> None:
    record = _record()

    assert record["schema"] == SCHEMA
    assert record["run_id"] == "run_001"
    assert record["task_type"] == "FOREX_BACKTEST_STUB"
    assert record["status"] == "PASS"


def test_no_queue_lock_approval_or_registry_mutation(tmp_path: Path) -> None:
    receipt = write_ledger_record(tmp_path / "ledger", _record())
    safety = receipt["safety"]

    assert safety["mutates_queue"] is False
    assert safety["mutates_locks"] is False
    assert safety["mutates_approval"] is False
    assert safety["mutates_registry"] is False
    assert safety["writes_reports"] is False
    assert safety["writes_telemetry"] is False
    assert safety["writes_relay"] is False
    assert safety["broker_or_live_trading"] is False
