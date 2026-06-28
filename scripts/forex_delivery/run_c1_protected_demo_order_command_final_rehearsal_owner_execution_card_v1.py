"""Run the P14 protected demo-order final rehearsal artifact generation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.c1_protected_demo_order_command_final_rehearsal_owner_execution_card_v1 import (  # noqa: E402
    evaluate_c1_protected_demo_order_command_final_rehearsal_owner_execution_card,
    render_next_action_queue,
    render_owner_report,
)

JSON_REPORT_PATH = (
    REPO_ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_C1_PROTECTED_DEMO_ORDER_COMMAND_FINAL_REHEARSAL_OWNER_EXECUTION_CARD_V1.json"
)
REPORT_PATH = (
    REPO_ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_C1_PROTECTED_DEMO_ORDER_COMMAND_FINAL_REHEARSAL_OWNER_EXECUTION_CARD_V1_REPORT.md"
)
QUEUE_PATH = (
    REPO_ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_C1_PROTECTED_DEMO_ORDER_COMMAND_FINAL_REHEARSAL_OWNER_EXECUTION_CARD_NEXT_ACTION_QUEUE_V1.md"
)


def generate_artifacts(
    owner_input: dict | None = None,
) -> dict:
    result = evaluate_c1_protected_demo_order_command_final_rehearsal_owner_execution_card(
        owner_input
    )
    JSON_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_REPORT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    REPORT_PATH.write_text(render_owner_report(result), encoding="utf-8")
    QUEUE_PATH.write_text(render_next_action_queue(result), encoding="utf-8")
    return result


def main() -> None:
    if len(sys.argv) != 1:
        raise SystemExit("This script accepts no command-line arguments.")
    result = generate_artifacts()
    print(f"p14_final_rehearsal_status: {result['p14_final_rehearsal_status']}")
    print(f"owner_execution_card_status: {result['owner_execution_card_status']}")
    print(f"post_p14_score: {result['post_p14_score']}")
    print(f"next_required_lane: {result['next_required_lane']}")


if __name__ == "__main__":
    main()

