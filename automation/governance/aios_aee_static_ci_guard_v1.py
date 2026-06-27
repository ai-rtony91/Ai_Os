from __future__ import annotations

"""Static CI and governance guard for compound campaign artifacts."""

from dataclasses import asdict, dataclass
import re
from typing import Iterable

from .aios_aee_campaign_state_classifier_v1 import FORBIDDEN_PATH_PREFIXES

MANDATORY_SAFETY_TEXT = [
    "This artifact does not authorize broker/API access.",
    "This artifact does not authorize credential access.",
    "This artifact does not authorize trading execution.",
    "This artifact does not authorize money movement.",
    "This artifact does not authorize commit/push/merge without explicit Human Owner approval.",
]

SENSITIVE_ASSIGNMENT_RE = re.compile(
    r"(?mi)^\s*(api_key|apikey|secret|password|token|broker)\s*=",
)
PLACEHOLDER_PATTERN = re.compile(
    r"@filename|\{[^}]+\}|TODO|TBD|path/to/",
    re.IGNORECASE,
)
BROAD_GIT_ADD_PATTERNS = (
    re.compile(r"(?m)^\s*git\s+add\s+\.\s*$", re.IGNORECASE),
    re.compile(r"(?m)^\s*git\s+add\s+--all\s*$", re.IGNORECASE),
    re.compile(r"(?m)^\s*git\s+add\s+-A\s*$", re.IGNORECASE),
    re.compile(r"(?m)^\s*git\s+add\s+-a\s*$", re.IGNORECASE),
)
BRANCH_SWITCH_RE = re.compile(r"git\s+switch\s+main", re.IGNORECASE)
SENSITIVE_BRANCH_RE = re.compile(r"git\s+pull\s+--ff-only\s+origin\s+main", re.IGNORECASE)


@dataclass(frozen=True)
class StaticGuardFinding:
    code: str
    severity: str
    message: str
    evidence: str


def _normalise_path(path: str) -> str:
    return path.replace("\\", "/").lower()


def scan_sensitive_assignment_names(text: str | Iterable[str]) -> list[StaticGuardFinding]:
    texts = [text] if isinstance(text, str) else list(text)
    findings: list[StaticGuardFinding] = []
    for item in texts:
        for line in str(item).splitlines():
            if SENSITIVE_ASSIGNMENT_RE.search(line):
                findings.append(
                    StaticGuardFinding(
                        code="AIOS-AEE-COMP-GUARD-1001",
                        severity="FAIL",
                        message="sensitive assignment name detected",
                        evidence=line.strip(),
                    )
                )
    return findings


def scan_broad_git_add(text: str) -> list[StaticGuardFinding]:
    findings: list[StaticGuardFinding] = []
    for pattern in BROAD_GIT_ADD_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                StaticGuardFinding(
                    code="AIOS-AEE-COMP-GUARD-1002",
                    severity="FAIL",
                    message="broad git add command detected",
                    evidence=match.group(0).strip(),
                )
            )
    return findings


def scan_placeholder_commands(text: str) -> list[StaticGuardFinding]:
    if not PLACEHOLDER_PATTERN.search(text):
        return []
    return [
        StaticGuardFinding(
            code="AIOS-AEE-COMP-GUARD-1003",
            severity="FAIL",
            message="placeholder token in executable block",
            evidence=PLACEHOLDER_PATTERN.search(text).group(0),
        )
    ]


def scan_protected_action_mix(publish_block: str, merge_block: str) -> list[StaticGuardFinding]:
    findings: list[StaticGuardFinding] = []
    lower_pub = publish_block.lower()
    lower_merge = merge_block.lower()

    if "gh pr merge" in lower_pub:
        findings.append(
            StaticGuardFinding(
                code="AIOS-AEE-COMP-GUARD-1004",
                severity="FAIL",
                message="merge should be in block2 only",
                evidence="gh pr merge in publish block",
            )
        )
    if "git switch" in lower_pub or "git pull --ff-only origin main" in lower_pub:
        findings.append(
            StaticGuardFinding(
                code="AIOS-AEE-COMP-GUARD-1004",
                severity="FAIL",
                message="merge/sync commands should be in block2 only",
                evidence="merge/sync in publish block",
            )
        )
    if "git add " in lower_merge and "git add " not in lower_merge.split("git add ")[0]:
        findings.append(
            StaticGuardFinding(
                code="AIOS-AEE-COMP-GUARD-1005",
                severity="FAIL",
                message="publish-only command appeared in merge/sync block",
                evidence="git add in merge block",
            )
        )
    if "git commit" in lower_merge:
        findings.append(
            StaticGuardFinding(
                code="AIOS-AEE-COMP-GUARD-1005",
                severity="FAIL",
                message="publish-only command appeared in merge/sync block",
                evidence="git commit in merge block",
            )
        )
    if "gh pr checks --watch" in lower_merge:
        findings.append(
            StaticGuardFinding(
                code="AIOS-AEE-COMP-GUARD-1006",
                severity="WARN",
                message="check-watch should remain in block1",
                evidence="gh pr checks --watch in merge block",
            )
        )

    publish_lines = [line.strip().lower() for line in publish_block.splitlines() if line.strip()]
    for index, line in enumerate(publish_lines[:-1]):
        if "gh pr checks --watch" in line and "gh pr merge" in publish_lines[index + 1]:
            findings.append(
                StaticGuardFinding(
                    code="AIOS-AEE-COMP-GUARD-1007",
                    severity="WARN",
                    message="merge appears immediately after check-watch in publish block",
                    evidence=line,
                )
            )

    if "gh pr checks --watch" not in lower_pub:
        findings.append(
            StaticGuardFinding(
                code="AIOS-AEE-COMP-GUARD-1008",
                severity="FAIL",
                message="block1 must include gh pr checks --watch",
                evidence="missing check-watch",
            )
        )
    return findings


def scan_forbidden_paths(changed_files: Iterable[str]) -> list[StaticGuardFinding]:
    findings: list[StaticGuardFinding] = []
    for item in changed_files:
        if _normalise_path(item).startswith(tuple(p.lower().rstrip("/") for p in FORBIDDEN_PATH_PREFIXES)):
            findings.append(
                StaticGuardFinding(
                    code="AIOS-AEE-COMP-GUARD-1009",
                    severity="FAIL",
                    message="forbidden path referenced",
                    evidence=item,
                )
            )
    return findings


def scan_report_checkpoint_contradiction(
    report_text: str,
    checkpoint_text: str,
) -> list[StaticGuardFinding]:
    report_status = ""
    checkpoint_complete = False
    for line in report_text.splitlines():
        if line.lower().startswith("final_status:"):
            report_status = line.split(":", 1)[1].strip().lower()
    for line in checkpoint_text.splitlines():
        if line.lower().startswith("current_phase:") and re.search(r"\bcomplete\b", line.lower()):
            checkpoint_complete = True
    if report_status == "complete" and not checkpoint_complete:
        return [
            StaticGuardFinding(
                code="AIOS-AEE-COMP-GUARD-1010",
                severity="WARN",
                message="report is complete but checkpoint is not marked complete",
                evidence="report status/checkpoint mismatch",
            )
        ]
    if report_status != "complete" and checkpoint_complete:
        return [
            StaticGuardFinding(
                code="AIOS-AEE-COMP-GUARD-1011",
                severity="WARN",
                message="checkpoint complete but report status not complete",
                evidence="report/checkpoint mismatch",
            )
        ]
    return []


def scan_static_ci_guard(
    *,
    publish_block: str,
    merge_block: str,
    changed_files: Iterable[str],
    report_text: str = "",
    checkpoint_text: str = "",
) -> list[StaticGuardFinding]:
    findings: list[StaticGuardFinding] = []
    findings.extend(scan_sensitive_assignment_names([publish_block, merge_block]))
    findings.extend(scan_broad_git_add(publish_block))
    findings.extend(scan_broad_git_add(merge_block))
    findings.extend(scan_placeholder_commands(publish_block))
    findings.extend(scan_placeholder_commands(merge_block))
    findings.extend(scan_protected_action_mix(publish_block, merge_block))
    findings.extend(scan_forbidden_paths(changed_files))
    findings.extend(scan_report_checkpoint_contradiction(report_text, checkpoint_text))

    combined = report_text + " " + checkpoint_text
    for item in MANDATORY_SAFETY_TEXT:
        if item not in combined:
            findings.append(
                StaticGuardFinding(
                    code="AIOS-AEE-COMP-GUARD-1012",
                    severity="FAIL",
                    message="safety boundary statement missing",
                    evidence=item,
                )
            )
    return findings


def result_to_markdown(findings: Iterable[StaticGuardFinding]) -> str:
    lines = ["# AIOS AEE Compound Campaign Static Guard", "", "## Findings"]
    items = list(findings)
    if not items:
        lines.append("- no findings")
        return "\n".join(lines) + "\n"

    for item in items:
        lines.append(f"- {item.code} {item.severity}: {item.message}")
        lines.append(f"  - {item.evidence}")
    return "\n".join(lines) + "\n"


def result_to_jsonable_dict(findings: Iterable[StaticGuardFinding]) -> dict[str, object]:
    return {"findings": [asdict(item) for item in findings]}


def result_to_operator_text(findings: Iterable[StaticGuardFinding]) -> str:
    items = list(findings)
    fails = sum(1 for item in items if item.severity == "FAIL")
    warns = sum(1 for item in items if item.severity == "WARN")
    return f"findings_fail={fails} findings_warn={warns}"
