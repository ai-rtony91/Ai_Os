from __future__ import annotations

from automation.forex_engine import stress_repair


def stress_repair_demo_lines(repair_result: dict[str, object]) -> list[str]:
    summary = stress_repair.summarize_stress_repair(repair_result)
    return [
        "AIOS Forex Stress Repair Demo",
        f"Mode: {summary['mode']}",
        f"Original stress classification: {summary['original_classification']}",
        f"Repaired stress classification: {summary['repaired_stress_classification']}",
        f"Original worst stress PnL: {summary['original_worst_stress_pnl']}",
        f"Repaired worst stress PnL: {summary['repaired_worst_stress_pnl']}",
        f"Stress survived pct: {summary['repaired_stress_survived_pct']}",
        f"Retained intents: {summary['retained_intents']}",
        f"Skipped intents: {summary['skipped_intents']}",
        f"Tradeoff: {summary['tradeoff_summary']}",
        "Broker-paper ready: false",
        "Live ready: false",
        "Protected gate required: true",
        f"Next safe action: {summary['next_safe_action']}",
        "Safety: no broker/API/network/live execution.",
    ]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    result = stress_repair.apply_local_stress_repair_policy()
    for line in stress_repair_demo_lines(result):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
