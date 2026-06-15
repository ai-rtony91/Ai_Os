from __future__ import annotations

from pathlib import Path

from automation.forex_engine import paper_forward_evidence_v2
from automation.forex_engine import paper_forward_stress
from automation.forex_engine import run_stress_and_oos_demo


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "paper_forward_stress.py"
DEMO_PATH = REPO_ROOT / "automation" / "forex_engine" / "run_stress_and_oos_demo.py"
ALLOWED_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}
REQUIRED_SCENARIOS = {
    "base",
    "double_spread",
    "double_slippage",
    "double_spread_double_slippage",
    "half_capture_rate",
    "minus_best_regime",
    "plus_drawdown_penalty",
    "conservative_extreme",
    "disaster_case",
}


def test_default_stress_scenarios_include_required_cases() -> None:
    scenarios = paper_forward_stress.default_stress_scenarios()
    scenario_ids = {scenario["scenario_id"] for scenario in scenarios}

    assert REQUIRED_SCENARIOS.issubset(scenario_ids)
    assert len(scenarios) >= len(REQUIRED_SCENARIOS)


def test_paper_forward_stress_result_includes_required_scenarios() -> None:
    bundle = paper_forward_evidence_v2.build_paper_forward_evidence_v2()
    result = paper_forward_stress.run_paper_forward_stress(bundle)
    scenario_ids = {scenario["scenario_id"] for scenario in result["scenario_results"]}

    assert result["mode"] == "PAPER_ONLY"
    assert REQUIRED_SCENARIOS.issubset(scenario_ids)
    assert result["classification"] in ALLOWED_CLASSIFICATIONS
    assert result["classification"] != "LIVE_READY"
    assert result["live_ready"] is False
    assert result["protected_gate_required"] is True
    assert result["safety"]["broker_allowed"] is False
    assert result["safety"]["network_allowed"] is False


def test_stress_scenario_outputs_are_simulated_only_and_never_live_ready() -> None:
    result = paper_forward_stress.run_paper_forward_stress()

    assert result["scenario_results"]
    for scenario in result["scenario_results"]:
        assert scenario["classification"] in ALLOWED_CLASSIFICATIONS
        assert scenario["classification"] != "LIVE_READY"
        assert scenario["live_ready"] is False
        assert scenario["protected_gate_required"] is True
        assert "broker_order_id" not in scenario or scenario["broker_order_id"] is None
        assert "pnl_after_stress" in scenario
        assert "return_pct_after_stress" in scenario


def test_stress_summary_and_combined_gate_block_live_readiness() -> None:
    bundle = paper_forward_evidence_v2.build_paper_forward_evidence_v2()
    stress = bundle["paper_forward_stress"]
    oos = bundle["out_of_sample_validation"]
    gate = paper_forward_stress.build_stress_oos_gate(stress, oos, bundle["risk_governor"])
    summary = paper_forward_stress.summarize_stress_results(stress)

    assert summary["scenario_count"] >= len(REQUIRED_SCENARIOS)
    assert summary["survived_scenarios_pct"] >= 0.0
    assert summary["classification"] in ALLOWED_CLASSIFICATIONS
    assert gate["combined_classification"] in ALLOWED_CLASSIFICATIONS
    assert gate["combined_classification"] != "LIVE_READY"
    assert gate["live_ready"] is False
    assert gate["protected_gate_required"] is True
    assert gate["broker_paper_sandbox_ready"] is False


def test_compact_stress_oos_demo_function_exists_and_prints_safety_note(capsys) -> None:
    assert run_stress_and_oos_demo.main([]) == 0
    output = capsys.readouterr().out

    assert "AIOS Forex Stress + OOS Demo" in output
    assert "Mode: PAPER_ONLY" in output
    assert "Combined classification:" in output
    assert "Live ready: false" in output
    assert "Protected gate required: true" in output
    assert "Safety: no broker/API/network/live execution." in output


def test_stress_modules_have_no_forbidden_imports_or_execution_calls() -> None:
    for path in (MODULE_PATH, DEMO_PATH):
        source = path.read_text(encoding="utf-8").lower()
        import_lines = "\n".join(
            line.strip()
            for line in source.splitlines()
            if line.startswith("import ") or line.startswith("from ")
        )

        for forbidden_import in ("requests", "socket", "urllib", "subprocess", "os", "schedule", "daemon"):
            assert forbidden_import not in import_lines
        for forbidden_call in (
            "os.environ",
            "getenv",
            "broker_sdk",
            "import broker",
            "from broker",
            "oanda",
            "schedule.every",
            "daemon.daemoncontext",
            "open(",
            "write_text(",
            "write_bytes(",
            "start-process",
        ):
            assert forbidden_call not in source
