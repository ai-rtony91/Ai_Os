from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.master_evidence_closure_v1 import (  # noqa: E402
    MASTER_EVIDENCE_PARTIAL,
    MASTER_EVIDENCE_READY,
    PROTECTED_PERMISSION_FLAGS,
    build_master_evidence_closure,
    master_evidence_closure_to_markdown,
    result_to_jsonable_dict,
    result_to_operator_text,
)
from automation.forex_engine.final_evidence_bundle_v1 import build_final_evidence_bundle  # noqa: E402


def assert_permissions_false(result: dict) -> None:
    for flag in PROTECTED_PERMISSION_FLAGS:
        assert result[flag] is False
        assert result["permissions"][flag] is False


def test_master_closure_reports_partial_for_missing_external_evidence(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    _write_replay_only(report_root)

    result = build_master_evidence_closure(report_root, ROOT)

    assert result["status"] == MASTER_EVIDENCE_PARTIAL
    assert result["readiness_state"] == "PARTIAL_EXTERNAL_EVIDENCE_REQUIRED"
    assert any(item.startswith("walk_forward_oos.") for item in result["missing_external_evidence"])
    assert any(item.startswith("observation_22h6d.") for item in result["missing_external_evidence"])
    assert any(item.startswith("broker_readonly.") for item in result["missing_external_evidence"])
    assert "git add ." not in result["protected_action_handoff"]["exact_git_add_command"]
    assert_permissions_false(result)


def test_master_closure_ready_requires_complete_sanitized_chain(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    _write_complete_evidence(report_root)

    result = build_master_evidence_closure(report_root, ROOT)

    assert result["status"] == MASTER_EVIDENCE_READY
    assert result["readiness_state"] == "READY_FOR_OWNER_REVIEW_ONLY"
    assert result["missing_external_evidence"] == []
    assert "No broker/API access" in result["exact_pr_body"]
    assert "Owner review only" in result["exact_pr_body"]
    assert_permissions_false(result)


def test_master_closure_markdown_contains_required_handoff_and_schema(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    _write_replay_only(report_root)

    result = build_master_evidence_closure(
        report_root,
        ROOT,
        metadata={
            "branch": "lane/forex-master-evidence-closure-60k-v1",
            "base_commit": "base",
            "current_commit": "head",
            "pr_baseline": "9cdf16b2 fix(forex): preserve integration hardening updates (#1152)",
            "generated_at": "2026-06-27T00:00:00-04:00",
        },
        validation_results=["python -m pytest tests/forex_engine/test_master_evidence_closure_v1.py -q -> PASS"],
    )

    text = master_evidence_closure_to_markdown(result)

    assert "## Evidence Categories Inspected" in text
    assert "## Missing Evidence" in text
    assert "AIOS_FOREX_MASTER_EVIDENCE_INPUT.v1.schema.json" in text
    assert "automation/forex_engine/final_evidence_bundle_v1.py" in text
    assert "git diff --cached --check" in text
    assert "git add ." not in text
    assert "--delete-branch" not in text
    assert "git reset --hard" not in text
    assert "git pull --ff-only origin main" in text
    assert "no broker/API access was performed" in text


def test_master_closure_outputs_are_stable_and_json_schema_parses() -> None:
    result = build_master_evidence_closure(
        Path("Reports/forex_delivery"),
        ROOT,
        metadata={"generated_at": "2026-06-27T00:00:00-04:00"},
    )
    schema = json.loads(
        (ROOT / "schemas/aios/forex/AIOS_FOREX_MASTER_EVIDENCE_INPUT.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )

    assert result_to_jsonable_dict(result)["closure_version"] == "master_evidence_closure_v1"
    assert "AIOS Forex Master Evidence Closure V1" in result_to_operator_text(result)
    assert schema["title"] == "AIOS Forex Master Evidence Input V1"
    assert schema["properties"]["safety"]["properties"]["broker_execution_allowed"]["const"] is False
    assert_permissions_false(result)


def test_master_aggregate_report_is_not_reingested_as_broker_evidence(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    _write_complete_evidence(report_root)
    (report_root / "AIOS_FOREX_MASTER_EVIDENCE_CLOSURE_60K_V1_REPORT.md").write_text(
        "\n".join(
            [
                "# Aggregate report, not source evidence",
                "- source_type: fixture",
                "- broker_account_reachable: False",
                "- trading_history_writeback_verified: False",
                "- secret_or_private_identifier_marker_present",
            ]
        ),
        encoding="utf-8",
    )

    result = build_final_evidence_bundle(report_root)
    broker = result["final_readiness_auxiliary_evidence"]["sanitized_broker_readonly_evidence"]

    assert broker["ready"] is True
    assert not any("MASTER_EVIDENCE_CLOSURE" in item for item in broker["source_files"])
    for flag in PROTECTED_PERMISSION_FLAGS:
        if flag in result:
            assert result[flag] is False


def test_absent_account_id_marker_does_not_hard_block_source_safety(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    _write_complete_evidence(report_root)
    (report_root / "AIOS_FOREX_DEMO_READINESS_PROFIT_TRUST_SPINE_V1.md").write_text(
        "\n".join(
            [
                "Persistent profitability evidence summary.",
                "- account_id: not included",
                "- credential_access_allowed: false",
                "- live_trading_allowed: false",
            ]
        ),
        encoding="utf-8",
    )

    result = build_master_evidence_closure(report_root, ROOT)

    assert result["status"] == MASTER_EVIDENCE_READY
    assert not any("account_id is unsafe evidence source data" in item for item in result["missing_external_evidence"])
    assert_permissions_false(result)


def _write_replay_only(report_root: Path) -> None:
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


def _write_complete_evidence(report_root: Path) -> None:
    _write_replay_only(report_root)
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
    (report_root / "AIOS_FOREX_DYNAMIC_OWNER_SOURCE_V1.md").write_text(
        "\n".join(
            [
                "- Owner packet status: `SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_READY_FOR_OWNER_REVIEW`",
                "- Anthony may review the local packet manually.",
                "- This does not authorize execution.",
            ]
        ),
        encoding="utf-8",
    )
    (report_root / "AIOS_FOREX_DYNAMIC_VALIDATOR_SOURCE_V1.md").write_text(
        "\n".join(
            [
                "## VALIDATORS RUN",
                "- `python -m pytest tests/forex_engine -q`",
                "## VALIDATORS PASSED",
                "- `python -m pytest tests/forex_engine -q`: PASS.",
            ]
        ),
        encoding="utf-8",
    )
    (report_root / "AIOS_FOREX_DYNAMIC_BROKER_READONLY_SOURCE_V1.md").write_text(
        "\n".join(
            [
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
