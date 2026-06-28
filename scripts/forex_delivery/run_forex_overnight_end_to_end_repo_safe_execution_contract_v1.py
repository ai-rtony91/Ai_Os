"""Run the overnight end-to-end repo-safe contract module."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.forex_overnight_end_to_end_repo_safe_execution_contract_v1 import (
    generate_artifacts,
)  # noqa: E402


def main() -> None:
    payload = generate_artifacts()
    print(f"overnight_contract_status: {payload['overnight_contract_status']}")
    print(f"overnight_contract_mode: {payload['overnight_contract_mode']}")
    print(f"target_return_band: {payload['target_return_band']}")
    print(f"runtime_objective: {payload['runtime_objective']}")
    print(f"flow2_contract_status: {payload['flow2_contract_status']}")
    print(f"flow3_contract_status: {payload['flow3_contract_status']}")
    print(f"live_exception_contract_status: {payload['live_exception_contract_status']}")
    print(f"next_required_flow: {payload['next_required_flow']}")


if __name__ == "__main__":
    main()
