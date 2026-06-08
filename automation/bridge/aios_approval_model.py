from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


DECISIONS = {"WAIT", "BLOCKED", "REQUIRES_APPROVAL", "APPLY_READY", "APPLY_EXECUTED", "COMPLETE"}
PROTECTED_ACTIONS = {"commit", "push", "merge", "reset", "stash", "clean", "pr", "branch protection"}
FORBIDDEN_TERMS = {"live trading", "live_order", "real_order", "place_order", "broker execution", "oanda"}
SECRET_TERMS = {"secret", "token", "api_key", "apikey", "password", "credential", "private_key", "bearer"}
PLACEHOLDER_MARKERS = [
    "@" + "filename",
    r"\{[^}]+\}",
    r"\[" + "REAL-" + r"[^\]]+\]",
    "path/" + "to/",
    "TO" + "DO",
    "TB" + "D",
]
PLACEHOLDER_PATTERN = re.compile("|".join(PLACEHOLDER_MARKERS), re.IGNORECASE)


@dataclass
class ApprovalRecord:
    approval_id: str
    source_packet_id: str
    created_utc: str
    operator: str
    decision: str
    mode_requested: str
    mode_allowed: str
    scope_summary: str
    allowed_paths: list[str]
    forbidden_paths: list[str]
    protected_actions_detected: list[str]
    approval_text: str
    approval_text_hash: str
    evidence_files: list[str]
    validator_chain: list[str]
    expires_utc: str
    status: str
    blockers: list[str] = field(default_factory=list)
    safe_next_command: str = "No command recommended."

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ApprovalRecord":
        text = str(data.get("approval_text", ""))
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return cls(
            approval_id=str(data.get("approval_id", "")),
            source_packet_id=str(data.get("source_packet_id", "")),
            created_utc=str(data.get("created_utc", "")),
            operator=str(data.get("operator", "")),
            decision=str(data.get("decision", "")),
            mode_requested=str(data.get("mode_requested", "")),
            mode_allowed=str(data.get("mode_allowed", "")),
            scope_summary=str(data.get("scope_summary", "")),
            allowed_paths=list(data.get("allowed_paths", [])),
            forbidden_paths=list(data.get("forbidden_paths", [])),
            protected_actions_detected=list(data.get("protected_actions_detected", [])),
            approval_text=text,
            approval_text_hash=str(data.get("approval_text_hash", digest)) or digest,
            evidence_files=list(data.get("evidence_files", [])),
            validator_chain=list(data.get("validator_chain", [])),
            expires_utc=str(data.get("expires_utc", "")),
            status=str(data.get("status", "")),
            blockers=list(data.get("blockers", [])),
            safe_next_command=str(data.get("safe_next_command", "No command recommended.")),
        )


@dataclass
class ApprovalDecision:
    status: str
    blockers: list[str]
    warnings: list[str]
    safe_next_command: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _is_expired(expires_utc: str) -> bool:
    if not expires_utc:
        return False
    try:
        expiry = datetime.fromisoformat(expires_utc.replace("Z", "+00:00"))
    except ValueError:
        return True
    return datetime.now(timezone.utc) > expiry


def compress_approval(record: ApprovalRecord) -> ApprovalDecision:
    text = " ".join(
        [
            record.approval_text,
            record.scope_summary,
            " ".join(record.allowed_paths),
            " ".join(record.forbidden_paths),
        ]
    ).lower()
    blockers: list[str] = []
    warnings: list[str] = []

    if not record.approval_text.strip():
        return ApprovalDecision("WAIT", ["approval_text_missing"], [], "Collect explicit Anthony approval.")
    if "apply" not in text and "execute" not in text:
        return ApprovalDecision("WAIT", ["explicit_apply_language_missing"], [], "Request explicit APPLY or execution approval.")
    if not record.scope_summary.strip() or not record.allowed_paths:
        blockers.append("scope_or_allowed_paths_missing")
    if PLACEHOLDER_PATTERN.search(text):
        blockers.append("unresolved_placeholder")
    if any(term in text for term in FORBIDDEN_TERMS):
        blockers.append("live_trading_or_broker_request_blocked")
    if any(term in text for term in SECRET_TERMS):
        blockers.append("secret_or_credential_request_blocked")
    protected = set(action.lower() for action in record.protected_actions_detected)
    for action in PROTECTED_ACTIONS:
        pattern = r"\b" + re.escape(action) + r"\b"
        if re.search(pattern, text):
            protected.add(action)
    if protected:
        if "commit" in protected and "explicit commit approval" not in text:
            warnings.append("commit_requires_separate_approval")
        if "push" in protected and "explicit push approval" not in text:
            warnings.append("push_requires_separate_approval")
        if any(action not in {"commit", "push"} for action in protected):
            warnings.append("protected_action_requires_anthony_approval")
    if _is_expired(record.expires_utc):
        return ApprovalDecision("REQUIRES_APPROVAL", ["approval_expired"], warnings, "Refresh approval against current repo state.")
    if blockers:
        return ApprovalDecision("BLOCKED", blockers, warnings, "Do not apply. Repair approval packet.")
    if warnings:
        return ApprovalDecision("REQUIRES_APPROVAL", [], warnings, "Request separate protected-action approval.")
    if not record.validator_chain:
        return ApprovalDecision("REQUIRES_APPROVAL", [], ["validator_chain_missing"], "Add validator chain before APPLY.")
    return ApprovalDecision("APPLY_READY", [], [], "Run scoped APPLY command, then stop before commit or push.")


def load_record(path: Path) -> ApprovalRecord:
    return ApprovalRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))
