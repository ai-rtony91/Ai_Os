"""Run the canonical AIOS work countdown from a repository-local input file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.orchestration.aios_work_countdown_v1 import (
    build_aios_work_countdown,
    build_owner_report,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--owner-report", action="store_true")
    args = parser.parse_args(argv)
    path = args.input.resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        parser.error("countdown input must be inside the repository")
    payload = json.loads(path.read_text(encoding="utf-8"))
    countdown = build_aios_work_countdown(
        mission=payload["mission"],
        work_items=payload.get("work_items", []),
        execution_receipts=payload.get("execution_receipts", []),
        workflow_state=payload.get("workflow_controller_state", {}),
        current_workflow_packet_id=payload.get(
            "current_workflow_packet_id", "AIOS_WORK_COUNTDOWN_V1"
        ),
    )
    output = build_owner_report(countdown) if args.owner_report else json.dumps(countdown, indent=2)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
