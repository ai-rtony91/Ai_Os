"""AI_OS runtime execution queue integrity validator (observe-only).

Given a canonical queue view (AIOS_RUNTIME_EXECUTION_QUEUE.v1), this validator checks
its integrity before any later drain/wiring packet consumes it: no duplicate ids across
sources, no unknown states, and no item carrying a protected/forbidden execution flag.
It returns PASS or BLOCK with a reason list. It mutates nothing and executes nothing.

A PASS is evidence only; it is not approval to enqueue, dispatch, or execute anything.

Pure standard library. No network, no mutation.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


VALIDATOR_NAME = "aios_runtime_execution_queue_validator"
SCHEMA = "AIOS_RUNTIME_EXECUTION_QUEUE_INTEGRITY.v1"
EXPECTED_VIEW_SCHEMA = "AIOS_RUNTIME_EXECUTION_QUEUE.v1"
CANONICAL_STATES = {"QUEUED", "RUNNING", "DONE", "ERROR", "BLOCKED", "DEFERRED"}
CANONICAL_PRIORITIES = {"P0", "P1", "P2", "P3"}
CANONICAL_MODES = {"DRY_RUN", "APPLY"}
CANONICAL_APPROVAL_STATES = {"NOT_REQUIRED", "PENDING", "APPROVED", "REJECTED"}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _finding(check_id: str, passed: bool, message: str, evidence: Any) -> dict:
    return {"check_id": check_id, "passed": bool(passed), "message": message, "evidence": evidence}


def validate_queue_view(view: Any, input_path: str = "<queue-view>") -> dict[str, object]:
    """Return PASS/BLOCK for a canonical queue view's integrity."""
    findings: list[dict] = []

    # 0. shape
    shaped = isinstance(view, dict) and view.get("schema") == EXPECTED_VIEW_SCHEMA and isinstance(view.get("items"), list)
    findings.append(_finding("RQV-000-VIEW-SHAPE", shaped,
                             "Input is a canonical queue view.", view.get("schema") if isinstance(view, dict) else type(view).__name__))
    if not shaped:
        return _result(findings, input_path, malformed=True)

    items = view["items"]

    # 1. no duplicate ids across sources (the adapter records these in id_collisions)
    collisions = view.get("id_collisions", []) or []
    findings.append(_finding("RQV-001-NO-DUPLICATE-IDS", not collisions,
                             "No id appears in more than one source.", collisions))

    # 2. every item state is canonical
    unknown = [{"id": it.get("id"), "state": it.get("state")} for it in items if it.get("state") not in CANONICAL_STATES]
    findings.append(_finding("RQV-002-CANONICAL-STATES", not unknown,
                             "Every item state is in the canonical state set.", unknown))

    # 3. no item carries a protected/forbidden execution flag
    protected = [{"id": it.get("id"), "kind": it.get("kind")} for it in items if it.get("protected_action")]
    findings.append(_finding("RQV-003-NO-PROTECTED-ITEM", not protected,
                             "No queue item carries a protected/forbidden execution flag.", protected))

    # 4. every item has an id (informational; synthetic ids allowed but surfaced)
    synthetic = [it.get("id") for it in items if it.get("synthetic_id")]
    findings.append(_finding("RQV-004-IDS-PRESENT", True,
                             "Items with synthesized ids are surfaced (informational).", synthetic))

    # 5. autonomous-development scheduling metadata is internally consistent
    extended_contract = isinstance(view.get("contract"), dict)
    invalid_contract = []
    for item in items if extended_contract else []:
        dependencies = item.get("depends_on")
        attempt = item.get("attempt")
        max_attempts = item.get("max_attempts")
        valid = (
            item.get("priority") in CANONICAL_PRIORITIES
            and item.get("mode") in CANONICAL_MODES
            and item.get("approval_state") in CANONICAL_APPROVAL_STATES
            and isinstance(dependencies, list)
            and item.get("id") not in dependencies
            and isinstance(attempt, int) and not isinstance(attempt, bool) and attempt >= 0
            and isinstance(max_attempts, int) and not isinstance(max_attempts, bool) and max_attempts >= 1
            and attempt <= max_attempts
        )
        if not valid:
            invalid_contract.append(item.get("id"))
    findings.append(_finding("RQV-005-AUTONOMY-CONTRACT", not invalid_contract,
                             "Autonomous workflow metadata is valid.", invalid_contract))

    # 6. APPLY remains human-gated; normalization must never manufacture approval
    ungated_apply = [
        item.get("id") for item in items
        if extended_contract
        if item.get("mode") == "APPLY"
        and (not item.get("approval_required") or item.get("approval_state") != "APPROVED")
    ]
    findings.append(_finding("RQV-006-APPLY-APPROVAL", not ungated_apply,
                             "Every APPLY item carries explicit approval.", ungated_apply))

    return _result(findings, input_path)


def _result(findings: list[dict], input_path: str, malformed: bool = False) -> dict[str, object]:
    # All checks except 004 are blocking integrity checks.
    blocking = [f for f in findings if not f["passed"] and f["check_id"] != "RQV-004-IDS-PRESENT"]
    status = "BLOCK" if (blocking or malformed) else "PASS"
    return {
        "validator_name": VALIDATOR_NAME,
        "schema": SCHEMA,
        "timestamp_utc": _now(),
        "input_path": input_path,
        "status": status,
        "approves_protected_action": False,
        "findings": findings,
        "blocking_findings": [f["check_id"] for f in blocking],
        "reasons": [f["message"] + " :: " + json.dumps(f["evidence"], default=str) for f in blocking],
        "safe_next_action": (
            "Queue integrity holds. PASS is evidence only; it approves no enqueue, dispatch, or execution."
            if status == "PASS"
            else "BLOCK: resolve duplicate ids / unknown states / protected items before any drain packet consumes this queue."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate canonical runtime execution queue integrity (observe-only).")
    parser.add_argument("--view", required=True, help="path to a queue view JSON")
    args = parser.parse_args()
    view = json.loads(Path(args.view).read_text(encoding="utf-8"))
    result = validate_queue_view(view, args.view)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
