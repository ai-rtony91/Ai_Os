"""CLI runner for the AIOS Forex finish-line mission controller."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_finish_line_mission_controller_v1 import (
    DEFAULT_DASHBOARD_OUTPUT_PATH,
    DEFAULT_NEXT_PACKET_OUTPUT_PATH,
    DEFAULT_REPORT_OUTPUT_PATH,
    DEFAULT_STATE_OUTPUT_PATH,
    STARTING_LINE,
    SUPPORTED_MODES,
    build_next_codex_packet,
    build_report_markdown,
    run_forex_finish_line_mission_controller_v1,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the AIOS Forex finish-line mission controller."
    )
    parser.add_argument(
        "--mode",
        choices=SUPPORTED_MODES,
        default=STARTING_LINE,
        help="Finish-line controller mode.",
    )
    parser.add_argument(
        "--write-state",
        action="store_true",
        help="Write AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json.",
    )
    parser.add_argument(
        "--write-report",
        action="store_true",
        help=(
            "Write AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_REPORT.md and "
            "AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_NEXT_CODEX_PACKET_V1.md."
        ),
    )
    parser.add_argument(
        "--write-dashboard",
        action="store_true",
        help="Write AIOS_FOREX_FINISH_LINE_EMOJI_DASHBOARD_PROJECTION_V1.json.",
    )
    args = parser.parse_args(argv)

    result = run_forex_finish_line_mission_controller_v1(mode=args.mode)

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
        DEFAULT_NEXT_PACKET_OUTPUT_PATH.write_text(
            build_next_codex_packet(result),
            encoding="utf-8",
        )
        result["report_output_path"] = str(DEFAULT_REPORT_OUTPUT_PATH)
        result["next_packet_output_path"] = str(DEFAULT_NEXT_PACKET_OUTPUT_PATH)

    if args.write_dashboard:
        DEFAULT_DASHBOARD_OUTPUT_PATH.write_text(
            json.dumps(
                result["emoji_dashboard_projection"],
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        result["dashboard_output_path"] = str(DEFAULT_DASHBOARD_OUTPUT_PATH)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
