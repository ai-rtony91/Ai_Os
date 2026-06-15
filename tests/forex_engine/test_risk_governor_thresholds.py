from __future__ import annotations

from pathlib import Path

from automation.forex_engine import opportunity_capture
from automation.forex_engine import paper_forward_evidence_v2
from automation.forex_engine import risk_governor_thresholds
from automation.forex_engine import run_risk_governor_demo


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "risk_governor_thresholds.py"
DEMO_PATH = REPO_ROOT / "automation" / "forex_engine" / "run_risk_governor_demo.py"
ALLOWED_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}


def _bundle() -> dict[str, object]:
    return paper_forward_evidence_v2.build_paper_forward_evidence_v2()


def _report(bundle: dict[str, object]) -> dict[str, object]:
    return opportunity_capture.calculate_opportunity_capture(bundle)


def test_default_policy_exists_with_required_thresholds() -> None:
    policy = risk_governor_thresholds.default_risk_governor_policy()

    for key in (
        "minimum_fixture_count",
        "minimum_regime_count",
        "minimum_total_intents",
        "minimum_total_ledger_entries",
        "minimum_consistency_pct",
        "minimum_capture_rate_pct",
        "minimum_risk_adjusted_return",
        "maximum_drawdown_pct",
        "maximum_cost_drag_pct",
        "maximum_missed_pnl_pct",
        "maximum_overtrade_ratio",
        "minimum_exit_efficiency_pct",
        "minimum_opportunity_quality_score",
    ):
        assert key in policy
    assert policy["require_protected_gate_for_live"] is True
    assert policy["live_ready_always_false"] is True


def test_evaluates_v2_evidence_and_keeps_live_blocked() -> None:
    bundle = _bundle()
    result = risk_governor_thresholds.evaluate_risk_governor_thresholds(bundle)

    assert result["mode"] == "PAPER_ONLY"
    assert result["classification"] in ALLOWED_CLASSIFICATIONS
    assert result["classification"] != "LIVE_READY"
    assert result["threshold_results"]
    assert result["passed_thresholds"]
    assert result["live_ready"] is False
    assert result["protected_gate_required"] is True
    assert result["safety"]["broker_allowed"] is False


def test_requires_fixture_count() -> None:
    bundle = _bundle()
    low_bundle = dict(bundle)
    multi_summary = dict(low_bundle["multi_fixture_paper_forward_summary"])
    multi_summary["fixture_count"] = 1
    low_bundle["multi_fixture_paper_forward_summary"] = multi_summary

    result = risk_governor_thresholds.evaluate_risk_governor_thresholds(low_bundle, _report(bundle))

    assert "minimum_fixture_count" in result["failed_thresholds"]


def test_requires_regime_count() -> None:
    bundle = _bundle()
    low_bundle = dict(bundle)
    regime = dict(low_bundle["regime_consistency"])
    regime["total_regimes"] = 1
    low_bundle["regime_consistency"] = regime

    result = risk_governor_thresholds.evaluate_risk_governor_thresholds(low_bundle, _report(bundle))

    assert "minimum_regime_count" in result["failed_thresholds"]


def test_requires_consistency_capture_rate_and_risk_adjusted_return() -> None:
    bundle = _bundle()
    low_bundle = dict(bundle)
    multi_summary = dict(low_bundle["multi_fixture_paper_forward_summary"])
    multi_summary["consistency_pct"] = 10.0
    low_bundle["multi_fixture_paper_forward_summary"] = multi_summary
    report = dict(_report(bundle))
    report["capture_rate_pct"] = 10.0
    report["risk_adjusted_return"] = 0.0

    result = risk_governor_thresholds.evaluate_risk_governor_thresholds(low_bundle, report)

    assert "minimum_consistency_pct" in result["failed_thresholds"]
    assert "minimum_capture_rate_pct" in result["failed_thresholds"]
    assert "minimum_risk_adjusted_return" in result["failed_thresholds"]


def test_blocks_excessive_drawdown_and_cost_drag() -> None:
    bundle = _bundle()
    report = dict(_report(bundle))
    report["max_drawdown_pct"] = 20.0
    report["cost_drag_pct"] = 40.0

    result = risk_governor_thresholds.evaluate_risk_governor_thresholds(bundle, report)

    assert "maximum_drawdown_pct" in result["failed_thresholds"]
    assert "maximum_cost_drag_pct" in result["failed_thresholds"]
    assert result["classification"] == "FAIL"


def test_run_cost_stress_scenarios_is_local_estimated_and_live_blocked() -> None:
    stress = risk_governor_thresholds.run_cost_stress_scenarios(_bundle())

    assert stress["mode"] == "PAPER_ONLY"
    assert stress["estimated"] is True
    assert len(stress["scenario_results"]) == 5
    for scenario in stress["scenario_results"]:
        assert scenario["classification"] in ALLOWED_CLASSIFICATIONS
        assert scenario["live_ready"] is False
        assert scenario["protected_gate_required"] is True


def test_assert_live_blocked_rejects_live_ready() -> None:
    result = risk_governor_thresholds.evaluate_risk_governor_thresholds(_bundle())
    bad = dict(result)
    bad["live_ready"] = True

    try:
        risk_governor_thresholds.assert_live_blocked(bad)
    except ValueError as exc:
        assert "live_ready" in str(exc)
    else:
        raise AssertionError("expected live_ready to be rejected")


def test_demo_function_exists_and_prints_safety_note(capsys) -> None:
    assert run_risk_governor_demo.main([]) == 0
    output = capsys.readouterr().out

    assert "AIOS Forex Risk Governor Demo" in output
    assert "Mode: PAPER_ONLY" in output
    assert "Starting balance: 500.0" in output
    assert "Live ready: false" in output
    assert "Protected gate required: true" in output
    assert "Safety: no broker/API/network/live execution." in output


def test_modules_have_no_forbidden_imports_or_calls() -> None:
    for path in (MODULE_PATH, DEMO_PATH):
        source = path.read_text(encoding="utf-8").lower()
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
