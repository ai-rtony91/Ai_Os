"""Run the AIOS forex PAPER_SIMULATION signal execution loop.

Default behavior is deterministic local paper simulation. The script requires
no secrets, performs no network calls, and never calls broker write behavior.
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

from forex_delivery.paper_signal_execution_loop import (  # noqa: E402
    build_paper_signal_execution_loop_result,
    cli_summary,
    write_paper_signal_execution_loop_report,
)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    try:
        result = build_paper_signal_execution_loop_result()
        write_paper_signal_execution_loop_report(result, repo_root=REPO_ROOT)
        print(json.dumps(cli_summary(result), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        payload = {
            "schema": "AIOS_FOREX_PAPER_SIGNAL_EXECUTION_LOOP_ERROR.v1",
            "status": "FAILED_SANITIZED",
            "error_type": type(exc).__name__,
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
