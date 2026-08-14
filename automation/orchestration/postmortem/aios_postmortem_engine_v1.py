"""AIOS post-mortem learning and bounded recovery engine, version 1.

This module only analyzes supplied evidence and writes optional reports.  It has
no authority to mutate Git, queues, workers, governance, trading, or production.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

VERSION = "1.0"
REPORT_ROOT = Path("Reports/orchestration/postmortem")
DURABILITY_STATES = {"REMOTE_VERIFIED", "USER_VISIBLE_CAPSULE_VERIFIED", "AT_RISK"}
OUTCOMES = (
    "SUCCESS", "RECOVERED", "BLOCKED_GOVERNANCE", "BLOCKED_EXTERNAL",
    "REPOSITORY_STATE_MISMATCH", "DIRTY_WORKTREE", "ORIGIN_ABSENT",
    "ORIGIN_INCORRECT", "AUTHORIZATION_UNAVAILABLE", "LOCAL_COMMIT_AT_RISK",
    "MISSING_COMMIT", "MISSING_BRANCH", "WORKER_LEASE_EXPIRED",
    "WORKER_STILL_ACTIVE", "STALE_APPLICATION_LOCK", "GIT_LOCK_REVIEW_REQUIRED",
    "ORPHANED_APPLY", "DUPLICATE_APPLY", "PACKET_COLLISION", "MALFORMED_PACKET",
    "VALIDATION_FAILURE", "CI_FAILURE", "CORRUPT_STATE", "QUARANTINED",
    "UNSAFE_TO_CONTINUE",
)
NEXT_ACTION = {
    "SUCCESS": "CLOSE_AFTER_VERIFICATION", "RECOVERED": "RUN_VALIDATORS",
    "BLOCKED_GOVERNANCE": "REQUEST_HUMAN_OWNER_REVIEW",
    "BLOCKED_EXTERNAL": "WAIT_FOR_EXTERNAL_DEPENDENCY",
    "REPOSITORY_STATE_MISMATCH": "REVIEW_REPOSITORY_IDENTITY",
    "DIRTY_WORKTREE": "PRESERVE_AND_REVIEW_WORKTREE",
    "ORIGIN_ABSENT": "REQUEST_APPROVAL_TO_ADD_ORIGIN",
    "ORIGIN_INCORRECT": "REVIEW_REQUIRED",
    "AUTHORIZATION_UNAVAILABLE": "REQUEST_PUBLICATION_AUTHORIZATION",
    "LOCAL_COMMIT_AT_RISK": "PUBLISH_AND_VERIFY_COMMIT",
    "MISSING_COMMIT": "REVIEW_REQUIRED", "MISSING_BRANCH": "REVIEW_REQUIRED",
    "WORKER_LEASE_EXPIRED": "RECLAIM_WITH_BOUNDED_PLAYBOOK",
    "WORKER_STILL_ACTIVE": "WAIT_FOR_WORKER",
    "STALE_APPLICATION_LOCK": "RECLAIM_WITH_BOUNDED_PLAYBOOK",
    "GIT_LOCK_REVIEW_REQUIRED": "REVIEW_REQUIRED",
    "ORPHANED_APPLY": "RECONCILE_APPLY_EVIDENCE",
    "DUPLICATE_APPLY": "BLOCK_DUPLICATE_APPLY",
    "PACKET_COLLISION": "REVIEW_REQUIRED", "MALFORMED_PACKET": "REJECT_PACKET",
    "VALIDATION_FAILURE": "REPAIR_AND_RERUN_VALIDATORS",
    "CI_FAILURE": "INSPECT_REQUIRED_CI",
    "CORRUPT_STATE": "QUARANTINE_EVIDENCE", "QUARANTINED": "REVIEW_REQUIRED",
    "UNSAFE_TO_CONTINUE": "REVIEW_REQUIRED",
}
REQUIRED = (
    "event_id incident_id packet_id task_id run_id worker_identity supervisor_identity lane timestamp "
    "repository_identity worktree branch base_sha head_sha tree_sha worktree_state remote_state "
    "failing_stage sanitized_detection_signature evidence_references evidence_hashes "
    "outcome_classification root_cause_status verified_root_cause hypotheses recovery_attempts "
    "recovery_result validators_after_recovery durability_state lesson_status promotion_status "
    "next_safe_action"
).split()
SECRET_KEYS = re.compile(r"(?:password|passwd|secret|token|credential|api[_-]?key|account|broker_payload)", re.I)
HEX_HASH = re.compile(r"^[0-9a-f]{64}$")
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")

TRANSITIONS = {
    "OBSERVED": {"EVIDENCE_CAPTURED", "QUARANTINED"},
    "EVIDENCE_CAPTURED": {"CLASSIFIED", "QUARANTINED"},
    "CLASSIFIED": {"LESSON_PROPOSED", "RECOVERY_PLANNED", "REVIEW_REQUIRED", "QUARANTINED"},
    "LESSON_PROPOSED": {"RECOVERY_PLANNED", "REVIEW_REQUIRED"},
    "RECOVERY_PLANNED": {"RECOVERABLE", "REVIEW_REQUIRED", "QUARANTINED"},
    "RECOVERABLE": {"RECOVERED", "REVIEW_REQUIRED"},
    "RECOVERED": {"VERIFIED", "REVIEW_REQUIRED", "QUARANTINED"},
    "VERIFIED": {"CLOSED"}, "REVIEW_REQUIRED": {"RECOVERY_PLANNED", "QUARANTINED"},
    "QUARANTINED": {"REVIEW_REQUIRED"}, "CLOSED": set(),
}

class ValidationError(ValueError): pass
class DuplicateEventError(ValidationError): pass

def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)

def evidence_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()

def _walk(value: Any, key: str = "") -> None:
    if SECRET_KEYS.search(key): raise ValidationError(f"secret-like field rejected: {key}")
    if isinstance(value, float) and not math.isfinite(value): raise ValidationError("non-finite value")
    if isinstance(value, Mapping):
        for k, v in value.items(): _walk(v, str(k))
    elif isinstance(value, list):
        for v in value: _walk(v, key)

def validate_event(event: Mapping[str, Any], seen_event_ids: set[str] | None = None) -> dict[str, Any]:
    if not isinstance(event, Mapping): raise ValidationError("event must be an object")
    unknown = set(event) - set(REQUIRED)
    missing = set(REQUIRED) - set(event)
    if missing or unknown: raise ValidationError(f"schema fields missing={sorted(missing)} unknown={sorted(unknown)}")
    _walk(event)
    for field in ("event_id", "incident_id", "packet_id", "task_id", "run_id"):
        if not isinstance(event[field], str) or not IDENTIFIER.fullmatch(event[field]): raise ValidationError(f"invalid {field}")
    if seen_event_ids is not None and event["event_id"] in seen_event_ids: raise DuplicateEventError(event["event_id"])
    for field in ("evidence_references", "evidence_hashes", "hypotheses", "recovery_attempts", "validators_after_recovery"):
        if not isinstance(event[field], list) or len(event[field]) != len({canonical_json(x) for x in event[field]}):
            raise ValidationError(f"{field} must be a duplicate-free array")
    if any(not isinstance(x, str) or not HEX_HASH.fullmatch(x) for x in event["evidence_hashes"]): raise ValidationError("invalid evidence hash")
    if event["outcome_classification"] not in OUTCOMES: raise ValidationError("unsupported outcome")
    if event["durability_state"] not in DURABILITY_STATES: raise ValidationError("unsupported durability state")
    if event["remote_state"] == "LOCAL_ONLY" and event["durability_state"] != "AT_RISK": raise ValidationError("local-only work must be AT_RISK")
    if event["root_cause_status"] == "VERIFIED" and not event["verified_root_cause"]: raise ValidationError("verified cause missing")
    if event["root_cause_status"] != "VERIFIED" and event["verified_root_cause"] is not None: raise ValidationError("unverified cause presented as verified")
    p = Path(event["worktree"])
    if ".." in p.parts: raise ValidationError("path escape")
    try: datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
    except (ValueError, AttributeError): raise ValidationError("invalid timestamp") from None
    result = deepcopy(dict(event))
    if seen_event_ids is not None: seen_event_ids.add(event["event_id"])
    return result

def classify(facts: Mapping[str, Any]) -> dict[str, str]:
    rules = (
        ("corrupt_evidence", "CORRUPT_STATE"), ("duplicate_apply", "DUPLICATE_APPLY"),
        ("packet_collision", "PACKET_COLLISION"), ("git_index_lock_persistent", "GIT_LOCK_REVIEW_REQUIRED"),
        ("application_lock_expired", "STALE_APPLICATION_LOCK"), ("worker_active", "WORKER_STILL_ACTIVE"),
        ("worker_lease_expired", "WORKER_LEASE_EXPIRED"), ("dirty_worktree", "DIRTY_WORKTREE"),
        ("repository_mismatch", "REPOSITORY_STATE_MISMATCH"), ("origin_incorrect", "ORIGIN_INCORRECT"),
        ("origin_absent", "ORIGIN_ABSENT"), ("authorization_unavailable", "AUTHORIZATION_UNAVAILABLE"),
        ("missing_branch", "MISSING_BRANCH"), ("missing_commit", "MISSING_COMMIT"),
        ("local_commit_only", "LOCAL_COMMIT_AT_RISK"), ("orphaned_apply", "ORPHANED_APPLY"),
        ("validators_failed", "VALIDATION_FAILURE"), ("ci_failed", "CI_FAILURE"),
        ("recovered", "RECOVERED"), ("success", "SUCCESS"),
    )
    outcome = next((name for flag, name in rules if facts.get(flag) is True), "UNSAFE_TO_CONTINUE")
    return {"outcome_classification": outcome, "next_safe_action": NEXT_ACTION[outcome],
            "durability_state": "AT_RISK" if facts.get("local_commit_only") or not facts.get("remote_verified") else "REMOTE_VERIFIED"}

class PatternMemory:
    def __init__(self) -> None:
        self.events: dict[str, str] = {}; self.incidents: dict[str, dict[str, Any]] = {}
    def observe(self, event: Mapping[str, Any], *, safety_critical: bool = False) -> dict[str, Any]:
        valid = validate_event(event)
        digest = evidence_hash(valid)
        eid, iid, sig = valid["event_id"], valid["incident_id"], valid["sanitized_detection_signature"]
        if eid in self.events:
            if self.events[eid] != digest: raise ValidationError("mutable replay rejected")
            return self.pattern(sig, safety_critical=safety_critical, duplicate=True)
        self.events[eid] = digest
        if iid in self.incidents and self.incidents[iid]["digest"] != digest: raise ValidationError("contradictory incident replay")
        self.incidents.setdefault(iid, {"signature": sig, "digest": digest, "hashes": valid["evidence_hashes"]})
        return self.pattern(sig, safety_critical=safety_critical)
    def pattern(self, signature: str, *, safety_critical: bool = False, duplicate: bool = False) -> dict[str, Any]:
        matches = sorted(i for i, x in self.incidents.items() if x["signature"] == signature)
        eligible = len(matches) >= 2 and not safety_critical
        return {"schema_version": VERSION, "signature": signature, "incident_ids": matches,
                "independent_incident_count": len(matches), "duplicate_suppressed": duplicate,
                "promotion_eligible": eligible, "human_owner_review_required": safety_critical or eligible,
                "authority": "OPERATIONAL_EVIDENCE_ONLY"}

def build_hypothesis(hypothesis_id: str, proposed_cause: str, supporting: Iterable[str], contradicting: Iterable[str], proposed_test: str, test_status: str) -> dict[str, Any]:
    support, contradict = sorted(set(supporting)), sorted(set(contradicting))
    passed = test_status == "PASSED" and bool(support) and not contradict
    return {"hypothesis_id": hypothesis_id, "proposed_cause": proposed_cause,
            "supporting_incidents": support, "contradicting_incidents": contradict,
            "proposed_test": proposed_test, "test_status": test_status,
            "confidence_level": "VERIFIED" if passed else "UNVERIFIED",
            "promotion_eligible": passed, "rejection_reason": None if passed else "BOUNDED_TEST_NOT_PASSED_OR_CONTRADICTED"}

def learn(event: Mapping[str, Any]) -> dict[str, Any]:
    valid = validate_event(event)
    verified = valid["root_cause_status"] == "VERIFIED"
    return {"schema_version": VERSION, "lesson_status": "PROPOSED_OPERATIONAL_LESSON",
            "authority": "EVIDENCE_NOT_GOVERNANCE", "detection_signature": valid["sanitized_detection_signature"],
            "verified_root_cause": valid["verified_root_cause"] if verified else None,
            "root_cause_status": valid["root_cause_status"], "evidence_hashes": sorted(valid["evidence_hashes"]),
            "recovery_attempts": valid["recovery_attempts"], "recovery_result": valid["recovery_result"],
            "prevention_guidance": "Apply the bounded recovery action and rerun named validators.",
            "governance_promotion": "SEPARATE_HUMAN_OWNER_APPROVAL_REQUIRED"}

def transition(current: str, target: str) -> dict[str, Any]:
    if current == target: return {"state": current, "changed": False}
    if current not in TRANSITIONS or target not in TRANSITIONS[current]: raise ValidationError(f"invalid transition {current}->{target}")
    return {"state": target, "changed": True}

class PostmortemEngine:
    def __init__(self) -> None: self.seen_event_ids: set[str] = set(); self.patterns = PatternMemory()
    def analyze(self, event: Mapping[str, Any]) -> dict[str, Any]: return validate_event(event, self.seen_event_ids)
    def classify(self, facts: Mapping[str, Any]) -> dict[str, str]: return classify(facts)
    def learn(self, event: Mapping[str, Any]) -> dict[str, Any]: return learn(event)
    def plan(self, facts: Mapping[str, Any]) -> dict[str, str]: return classify(facts)
    def verify(self, facts: Mapping[str, Any]) -> dict[str, Any]: return {"verified": bool(facts.get("validators_passed") and facts.get("evidence_intact")), "state": "VERIFIED" if facts.get("validators_passed") and facts.get("evidence_intact") else "REVIEW_REQUIRED"}
    def close(self, state: str) -> dict[str, Any]: return transition(state, "CLOSED")

def _safe_output(path: str) -> Path:
    candidate = Path(path)
    resolved_root = (Path.cwd() / REPORT_ROOT).resolve()
    resolved = (Path.cwd() / candidate).resolve()
    if resolved != resolved_root and resolved_root not in resolved.parents: raise ValidationError("output path outside approved report root")
    return resolved

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("analyze", "classify", "learn", "plan", "verify", "close")); parser.add_argument("input"); parser.add_argument("--output")
    args = parser.parse_args(argv); data = json.loads(Path(args.input).read_text(encoding="utf-8")); engine = PostmortemEngine()
    result = getattr(engine, args.command)(data if args.command != "close" else str(data["state"]))
    rendered = canonical_json(result) + "\n"
    if args.output:
        output = _safe_output(args.output); output.parent.mkdir(parents=True, exist_ok=True); output.write_text(rendered, encoding="utf-8")
    else: print(rendered, end="")
    return 0

if __name__ == "__main__": raise SystemExit(main())
