from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.c1_owner_controlled_protected_demo_order_run_handoff_preparation_v1 import (  # noqa: E402
    evaluate_c1_owner_controlled_protected_demo_order_run_handoff_preparation as evaluate_p10_handoff_preparation,
    render_next_action_queue,
    render_owner_report,
)

JSON_PATH = REPO_ROOT / (
    "Reports/forex_delivery/"
    "AIOS_FOREX_C1_OWNER_CONTROLLED_PROTECTED_DEMO_ORDER_RUN_HANDOFF_PREPARATION_V1.json"
)
REPORT_PATH = REPO_ROOT / (
    "Reports/forex_delivery/"
    "AIOS_FOREX_C1_OWNER_CONTROLLED_PROTECTED_DEMO_ORDER_RUN_HANDOFF_PREPARATION_V1_REPORT.md"
)
QUEUE_PATH = REPO_ROOT / (
    "Reports/forex_delivery/"
    "AIOS_FOREX_C1_OWNER_CONTROLLED_PROTECTED_DEMO_ORDER_RUN_HANDOFF_PREPARATION_NEXT_ACTION_QUEUE_V1.md"
)


def generate_artifacts() -> dict[str, Any]:
    result = evaluate_p10_handoff_preparation()

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
    print(f"p10_handoff_status: {result['p10_handoff_status']}")
    print(f"owner_run_handoff_status: {result['owner_run_handoff_status']}")
    print(f"post_p10_score: {result['post_p10_score']}")
    print(f"next_required_lane: {result['next_required_lane']}")


if __name__ == "__main__":
    main()
