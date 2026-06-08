from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_FIELDS = [
    ("AIOS-PACKET-001-CODEX-ONLY-FIRST-LINE", "CODEX-ONLY PROMPT"),
    ("AIOS-PACKET-002-EXECUTION-TOKEN", "AI_OS EXECUTION TOKEN"),
    ("AIOS-PACKET-003-BOOTSTRAP-REQUIRED", "AI_OS BOOTSTRAP REQUIRED"),
    ("AIOS-PACKET-004-IDENTITY-MARKER", "IDENTITY MARKER"),
    ("AIOS-PACKET-005-SUPERVISOR-IDENTITY", "SUPERVISOR IDENTITY"),
    ("AIOS-PACKET-006-PACKET-ID", "PACKET ID"),
    ("AIOS-PACKET-007-MODE", "MODE"),
    ("AIOS-PACKET-008-ZONE", "ZONE"),
    ("AIOS-PACKET-009-WORKER-IDENTITY", "WORKER IDENTITY"),
    ("AIOS-PACKET-010-LANE", "LANE"),
    ("AIOS-PACKET-011-WORKTREE", "WORKTREE"),
    ("AIOS-PACKET-012-BRANCH", "BRANCH"),
    ("AIOS-PACKET-013-ALLOWED-PATHS", "ALLOWED"),
    ("AIOS-PACKET-014-FORBIDDEN-PATHS", "FORBIDDEN"),
    ("AIOS-PACKET-015-APPROVAL-AUTHORITY", "APPROVAL AUTHORITY"),
    ("AIOS-PACKET-016-VALIDATOR-CHAIN", "VALIDATOR CHAIN"),
    ("AIOS-PACKET-017-STOP-POINT", "STOP POINT"),
    ("AIOS-PACKET-018-MISSION", "MISSION"),
    ("AIOS-PACKET-019-PREFLIGHT", "PREFLIGHT"),
    ("AIOS-PACKET-020-FINAL-REPORT-FORMAT", "FINAL REPORT FORMAT"),
]
PLACEHOLDER_PATTERN = r"@" + r"filename|\{[^}]+\}|\[REAL-[^\]]+\]|path/" + r"to/"


@dataclass
class RuleResult:
    rule_id: str
    severity: str
    passed_boolean: bool
    message: str
    evidence: str


def _contains(text: str, needle: str) -> bool:
    return needle.lower() in text.lower()


def validate_packet_text(text: str, input_path: str = "<text>") -> dict[str, object]:
    rules: list[RuleResult] = []
    lines = text.splitlines()
    first_line_ok = bool(lines and lines[0] == "CODEX-ONLY PROMPT")
    rules.append(
        RuleResult(
            "AIOS-PACKET-001-CODEX-ONLY-FIRST-LINE",
            "BLOCK",
            first_line_ok,
            "Codex packets must begin with CODEX-ONLY PROMPT.",
            lines[0] if lines else "<empty>",
        )
    )
    for rule_id, marker in REQUIRED_FIELDS[1:]:
        rules.append(
            RuleResult(
                rule_id,
                "FAIL",
                _contains(text, marker),
                f"Required marker present: {marker}",
                marker,
            )
        )
    hazard_rules = [
        ("AIOS-PACKET-021-LEGACY-PATH-BLOCK", "BLOCK", r"C:\\Users\\mylab\\OneDrive\\GitHub\\ai-rtony91_Ai_Os_CLEAN", "legacy active worktree path"),
        ("AIOS-PACKET-022-PLACEHOLDER-BLOCK", "BLOCK", PLACEHOLDER_PATTERN, "unresolved placeholder"),
        ("AIOS-PACKET-023-DUPLICATE-AUTHORITY-BLOCK", "FAIL", r"duplicate governance authority|parallel governance head", "duplicate authority language"),
        ("AIOS-PACKET-024-LIVE-TRADING-BLOCK", "BLOCK", r"enable live trading|real_order|live_order|place_order", "live trading enablement"),
        ("AIOS-PACKET-025-BROKER-BLOCK", "BLOCK", r"broker execution|connect broker|OANDA integration", "broker execution enablement"),
        ("AIOS-PACKET-026-SECRET-PRINTING-BLOCK", "BLOCK", r"print secret|show secret|display token|print token", "secret printing instruction"),
    ]
    for rule_id, severity, pattern, label in hazard_rules:
        found = re.search(pattern, text, re.IGNORECASE) is not None
        rules.append(RuleResult(rule_id, severity, not found, f"Block {label}.", label))
    for rule_id, action in [
        ("AIOS-PACKET-027-COMMIT-APPROVAL", "commit"),
        ("AIOS-PACKET-028-PUSH-APPROVAL", "push"),
        ("AIOS-PACKET-029-MERGE-APPROVAL", "merge"),
    ]:
        asks_action = re.search(rf"\b{action}\b", text, re.IGNORECASE) is not None
        explicit = re.search(rf"explicitly approves.*\b{action}\b", text, re.IGNORECASE | re.DOTALL) is not None
        rules.append(RuleResult(rule_id, "WARN", (not asks_action) or explicit, f"{action} requires separate explicit approval.", action))
    rules.append(
        RuleResult(
            "AIOS-PACKET-030-SAFE-NEXT-ACTION",
            "WARN",
            _contains(text, "SAFE NEXT"),
            "Packet should include a safe next action.",
            "SAFE NEXT",
        )
    )
    errors = [asdict(rule) for rule in rules if not rule.passed_boolean and rule.severity in {"FAIL", "BLOCK"}]
    warnings = [asdict(rule) for rule in rules if not rule.passed_boolean and rule.severity == "WARN"]
    status = "PASS"
    if any(rule["severity"] == "BLOCK" for rule in errors):
        status = "BLOCKED"
    elif errors:
        status = "FAIL"
    elif warnings:
        status = "WARN"
    return {
        "validator_name": "aios_governance_validator",
        "version": "1.0",
        "timestamp_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "input_path": input_path,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "rules_checked": [asdict(rule) for rule in rules],
        "blocked_actions": [item["message"] for item in errors if item["severity"] == "BLOCK"],
        "safe_next_action": "Repair packet fields before execution." if status != "PASS" else "Proceed only within packet scope.",
    }


def sample_valid_packet() -> str:
    return """CODEX-ONLY PROMPT
AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED
IDENTITY MARKER:
AI_OS_LOCAL_REPO_OPERATOR_PACKET
SUPERVISOR IDENTITY:
ChatGPT plans. Codex executes. Anthony approves.
PACKET ID:
AIOS-SAMPLE-VALID-001
MODE:
DRY_RUN
ZONE:
VALIDATION
WORKER IDENTITY:
Codex validator
LANE:
SAMPLE_VALIDATION_ONLY
WORKTREE:
C:\\Dev\\Ai.Os
BRANCH:
resolve after preflight
ALLOWED PATHS:
Reports/
FORBIDDEN PATHS:
AGENTS.md
APPROVAL AUTHORITY:
Anthony
MISSION:
Validate packet shape.
PREFLIGHT:
git status --short --branch
VALIDATOR CHAIN:
git diff --check
STOP POINT:
Stop after report.
FINAL REPORT FORMAT:
SUMMARY:
SAFE NEXT ACTION:
git status --short --branch
STATUS:
DRY_RUN COMPLETE
"""


def sample_invalid_packet() -> str:
    placeholder = "{" + "feature" + "}"
    return f"CODEX-ONLY PROMPT\nMISSION:\nApply {placeholder} and print token.\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AI_OS executable packet shape.")
    parser.add_argument("--input")
    parser.add_argument("--sample-check", action="store_true")
    args = parser.parse_args()
    if args.sample_check:
        valid = validate_packet_text(sample_valid_packet(), "<sample-valid>")
        invalid = validate_packet_text(sample_invalid_packet(), "<sample-invalid>")
        payload = {"valid": valid, "invalid": invalid}
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if valid["status"] == "PASS" and invalid["status"] in {"FAIL", "BLOCKED"} else 1
    if not args.input:
        print(json.dumps({"status": "BLOCKED", "reason": "--input or --sample-check required"}, indent=2))
        return 2
    path = Path(args.input)
    print(json.dumps(validate_packet_text(path.read_text(encoding="utf-8"), str(path)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
