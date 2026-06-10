"""AI_OS packet completeness / promotion review (observe-only).

A1 (decision_to_packet_drafter) produces a packet DRAFT. Before a human spends
review time, this module decides whether the draft is even promotion-ready: it
runs the governance validator for SHAPE and adds readiness checks (paths scoped,
mission/objective present, STOP point present, per-action approval language). It
emits exactly one promotion verdict.

It decides readiness for HUMAN REVIEW, never APPLY. A READY verdict is not an
approval and authorizes no commit, push, merge, or execution.

Verdicts:
  READY_FOR_HUMAN_REVIEW  - shape clean, scoped, complete; a human may now review.
  INCOMPLETE              - missing/unscoped sections; not worth review yet.
  PROMOTION_BLOCKED       - a governance BLOCK hazard is present; do not promote.

Pure standard library. Read-only. No mutation.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Callable, Optional


SCHEMA = "AIOS_PACKET_COMPLETENESS_REVIEW.v1"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_governance_validator() -> Optional[Callable[[str, str], dict]]:
    path = _repo_root() / "automation" / "validators" / "aios_governance_validator.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location("aios_governance_validator", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return getattr(module, "validate_packet_text", None)


# Readiness markers that must be present and meaningfully filled for promotion.
READINESS_MARKERS = ["MISSION", "OBJECTIVE", "ALLOWED PATHS", "STOP POINT", "APPROVAL AUTHORITY"]


def _check(passed: bool, check_id: str, message: str, evidence: str = "") -> dict:
    return {"check_id": check_id, "passed": bool(passed), "message": message, "evidence": evidence}


def review_packet_completeness(
    packet_text: str,
    *,
    path_status: Optional[str] = None,
    validate: Optional[Callable[[str, str], dict]] = None,
    input_path: str = "<draft>",
) -> dict[str, object]:
    """Review a draft packet for promotion-readiness (observe-only)."""
    checks: list[dict] = []
    text = packet_text or ""

    # 1. governance shape
    if validate is None:
        validate = _load_governance_validator()
    if validate is None:
        gov = {"status": "UNAVAILABLE", "errors": [], "warnings": []}
        gov_available = False
    else:
        gov = validate(text, input_path)
        gov_available = True

    gov_status = gov.get("status", "UNAVAILABLE")
    gov_errors = gov.get("errors", []) or []
    has_block = any(e.get("severity") == "BLOCK" for e in gov_errors)
    has_fail = any(e.get("severity") == "FAIL" for e in gov_errors)

    checks.append(_check(gov_available, "PCR-001-GOVERNANCE-AVAILABLE", "Governance validator is available.", gov_status))
    checks.append(_check(not has_block, "PCR-002-NO-HAZARD-BLOCK", "No governance BLOCK hazard present.",
                         str([e.get("rule_id") for e in gov_errors if e.get("severity") == "BLOCK"])))
    checks.append(_check(not has_fail, "PCR-003-NO-SHAPE-FAIL", "No required-section FAIL present.",
                         str([e.get("rule_id") for e in gov_errors if e.get("severity") == "FAIL"])))

    # 2. readiness markers present
    upper = text.upper()
    missing_markers = [m for m in READINESS_MARKERS if m not in upper]
    checks.append(_check(not missing_markers, "PCR-004-READINESS-MARKERS", "All readiness sections present.",
                         f"missing={missing_markers}"))

    # 3. paths scoped (the A1 honesty flag, or a heuristic if not supplied)
    if path_status is not None:
        scoped = path_status == "SCOPED"
    else:
        scoped = "NEEDS_PATH_CONFIRMATION" not in upper
    checks.append(_check(scoped, "PCR-005-PATHS-SCOPED", "Allowed paths are operator-scoped, not auto-derived.",
                         f"path_status={path_status}"))

    # 4. per-action approval language present (separate approval per protected action)
    has_per_action = "separate explicit" in text.lower() and "approval does not transfer" in text.lower()
    checks.append(_check(has_per_action, "PCR-006-PER-ACTION-APPROVAL",
                         "States commit/push/merge need separate explicit approval.",
                         "per-action approval language present" if has_per_action else "missing per-action approval language"))

    failed = [c for c in checks if not c["passed"]]

    if has_block:
        verdict = "PROMOTION_BLOCKED"
    elif failed:
        verdict = "INCOMPLETE"
    else:
        verdict = "READY_FOR_HUMAN_REVIEW"

    return {
        "schema": SCHEMA,
        "input_path": input_path,
        "verdict": verdict,
        "promotion_ready": verdict == "READY_FOR_HUMAN_REVIEW",
        "requires_human": True,  # promotion review is for a human; never auto-promotes
        "approves_protected_action": False,
        "governance_status": gov_status,
        "checks": checks,
        "failed_checks": [c["check_id"] for c in failed],
        "reasons": [c["message"] + " :: " + c["evidence"] for c in failed],
        "safe_next_action": (
            "Surface to the human approval review. This verdict is readiness evidence "
            "only; it approves no APPLY, commit, push, or merge."
            if verdict == "READY_FOR_HUMAN_REVIEW"
            else "Do not promote. Resolve the failed checks first; a draft is not an approval."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Review a draft packet for promotion-readiness (observe-only).")
    parser.add_argument("--packet", required=True, help="path to a draft packet .md")
    parser.add_argument("--path-status", default=None, help="SCOPED | NEEDS_PATH_CONFIRMATION (from the drafter)")
    args = parser.parse_args()
    text = Path(args.packet).read_text(encoding="utf-8")
    result = review_packet_completeness(text, path_status=args.path_status, input_path=args.packet)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] != "PROMOTION_BLOCKED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
