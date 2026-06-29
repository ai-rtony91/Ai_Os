"""CLI runner for broker connection proof boundary readiness V1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.broker_connection_proof_boundary_readiness_v1 import (
    DEFAULT_NEXT_PACKET_OUTPUT_PATH,
    DEFAULT_REPORT_OUTPUT_PATH,
    DEFAULT_STATE_OUTPUT_PATH,
    build_next_codex_packet,
    build_report_markdown,
    run_broker_connection_proof_boundary_readiness_v1,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-state", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--write-next-packet", action="store_true")
    args = parser.parse_args(argv)

    result = run_broker_connection_proof_boundary_readiness_v1()
    if args.write_state:
        DEFAULT_STATE_OUTPUT_PATH.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    if args.write_report:
        DEFAULT_REPORT_OUTPUT_PATH.write_text(build_report_markdown(result), encoding="utf-8")
    if args.write_next_packet:
        DEFAULT_NEXT_PACKET_OUTPUT_PATH.write_text(build_next_codex_packet(result), encoding="utf-8")

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
