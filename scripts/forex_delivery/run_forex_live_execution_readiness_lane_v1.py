"""Run the Forex execution-readiness lane contract and write repo artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_live_execution_readiness_lane_v1 import (
    REPORT_NAME,
    STATE_NAME,
    run_forex_live_execution_readiness_lane_v1,
)

def _resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = ROOT / path
    return path


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Forex live execution-readiness lane.")
    parser.add_argument(
        "--state-path",
        default=str(ROOT / "Reports" / "forex_delivery" / STATE_NAME),
        help="Target path for the JSON state artifact.",
    )
    parser.add_argument(
        "--report-path",
        default=str(ROOT / "Reports" / "forex_delivery" / REPORT_NAME),
        help="Target path for the markdown readiness report.",
    )
    args = parser.parse_args(argv)

    payload = run_forex_live_execution_readiness_lane_v1()
    state_path = _resolve_path(args.state_path)
    report_path = _resolve_path(args.report_path)

    state_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    state_path.write_text(
        json.dumps({"state": payload["input"], "result": payload["result"]}, indent=2, ensure_ascii=True)
        + "\n",
        encoding="utf-8",
    )
    report_path.write_text(payload["report"], encoding="utf-8")

    if stdout is None:
        stdout = sys.stdout
    stdout.write(json.dumps(payload["result"], sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
