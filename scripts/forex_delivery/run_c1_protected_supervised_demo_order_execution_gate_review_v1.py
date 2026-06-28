from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.c1_protected_supervised_demo_order_execution_gate_review_v1 import (  # noqa: E402
    evaluate_c1_protected_supervised_demo_order_execution_gate_review,
    render_next_action_queue,
    render_owner_report,
)


JSON_PATH = REPO_ROOT / (
    "Reports/forex_delivery/"
    "AIOS_FOREX_C1_PROTECTED_SUPERVISED_DEMO_ORDER_EXECUTION_GATE_REVIEW_V1.json"
)
REPORT_PATH = REPO_ROOT / (
    "Reports/forex_delivery/"
    "AIOS_FOREX_C1_PROTECTED_SUPERVISED_DEMO_ORDER_EXECUTION_GATE_REVIEW_V1_REPORT.md"
)
QUEUE_PATH = REPO_ROOT / (
    "Reports/forex_delivery/"
    "AIOS_FOREX_C1_PROTECTED_SUPERVISED_DEMO_ORDER_EXECUTION_GATE_REVIEW_NEXT_ACTION_QUEUE_V1.md"
)


def generate_artifacts() -> dict[str, Any]:
    result = evaluate_c1_protected_supervised_demo_order_execution_gate_review()

    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(render_owner_report(result), encoding="utf-8")
    QUEUE_PATH.write_text(render_next_action_queue(result), encoding="utf-8")

    return result


def main() -> None:
    result = generate_artifacts()
    print(f"p9_execution_gate_status: {result['p9_execution_gate_status']}")
    print(
        "protected_demo_order_gate_status: "
        f"{result['protected_demo_order_gate_status']}"
    )
    print(f"post_p9_score: {result['post_p9_score']}")
    print(f"next_required_lane: {result['next_required_lane']}")


if __name__ == "__main__":
    main()
