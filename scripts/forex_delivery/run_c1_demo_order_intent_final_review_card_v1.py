from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.c1_demo_order_intent_final_review_card_v1 import (
    evaluate_c1_demo_order_intent_final_review_card,
    render_next_action_queue,
    render_owner_report,
)


JSON_PATH = (
    REPO_ROOT
    / "Reports/forex_delivery/AIOS_FOREX_C1_DEMO_ORDER_INTENT_FINAL_REVIEW_CARD_V1.json"
)
REPORT_PATH = (
    REPO_ROOT
    / "Reports/forex_delivery/AIOS_FOREX_C1_DEMO_ORDER_INTENT_FINAL_REVIEW_CARD_V1_REPORT.md"
)
QUEUE_PATH = (
    REPO_ROOT
    / "Reports/forex_delivery/AIOS_FOREX_C1_DEMO_ORDER_INTENT_FINAL_REVIEW_CARD_NEXT_ACTION_QUEUE_V1.md"
)


def generate_artifacts() -> dict[str, object]:
    result = evaluate_c1_demo_order_intent_final_review_card()
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(render_owner_report(result), encoding="utf-8")
    QUEUE_PATH.write_text(render_next_action_queue(result), encoding="utf-8")
    return result


def main() -> None:
    if len(sys.argv) != 1:
        raise SystemExit("This runner accepts no command-line arguments.")
    result = generate_artifacts()
    print(f"status={result['p6d_final_review_status']}")
    print(f"score={result['post_p6d_score']}")
    print(f"next_required_lane={result['next_required_lane']}")


if __name__ == "__main__":
    main()
