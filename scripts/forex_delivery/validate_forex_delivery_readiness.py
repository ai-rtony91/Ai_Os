"""Print the governed Forex Delivery readiness result.

This script is DRY_RUN only. It does not read credentials, call brokers, use
network APIs, write reports, or submit orders.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from forex_delivery.governed_readiness import (  # noqa: E402
    build_live_arming_checklist,
    run_governed_paper_flow,
    submit_live_order,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate governed Forex Delivery readiness.")
    parser.add_argument("--mode", choices=["paper", "live-arming-check"], default="paper")
    parser.add_argument("--approval-json", default="", help="External sanitized approval field JSON for checklist review.")
    args = parser.parse_args()

    if args.mode == "paper":
        result = run_governed_paper_flow()
    else:
        approval_fields = {}
        if args.approval_json:
            approval_path = Path(args.approval_json)
            approval_fields = json.loads(approval_path.read_text(encoding="utf-8"))
        result = build_live_arming_checklist(approval_fields)
        try:
            submit_live_order({})
        except Exception as exc:
            result["live_submit_probe"] = {
                "blocked": True,
                "error_type": type(exc).__name__,
                "message": str(exc),
            }

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
