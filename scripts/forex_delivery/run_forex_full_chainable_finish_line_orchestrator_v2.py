"""CLI runner for the AIOS Forex full chainable finish-line orchestrator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_full_chainable_finish_line_orchestrator_v2 import (
    DEFAULT_NEXT_PACKET_OUTPUT_PATH,
    DEFAULT_REPORT_OUTPUT_PATH,
    DEFAULT_STATE_OUTPUT_PATH,
    build_next_codex_packet,
    build_report_markdown,
    run_forex_full_chainable_finish_line_orchestrator_v2,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the AIOS Forex full chainable finish-line orchestrator."
    )
    parser.add_argument(
        "--write-state",
        action="store_true",
        help="Write AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_STATE.json.",
    )
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Write AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_REPORT.md.",
    )
    parser.add_argument(
        "--write-next-packet",
        action="store_true",
        help="Write AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_NEXT_CODEX_PACKET_V2.md.",
    )
    args = parser.parse_args(argv)

    result = run_forex_full_chainable_finish_line_orchestrator_v2()

    if args.write_state:
        DEFAULT_STATE_OUTPUT_PATH.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        result["state_output_path"] = str(DEFAULT_STATE_OUTPUT_PATH)

    if args.write_report:
        DEFAULT_REPORT_OUTPUT_PATH.write_text(
            build_report_markdown(result),
            encoding="utf-8",
        )
        result["report_output_path"] = str(DEFAULT_REPORT_OUTPUT_PATH)

    if args.write_next_packet:
        DEFAULT_NEXT_PACKET_OUTPUT_PATH.write_text(
            build_next_codex_packet(result),
            encoding="utf-8",
        )
        result["next_packet_output_path"] = str(DEFAULT_NEXT_PACKET_OUTPUT_PATH)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
