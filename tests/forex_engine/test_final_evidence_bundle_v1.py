from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.evidence_milestone_selector_v1 import EVIDENCE_MILESTONE_COMPLETE  # noqa: E402
from automation.forex_engine.final_closure_evidence_v1 import (  # noqa: E402
    FINAL_CLOSURE_BLOCKED,
    FINAL_CLOSURE_REVIEW_READY,
)
from automation.forex_engine.final_evidence_bundle_v1 import (  # noqa: E402
    EVIDENCE_CHAIN_STAGE_ORDER,
    FINAL_EVIDENCE_CHAIN_BLOCKED,
    FINAL_EVIDENCE_CHAIN_REVIEW_READY,
    FINAL_EVIDENCE_BUNDLE_BLOCKED,
    FINAL_EVIDENCE_BUNDLE_REVIEW_READY,
    build_final_evidence_bundle,
    build_replay_walkforward_profitability_evidence_chain,
    result_to_jsonable_dict,
    result_to_operator_text,
    write_final_evidence_report,
)
from automation.forex_engine.observation_evidence_intake_v1 import (  # noqa: E402
    SUPERVISED_OBSERVATION_READY,
)
from automation.forex_engine.persistent_profitability_evidence_v1 import (  # noqa: E402
    PERSISTENT_PROFITABILITY_READY,
)
from automation.forex_engine.replay_proof_evidence_v1 import REPLAY_PROOF_READY  # noqa: E402
from automation.forex_engine.walk_forward_oos_evidence_v1 import WALK_FORWARD_OOS_READY  # noqa: E402


PROTECTED_FLAGS = (
    "broker_execution_allowed",
    "live_trading_allowed",
    "order_submission_allowed",
    "credential_access_allowed",
    "account_access_allowed",
    "dashboard_execution_authority",
    "owner_approval_created",
)


def assert_permissions_false(result: dict) -> None:
    for flag in PROTECTED_FLAGS:
        assert result[flag] is False
        assert result["permissions"][flag] is False


def test_final_bundle_consumes_ready_intakes_but_keeps_final_review_blocked(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    _write_ready_report_set(report_root)

    result = build_final_evidence_bundle(report_root)

    assert result["status"] == FINAL_EVIDENCE_BUNDLE_BLOCKED
    assert result["program_status"] == "CONTINUE_READY"
    assert result["intakes"]["replay"]["status"] == REPLAY_PROOF_READY
    assert result["intakes"]["walk_forward"]["status"] == WALK_FORWARD_OOS_READY
    assert result["intakes"]["profitability"]["status"] == PERSISTENT_PROFITABILITY_READY
    assert result["intakes"]["observation"]["status"] == SUPERVISED_OBSERVATION_READY
    assert result["final_closure_result"]["final_closure_status"] == FINAL_CLOSURE_BLOCKED
    assert any("sanitized_broker_readonly_evidence" in item for item in result["remaining_evidence"])
    assert any("owner_review_evidence" in item for item in result["remaining_evidence"])
    assert any("validator_evidence" in item for item in result["remaining_evidence"])
    assert_permissions_false(result)


def test_final_bundle_consumes_owner_and_validator_reports_but_keeps_broker_readonly_blocked(
    tmp_path: Path,
) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    _write_ready_report_set(report_root)
    _write_owner_review_report(report_root)
    _write_validator_report(report_root)
    _write_blocked_broker_readonly_report(report_root)

    result = build_final_evidence_bundle(report_root)
    final_readiness = result["closure_inputs"]["final_readiness_evidence"]
    auxiliary = result["final_readiness_auxiliary_evidence"]

    assert result["status"] == FINAL_EVIDENCE_BUNDLE_BLOCKED
    assert auxiliary["owner_review_evidence"]["ready"] is True
    assert auxiliary["validator_evidence"]["ready"] is True
    assert auxiliary["sanitized_broker_readonly_evidence"]["ready"] is False
    assert "owner_review_evidence" not in final_readiness["missing_evidence"]
    assert "validator_evidence" not in final_readiness["missing_evidence"]
    assert "sanitized_broker_readonly_evidence" in final_readiness["missing_evidence"]
    assert any("broker_live_read_only_source_type" in item for item in result["remaining_evidence"])
    assert_permissions_false(result)


def test_final_bundle_discovers_auxiliary_reports_by_content(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    _write_ready_report_set(report_root)
    _write_dynamic_owner_review_report(report_root)
    _write_dynamic_validator_report(report_root)
    _write_dynamic_broker_readonly_report(report_root)

    result = build_final_evidence_bundle(report_root)
    auxiliary = result["final_readiness_auxiliary_evidence"]

    assert result["status"] == FINAL_EVIDENCE_BUNDLE_REVIEW_READY
    assert result["program_status"] == "PROGRAM_COMPLETE"
    assert any("AIOS_FOREX_DYNAMIC_OWNER_SOURCE_V1.md" in item for item in auxiliary["owner_review_evidence"]["source_files"])
    assert any("AIOS_FOREX_DYNAMIC_VALIDATOR_SOURCE_V1.md" in item for item in auxiliary["validator_evidence"]["source_files"])
    assert any(
        "AIOS_FOREX_DYNAMIC_BROKER_READONLY_SOURCE_V1.md" in item
        for item in auxiliary["sanitized_broker_readonly_evidence"]["source_files"]
    )
    assert_permissions_false(result)


def test_end_to_end_chain_proves_ready_path_and_required_fail_closed_cases(tmp_path: Path) -> None:
    ready_root = tmp_path / "ready"
    _write_complete_chain_report_set(ready_root)

    ready = build_replay_walkforward_profitability_evidence_chain(ready_root)

    assert ready["status"] == FINAL_EVIDENCE_CHAIN_REVIEW_READY
    assert ready["chain_integrated_end_to_end"] is True
    assert ready["deterministic_sample_only"] is True
    assert ready["real_profit_proving"] is False
    assert ready["canonical_entrypoint"] == "build_replay_walkforward_profitability_evidence_chain"
    assert ready["canonical_final_output"] == "final_closure_result"
    assert ready["stage_order"] == list(EVIDENCE_CHAIN_STAGE_ORDER)
    assert ready["final_closure_result"]["final_closure_status"] == FINAL_CLOSURE_REVIEW_READY
    assert ready["stage_results"]["final_evidence_bundle"]["status"] == FINAL_EVIDENCE_BUNDLE_REVIEW_READY
    assert ready["stage_results"]["evidence_milestone_selector"]["next_evidence_milestone"] == "final_closure_evidence"
    assert ready["final_evidence_milestone_result"]["status"] == EVIDENCE_MILESTONE_COMPLETE
    assert ready["final_evidence_milestone_result"]["remaining_evidence_milestones"] == []
    assert_permissions_false(ready)

    scenarios = {
        "insufficient_replay_proof": (
            lambda root: _replace_report_value(
                root / "AIOS_FOREX_SESSION_REPLAY_V1_REPORT.md",
                "mismatch_count: 0",
                "mismatch_count: 1",
            ),
            "replay mismatches are present",
        ),
        "insufficient_walk_forward_oos_proof": (
            lambda root: _replace_report_value(
                root / "AIOS_FOREX_WALK_FORWARD_DEPTH_PACKET_R_V1_REPORT.md",
                "oos_segments_passed: 3",
                "oos_segments_passed: 1",
            ),
            "OOS pass rate is below threshold",
        ),
        "insufficient_profitability_proof": (
            lambda root: _replace_report_value(
                root / "AIOS_FOREX_PROFITABILITY_VERDICT_V1.md",
                "expectancy: 0.40",
                "expectancy: 0.00",
            ),
            "expectancy is below threshold",
        ),
        "missing_22h6d_observation": (
            lambda root: (root / "AIOS_FOREX_TRUSTED_PROFIT_22_6_READINESS_V1.md").unlink(),
            "missing evidence: twenty_two_hour_six_day_observation",
        ),
        "unsafe_broker_live_credential_account_flags": (
            lambda root: _append_unsafe_source_fields(root / "AIOS_FOREX_SESSION_REPLAY_V1_REPORT.md"),
            "broker_execution_allowed is unsafe evidence source data",
        ),
    }
    for name, (mutate, expected_blocker) in scenarios.items():
        report_root = tmp_path / name
        _write_complete_chain_report_set(report_root)
        mutate(report_root)

        result = build_replay_walkforward_profitability_evidence_chain(report_root)
        blockers = "\n".join(str(item) for item in result["blockers"])

        assert result["status"] == FINAL_EVIDENCE_CHAIN_BLOCKED
        assert result["final_closure_result"]["final_closure_status"] == FINAL_CLOSURE_BLOCKED
        assert expected_blocker in blockers
        assert_permissions_false(result)


def test_final_bundle_report_contains_packet_headings(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    _write_ready_report_set(report_root)
    bundle = build_final_evidence_bundle(report_root)
    report_path = tmp_path / "AIOS_FOREX_REAL_EVIDENCE_INTAKE_V1_REPORT.md"

    written = write_final_evidence_report(bundle, report_path)

    text = written.read_text(encoding="utf-8")
    assert "## SUMMARY" in text
    assert "## DISCOVERED EVIDENCE" in text
    assert "## FINAL BUNDLE STATUS" in text
    assert "## STATUS:" in text
    assert "populated after validator execution" not in text
    assert "none recorded in generated report" not in text
    assert result_to_jsonable_dict(bundle)["status"] == FINAL_EVIDENCE_BUNDLE_BLOCKED
    assert "program_status: CONTINUE_READY" in result_to_operator_text(bundle)


def test_final_bundle_next_milestone_keeps_chain_order(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()

    result = build_final_evidence_bundle(report_root)

    assert result["status"] == FINAL_EVIDENCE_BUNDLE_BLOCKED
    assert result["next_unfinished_milestone"] == "collect walk-forward and out-of-sample segment counts"
    assert_permissions_false(result)


def _write_complete_chain_report_set(report_root: Path) -> None:
    report_root.mkdir()
    _write_ready_report_set(report_root)
    _write_dynamic_owner_review_report(report_root)
    _write_dynamic_validator_report(report_root)
    _write_dynamic_broker_readonly_report(report_root)


def _replace_report_value(path: Path, old: str, new: str) -> None:
    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


def _append_unsafe_source_fields(path: Path) -> None:
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\n"
        + "\n".join(
            [
                "- broker_execution_allowed: true",
                "- live_trading_allowed: true",
                "- credential_access_allowed: true",
                "- account_id: not-allowed",
            ]
        ),
        encoding="utf-8",
    )


def _write_ready_report_set(report_root: Path) -> None:
    (report_root / "AIOS_FOREX_SESSION_REPLAY_V1_REPORT.md").write_text(
        "\n".join(
            [
                "- replay_id: replay-direct-001",
                "- run_count: 2",
                "- event_count: 30",
                "- mismatch_count: 0",
                "- deterministic_replay: true",
                "- sanitized: true",
                "- evidence_age_days: 1",
                "- max_evidence_age_days: 7",
            ]
        ),
        encoding="utf-8",
    )
    (report_root / "AIOS_FOREX_WALK_FORWARD_DEPTH_PACKET_R_V1_REPORT.md").write_text(
        "\n".join(
            [
                "- windows_total: 4",
                "- windows_passed: 4",
                "- oos_segments_total: 3",
                "- oos_segments_passed: 3",
                "- min_pass_rate: 0.75",
                "- max_drawdown: 0.02",
                "- max_allowed_drawdown: 0.05",
                "- sanitized: true",
                "- evidence_age_days: 1",
                "- max_evidence_age_days: 7",
            ]
        ),
        encoding="utf-8",
    )
    (report_root / "AIOS_FOREX_PROFITABILITY_VERDICT_V1.md").write_text(
        "\n".join(
            [
                "- closed_trade_count: 40",
                "- min_closed_trade_count: 30",
                "- expectancy: 0.40",
                "- min_expectancy: 0.05",
                "- profit_factor: 1.50",
                "- min_profit_factor: 1.25",
                "- max_drawdown: 0.02",
                "- max_allowed_drawdown: 0.05",
                "- consecutive_profitable_periods: 5",
                "- min_profitable_periods: 4",
                "- after_costs: true",
                "- sanitized: true",
                "- evidence_age_days: 1",
                "- max_evidence_age_days: 7",
            ]
        ),
        encoding="utf-8",
    )
    (report_root / "AIOS_FOREX_TRUSTED_PROFIT_22_6_READINESS_V1.md").write_text(
        "\n".join(
            [
                "- observed_hours: 23",
                "- required_hours: 22",
                "- observed_sessions: 6",
                "- required_sessions: 6",
                "- observed_days: 6",
                "- required_days: 6",
                "- interruption_count: 0",
                "- max_interruption_count: 2",
                "- manual_override_count: 0",
                "- max_manual_override_count: 1",
                "- sanitized: true",
                "- evidence_age_days: 1",
                "- max_evidence_age_days: 7",
            ]
        ),
        encoding="utf-8",
    )


def _write_owner_review_report(report_root: Path) -> None:
    (report_root / "AIOS_FOREX_SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_V1.md").write_text(
        "\n".join(
            [
                "# AIOS Forex Supervised Demo Owner Approval Packet V1",
                "",
                "- Owner packet status: `SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_READY_FOR_OWNER_REVIEW`",
                "- No broker action is authorized by Codex.",
                "- Anthony may review the local packet manually.",
            ]
        ),
        encoding="utf-8",
    )


def _write_validator_report(report_root: Path) -> None:
    (report_root / "AIOS_FOREX_FINAL_BUNDLE_REPAIR_V1_REPORT.md").write_text(
        "\n".join(
            [
                "# AIOS Forex Final Bundle Repair V1 Report",
                "",
                "## VALIDATORS RUN",
                "- `python scripts/forex_delivery/run_final_evidence_bundle_v1.py --write-report --json`",
                "",
                "## VALIDATORS PASSED",
                "- Final evidence bundle command: passed.",
                "- `git diff --check`: PASS.",
            ]
        ),
        encoding="utf-8",
    )


def _write_blocked_broker_readonly_report(report_root: Path) -> None:
    (report_root / "AIOS_FOREX_READ_ONLY_EVIDENCE_APPROVAL_AND_RECONCILIATION_DRY_RUN_V1.md").write_text(
        "\n".join(
            [
                "# AIOS Forex Read-Only Evidence Approval And Reconciliation Dry Run V1",
                "",
                "## Approval Status",
                "- READ_ONLY_EVIDENCE_APPROVED_FOR_FUTURE_LIVE_REVIEW: False",
                "- live_execution_allowed: False",
                "- source_type: fixture",
                "- source_label: FIXTURE_NOT_LIVE",
                "",
                "## Reconciliation Status",
                "- broker_account_reachable: False",
                "- open_positions_reconciled: False",
                "- daily_pl_available: False",
                "- realized_pl_available: False",
                "- unrealized_pl_available: False",
                "- margin_risk_available: False",
                "- trading_history_writeback_verified: False",
                "",
                "## Evidence Missing",
                "- broker_live_read_only_source_type",
                "- sanitized_broker_source_label",
                "",
                "## Blockers Remaining",
                "- read_only_bridge_fixture_source_not_live_permitted",
            ]
        ),
        encoding="utf-8",
    )


def _write_dynamic_owner_review_report(report_root: Path) -> None:
    (report_root / "AIOS_FOREX_DYNAMIC_OWNER_SOURCE_V1.md").write_text(
        "\n".join(
            [
                "# Dynamic Owner Review Source",
                "",
                "- Owner packet status: `SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_READY_FOR_OWNER_REVIEW`",
                "- Anthony may review the local packet manually.",
                "- This does not authorize execution.",
            ]
        ),
        encoding="utf-8",
    )


def _write_dynamic_validator_report(report_root: Path) -> None:
    (report_root / "AIOS_FOREX_DYNAMIC_VALIDATOR_SOURCE_V1.md").write_text(
        "\n".join(
            [
                "# Dynamic Validator Source",
                "",
                "## VALIDATORS RUN",
                "- `python -m pytest tests/forex_engine -q`",
                "",
                "## VALIDATORS PASSED",
                "- `python -m pytest tests/forex_engine -q`: PASS.",
                "- `git diff --check`: PASS.",
            ]
        ),
        encoding="utf-8",
    )


def _write_dynamic_broker_readonly_report(report_root: Path) -> None:
    (report_root / "AIOS_FOREX_DYNAMIC_BROKER_READONLY_SOURCE_V1.md").write_text(
        "\n".join(
            [
                "# Dynamic Broker Read-Only Source",
                "",
                "- READ_ONLY_EVIDENCE_APPROVED_FOR_FUTURE_LIVE_REVIEW: True",
                "- source_type: broker read-only sanitized evidence",
                "- source_label: SANITIZED_DEMO_READONLY",
                "- broker_account_reachable: True",
                "- open_positions_reconciled: True",
                "- daily_pl_available: True",
                "- realized_pl_available: True",
                "- unrealized_pl_available: True",
                "- margin_risk_available: True",
                "- trading_history_writeback_verified: True",
            ]
        ),
        encoding="utf-8",
    )
