"""Generate P6A C1 owner snapshot and approval decision gate artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from automation.forex_engine.c1_owner_snapshot_approval_decision_gate_v1 import (
    evaluate_c1_owner_snapshot_approval_decision_gate,
    render_next_action_queue,
    render_owner_report,
)


JSON_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_C1_OWNER_SNAPSHOT_APPROVAL_DECISION_GATE_V1.json"
)
REPORT_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_C1_OWNER_SNAPSHOT_APPROVAL_DECISION_GATE_V1_REPORT.md"
)
QUEUE_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_C1_OWNER_SNAPSHOT_APPROVAL_DECISION_GATE_NEXT_ACTION_QUEUE_V1.md"
)


def generate_artifacts() -> dict:
    """Generate repo-local P6A owner-input gate artifacts."""

    result = evaluate_c1_owner_snapshot_approval_decision_gate()
    JSON_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(render_owner_report(result), encoding="utf-8")
    QUEUE_PATH.write_text(render_next_action_queue(result), encoding="utf-8")
    return result


def main() -> int:
    """Run the artifact generator with no command-line arguments."""

    if len(sys.argv) != 1:
        raise SystemExit("This runner accepts no command-line arguments.")
    result = generate_artifacts()
    print(f"p6a_gate_status: {result['p6a_gate_status']}")
    print(f"owner_input_status: {result['owner_input_status']}")
    print(f"post_p6a_score: {result['post_p6a_score']}")
    print(f"next_required_lane: {result['next_required_lane']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
