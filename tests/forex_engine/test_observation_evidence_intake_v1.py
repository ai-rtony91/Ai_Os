from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.observation_evidence_intake_v1 import (  # noqa: E402
    SUPERVISED_OBSERVATION_INCOMPLETE,
    SUPERVISED_OBSERVATION_READY,
    intake_observation_evidence,
    result_to_jsonable_dict,
    result_to_operator_text,
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


def test_observation_intake_accepts_complete_direct_evidence(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
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

    result = intake_observation_evidence(report_root)

    assert result["status"] == SUPERVISED_OBSERVATION_READY
    assert result["normalized_summary"]["observed_hours"] == 23
    assert result["normalized_summary"]["observed_days"] == 6
    assert result["parse_notes"] == []
    assert_permissions_false(result)


def test_observation_intake_requires_real_observed_window(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "AIOS_FOREX_TRUSTED_PROFIT_22_6_READINESS_V1.md").write_text(
        "\n".join(
            [
                "This is not a trade approval.",
                "Missing minimum 22/6 observation window.",
                "No broker_action_allowed: false",
            ]
        ),
        encoding="utf-8",
    )

    result = intake_observation_evidence(report_root)

    assert result["status"] == SUPERVISED_OBSERVATION_INCOMPLETE
    assert "observed_hours" in result["missing_fields"]
    assert any("minimum 22/6 observation window" in note for note in result["parse_notes"])
    assert_permissions_false(result)


def test_observation_intake_discovers_matching_report_by_content(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "AIOS_FOREX_CUSTOM_OBSERVATION_SOURCE_V1.md").write_text(
        "\n".join(
            [
                "Completed 22H/6D supervised observation evidence.",
                "- observed_hours: 22",
                "- required_hours: 22",
                "- observed_sessions: 6",
                "- required_sessions: 6",
                "- observed_days: 6",
                "- required_days: 6",
                "- interruption_count: 0",
                "- max_interruption_count: 1",
                "- manual_override_count: 0",
                "- max_manual_override_count: 1",
                "- sanitized: true",
                "- evidence_age_days: 1",
                "- max_evidence_age_days: 7",
            ]
        ),
        encoding="utf-8",
    )

    result = intake_observation_evidence(report_root)

    assert result["status"] == SUPERVISED_OBSERVATION_READY
    assert any("AIOS_FOREX_CUSTOM_OBSERVATION_SOURCE_V1.md" in item for item in result["source_files"])
    assert result["normalized_summary"]["observed_sessions"] == 6
    assert_permissions_false(result)


def test_observation_intake_accepts_markdown_table_evidence(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "AIOS_FOREX_TABLE_OBSERVATION_SOURCE_V1.md").write_text(
        "\n".join(
            [
                "# 22H/6D Supervised Observation Evidence",
                "",
                "| Field | Value |",
                "| --- | --- |",
                "| observed hours | 22 |",
                "| required hours | 22 |",
                "| observed sessions | 6 |",
                "| required sessions | 6 |",
                "| observed days | 6 |",
                "| required days | 6 |",
                "| interruptions | 0 |",
                "| interruption limit | 1 |",
                "| manual overrides | 0 |",
                "| manual override limit | 1 |",
                "| freshness age days | 1 |",
                "| freshness limit days | 7 |",
                "",
                "- sanitized: true",
            ]
        ),
        encoding="utf-8",
    )

    result = intake_observation_evidence(report_root)

    assert result["status"] == SUPERVISED_OBSERVATION_READY
    assert result["normalized_summary"]["observed_hours"] == 22
    assert result["normalized_summary"]["interruption_count"] == 0
    assert result["normalized_summary"]["max_manual_override_count"] == 1
    assert result["owner_collection_requirements"] == []
    assert any("AIOS_FOREX_TABLE_OBSERVATION_SOURCE_V1.md" in item for item in result["source_files"])
    assert_permissions_false(result)


def test_observation_intake_ignores_fenced_sample_values(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "AIOS_FOREX_SAMPLE_ONLY_OBSERVATION_SOURCE_V1.md").write_text(
        "\n".join(
            [
                "# 22H/6D Supervised Observation Template",
                "",
                "```text",
                "- observed_hours: 22",
                "- required_hours: 22",
                "- observed_sessions: 6",
                "- required_sessions: 6",
                "- observed_days: 6",
                "- required_days: 6",
                "- interruption_count: 0",
                "- max_interruption_count: 1",
                "- manual_override_count: 0",
                "- max_manual_override_count: 1",
                "- sanitized: true",
                "- evidence_age_days: 1",
                "- max_evidence_age_days: 7",
                "```",
                "",
                "This sample is not collected observation evidence.",
            ]
        ),
        encoding="utf-8",
    )

    result = intake_observation_evidence(report_root)

    assert result["status"] == SUPERVISED_OBSERVATION_INCOMPLETE
    assert "observed_hours" in result["missing_fields"]
    assert "observed_hours" not in result["normalized_summary"]
    assert any("observed_hours" in item for item in result["owner_collection_requirements"])
    assert_permissions_false(result)


def test_observation_intake_operator_outputs_are_stable(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "AIOS_FOREX_TRUSTED_PROFIT_22_6_READINESS_V1.md").write_text(
        "\n".join(
            [
                "- observed_hours: 22",
                "- required_hours: 22",
                "- observed_sessions: 6",
                "- required_sessions: 6",
                "- observed_days: 6",
                "- required_days: 6",
                "- interruption_count: 0",
                "- max_interruption_count: 0",
                "- manual_override_count: 0",
                "- max_manual_override_count: 0",
                "- sanitized: true",
                "- evidence_age_days: 0",
                "- max_evidence_age_days: 1",
            ]
        ),
        encoding="utf-8",
    )

    result = intake_observation_evidence(report_root)

    assert result_to_jsonable_dict(result)["status"] == SUPERVISED_OBSERVATION_READY
    assert "AIOS Forex Observation Evidence Intake V1" in result_to_operator_text(result)
    assert_permissions_false(result)
