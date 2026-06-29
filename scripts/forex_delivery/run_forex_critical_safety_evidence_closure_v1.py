"""CLI runner for the AIOS Forex critical safety evidence closure layer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_critical_safety_evidence_closure_v1 import (
    run_forex_critical_safety_evidence_closure_v1,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the AIOS Forex critical safety evidence closure classifier."
    )
    parser.add_argument(
        "--write-state",
        action="store_true",
        help="Write AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_STATE.json.",
    )
    parser.add_argument(
        "--write-report",
        action="store_true",
        help=(
            "Write AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_REPORT.md and "
            "AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_NEXT_CODEX_PACKET_V1.md."
        ),
    )
    args = parser.parse_args(argv)

    result = run_forex_critical_safety_evidence_closure_v1(
        write_state=args.write_state,
        write_report=args.write_report,
    )
    sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
