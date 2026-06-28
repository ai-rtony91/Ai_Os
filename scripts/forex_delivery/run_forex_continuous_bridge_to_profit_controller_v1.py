"""Runner for the continuous Forex bridge-to-profit controller."""

from __future__ import annotations

import sys
from pathlib import Path

def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from automation.forex_engine.forex_continuous_bridge_to_profit_controller_v1 import (
        JSON_REPORT_PATH,
        REPORT_PATH,
        QUEUE_PATH,
        generate_artifacts,
    )

    result = generate_artifacts()

    print(f"controller_status: {result['controller_status']}")
    print(f"controller_mode: {result['controller_mode']}")
    print(f"owner_live_capital_intent_usd: {result['owner_live_capital_intent_usd']}")
    print(f"target_return_band: {result['target_return_band']}")
    print(f"profit_return_rate_status: {result['profit_return_rate_status']}")
    print(f"runtime_status: {result['runtime_status']}")
    print(f"vacation_mode_status: {result['vacation_mode_status']}")
    print(f"next_required_flow: {result['next_required_flow']}")
    print(f"json_report_path: {JSON_REPORT_PATH}")
    print(f"report_path: {REPORT_PATH}")
    print(f"queue_path: {QUEUE_PATH}")


if __name__ == "__main__":
    main()
