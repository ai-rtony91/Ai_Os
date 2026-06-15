from __future__ import annotations

from automation.forex_engine import out_of_sample_validator
from automation.forex_engine import paper_forward_evidence_v2
from automation.forex_engine import paper_forward_stress


def main(_argv: list[str] | None = None) -> int:
    bundle = paper_forward_evidence_v2.build_paper_forward_evidence_v2()
    stress = bundle["paper_forward_stress"]
    oos = bundle["out_of_sample_validation"]
    gate = bundle["combined_stress_oos_gate"]
    stress_summary = paper_forward_stress.summarize_stress_results(stress)
    oos_summary = out_of_sample_validator.summarize_oos_validation(oos)

    lines = [
        "AIOS Forex Stress + OOS Demo",
        f"Mode: {bundle['mode']}",
        f"Fixtures: {oos_summary['fixture_count']}",
        f"Stress scenarios: {stress_summary['scenario_count']}",
        f"Stress survived pct: {stress_summary['survived_scenarios_pct']}",
        f"Heldout fixtures: {oos_summary['heldout_count']}",
        f"Heldout consistency pct: {oos_summary['heldout_consistency_pct']}",
        f"Worst stress PnL: {stress_summary['worst_stress_pnl']}",
        f"Worst stress return pct: {stress_summary['worst_stress_return_pct']}",
        f"Degradation pct: {gate['degradation_pct']}",
        f"Combined classification: {gate['combined_classification']}",
        "Live ready: false",
        "Protected gate required: true",
        f"Next safe action: {gate['next_safe_action']}",
        "Safety: no broker/API/network/live execution.",
    ]
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
