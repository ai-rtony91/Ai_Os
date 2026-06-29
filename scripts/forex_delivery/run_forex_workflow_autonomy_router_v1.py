"""CLI runner for the AIOS Forex workflow autonomy router."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.forex_workflow_autonomy_router_v1 import (  # noqa: E402
    run_forex_workflow_autonomy_router_v1 as run_router,
    parse_args,
)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_router(
        discovery_report_path=args.discovery_report_path,
        collection_state_path=args.collection_state_path,
        verification_prep_state_path=args.verification_prep_state_path,
        critical_safety_closure_state_path=args.critical_safety_closure_state_path,
        finish_line_state_path=args.finish_line_state_path,
        governor_state_path=args.governor_state_path,
        write_state=args.write_state,
        write_state_path=args.state_output_path,
        write_report=args.write_report,
        write_report_path=args.report_output_path,
        write_next_packet=args.write_next_packet,
        write_next_packet_path=args.next_packet_output_path,
    )
    sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
