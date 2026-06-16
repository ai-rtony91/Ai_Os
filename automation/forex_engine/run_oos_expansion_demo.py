from __future__ import annotations

from automation.forex_engine import oos_expansion


def oos_expansion_demo_lines(result: dict[str, object]) -> list[str]:
    summary = oos_expansion.summarize_expanded_oos(result)
    return [
        "AIOS Forex OOS Expansion Demo",
        f"Mode: {summary['mode']}",
        f"Fixtures: {summary['fixture_count']}",
        f"Splits: {summary['split_count']}",
        f"Heldout consistency pct: {summary['heldout_consistency_pct']}",
        f"Max degradation pct: {summary['max_degradation_pct']}",
        f"Weakest split: {summary['weakest_split_id']}",
        f"Classification: {summary['classification']}",
        f"Broker-paper contract ready: {str(summary['broker_paper_contract_ready']).lower()}",
        "Live ready: false",
        "Protected gate required: true",
        f"Next safe action: {summary['next_safe_action']}",
        "Safety: no broker/API/network/live execution.",
    ]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    result = oos_expansion.run_expanded_oos_validation()
    for line in oos_expansion_demo_lines(result):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
