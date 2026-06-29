"""CLI runner for Forex 110 vacation-grade profit engine V1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_110_vacation_grade_profit_engine_v1 import (
    build_report_markdown,
    run_forex_110_vacation_grade_profit_engine_v1,
)


STATE_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_110_VACATION_GRADE_PROFIT_ENGINE_V1_STATE.json"
)
REPORT_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_110_VACATION_GRADE_PROFIT_ENGINE_V1_REPORT.md"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-state", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args(argv)

    result = run_forex_110_vacation_grade_profit_engine_v1(args.repo_root)
    if args.write_state:
        STATE_PATH.write_text(
            json.dumps(result, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
    if args.write_report:
        REPORT_PATH.write_text(build_report_markdown(result), encoding="utf-8")

    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
