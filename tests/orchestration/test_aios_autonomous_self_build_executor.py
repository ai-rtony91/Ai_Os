from pathlib import Path

from automation.orchestration.self_development.aios_autonomous_self_build_executor import (
    APPLY_APPROVAL,
    COMMIT_APPROVAL,
    build_autonomous_self_build_executor_result,
)


def _payload(tmp_path: Path, **overrides: object) -> dict:
    payload = {
        "mode": "DRY_RUN",
        "supervisor_mode": "FULL_LOCAL_SELF_BUILD_STUB",
        "human_owner_self_build_approval": "",
        "max_supervisor_cycles": 1,
        "max_repair_attempts": 2,
        "max_runtime_minutes": 60,
        "stop_on_first_failure": True,
        "allow_local_commit": False,
        "output_root": str(tmp_path / "ledger"),
        "write_ledger": False,
    }
    payload.update(overrides)
    return payload


def test_missing_approval_blocks_apply(tmp_path: Path) -> None:
    result = build_autonomous_self_build_executor_result(_payload(tmp_path, mode="APPLY"))

    assert result["safety"]["status"] == "BLOCKED"
    assert "HUMAN_OWNER_SELF_BUILD_APPROVAL_MISSING" in result["stop_conditions"]
    assert result["run_ledger"]["written"] is False


def test_dry_run_writes_no_ledger(tmp_path: Path) -> None:
    result = build_autonomous_self_build_executor_result(_payload(tmp_path, mode="DRY_RUN"))

    assert result["mode"] == "DRY_RUN"
    assert result["run_ledger"]["written"] is False
    assert not (tmp_path / "ledger").exists()
    assert result["safety"]["writes_files"] is False


def test_apply_writes_ledger_only(tmp_path: Path) -> None:
    result = build_autonomous_self_build_executor_result(
        _payload(
            tmp_path,
            mode="APPLY",
            human_owner_self_build_approval=APPLY_APPROVAL,
            write_ledger=True,
        )
    )

    assert result["safety"]["status"] == "PASS"
    assert result["executed_autonomously"] is True
    assert result["run_ledger"]["written"] is True
    assert Path(result["run_ledger"]["path"]).exists()
    assert result["safety"]["writes_only_approved_run_ledger"] is True
    assert result["safety"]["arbitrary_source_edit"] is False


def test_plan_only_returns_plan(tmp_path: Path) -> None:
    result = build_autonomous_self_build_executor_result(_payload(tmp_path, supervisor_mode="PLAN_ONLY"))

    assert result["supervisor_mode"] == "PLAN_ONLY"
    assert result["selected_candidate"]["candidate_id"]
    assert result["execution_packet"]["packet_id"]


def test_select_next_candidate_returns_candidate(tmp_path: Path) -> None:
    result = build_autonomous_self_build_executor_result(
        _payload(tmp_path, supervisor_mode="SELECT_NEXT_CANDIDATE")
    )

    assert result["selected_candidate"]["candidate_lane"] == "runner_hardening"


def test_build_execution_packet_returns_packet(tmp_path: Path) -> None:
    result = build_autonomous_self_build_executor_result(
        _payload(tmp_path, supervisor_mode="BUILD_EXECUTION_PACKET")
    )

    assert result["execution_packet"]["schema"] == "AIOS_SELF_BUILD_EXECUTION_PACKET.v1"
    assert result["execution_packet"]["commit_policy"] == "LOCAL_COMMIT_ONLY_WITH_APPROVAL"


def test_validate_and_repair_stub_runs_repair_loop(tmp_path: Path) -> None:
    result = build_autonomous_self_build_executor_result(
        _payload(
            tmp_path,
            supervisor_mode="VALIDATE_AND_REPAIR_STUB",
            validator_results=[{"validator_id": "chain", "status": "FAIL"}],
        )
    )

    assert result["validation_repair_result"]["status"] == "REPAIR_ATTEMPT_AVAILABLE"
    assert "STOP_ON_FIRST_FAILURE" in result["stop_conditions"]


def test_full_local_self_build_stub_runs_candidate_packet_repair_ledger(tmp_path: Path) -> None:
    result = build_autonomous_self_build_executor_result(
        _payload(
            tmp_path,
            mode="APPLY",
            supervisor_mode="FULL_LOCAL_SELF_BUILD_STUB",
            human_owner_self_build_approval=APPLY_APPROVAL,
            write_ledger=True,
        )
    )

    assert result["selected_candidate"]["candidate_id"]
    assert result["execution_packet"]["packet_id"]
    assert result["validation_repair_result"]["status"] == "PASS"
    assert result["run_ledger"]["written"] is True


def test_max_supervisor_cycles_caps(tmp_path: Path) -> None:
    result = build_autonomous_self_build_executor_result(
        _payload(tmp_path, max_supervisor_cycles=3)
    )

    assert result["cycles_requested"] == 3
    assert result["cycles_completed"] <= 3


def test_max_runtime_minutes_validates(tmp_path: Path) -> None:
    result = build_autonomous_self_build_executor_result(
        _payload(tmp_path, max_runtime_minutes=241)
    )

    assert result["safety"]["status"] == "BLOCKED"
    assert "MAX_RUNTIME_OUT_OF_RANGE" in result["stop_conditions"]


def test_stop_on_first_failure_works(tmp_path: Path) -> None:
    result = build_autonomous_self_build_executor_result(
        _payload(
            tmp_path,
            validator_results=[{"validator_id": "chain", "status": "FAIL"}],
            stop_on_first_failure=True,
        )
    )

    assert "STOP_ON_FIRST_FAILURE" in result["stop_conditions"]
    assert result["safety"]["status"] == "BLOCKED"


def test_no_push_pr_merge_or_commit_without_explicit_commit_approval(tmp_path: Path) -> None:
    result = build_autonomous_self_build_executor_result(
        _payload(
            tmp_path,
            mode="APPLY",
            human_owner_self_build_approval=APPLY_APPROVAL,
            allow_local_commit=True,
        )
    )

    assert result["safety"]["pushes"] is False
    assert result["safety"]["creates_pr"] is False
    assert result["safety"]["merges"] is False
    assert result["safety"]["local_commit_allowed"] is False
    assert "LOCAL_COMMIT_APPROVAL_MISSING" in result["stop_conditions"]


def test_commit_approval_is_still_blocked_in_burn_in(tmp_path: Path) -> None:
    result = build_autonomous_self_build_executor_result(
        _payload(
            tmp_path,
            mode="APPLY",
            human_owner_self_build_approval=COMMIT_APPROVAL,
            allow_local_commit=True,
        )
    )

    assert result["safety"]["pushes"] is False
    assert result["safety"]["creates_pr"] is False
    assert result["safety"]["merges"] is False
    assert "LOCAL_COMMIT_BLOCKED_IN_BURN_IN" in result["stop_conditions"]


def test_no_arbitrary_source_edit_in_burn_in(tmp_path: Path) -> None:
    result = build_autonomous_self_build_executor_result(
        _payload(tmp_path, mode="APPLY", human_owner_self_build_approval=APPLY_APPROVAL, write_ledger=True)
    )

    assert result["safety"]["arbitrary_source_edit"] is False
    assert result["safety"]["mutates_queue"] is False
    assert result["safety"]["mutates_locks"] is False
    assert result["safety"]["mutates_approval"] is False
    assert result["safety"]["mutates_registry"] is False


def test_executed_autonomously_true_in_apply(tmp_path: Path) -> None:
    result = build_autonomous_self_build_executor_result(
        _payload(tmp_path, mode="APPLY", human_owner_self_build_approval=APPLY_APPROVAL, write_ledger=True)
    )

    assert result["executed_autonomously"] is True
    assert result["safety"]["self_build_allowed"] is True
