"""Print the local PAPER_ONLY daily edge report preview."""

from automation.forex_engine.daily_edge_report import build_daily_edge_report, format_daily_edge_report


def main() -> int:
    report = build_daily_edge_report()
    print(format_daily_edge_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
