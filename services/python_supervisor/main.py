"""AI_OS Python supervisor skeleton.

Standard library only. Preview-only. No subprocess execution, network calls,
daemon loops, queue mutation, approval mutation, MCP execution, cloud actions,
or trading actions.
"""

from __future__ import annotations

import json
from pathlib import Path

from queue_reader import read_queue_preview
from runtime_state import build_runtime_state
from telemetry_writer import build_preview_event
from worker_router import route_worker_preview


def build_supervisor_preview(repo_root: Path) -> dict[str, object]:
    queue_path = repo_root / "automation" / "orchestration" / "command_queue" / "AIOS_COMMAND_QUEUE.json"
    runtime_state = build_runtime_state(repo_root)
    queue = read_queue_preview(queue_path)
    first_packet = queue["items"][0] if queue.get("items") else None
    routing = route_worker_preview(first_packet if isinstance(first_packet, dict) else None)
    telemetry = build_preview_event(
        "python_supervisor_preview",
        "services/python_supervisor/main.py",
        {"queue_status": queue["status"], "recommended_worker": routing["recommended_worker"]},
    )

    return {
        "schema": "AIOS_PYTHON_SUPERVISOR_PREVIEW.v1",
        "mode": "DRY_RUN",
        "execution_enabled": False,
        "runtime_state": runtime_state.to_dict(),
        "queue_preview": queue,
        "worker_routing_preview": routing,
        "telemetry_preview": telemetry,
        "blocked_actions": [
            "subprocess execution",
            "network calls",
            "queue mutation",
            "approval mutation",
            "daemon startup",
            "MCP execution",
            "secrets",
            "cloud provisioning",
            "broker/OANDA/trading/webhook/live orders",
        ],
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    print(json.dumps(build_supervisor_preview(repo_root), indent=2))


if __name__ == "__main__":
    main()
