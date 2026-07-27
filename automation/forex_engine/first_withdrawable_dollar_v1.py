"""Fail-closed, read-only First Withdrawable Dollar evidence projection."""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from copy import deepcopy
from typing import Any, Mapping, Sequence

SCHEMA = "AIOS_FIRST_WITHDRAWABLE_DOLLAR.v1"
SHA = re.compile(r"^[0-9a-fA-F]{7,64}$")
PASS = {"pass", "passed", "success", "successful", "completed"}
PLACEHOLDER = re.compile(r"(?i)(?:^|\b)(todo|tbd|null|unknown|placeholder|example)(?:\b|$)|[@{}<>]")


def _protected_actions() -> dict[str, bool]:
    return {key: False for key in (
        "broker_access", "credential_access", "order_placement", "trade_modification",
        "trade_closure", "withdrawal", "money_movement", "git_stage", "git_commit",
        "git_push", "pr_create", "git_merge",
    )}


def _text(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip() or PLACEHOLDER.search(value.strip()):
        return None
    return value.strip()


def _hours(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) and number >= 0 else None


def _receipt(receipt: Mapping[str, Any]) -> tuple[dict[str, Any], list[str]]:
    reasons: list[str] = []
    required = ("packet_id", "evidence_provenance", "pr_id", "test_command", "test_conclusion", "ci_check_id", "ci_conclusion")
    values = {key: _text(receipt.get(key)) for key in required}
    reasons.extend(f"{key}_missing_or_placeholder" for key, value in values.items() if value is None)
    sha = _text(receipt.get("merge_commit_sha"))
    if sha is None or not SHA.fullmatch(sha):
        reasons.append("merge_commit_sha_invalid")
    hours = _hours(receipt.get("engineering_hours"))
    if hours is None:
        reasons.append("engineering_hours_invalid")
    if receipt.get("canonical") is not True:
        reasons.append("canonical_marker_missing")
    if receipt.get("merged") is not True:
        reasons.append("merged_state_not_true")
    for field in ("test_conclusion", "ci_conclusion"):
        value = values[field]
        if value is not None and value.lower() not in PASS:
            reasons.append(f"{field}_not_passing")
    return {
        "packet_id": values["packet_id"], "merge_commit_sha": sha,
        "engineering_hours": hours, "credited": not reasons,
        "reasons": sorted(reasons), "evidence_provenance": values["evidence_provenance"],
    }, reasons


def build_first_withdrawable_dollar(evidence: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Project explicit receipts and estimates without mutating the supplied evidence."""
    supplied = deepcopy(dict(evidence or {}))
    raw_receipts = supplied.get("execution_receipts")
    receipts: Sequence[Any] = raw_receipts if isinstance(raw_receipts, list) else []
    reviewed: list[dict[str, Any]] = []
    invalid_count = 0
    for item in receipts:
        if not isinstance(item, Mapping):
            reviewed.append({"packet_id": None, "credited": False, "reasons": ["receipt_not_mapping"]})
            invalid_count += 1
            continue
        result, reasons = _receipt(item)
        reviewed.append(result)
        invalid_count += bool(reasons)

    ids = [item["packet_id"] for item in reviewed if item.get("packet_id")]
    duplicate_ids = sorted(key for key, count in Counter(ids).items() if count > 1)
    shas: dict[str, set[str]] = defaultdict(set)
    for item in reviewed:
        if item.get("packet_id") and item.get("merge_commit_sha"):
            shas[item["packet_id"]].add(item["merge_commit_sha"].lower())
    conflicting_ids = sorted(key for key, values in shas.items() if len(values) > 1)
    conflicts = sorted(set(duplicate_ids) | set(conflicting_ids))
    for item in reviewed:
        if item.get("packet_id") in conflicts:
            item["credited"] = False
            item["reasons"] = sorted(set(item.get("reasons", [])) | {"duplicate_or_conflicting_packet_evidence"})

    credited = [item for item in reviewed if item.get("credited")]
    completed = round(sum(item["engineering_hours"] for item in credited), 2)
    remaining = supplied.get("remaining_hours")
    remaining = remaining if isinstance(remaining, Mapping) else {}
    low, best, high = (_hours(remaining.get(key)) for key in ("low", "best", "high"))
    bounds_valid = low is not None and best is not None and high is not None and low <= best <= high
    if not bounds_valid:
        low = best = high = None
    denominator = completed + best if best is not None else None
    percentage = round(completed / denominator * 100, 2) if denominator and denominator > 0 else None
    expected = supplied.get("expected_packet_count")
    expected = expected if isinstance(expected, int) and not isinstance(expected, bool) and expected >= 0 else None
    coverage = len(credited) / expected if expected else (1.0 if credited and len(credited) == len(reviewed) else 0.0)
    confidence_score = round(max(0.0, min(1.0, coverage * (1.0 if bounds_valid else 0.75) * (1.0 if not conflicts else 0.5))) * 100, 2)
    external = sorted(str(item) for item in supplied.get("external_dependencies", []) if _text(item)) if isinstance(supplied.get("external_dependencies"), list) else []
    owner_required = supplied.get("owner_action_required") is True
    if conflicts:
        blocker = "REPAIR_CONFLICTING_CANONICAL_EXECUTION_RECEIPTS"
    elif invalid_count or len(credited) < len(reviewed):
        blocker = "REPAIR_INVALID_CANONICAL_EXECUTION_RECEIPTS"
    elif expected is not None and len(credited) < expected:
        blocker = "BACKFILL_MERGED_AND_VALIDATED_EXECUTION_RECEIPTS"
    elif not bounds_valid:
        blocker = "SUPPLY_EVIDENCE_BACKED_REMAINING_HOUR_BOUNDS"
    else:
        blocker = _text(supplied.get("highest_verified_blocker"))
    return {
        "schema": SCHEMA, "mode": "READ_ONLY_EVIDENCE_PROJECTION",
        "provider_status": "EVIDENCE_PROJECTED" if reviewed or bounds_valid else "EVIDENCE_NOT_SUPPLIED",
        "verification_scope": "LOCALLY_RECORDED_ASSERTIONS_NOT_INDEPENDENT_GITHUB_VERIFICATION",
        "hours_completed": completed, "hours_remaining_low": low,
        "hours_remaining_best": best, "hours_remaining_high": high,
        "weeks_remaining_50h_low": round(low / 50, 2) if low is not None else None,
        "weeks_remaining_50h_best": round(best / 50, 2) if best is not None else None,
        "weeks_remaining_50h_high": round(high / 50, 2) if high is not None else None,
        "derived_completion_percentage": percentage,
        "confidence": confidence_score,
        "confidence_basis": {"expected_receipts": expected, "valid_receipts": len(credited), "submitted_receipts": len(reviewed), "remaining_bounds_valid": bounds_valid, "conflicts": conflicts},
        "credited_packet_count": len(credited), "uncredited_packet_count": len(reviewed) - len(credited),
        "receipt_results": sorted(reviewed, key=lambda item: str(item.get("packet_id") or "")),
        "highest_verified_blocker": blocker, "next_verified_blocker": blocker,
        "external_dependencies": external, "owner_action_required": owner_required,
        "repository_presence_credit": 0, "source_evidence_modified": False,
        "protected_actions": _protected_actions(),
    }


def stable_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
