"""Generate C1 walk-forward/OOS proof artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.c1_walk_forward_oos_proof_v1 import (  # noqa: E402
    evaluate_c1_walk_forward_oos_proof,
    render_next_action_queue,
    render_owner_report,
)


REPORT_DIR = REPO_ROOT / "Reports" / "forex_delivery"
JSON_PATH = REPORT_DIR / "AIOS_FOREX_C1_WALK_FORWARD_OOS_PROOF_V1.json"
REPORT_PATH = REPORT_DIR / "AIOS_FOREX_C1_WALK_FORWARD_OOS_PROOF_V1_REPORT.md"
QUEUE_PATH = REPORT_DIR / "AIOS_FOREX_C1_WALK_FORWARD_OOS_PROOF_NEXT_ACTION_QUEUE_V1.md"


def generate_artifacts() -> dict:
    result = evaluate_c1_walk_forward_oos_proof()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    JSON_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(render_owner_report(result), encoding="utf-8")
    QUEUE_PATH.write_text(render_next_action_queue(result), encoding="utf-8")
    return result


def main() -> int:
    if len(sys.argv) > 1:
        raise SystemExit("This runner accepts no command-line arguments.")

    result = generate_artifacts()
    print(f"p3_proof_status={result['p3_proof_status']}")
    print(f"p4_readiness={result['p4_readiness']}")
    print(f"post_p3_score={result['post_p3_score']}")
    print(f"next_required_lane={result['next_required_lane']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
