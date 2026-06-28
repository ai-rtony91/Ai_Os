"""Run the Flow 1 active execution authority runtime SOS profit countdown module."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.forex_flow1_active_execution_authority_runtime_sos_profit_countdown_v2 import (
    generate_artifacts,
)  # noqa: E402


def main() -> None:
    payload = generate_artifacts()
    print(f"flow1_status: {payload['flow1_status']}")
    print(f"flow1_mode: {payload['flow1_mode']}")
    print(f"owner_live_capital_intent_usd: {payload['owner_live_capital_intent_usd']}")
    print(f"requested_max_open_positions: {payload['requested_max_open_positions']}")
    print(f"final_position_capacity: {payload['final_position_capacity']}")
    print(f"position_capacity_status: {payload['position_capacity_status']}")
    print(f"target_return_band: {payload['target_return_band']}")
    print(f"profit_return_rate_status: {payload['profit_return_rate_status']}")
    print(f"runtime_objective: {payload['runtime_objective']}")
    print(f"runtime_status: {payload['runtime_status']}")
    print(f"vacation_mode_status: {payload['vacation_mode_status']}")
    print(f"sos_alert_integration_status: {payload['sos_alert_integration_status']}")
    print(f"flow2_handoff_status: {payload['flow2_handoff_status']}")
    print(f"next_required_flow: {payload['next_required_flow']}")


if __name__ == "__main__":
    main()
