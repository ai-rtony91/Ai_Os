"""Run the AIOS one-shot live micro-trade execution review dry run.

This script reads sanitized local evidence reports only. It never reads
secrets, calls brokers, places orders, or closes trades.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.forex_delivery.one_shot_live_micro_trade_execution_review import (  # noqa: E402
    build_one_shot_live_micro_trade_execution_review_result,
    cli_summary,
    write_one_shot_live_micro_trade_execution_review_report,
)


def main(argv: list[str] | None = None) -> int:
    del argv
    result = build_one_shot_live_micro_trade_execution_review_result(repo_root=REPO_ROOT)
    write_one_shot_live_micro_trade_execution_review_report(
        result, repo_root=REPO_ROOT
    )
    print(json.dumps(cli_summary(result), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
