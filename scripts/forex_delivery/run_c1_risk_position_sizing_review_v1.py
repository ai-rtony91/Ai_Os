"""Generate P4 C1 risk and position-sizing review artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.c1_risk_position_sizing_review_v1 import (
    evaluate_c1_risk_position_sizing_review,
    render_next_action_queue,
    render_owner_report,
)


JSON_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_C1_RISK_POSITION_SIZING_REVIEW_V1.json"
)
REPORT_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_C1_RISK_POSITION_SIZING_REVIEW_V1_REPORT.md"
)
QUEUE_PATH = Path(
    "Reports/forex_delivery/AIOS_FOREX_C1_RISK_POSITION_SIZING_REVIEW_NEXT_ACTION_QUEUE_V1.md"
)


def generate_artifacts() -> dict[str, Any]:
    """Write the P4 review JSON, owner report, and next-action queue."""

    result = evaluate_c1_risk_position_sizing_review()
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(render_owner_report(result), encoding="utf-8")
    QUEUE_PATH.write_text(render_next_action_queue(result), encoding="utf-8")
    return result


def main() -> int:
    """Run the artifact generator without command-line arguments."""

    if len(sys.argv) != 1:
        raise SystemExit(
            "run_c1_risk_position_sizing_review_v1.py accepts no command-line arguments"
        )

    result = generate_artifacts()
    print(f"p4_review_status: {result['p4_review_status']}")
    print(f"p5_readiness: {result['p5_readiness']}")
    print(f"post_p4_score: {result['post_p4_score']}")
    print(f"next_required_lane: {result['next_required_lane']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
