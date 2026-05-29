"""AI_OS Night Supervisor effector-intent builder (downstream of Codex V2).

Schema/contract reference:
  schemas/aios/orchestration/supervisor_action_intent.schema.json
  (source_contract -> schemas/aios/orchestration/packet_routing_contract.v1.json)
Mode: DRY_RUN
blocked_capabilities: worker_launch, packet_movement, approval_mutation,
queue_mutation, lock_write, git_stage_commit_push
next_safe_action: Treat every intent as a proposal only. Execution is gated by
effector_dispatcher and is OFF by default.
commit_performed: NO / push_performed: NO

This module turns an APPROVED Codex V2 ``routing_contract`` into a concrete,
blocked-by-default effector intent. It does NOT read the approval inbox or scan
locks; that authority belongs to the Codex spine (approval_officer / lock_manager).
The intent simply records what the contract already cleared and which hand-script
would carry it out.
"""

from __future__ import annotations

import argparse
import json
from typing import Any


# Logical effector -> repo-relative hand-script + risk tier.
# Ordered weakest-to-strongest for the graduated-enable ladder.
EFFECTOR_CATALOG: dict[str, dict[str, Any]] = {
    "heartbeat": {"script": "scripts/write-worker-heartbeat.ps1", "risk_tier": "low"},
    "claim_lock": {"script": "scripts/claim-packet-lock.ps1", "risk_tier": "low"},
    "assign": {"script": "scripts/assign-next-queue-item.ps1", "risk_tier": "medium"},
    "mark_done": {"script": "scripts/mark-queue-item-done.ps1", "risk_tier": "medium"},
    "release_lock": {"script": "scripts/release-packet-lock.ps1", "risk_tier": "low"},
}

CAPABILITY_LADDER = ["heartbeat", "claim_lock", "assign", "mark_done", "release_lock"]

# Codex packet states (from queue_scanner) that justify a mutating proposal.
_ASSIGNABLE_STATES = {"PENDING", "ASSIGNED", "READY", "READY_FOR_REVIEW"}


def _worker(contract: dict[str, Any]) -> str:
    worker = str(contract.get("assigned_worker") or contract.get("recommended_worker") or "").strip()
    return worker if worker not in {"", "UNASSIGNED", "UNKNOWN"} else ""


def _effector_for_contract(contract: dict[str, Any]) -> str:
    """Pick the single safest effector an approved contract justifies."""

    state = str(contract.get("packet_state") or "").upper()
    worker = _worker(contract)
    if state in {"COMPLETE", "DONE", "CLOSED"}:
        return "mark_done"
    if state in _ASSIGNABLE_STATES and worker:
        return "assign"
    return "noop"


def build_effector_intents(routing_contracts: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Build blocked-by-default effector intents from Codex routing contracts."""

    intents: list[dict[str, Any]] = []
    for contract in routing_contracts or []:
        packet_id = str(contract.get("packet_id") or "UNKNOWN")
        worker = _worker(contract) or "UNASSIGNED"
        effector = _effector_for_contract(contract)
        spec = EFFECTOR_CATALOG.get(effector, {})

        intents.append(
            {
                "intent_id": f"intent:{effector}:{packet_id}",
                "packet_id": packet_id,
                "worker_id": worker,
                "effector": effector,
                "effector_script": str(spec.get("script") or ""),
                "args": {"PacketId": packet_id, "WorkerId": worker},
                "risk_tier": "read_only" if effector == "noop" else str(spec.get("risk_tier", "medium")),
                "blocked_by_default": True,
                # Echo the spine's verdict; the dispatcher trusts these, never re-judges.
                "source_contract": {
                    "packet_id": packet_id,
                    "dispatch_status": str(contract.get("dispatch_status") or "UNKNOWN"),
                    "approval_status": str(contract.get("approval_status") or "UNKNOWN"),
                    "lock_status": str(contract.get("lock_status") or "UNKNOWN"),
                    "dispatch_mode": str(contract.get("dispatch_mode") or "DRY_RUN"),
                },
                "reason": str(contract.get("blocked_reason") or "Approved contract; proposal only."),
            }
        )
    return intents


def main() -> int:
    parser = argparse.ArgumentParser(description="Build effector intents from Codex routing contracts.")
    parser.add_argument("--contracts-json", required=True, help="Path to a routing_contracts JSON array.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    args = parser.parse_args()
    from pathlib import Path

    contracts = json.loads(Path(args.contracts_json).read_text(encoding="utf-8"))
    print(json.dumps(build_effector_intents(contracts), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
