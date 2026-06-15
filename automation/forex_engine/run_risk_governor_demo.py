from __future__ import annotations

from automation.forex_engine import paper_forward_evidence_v2


def main(_argv: list[str] | None = None) -> int:
    bundle = paper_forward_evidence_v2.build_paper_forward_evidence_v2()
    report = bundle["opportunity_capture"]
    governor = bundle["risk_governor"]
    summary = bundle["multi_fixture_paper_forward_summary"]
    regime = bundle["regime_consistency"]

    lines = [
        "AIOS Forex Risk Governor Demo",
        f"Mode: {governor['mode']}",
        f"Starting balance: {report['starting_balance']}",
        f"Ending balance: {report['ending_balance']}",
        f"Aggregate paper PnL: {report['aggregate_paper_pnl']}",
        f"Return pct: {report['return_pct']}",
        f"Fixtures: {summary['fixture_count']}",
        f"Regimes: {regime['total_regimes']}",
        f"Total intents: {report['total_intents']}",
        f"Simulated entries: {report['simulated_ledger_entries']}",
        f"Capture rate pct: {report['capture_rate_pct']}",
        f"Missed signal count: {report['missed_signal_count']}",
        f"Missed PnL estimate: {report['missed_pnl_estimate']}",
        f"Cost drag pct: {report['cost_drag_pct']}",
        f"Risk-adjusted return: {report['risk_adjusted_return']}",
        f"Max drawdown pct: {report['max_drawdown_pct']}",
        f"Opportunity quality score: {report['opportunity_quality_score']}",
        f"Classification: {governor['classification']}",
        "Live ready: false",
        "Protected gate required: true",
        f"Next safe action: {governor['next_safe_action']}",
        "Safety: no broker/API/network/live execution.",
    ]
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
