from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.walk_forward_evidence_intake_v1 import (  # noqa: E402
    intake_walk_forward_evidence,
    result_to_jsonable_dict,
    result_to_operator_text,
)
from automation.forex_engine.walk_forward_oos_evidence_v1 import (  # noqa: E402
    WALK_FORWARD_OOS_INCOMPLETE,
    WALK_FORWARD_OOS_READY,
)


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


def test_walk_forward_intake_accepts_complete_direct_evidence(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
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

    result = intake_walk_forward_evidence(report_root)

    assert result["status"] == WALK_FORWARD_OOS_READY
    assert result["normalized_summary"]["windows_total"] == 4
    assert result["normalized_summary"]["oos_segments_total"] == 3
    assert result["parse_notes"] == []
    assert_permissions_false(result)


def test_walk_forward_intake_requires_oos_segment_counts(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "AIOS_FOREX_WALK_FORWARD_WINDOW_MATRIX_V1.md").write_text(
        "\n".join(
            [
                "- total_windows: 4",
                "- passing_windows: 1",
                "- min_pass_rate: 1.0",
                "- max_drawdown: 75.20",
                "- max_allowed_drawdown: 8.0",
                "- sanitized: true",
                "- evidence_age_days: 1",
                "- max_evidence_age_days: 7",
            ]
        ),
        encoding="utf-8",
    )

    result = intake_walk_forward_evidence(report_root)

    assert result["status"] == WALK_FORWARD_OOS_INCOMPLETE
    assert "oos_segments_total" in result["missing_fields"]
    assert any("out-of-sample segment counts" in note for note in result["parse_notes"])
    assert_permissions_false(result)


def test_walk_forward_intake_accepts_oos_fold_aliases(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "AIOS_FOREX_WALK_FORWARD_DEPTH_PACKET_R_V1_REPORT.md").write_text(
        "\n".join(
            [
                "- total_windows: 3",
                "- passing_windows: 3",
                "- out_of_sample_folds: 3",
                "- out_of_sample_folds_passed: 3",
                "- min_pass_rate: 1.0",
                "- max_drawdown: 0.02",
                "- max_allowed_drawdown: 0.05",
                "- sanitized: true",
                "- evidence_age_days: 1",
                "- max_evidence_age_days: 7",
            ]
        ),
        encoding="utf-8",
    )

    result = intake_walk_forward_evidence(report_root)

    assert result["status"] == WALK_FORWARD_OOS_READY
    assert result["normalized_summary"]["oos_segments_total"] == 3
    assert result["normalized_summary"]["oos_segments_passed"] == 3
    assert result["parse_notes"] == []
    assert_permissions_false(result)


def test_walk_forward_intake_accepts_combined_oos_segment_counts(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "AIOS_FOREX_WALK_FORWARD_DEPTH_PACKET_R_V1_REPORT.md").write_text(
        "\n".join(
            [
                "- total_windows: 3",
                "- passing_windows: 3",
                "- OOS segments: 3/3 passed",
                "- min_pass_rate: 1.0",
                "- max_drawdown: 0.02",
                "- max_allowed_drawdown: 0.05",
                "- sanitized: true",
                "- evidence_age_days: 1",
                "- max_evidence_age_days: 7",
            ]
        ),
        encoding="utf-8",
    )

    result = intake_walk_forward_evidence(report_root)

    assert result["status"] == WALK_FORWARD_OOS_READY
    assert result["normalized_summary"]["oos_segments_total"] == 3
    assert result["normalized_summary"]["oos_segments_passed"] == 3
    assert result["parse_notes"] == []
    assert_permissions_false(result)


def test_walk_forward_intake_counts_oos_segment_table_rows(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "AIOS_FOREX_WALK_FORWARD_WINDOW_MATRIX_V1.md").write_text(
        "\n".join(
            [
                "| oos_segment_id | status | blockers |",
                "|---|---|---|",
                "| oos-01 | pass | none |",
                "| oos-02 | fail | drawdown |",
                "| oos-03 | ready | none |",
                "- windows_total: 3",
                "- windows_passed: 2",
                "- min_pass_rate: 0.5",
                "- max_drawdown: 0.02",
                "- max_allowed_drawdown: 0.05",
                "- sanitized: true",
                "- evidence_age_days: 1",
                "- max_evidence_age_days: 7",
            ]
        ),
        encoding="utf-8",
    )

    result = intake_walk_forward_evidence(report_root)

    assert result["status"] == WALK_FORWARD_OOS_READY
    assert result["normalized_summary"]["oos_segments_total"] == 3
    assert result["normalized_summary"]["oos_segments_passed"] == 2
    assert result["parse_notes"] == []
    assert_permissions_false(result)


def test_walk_forward_intake_discovers_matching_report_by_content(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "AIOS_FOREX_CUSTOM_EVIDENCE_SOURCE_V1.md").write_text(
        "\n".join(
            [
                "Walk-forward and OOS evidence summary.",
                "- windows_total: 5",
                "- windows_passed: 5",
                "- oos_segments_total: 4",
                "- oos_segments_passed: 4",
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

    result = intake_walk_forward_evidence(report_root)

    assert result["status"] == WALK_FORWARD_OOS_READY
    assert "Reports/forex_delivery" not in result["source_files"][0]
    assert any("AIOS_FOREX_CUSTOM_EVIDENCE_SOURCE_V1.md" in item for item in result["source_files"])
    assert result["normalized_summary"]["oos_segments_total"] == 4
    assert_permissions_false(result)


def test_walk_forward_intake_counts_window_table_rows(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "AIOS_FOREX_WALK_FORWARD_WINDOW_MATRIX_V1.md").write_text(
        "\n".join(
            [
                "| window_id | promotion status | blocker reasons | max drawdown |",
                "|---|---|---|---:|",
                "| wf-01 | PROFIT_OBJECTIVE_READY | none | 0.00 |",
                "| wf-02 | REJECT_LOW_PROFIT_FACTOR | low_profit_factor | 4.00 |",
                "- oos_segments_total: 2",
                "- oos_segments_passed: 1",
                "- min_pass_rate: 0.5",
                "- max_allowed_drawdown: 5.0",
                "- sanitized: true",
                "- evidence_age_days: 1",
                "- max_evidence_age_days: 7",
            ]
        ),
        encoding="utf-8",
    )

    result = intake_walk_forward_evidence(report_root)

    assert result["status"] == WALK_FORWARD_OOS_READY
    assert result["normalized_summary"]["windows_total"] == 2
    assert result["normalized_summary"]["windows_passed"] == 1
    assert result["normalized_summary"]["max_drawdown"] == 4
    assert_permissions_false(result)


def test_walk_forward_intake_operator_outputs_are_stable(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "AIOS_FOREX_WALK_FORWARD_DEPTH_PACKET_R_V1_REPORT.md").write_text(
        "\n".join(
            [
                "- windows_total: 1",
                "- windows_passed: 1",
                "- oos_segments_total: 1",
                "- oos_segments_passed: 1",
                "- min_pass_rate: 1.0",
                "- max_drawdown: 0",
                "- max_allowed_drawdown: 1",
                "- sanitized: true",
                "- evidence_age_days: 0",
                "- max_evidence_age_days: 1",
            ]
        ),
        encoding="utf-8",
    )

    result = intake_walk_forward_evidence(report_root)

    assert result_to_jsonable_dict(result)["status"] == WALK_FORWARD_OOS_READY
    assert "AIOS Forex Walk Forward Evidence Intake V1" in result_to_operator_text(result)
    assert_permissions_false(result)
