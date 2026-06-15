from __future__ import annotations

from pathlib import Path

from automation.forex_engine import opportunity_capture
from automation.forex_engine import paper_forward_evidence_v2


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "opportunity_capture.py"


def test_calculates_capture_rate() -> None:
    assert opportunity_capture.calculate_capture_rate(10, 8, missed_count=2) == 66.6667


def test_calculates_opportunity_capture_from_v2_evidence() -> None:
    bundle = paper_forward_evidence_v2.build_paper_forward_evidence_v2()
    report = opportunity_capture.calculate_opportunity_capture(bundle)

    assert report["mode"] == "PAPER_ONLY"
    assert report["total_intents"] > 0
    assert report["simulated_ledger_entries"] == report["total_intents"]
    assert report["missed_signal_count"] >= 0
    assert report["missed_pnl_estimate"] >= 0
    assert report["starting_balance"] == 500.0
    assert report["ending_balance"] == report["starting_balance"] + report["aggregate_paper_pnl"]
    assert report["return_pct"] > 0
    assert report["risk_adjusted_return"] > 0
    assert report["cost_drag_usd"] >= 0
    assert report["cost_drag_pct"] >= 0
    assert report["exit_efficiency_pct"] >= 0
    assert report["position_efficiency_pct"] >= 0
    assert report["opportunity_quality_score"] >= 0
    assert report["live_ready"] is False
    assert report["protected_gate_required"] is True


def test_estimates_missed_opportunities_and_pnl_conservatively() -> None:
    per_fixture = [
        {"fixture_id": "A", "intent_count": 3, "ledger_entry_count": 2, "paper_pnl_usd": 30.0},
        {"fixture_id": "B", "intent_count": 2, "ledger_entry_count": 0, "paper_pnl_usd": 0.0},
    ]

    missed = opportunity_capture.estimate_missed_opportunities(per_fixture)
    missed_pnl = opportunity_capture.calculate_missed_pnl_estimate(per_fixture)

    assert missed["missed_signal_count"] == 4
    assert missed["estimated"] is True
    assert missed_pnl == 30.0


def test_calculates_cost_drag_exit_efficiency_and_position_efficiency() -> None:
    summary = {
        "simulated_ledger_entries": 10,
        "aggregate_paper_pnl": 100.0,
        "estimated_round_turn_cost_usd": 0.25,
    }
    per_fixture = [
        {"ledger_entry_count": 4, "paper_pnl_usd": 30.0},
        {"ledger_entry_count": 2, "paper_pnl_usd": -10.0},
    ]

    cost_drag = opportunity_capture.calculate_cost_drag(summary)
    exit_efficiency = opportunity_capture.calculate_exit_efficiency(per_fixture)
    position_efficiency = opportunity_capture.calculate_position_efficiency(per_fixture)

    assert cost_drag["cost_drag_usd"] == 2.5
    assert cost_drag["cost_drag_pct"] > 0
    assert exit_efficiency["exit_efficiency_pct"] == 75.0
    assert position_efficiency["position_efficiency_pct"] == 100.0


def test_handles_missing_fields_conservatively() -> None:
    report = opportunity_capture.calculate_opportunity_capture({})

    assert report["estimated"] is True
    assert report["starting_balance"] == 500.0
    assert report["ending_balance"] == 500.0
    assert report["return_pct"] == 0.0
    assert report["risk_adjusted_return"] == 0.0
    assert report["blockers"]
    assert report["live_ready"] is False


def test_opportunity_capture_summary_is_compact_and_live_blocked() -> None:
    bundle = paper_forward_evidence_v2.build_paper_forward_evidence_v2()
    report = opportunity_capture.calculate_opportunity_capture(bundle)
    summary = opportunity_capture.opportunity_capture_summary(report)

    assert summary["mode"] == "PAPER_ONLY"
    assert summary["starting_balance"] == 500.0
    assert summary["ending_balance"] >= 500.0
    assert summary["capture_rate_pct"] >= 0
    assert summary["opportunity_quality_score"] >= 0
    assert summary["live_ready"] is False
    assert summary["protected_gate_required"] is True


def test_module_has_no_forbidden_imports_or_calls() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    import_lines = "\n".join(
        line.strip()
        for line in source.splitlines()
        if line.startswith("import ") or line.startswith("from ")
    )

    for forbidden_import in ("requests", "socket", "urllib", "subprocess", "os", "dotenv"):
        assert forbidden_import not in import_lines
    for forbidden_call in ("os.environ", "getenv", "open(", "write_text(", "write_bytes(", "start-process"):
        assert forbidden_call not in source
    for forbidden_call in ("broker sdk", "broker_sdk", "schedule.every", "daemon.daemoncontext"):
        assert forbidden_call not in source
