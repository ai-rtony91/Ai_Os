"""CLI runner for the AIOS Forex owner safety evidence artifact verifier."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_owner_safety_evidence_artifact_verifier_v1 import (
    INTAKE_PATH,
    NEXT_PACKET_OUTPUT_PATH,
    PREP_STATE_PATH,
    REPORT_OUTPUT_PATH,
    STATE_OUTPUT_PATH,
    run_artifact_verifier,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the AIOS Forex owner safety evidence artifact verifier."
    )
    parser.add_argument("--intake-path", default=str(INTAKE_PATH))
    parser.add_argument("--prep-state-path", default=str(PREP_STATE_PATH))
    parser.add_argument("--write-state", action="store_true")
    parser.add_argument("--state-output-path", default=str(STATE_OUTPUT_PATH))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--report-output-path", default=str(REPORT_OUTPUT_PATH))
    parser.add_argument("--write-next-packet", action="store_true")
    parser.add_argument("--next-packet-output-path", default=str(NEXT_PACKET_OUTPUT_PATH))
    args = parser.parse_args(argv)

    result = run_artifact_verifier(
        intake_path=Path(args.intake_path),
        prep_state_path=Path(args.prep_state_path),
        write_state=args.write_state,
        state_output_path=Path(args.state_output_path),
        write_report=args.write_report,
        report_output_path=Path(args.report_output_path),
        write_next_packet=args.write_next_packet,
        next_packet_output_path=Path(args.next_packet_output_path),
    )
    sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
