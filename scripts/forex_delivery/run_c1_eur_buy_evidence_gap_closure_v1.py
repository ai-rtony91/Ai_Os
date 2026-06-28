"""Generate C1 EUR BUY evidence-gap closure artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.c1_eur_buy_evidence_gap_closure_v1 import (  # noqa: E402
    evaluate_c1_eur_buy_gap_closure,
    render_next_action_queue,
    render_owner_report,
)


REPORT_DIR = REPO_ROOT / "Reports" / "forex_delivery"
JSON_PATH = REPORT_DIR / "AIOS_FOREX_C1_EUR_BUY_EVIDENCE_GAP_CLOSURE_V1.json"
REPORT_PATH = REPORT_DIR / "AIOS_FOREX_C1_EUR_BUY_EVIDENCE_GAP_CLOSURE_V1_REPORT.md"
QUEUE_PATH = REPORT_DIR / "AIOS_FOREX_C1_EUR_BUY_EVIDENCE_GAP_CLOSURE_NEXT_ACTION_QUEUE_V1.md"


def main() -> int:
    if len(sys.argv) > 1:
        raise SystemExit("This runner accepts no command-line arguments.")

    result = evaluate_c1_eur_buy_gap_closure()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    JSON_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(render_owner_report(result), encoding="utf-8")
    QUEUE_PATH.write_text(render_next_action_queue(result), encoding="utf-8")

    print(f"gap_closure_status={result['gap_closure_status']}")
    print(f"p3_readiness={result['p3_readiness']}")
    print(f"post_closure_score={result['post_closure_score']}")
    print(f"next_required_lane={result['next_required_lane']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
