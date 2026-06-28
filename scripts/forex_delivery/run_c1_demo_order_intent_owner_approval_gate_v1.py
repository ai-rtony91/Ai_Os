from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.c1_demo_order_intent_owner_approval_gate_v1 import (  # noqa: E402
    evaluate_c1_demo_order_intent_owner_approval_gate,
    render_next_action_queue,
    render_owner_report,
)


REPORT_DIR = Path("Reports/forex_delivery")
JSON_PATH = (
    REPORT_DIR / "AIOS_FOREX_C1_DEMO_ORDER_INTENT_OWNER_APPROVAL_GATE_V1.json"
)
REPORT_PATH = (
    REPORT_DIR
    / "AIOS_FOREX_C1_DEMO_ORDER_INTENT_OWNER_APPROVAL_GATE_V1_REPORT.md"
)
QUEUE_PATH = (
    REPORT_DIR
    / "AIOS_FOREX_C1_DEMO_ORDER_INTENT_OWNER_APPROVAL_GATE_NEXT_ACTION_QUEUE_V1.md"
)


def generate_artifacts() -> dict[str, object]:
    result = evaluate_c1_demo_order_intent_owner_approval_gate()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    JSON_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(render_owner_report(result), encoding="utf-8")
    QUEUE_PATH.write_text(render_next_action_queue(result), encoding="utf-8")

    return result


def main() -> int:
    if len(sys.argv) != 1:
        raise SystemExit("This runner accepts no command-line arguments.")

    result = generate_artifacts()
    print(f"p6_gate_status: {result['p6_gate_status']}")
    print(f"owner_action_status: {result['owner_action_status']}")
    print(f"post_p6_score: {result['post_p6_score']}")
    print(f"next_required_lane: {result['next_required_lane']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
