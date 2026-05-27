"""Worker routing preview for the AI_OS Python supervisor skeleton."""

from __future__ import annotations

from typing import Any


def route_worker_preview(packet: dict[str, Any] | None) -> dict[str, Any]:
    lane = "UNKNOWN"
    if packet:
        lane = str(packet.get("lane") or packet.get("owner_lane") or "UNKNOWN")

    worker = "SUPERVISOR"
    if "validator" in lane.lower():
        worker = "VALIDATOR_01"
    elif "pr" in lane.lower():
        worker = "PR_01"
    elif "cleanup" in lane.lower():
        worker = "CLEANUP_01"
    elif "west" in lane.lower():
        worker = "WEST_OCC_01"
    elif lane != "UNKNOWN":
        worker = "EAST_OCC_01"

    return {
        "lane": lane,
        "recommended_worker": worker,
        "worker_launch_enabled": False,
        "queue_mutation_enabled": False,
    }
