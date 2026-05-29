"""AI_OS Night Supervisor action-intent builder.

Schema/contract reference: schemas/aios/orchestration/supervisor_action_intent.schema.json
Mode: DRY_RUN
blocked_capabilities: worker_launch, packet_movement, approval_mutation,
queue_mutation, lock_write, git_stage_commit_push
next_safe_action: Treat every intent as a proposal only. Execution requires the
dispatcher with approval + lock + capability allowlist all satisfied.
commit_performed: NO / push_performed: NO

This module converts the brainstem's read-only ``packet_flow`` into concrete,
typed action intents (the wiring between the "brainstem" and the "hands").
Building an intent NEVER executes anything. Every intent is born blocked.
"""

from __future__ import annotations

import argparse
import json
from typing import Any


# Logical effector -> repo-relative hand-script + risk tier.
# Ordered weakest-to-strongest for the graduated-enable ladder (step 10).
EFFECTOR_CATALOG: dict[str, dict[str, Any]] = {
    "heartbeat": {
        "script": "scripts/write-worker-heartbeat.ps1",
        "risk_tier": "low",
        "requires_approval": False,
        "requires_lock": False,
    },
    "claim_lock": {
        "script": "scripts/claim-packet-lock.ps1",
        "risk_tier": "low",
        "requires_approval": True,
        "requires_lock": False,
    },
    "assign": {
        "script": "scripts/assign-next-queue-item.ps1",
        "risk_tier": "medium",
        "requires_approval": True,
        "requires_lock": True,
    },
    "mark_done": {
        "script": "scripts/mark-queue-item-done.ps1",
        "risk_tier": "medium",
        "requires_approval": True,
        "requires_lock": True,
    },
    "release_lock": {
        "script": "scripts/release-packet-lock.ps1",
        "risk_tier": "low",
        "requires_approval": True,
        "requires_lock": False,
    },
}

# Capability ladder order used by the dispatcher allowlist (step 10).
CAPABILITY_LADDER = ["heartbeat", "claim_lock", "assign", "mark_done", "release_lock"]


def _effector_for_state(packet_state: str, worker_id: str) -> str:
    """Pick the single safest effector a packet state would justify.

    The mapping is intentionally conservative: anything blocked, stale, or
    needing approval/validation produces a ``noop`` (surface-only) intent.
    """

    state = (packet_state or "").upper()
    has_worker = bool(worker_id) and worker_id not in {"UNASSIGNED", "UNKNOWN", ""}
    if state == "READY_FOR_REVIEW" and has_worker:
        # A reviewed, worker-bound packet is the only thing that justifies a
        # mutating proposal, and even then only the lowest assignment step.
        return "assign"
    if state == "READY_FOR_REVIEW":
        return "heartbeat"
    return "noop"


def build_action_intents(packet_flow: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Build blocked-by-default action intents from brainstem packet_flow."""

    intents: list[dict[str, Any]] = []
    for entry in packet_flow or []:
        packet_id = str(entry.get("packet_id") or "UNKNOWN")
        lane = str(entry.get("lane") or "UNKNOWN")
        worker_id = str(entry.get("worker_identity") or entry.get("worker_id") or "UNASSIGNED")
        packet_state = str(entry.get("packet_state") or "UNKNOWN")
        approval_required = bool(entry.get("approval_required"))

        effector = _effector_for_state(packet_state, worker_id)
        spec = EFFECTOR_CATALOG.get(effector, {})
        requires_approval = bool(spec.get("requires_approval", True)) or approval_required

        intents.append(
            {
                "intent_id": f"intent:{effector}:{packet_id}",
                "packet_id": packet_id,
                "lane": lane,
                "worker_id": worker_id,
                "effector": effector,
                "effector_script": str(spec.get("script") or ""),
                "args": {"PacketId": packet_id, "WorkerId": worker_id},
                "risk_tier": "read_only" if effector == "noop" else str(spec.get("risk_tier", "medium")),
                "requires_approval": requires_approval,
                "requires_lock": bool(spec.get("requires_lock", False)),
                "blocked_by_default": True,
                "source_packet_state": packet_state,
                "reason": str(entry.get("next_safe_action") or "Proposal only; awaiting gates."),
            }
        )
    return intents


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Night Supervisor action intents from packet_flow JSON.")
    parser.add_argument("--packet-flow-json", default=None, help="Path to a packet_flow JSON array.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    args = parser.parse_args()

    packet_flow: list[dict[str, Any]] = []
    if args.packet_flow_json:
        from pathlib import Path

        packet_flow = json.loads(Path(args.packet_flow_json).read_text(encoding="utf-8"))
    print(json.dumps(build_action_intents(packet_flow), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
