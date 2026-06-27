from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.persistent_profitability_evidence_v1 import (  # noqa: E402
    PERSISTENT_PROFITABILITY_BLOCKED,
    PERSISTENT_PROFITABILITY_INCOMPLETE,
    PERSISTENT_PROFITABILITY_READY,
)
from automation.forex_engine.profitability_evidence_intake_v1 import (  # noqa: E402
    intake_profitability_evidence,
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


def test_profitability_intake_accepts_complete_direct_evidence(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
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

    result = intake_profitability_evidence(report_root)

    assert result["status"] == PERSISTENT_PROFITABILITY_READY
    assert result["normalized_summary"]["closed_trade_count"] == 40
    assert result["normalized_summary"]["after_costs"] is True
    assert result["parse_notes"] == []
    assert_permissions_false(result)


def test_profitability_intake_does_not_invent_missing_persistence(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "AIOS_FOREX_PROFITABILITY_VERDICT_V1.md").write_text(
        "\n".join(
            [
                "Measurable paper edge exists on 3 closed trades.",
                "- best candidate expectancy: 200",
                "- actual profit factor: 999",
                "- actual drawdown: 0",
                "This report does not call brokers and does not use credentials.",
            ]
        ),
        encoding="utf-8",
    )
    (report_root / "AIOS_FOREX_PROFIT_PROOF_LEDGER_V1.md").write_text(
        "\n".join(
            [
                "Minimum total trades default: 30",
                "Minimum profit factor default: 1.25",
                "Maximum drawdown default: 0.05",
                "Positive expectancy required.",
            ]
        ),
        encoding="utf-8",
    )

    result = intake_profitability_evidence(report_root)

    assert result["status"] == PERSISTENT_PROFITABILITY_INCOMPLETE
    assert "after_costs" in result["missing_fields"]
    assert "consecutive_profitable_periods" in result["missing_fields"]
    assert any("after-cost" in note for note in result["parse_notes"])
    assert_permissions_false(result)


def test_profitability_intake_normalizes_proof_gate_default_numbers(tmp_path: Path) -> None:
    accepted_tokens = ("1.25", "1.25.", "1.25,", "1.25%", "`1.25`")
    for index, token in enumerate(accepted_tokens):
        report_root = tmp_path / f"reports_{index}"
        report_root.mkdir()
        (report_root / "AIOS_FOREX_PROFIT_PROOF_LEDGER_V1.md").write_text(
            "\n".join(
                [
                    "Minimum total trades default: 30.",
                    f"Minimum profit factor default: {token}",
                    "Maximum drawdown default: 0.05,",
                    "Positive expectancy required.",
                ]
            ),
            encoding="utf-8",
        )

        result = intake_profitability_evidence(report_root)

        assert result["normalized_summary"]["min_closed_trade_count"] == 30
        assert result["normalized_summary"]["min_profit_factor"] == 1.25
        assert result["normalized_summary"]["max_allowed_drawdown"] == 0.05
        assert result["normalized_summary"]["min_expectancy"] == 0
        assert_permissions_false(result)


def test_profitability_intake_rejects_malformed_proof_gate_default_number(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "AIOS_FOREX_PROFIT_PROOF_LEDGER_V1.md").write_text(
        "\n".join(
            [
                "Minimum total trades default: 30",
                "Minimum profit factor default: 1.25.3",
                "Maximum drawdown default: 0.05",
                "Positive expectancy required.",
            ]
        ),
        encoding="utf-8",
    )

    result = intake_profitability_evidence(report_root)

    assert "min_profit_factor" not in result["normalized_summary"]
    assert result["normalized_summary"]["min_closed_trade_count"] == 30
    assert result["normalized_summary"]["max_allowed_drawdown"] == 0.05
    assert_permissions_false(result)


def test_profitability_intake_consumes_after_cost_pnl_evidence(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
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
                "- sanitized: true",
                "- evidence_age_days: 1",
                "- max_evidence_age_days: 7",
            ]
        ),
        encoding="utf-8",
    )
    (report_root / "AIOS_FOREX_EVIDENCE_DEPTH_QUALITY_GATE_V1.md").write_text(
        "\n".join(
            [
                "- positive_total_net_pnl_after_costs",
                "- Source total net PnL after costs: `30.00`",
            ]
        ),
        encoding="utf-8",
    )

    result = intake_profitability_evidence(report_root)

    assert result["status"] == PERSISTENT_PROFITABILITY_READY
    assert result["normalized_summary"]["after_costs"] is True
    assert_permissions_false(result)


def test_profitability_intake_discovers_matching_report_by_content(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "AIOS_FOREX_CUSTOM_PROOF_SOURCE_V1.md").write_text(
        "\n".join(
            [
                "Persistent profitability evidence summary.",
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

    result = intake_profitability_evidence(report_root)

    assert result["status"] == PERSISTENT_PROFITABILITY_READY
    assert any("AIOS_FOREX_CUSTOM_PROOF_SOURCE_V1.md" in item for item in result["source_files"])
    assert result["normalized_summary"]["consecutive_profitable_periods"] == 5
    assert_permissions_false(result)


def test_profitability_intake_consumes_failing_persistence_window_evidence(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
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
                "- after_costs: true",
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
                "| window_id | expectancy | profit factor | promotion status | blocker reasons |",
                "|---|---:|---:|---|---|",
                "| wf-01 | 200.00 | 999.00 | PROFIT_OBJECTIVE_READY | none |",
                "| wf-02 | -0.80 | 0.93 | REJECT_LOW_PROFIT_FACTOR | negative_expectancy |",
                "| wf-03 | -2.00 | 0.61 | REJECT_LOW_PROFIT_FACTOR | negative_expectancy |",
            ]
        ),
        encoding="utf-8",
    )
    (report_root / "AIOS_FOREX_DEMO_READINESS_PROFIT_TRUST_SPINE_V1.md").write_text(
        "- minimum_walk_forward_folds: 3\n",
        encoding="utf-8",
    )

    result = intake_profitability_evidence(report_root)

    assert result["status"] == PERSISTENT_PROFITABILITY_BLOCKED
    assert result["missing_fields"] == []
    assert result["normalized_summary"]["consecutive_profitable_periods"] == 1
    assert result["normalized_summary"]["min_profitable_periods"] == 3
    assert "profitable periods are below threshold" in result["blockers"]
    assert_permissions_false(result)


def test_profitability_intake_operator_outputs_are_stable(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "AIOS_FOREX_PROFITABILITY_VERDICT_V1.md").write_text(
        "\n".join(
            [
                "- closed_trade_count: 30",
                "- min_closed_trade_count: 30",
                "- expectancy: 1",
                "- min_expectancy: 0",
                "- profit_factor: 2",
                "- min_profit_factor: 1.25",
                "- max_drawdown: 0",
                "- max_allowed_drawdown: 1",
                "- consecutive_profitable_periods: 4",
                "- min_profitable_periods: 4",
                "- after_costs: true",
                "- sanitized: true",
                "- evidence_age_days: 0",
                "- max_evidence_age_days: 1",
            ]
        ),
        encoding="utf-8",
    )

    result = intake_profitability_evidence(report_root)

    assert result_to_jsonable_dict(result)["status"] == PERSISTENT_PROFITABILITY_READY
    assert "AIOS Forex Profitability Evidence Intake V1" in result_to_operator_text(result)
    assert_permissions_false(result)
