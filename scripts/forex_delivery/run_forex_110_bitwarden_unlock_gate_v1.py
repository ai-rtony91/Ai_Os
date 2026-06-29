"""CLI runner for Forex 110 completion and Bitwarden lock gate V1."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_110_bitwarden_unlock_gate_v1 import (
    BITWARDEN_LOCK_OUTPUT_PATH,
    BROKER_HANDOFF_OUTPUT_PATH,
    DASHBOARD_UX_OUTPUT_PATH,
    EMOJI_MAP_OUTPUT_PATH,
    REPORT_OUTPUT_PATH,
    STATE_OUTPUT_PATH,
    build_bitwarden_lock_markdown,
    build_broker_handoff_markdown,
    build_dashboard_ux_markdown,
    build_emoji_map_markdown,
    build_report_markdown,
    run_forex_110_bitwarden_unlock_gate_v1,
    to_json_text,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-state", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--write-dashboard-ux", action="store_true")
    parser.add_argument("--write-emoji-map", action="store_true")
    parser.add_argument("--write-bitwarden-lock", action="store_true")
    parser.add_argument("--write-broker-handoff", action="store_true")
    args = parser.parse_args(argv)

    result = run_forex_110_bitwarden_unlock_gate_v1()
    if args.write_state:
        STATE_OUTPUT_PATH.write_text(to_json_text(result), encoding="utf-8")
    if args.write_report:
        REPORT_OUTPUT_PATH.write_text(build_report_markdown(result), encoding="utf-8")
    if args.write_dashboard_ux:
        DASHBOARD_UX_OUTPUT_PATH.write_text(build_dashboard_ux_markdown(result), encoding="utf-8")
    if args.write_emoji_map:
        EMOJI_MAP_OUTPUT_PATH.write_text(build_emoji_map_markdown(result), encoding="utf-8")
    if args.write_bitwarden_lock:
        BITWARDEN_LOCK_OUTPUT_PATH.write_text(build_bitwarden_lock_markdown(result), encoding="utf-8")
    if args.write_broker_handoff:
        BROKER_HANDOFF_OUTPUT_PATH.write_text(build_broker_handoff_markdown(result), encoding="utf-8")

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(to_json_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
