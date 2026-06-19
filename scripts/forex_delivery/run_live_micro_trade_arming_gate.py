"""Run the AIOS live micro-trade arming gate dry-run review.

This script is review-only. It reads sanitized evidence reports, writes a
sanitized arming report, and never reads secrets, calls brokers, places orders,
or closes trades.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from forex_delivery.live_micro_trade_arming_gate import (  # noqa: E402
    build_live_micro_trade_arming_gate_result,
    cli_summary,
    write_live_micro_trade_arming_gate_report,
)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    try:
        result = build_live_micro_trade_arming_gate_result(repo_root=REPO_ROOT)
        write_live_micro_trade_arming_gate_report(result, repo_root=REPO_ROOT)
        print(json.dumps(cli_summary(result), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = {
            "schema": "AIOS_FOREX_LIVE_MICRO_TRADE_ARMING_GATE_ERROR.v1",
            "status": "FAILED_SANITIZED",
            "error_type": type(exc).__name__,
            "LIVE_ARMABLE": False,
            "live_execution_allowed": False,
            "broker_write_calls_allowed": False,
            "order_placement_allowed": False,
            "close_trade_allowed": False,
            "secret_values_printed": False,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
