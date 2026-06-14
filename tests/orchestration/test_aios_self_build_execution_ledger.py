from pathlib import Path

import pytest

from automation.orchestration.self_development.aios_self_build_execution_ledger import (
    SCHEMA,
    SelfBuildLedgerPathError,
    build_self_build_ledger_record,
    resolve_self_build_ledger_output_root,
    write_self_build_ledger_record,
)


def _record() -> dict:
    return build_self_build_ledger_record(
        run_id="self_build_test",
        candidate_id="AIOS-SELF-BUILD-RUNNER-HARDENING-CANDIDATE",
        packet_id="AIOS-SELF-BUILD-RUNNER-HARDENING-CANDIDATE-EXECUTION-PACKET",
        mode="APPLY",
        status="PASS",
        validator_summary={"pass_count": 3, "fail_count": 0},
        repair_attempts=0,
        stop_reason="COMPLETED",
        next_safe_action="Stop before push/PR/merge.",
    )


def test_ledger_writes_only_inside_approved_output_root(tmp_path: Path) -> None:
    output_root = tmp_path / "self_build_ledger"
    receipt = write_self_build_ledger_record(output_root, _record())
    ledger_path = Path(receipt["path"])

    assert receipt["written"] is True
    assert ledger_path.exists()
    assert output_root.resolve() in ledger_path.resolve().parents


def test_path_traversal_is_blocked(tmp_path: Path) -> None:
    with pytest.raises(SelfBuildLedgerPathError):
        resolve_self_build_ledger_output_root(tmp_path / ".." / "outside")


@pytest.mark.parametrize("blocked", ["secrets", ".env", "broker", "live", "OANDA"])
def test_secrets_live_broker_paths_are_blocked(tmp_path: Path, blocked: str) -> None:
    with pytest.raises(SelfBuildLedgerPathError):
        resolve_self_build_ledger_output_root(tmp_path / blocked)


def test_record_schema_emitted() -> None:
    record = _record()

    assert record["schema"] == SCHEMA
    assert record["run_id"] == "self_build_test"
    assert record["candidate_id"]
    assert record["packet_id"]


def test_no_queue_lock_approval_registry_mutation(tmp_path: Path) -> None:
    receipt = write_self_build_ledger_record(tmp_path / "self_build_ledger", _record())

    assert receipt["safety"]["mutates_queue"] is False
    assert receipt["safety"]["mutates_locks"] is False
    assert receipt["safety"]["mutates_approval"] is False
    assert receipt["safety"]["mutates_registry"] is False
