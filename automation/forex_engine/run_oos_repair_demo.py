from __future__ import annotations

from automation.forex_engine import oos_repair


def oos_repair_demo_lines(repair_result: dict[str, object]) -> list[str]:
    summary = oos_repair.summarize_oos_repair(repair_result)
    return [
        "AIOS Forex OOS Repair Demo",
        f"Mode: {summary['mode']}",
        f"Original max degradation pct: {summary['original_max_degradation_pct']}",
        f"Repaired max degradation pct: {summary['repaired_max_degradation_pct']}",
        f"Degradation improvement pct: {summary['degradation_improvement_pct']}",
        f"Weakest split: {summary['weakest_split']}",
        f"Retained intents: {summary['retained_intents']}",
        f"Skipped low-vol intents: {summary['skipped_low_vol_intents']}",
        f"Classification: {summary['classification']}",
        f"Broker-paper contract ready: {str(summary['broker_paper_contract_ready']).lower()}",
        "Live ready: false",
        "Protected gate required: true",
        f"Next safe action: {summary['next_safe_action']}",
        "Safety: no broker/API/network/live execution.",
    ]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    result = oos_repair.apply_oos_repair_policy()
    for line in oos_repair_demo_lines(result):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
