"""Run the Forex 110 walk-forward/OOS sufficiency truth lock."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_110_walkforward_oos_sufficiency_truth_lock_v1 import (  # noqa: E402
    build_report_markdown,
    run_walkforward_oos_sufficiency_truth_lock,
)


STATE_NAME = "AIOS_FOREX_110_WALKFORWARD_OOS_SUFFICIENCY_TRUTH_LOCK_V1_STATE.json"
REPORT_NAME = "AIOS_FOREX_110_WALKFORWARD_OOS_SUFFICIENCY_TRUTH_LOCK_V1_REPORT.md"
DEFAULT_OUTPUT_ROOT = ROOT / "Reports" / "forex_delivery"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--write-state", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args(argv)

    result = run_walkforward_oos_sufficiency_truth_lock(args.report_root)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    if args.write_state:
        (output_root / STATE_NAME).write_text(
            json.dumps(result, indent=2, ensure_ascii=True, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.write_report:
        (output_root / REPORT_NAME).write_text(build_report_markdown(result), encoding="utf-8")
    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=True, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
