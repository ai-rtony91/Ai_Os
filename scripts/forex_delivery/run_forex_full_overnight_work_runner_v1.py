"""Run the overnight full runner artifact generator."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.forex_full_overnight_work_runner_v1 import (  # noqa: E402
    generate_artifacts,
)


def main() -> None:
    payload = generate_artifacts()
    print(f"runner_status: {payload['runner_status']}")
    print(f"runner_mode: {payload['runner_mode']}")
    print(f"active_anchor: {payload['active_anchor']}")
    print(f"next_packet_id: {payload['next_packet_id']}")
    print(f"next_required_flow: {payload['next_required_flow']}")
    print(f"overnight_loop_status: {payload['overnight_loop_status']}")


if __name__ == "__main__":
    main()
