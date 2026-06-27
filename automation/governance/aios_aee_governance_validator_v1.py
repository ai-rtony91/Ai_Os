from __future__ import annotations

"""Deterministic local validator for AEE governance and workflow artifacts."""

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


VALIDATOR_NAME = "AIOS AEE Governance Validator V1"
VALIDATOR_VERSION = "1.0.0"
REPO_DEFAULT = Path(__file__).resolve().parents[2]


REQUIRED_DAOCTRINE_ARTIFACTS = [
    "docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md",
    "docs/workflows/AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md",
    "docs/workflows/AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md",
    "docs/governance/AIOS_FAILURE_MEMORY_V1.md",
    "docs/workflows/AIOS_CAMPAIGN_CHECKPOINT_AND_RESUME_V1.md",
    "docs/governance/AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md",
    "docs/workflows/AIOS_ISOLATED_WORKTREE_CAMPAIGN_EXECUTION_V1.md",
    "docs/workflows/AIOS_LONG_CAMPAIGN_CODEX_OPERATING_MODE_V1.md",
    "docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md",
    "docs/workflows/AIOS_GITHUB_CI_FAILURE_RECOVERY_V1.md",
]

REQUIRED_VALIDATOR_ARTIFACTS = [
    "docs/workflows/AIOS_AEE_GOVERNANCE_VALIDATOR_V1.md",
    "automation/governance/aios_aee_governance_validator_v1.py",
    "scripts/governance/run_aios_aee_governance_validator_v1.py",
    "tests/governance/test_aios_aee_governance_validator_v1.py",
    "tests/fixtures/governance/aee_validator/",
    "Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_CHECKPOINT.md",
    "Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_REPORT.md",
]

REQUIRED_REPORT_FILES = [
    "Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_CHECKPOINT.md",
    "Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_REPORT.md",
]

REQUIRED_ARTIFACTS = REQUIRED_DAOCTRINE_ARTIFACTS + REQUIRED_VALIDATOR_ARTIFACTS

REQUIRED_SECTION_ARTIFACTS = [
    *REQUIRED_DAOCTRINE_ARTIFACTS,
    "docs/workflows/AIOS_AEE_GOVERNANCE_VALIDATOR_V1.md",
]

REQUIRED_SAFETY_ARTIFACTS = REQUIRED_SECTION_ARTIFACTS + [
    "docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md"
]

SAFETY_PHRASES = [
    "does not authorize broker/API access",
    "does not authorize credential access",
    "does not authorize trading execution",
    "does not authorize money movement",
    "does not authorize commit/push/merge without explicit Human Owner approval",
]

CROSS_LINK_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md": (
        "AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md",
        "AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md",
        "AIOS_FAILURE_MEMORY_V1.md",
    ),
    "docs/workflows/AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md": (
        "AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md",
        "AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md",
        "AIOS_CAMPAIGN_CHECKPOINT_AND_RESUME_V1.md",
    ),
    "docs/workflows/AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md": (
        "AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md",
        "AIOS_FAILURE_MEMORY_V1.md",
    ),
    "docs/governance/AIOS_FAILURE_MEMORY_V1.md": (
        "AIOS_CAMPAIGN_CHECKPOINT_AND_RESUME_V1.md",
        "AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md",
    ),
    "docs/workflows/AIOS_CAMPAIGN_CHECKPOINT_AND_RESUME_V1.md": (
        "AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md",
        "AIOS_AEE_GOVERNANCE_VALIDATOR_V1.md",
    ),
    "docs/governance/AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md": (
        "AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md",
        "AIOS_ISOLATED_WORKTREE_CAMPAIGN_EXECUTION_V1.md",
    ),
    "docs/workflows/AIOS_ISOLATED_WORKTREE_CAMPAIGN_EXECUTION_V1.md": (
        "AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md",
        "AIOS_AEE_GOVERNANCE_VALIDATOR_V1.md",
    ),
    "docs/workflows/AIOS_LONG_CAMPAIGN_CODEX_OPERATING_MODE_V1.md": (
        "AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md",
    ),
    "docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md": (
        "AI_OS_COMMIT_PUSH_GATE.md",
        "AI_OS_PR_LANE_RUNNER.md",
    ),
    "docs/workflows/AIOS_GITHUB_CI_FAILURE_RECOVERY_V1.md": (
        "AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md",
    ),
    "docs/workflows/AIOS_AEE_GOVERNANCE_VALIDATOR_V1.md": (
        "AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md",
        "AIOS_GITHUB_CI_FAILURE_RECOVERY_V1.md",
        "AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md",
        "AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md",
    ),
}

PROTECTED_HANDOFF_REQUIRED_TOKENS = [
    "git status --short --branch",
    "git add --",
    "git diff --cached --check",
    "git commit",
    "git push",
    "gh pr create",
    "gh pr checks --watch",
]

PROTECTED_HANDOFF_BLOCK_MARKERS = {
    "publish": re.compile(r"block 1", re.IGNORECASE),
    "merge": re.compile(r"block 2", re.IGNORECASE),
}

PROTECTED_MERGE_COMMANDS = [
    "gh pr merge",
    "git merge",
    "git pull --ff-only",
]

PLACEHOLDER_PATTERN = re.compile(
    r"@filename|\{[^}]+\}|path/to/|TODO|TBD",
    re.IGNORECASE,
)

CI_ASSIGNMENT_RE = re.compile(
    r"(?im)^\s*(api_key|apikey|secret|token|password|broker)\s*=",
)

SECTION_H1_RE = re.compile(r"^#\s+\S+", re.MULTILINE)
SECTION_PURPOSE_RE = re.compile(r"^##\s*Purpose\b", re.IGNORECASE | re.MULTILINE)
SECTION_SCOPE_RE = re.compile(r"^##\s*Scope\b", re.IGNORECASE | re.MULTILINE)
STAGING_CMD_PATTERNS = [
    re.compile(r"(?m)^\s*git\s+add\s+\.\s*$", re.IGNORECASE),
    re.compile(r"(?m)^\s*git\s+add\s+-A\b", re.IGNORECASE),
]
LANE_PACKET_LAW_LINES = [
    "The lane is the execution target.",
    "The packet is the authorization boundary.",
    "The worktree is the isolation boundary.",
    "Recoverable failures become work items.",
    "Reports are evidence, not endpoints.",
    "Codex continues inside approved scope.",
    "Codex stops at true governance gates.",
]


@dataclass(frozen=True)
class AEEValidationFinding:
    code: str
    severity: str
    message: str
    evidence: str


@dataclass(frozen=True)
class AEEGovernanceValidationResult:
    validator_name: str
    version: str
    repo_root: str
    status: str
    timestamp_utc: str
    files_checked: list[str]
    files_missing: list[str]
    findings: list[dict[str, object]]
    failure_count: int
    warning_count: int
    passed: list[str]
    failed: list[str]
    checkpoint_present: bool
    report_present: bool
    checkpoint_has_1312_recovery: bool
    protected_handoff_block_separated: bool


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _normalise_path(path: Path) -> str:
    return path.as_posix().replace("\\", "/")


def _to_lines(text: str) -> list[str]:
    return text.replace("\r\n", "\n").splitlines()


def _has_section(content: str, pattern: re.Pattern[str]) -> bool:
    return bool(pattern.search(content))


def validate_required_artifacts(
    repo_root: Path,
    required_paths: list[str],
    *,
    include_file_checker: Callable[[Path, str], bool] | None = None,
) -> tuple[list[AEEValidationFinding], list[str], list[str]]:
    findings: list[AEEValidationFinding] = []
    missing: list[str] = []
    present: list[str] = []
    for rel_path in required_paths:
        if include_file_checker is not None and not include_file_checker(repo_root / rel_path, rel_path):
            continue
        candidate = repo_root / rel_path
        if not candidate.exists():
            findings.append(
                AEEValidationFinding(
                    code="AIOS-AEE-V1-1000",
                    severity="FAIL",
                    message="Required artifact missing.",
                    evidence=rel_path,
                )
            )
            missing.append(rel_path)
            continue
        if rel_path.endswith("/"):
            if not candidate.is_dir():
                findings.append(
                    AEEValidationFinding(
                        code="AIOS-AEE-V1-1001",
                        severity="FAIL",
                        message="Expected directory, found non-directory path.",
                        evidence=rel_path,
                    )
                )
                missing.append(rel_path)
                continue
        elif not candidate.is_file():
            findings.append(
                AEEValidationFinding(
                    code="AIOS-AEE-V1-1002",
                    severity="FAIL",
                    message="Expected file, found directory or unsupported path type.",
                    evidence=rel_path,
                )
            )
            missing.append(rel_path)
            continue
        present.append(rel_path)
    return findings, missing, sorted(set(present))


def validate_required_sections(contents: dict[str, str]) -> list[AEEValidationFinding]:
    findings: list[AEEValidationFinding] = []
    for rel_path in REQUIRED_SECTION_ARTIFACTS:
        content = contents.get(rel_path, "")
        if not _has_section(content, SECTION_H1_RE):
            findings.append(
                AEEValidationFinding(
                    code="AIOS-AEE-V1-1101",
                    severity="FAIL",
                    message="Missing top-level heading.",
                    evidence=rel_path,
                )
            )
        if not _has_section(content, SECTION_PURPOSE_RE):
            findings.append(
                AEEValidationFinding(
                    code="AIOS-AEE-V1-1102",
                    severity="FAIL",
                    message="Missing Purpose section.",
                    evidence=rel_path,
                )
            )
        if not _has_section(content, SECTION_SCOPE_RE):
            findings.append(
                AEEValidationFinding(
                    code="AIOS-AEE-V1-1103",
                    severity="FAIL",
                    message="Missing Scope section.",
                    evidence=rel_path,
                )
            )
    return findings


def validate_safety_boundaries(contents: dict[str, str]) -> list[AEEValidationFinding]:
    findings: list[AEEValidationFinding] = []
    for rel_path in REQUIRED_SAFETY_ARTIFACTS:
        content = contents.get(rel_path, "").lower()
        for phrase in SAFETY_PHRASES:
            if phrase.lower() not in content:
                findings.append(
                    AEEValidationFinding(
                        code="AIOS-AEE-V1-1201",
                        severity="FAIL",
                        message="Missing required safety boundary phrase.",
                        evidence=f"{rel_path}: {phrase}",
                    )
                )
    return findings


def validate_cross_links(contents: dict[str, str]) -> list[AEEValidationFinding]:
    findings: list[AEEValidationFinding] = []
    lowered = {path: text.lower() for path, text in contents.items()}
    for path, targets in CROSS_LINK_REQUIREMENTS.items():
        text = lowered.get(path, "")
        if not text:
            findings.append(
                AEEValidationFinding(
                    code="AIOS-AEE-V1-1301",
                    severity="WARN",
                    message="Cross-link source artifact missing; cannot validate relationship.",
                    evidence=path,
                )
            )
            continue
        missing = [target for target in targets if target.lower() not in text]
        if missing:
            findings.append(
                AEEValidationFinding(
                    code="AIOS-AEE-V1-1301",
                    severity="WARN",
                    message="Cross-link dependency missing.",
                    evidence=f"{path} missing {missing}",
                )
            )
    return findings


def validate_agents_pointer(contents: dict[str, str]) -> list[AEEValidationFinding]:
    agents_text = contents.get("AGENTS.md", "").lower()
    if not agents_text:
        return [
            AEEValidationFinding(
                code="AIOS-AEE-V1-1302",
                severity="WARN",
                message="AGENTS.md not available for pointer validation.",
                evidence="AGENTS.md",
            )
        ]
    required_pointer_tokens = [
        "AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md",
        "AIOS_AEE_GOVERNANCE_VALIDATOR_V1.md",
    ]
    missing = [token for token in required_pointer_tokens if token.lower() not in agents_text]
    if missing:
        return [
            AEEValidationFinding(
                code="AIOS-AEE-V1-1302",
                severity="WARN",
                message="AGENTS.md pointer list missing required references.",
                evidence="; ".join(missing),
            )
        ]
    return []


def _extract_block(text: str, marker_key: str) -> str:
    lines = _to_lines(text)
    start = -1
    for index, line in enumerate(lines):
        if PROTECTED_HANDOFF_BLOCK_MARKERS[marker_key].search(line):
            start = index + 1
            break
    if start < 0:
        return ""
    end = len(lines)
    for index in range(start, len(lines)):
        if marker_key == "publish" and PROTECTED_HANDOFF_BLOCK_MARKERS["merge"].search(lines[index]):
            end = index
            break
        if marker_key == "merge" and index > start and PROTECTED_HANDOFF_BLOCK_MARKERS["publish"].search(lines[index]):
            end = index
            break
    return "\n".join(lines[start:end])


def validate_protected_handoff(contents: dict[str, str]) -> list[AEEValidationFinding]:
    findings: list[AEEValidationFinding] = []
    handoff = contents.get("docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md", "")
    if not handoff.strip():
        return [
            AEEValidationFinding(
                code="AIOS-AEE-V1-1501",
                severity="FAIL",
                message="Protected publishing handoff artifact missing required content.",
                evidence="docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md",
            )
        ]

    for token in PROTECTED_HANDOFF_REQUIRED_TOKENS:
        if token not in handoff:
            findings.append(
                AEEValidationFinding(
                    code="AIOS-AEE-V1-1501",
                    severity="FAIL",
                    message="Protected handoff does not include required protected-action command text.",
                    evidence=token,
                )
            )

    block1 = _extract_block(handoff, "publish")
    block2 = _extract_block(handoff, "merge")
    if not block1 or not block2:
        findings.append(
            AEEValidationFinding(
                code="AIOS-AEE-V1-1502",
                severity="FAIL",
                message="Protected handoff block separation is missing.",
                evidence="Expected Block 1 and Block 2 sections.",
            )
        )
        return findings

    block1_merge = any(cmd in block1.lower() for cmd in PROTECTED_MERGE_COMMANDS)
    if block1_merge:
        findings.append(
            AEEValidationFinding(
                code="AIOS-AEE-V1-1503",
                severity="FAIL",
                message="Merge/sync command appears in fix/check block.",
                evidence="Block 1 contains merge/sync command",
            )
        )

    # Validate check-watch and merge adjacency: a hard stop must exist before merge/sync.
    block1_lines = [line.lower() for line in _to_lines(block1)]
    for index, line in enumerate(block1_lines):
        if "pr checks --watch" in line and any(cmd in "\n".join(block1_lines[index + 1:index + 6]) for cmd in PROTECTED_MERGE_COMMANDS):
            findings.append(
                AEEValidationFinding(
                    code="AIOS-AEE-V1-1503",
                    severity="FAIL",
                    message="Merge is not separated from check-watch block.",
                    evidence="Block 1 check-watch ordering",
                )
            )
            break

    # Guard against command-only proximity in block2 where check-watch exists in block1.
    if block2 and "pr checks --watch" in block1.lower() and any(cmd in block2.lower() for cmd in PROTECTED_MERGE_COMMANDS):
        # allowed, but only if explicit block separation exists.
        pass

    return findings


def validate_placeholder_patterns(contents: dict[str, str]) -> list[AEEValidationFinding]:
    findings: list[AEEValidationFinding] = []
    for path, content in contents.items():
        if PLACEHOLDER_PATTERN.search(content):
            findings.append(
                AEEValidationFinding(
                    code="AIOS-AEE-V1-1601",
                    severity="FAIL",
                    message="Placeholder text detected in required artifacts.",
                    evidence=path,
                )
            )
    return findings


def validate_ci_sensitive_assignments(contents: dict[str, str]) -> list[AEEValidationFinding]:
    findings: list[AEEValidationFinding] = []
    for path, content in contents.items():
        if path.startswith("tests/fixtures/governance/aee_validator/"):
            continue
        for line in _to_lines(content):
            if CI_ASSIGNMENT_RE.search(line):
                findings.append(
                    AEEValidationFinding(
                        code="AIOS-AEE-V1-1701",
                        severity="FAIL",
                        message="CI-sensitive assignment name found.",
                        evidence=f"{path}: {line.strip()}",
                    )
                )
    return findings


def validate_staging_commands(contents: dict[str, str]) -> list[AEEValidationFinding]:
    findings: list[AEEValidationFinding] = []
    for path, content in contents.items():
        for pattern in STAGING_CMD_PATTERNS:
            if pattern.search(content):
                findings.append(
                    AEEValidationFinding(
                        code="AIOS-AEE-V1-1702",
                        severity="FAIL",
                        message="Broad staging command detected.",
                        evidence=f"{path}: {pattern.pattern}",
                    )
                )
    return findings


def validate_1312_recovery(contents: dict[str, str]) -> list[AEEValidationFinding]:
    checkpoint = contents.get("Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_CHECKPOINT.md", "").lower()
    findings: list[AEEValidationFinding] = []
    if "createprocessasuserw failed: 1312" in checkpoint:
        if "owner powershell" not in checkpoint and "exact owner powershell handoff" not in checkpoint:
            findings.append(
                AEEValidationFinding(
                    code="AIOS-AEE-V1-1801",
                    severity="FAIL",
                    message="1312 recovery instruction missing from checkpoint.",
                    evidence="AIOS_AEE_GOVERNANCE_VALIDATOR_V1_CHECKPOINT.md",
                )
            )
    return findings


def validate_checkpoint_report_pairing(contents: dict[str, str]) -> list[AEEValidationFinding]:
    checkpoint_present = bool(contents.get("Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_CHECKPOINT.md", "").strip())
    report_present = bool(contents.get("Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_REPORT.md", "").strip())
    if checkpoint_present != report_present:
        return [
            AEEValidationFinding(
                code="AIOS-AEE-V1-1401",
                severity="FAIL",
                message="Report/checkpoint pairing is broken.",
                evidence="AIOS_AEE_GOVERNANCE_VALIDATOR_V1_CHECKPOINT.md/report",
            )
        ]
    return []


def validate_lane_packet_worktree_law(contents: dict[str, str]) -> list[AEEValidationFinding]:
    law_text = contents.get(
        "docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md",
        "",
    )
    findings: list[AEEValidationFinding] = []
    missing = [line for line in LANE_PACKET_LAW_LINES if line not in law_text]
    if missing:
        findings.extend(
            AEEValidationFinding(
                code="AIOS-AEE-V1-1901",
                severity="FAIL",
                message="Lane/packet/worktree law statement missing.",
                evidence=missing_line,
            )
            for missing_line in missing
        )
    return findings


def _load_required_contents(
    repo_root: Path,
    required_paths: list[str],
) -> dict[str, str]:
    contents: dict[str, str] = {}
    for rel_path in required_paths:
        candidate = repo_root / rel_path
        if candidate.exists() and candidate.is_file():
            contents[rel_path] = _read_text(candidate)
    if (repo_root / "AGENTS.md").exists():
        contents["AGENTS.md"] = _read_text(repo_root / "AGENTS.md")
    return contents


def _status_from_findings(findings: list[AEEValidationFinding]) -> str:
    if any(item.severity == "FAIL" for item in findings):
        return "FAIL"
    if any(item.severity == "WARN" for item in findings):
        return "PARTIAL"
    return "PASS"


def build_aee_governance_validation(
    repo_root: str | Path,
    *,
    artifact_paths: list[str] | None = None,
    include_file_checker: Callable[[Path, str], bool] | None = None,
) -> AEEGovernanceValidationResult:
    root = Path(repo_root).expanduser().resolve()
    selected_paths = artifact_paths or REQUIRED_ARTIFACTS
    if include_file_checker is not None:
        selected_paths = [path for path in selected_paths if include_file_checker(root / path, path)]

    required_findings, missing, checked = validate_required_artifacts(
        root,
        selected_paths,
        include_file_checker=include_file_checker,
    )
    contents = _load_required_contents(root, checked)

    findings: list[AEEValidationFinding] = list(required_findings)
    findings.extend(validate_required_sections(contents))
    findings.extend(validate_safety_boundaries(contents))
    findings.extend(validate_cross_links(contents))
    findings.extend(validate_agents_pointer(contents))
    findings.extend(validate_checkpoint_report_pairing(contents))
    findings.extend(validate_protected_handoff(contents))
    findings.extend(validate_placeholder_patterns(contents))
    findings.extend(validate_ci_sensitive_assignments(contents))
    findings.extend(validate_staging_commands(contents))
    findings.extend(validate_1312_recovery(contents))
    findings.extend(validate_lane_packet_worktree_law(contents))

    status = _status_from_findings(findings)
    passed = [item.code for item in findings if item.severity == "PASS"]
    failed = [item.code for item in findings if item.severity in {"FAIL", "WARN"}]

    checkpoint_text = contents.get("Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_CHECKPOINT.md", "")
    report_text = contents.get("Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_REPORT.md", "")
    checkpoint_lower = checkpoint_text.lower()
    handoff_text = contents.get("docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md", "").lower()

    return AEEGovernanceValidationResult(
        validator_name=VALIDATOR_NAME,
        version=VALIDATOR_VERSION,
        repo_root=str(root),
        status=status,
        timestamp_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        files_checked=sorted(set(checked + [f"AGENTS.md"])),
        files_missing=sorted(set(missing)),
        findings=[asdict(item) for item in findings],
        failure_count=sum(1 for item in findings if item.severity == "FAIL"),
        warning_count=sum(1 for item in findings if item.severity == "WARN"),
        passed=passed,
        failed=failed,
        checkpoint_present=bool(checkpoint_text.strip()),
        report_present=bool(report_text.strip()),
        checkpoint_has_1312_recovery=("owner powershell" in checkpoint_lower and "1312" in checkpoint_lower),
        protected_handoff_block_separated=("block 1" in handoff_text and "block 2" in handoff_text),
    )


def result_to_operator_text(result: AEEGovernanceValidationResult) -> str:
    lines = [
        f"{result.validator_name} v{result.version}",
        f"repo: {result.repo_root}",
        f"status: {result.status}",
        f"failures: {result.failure_count}",
        f"warnings: {result.warning_count}",
        f"checkpoint_present: {str(result.checkpoint_present).lower()}",
        f"report_present: {str(result.report_present).lower()}",
        f"protected_handoff_block_separated: {str(result.protected_handoff_block_separated).lower()}",
        "",
        "findings:",
    ]
    if not result.findings:
        lines.append("- none")
    else:
        for item in result.findings:
            lines.append(f"- {item['severity']} {item['code']} {item['message']}")
            lines.append(f"  evidence: {item['evidence']}")
    return "\n".join(lines) + "\n"


def result_to_jsonable_dict(result: AEEGovernanceValidationResult) -> dict[str, object]:
    return asdict(result)


def result_to_markdown(result: AEEGovernanceValidationResult) -> str:
    lines = [
        "# AIOS AEE Governance Validator V1 Report",
        "",
        f"- validator: {result.validator_name}",
        f"- version: {result.version}",
        f"- status: {result.status}",
        f"- timestamp (UTC): {result.timestamp_utc}",
        f"- repo_root: {result.repo_root}",
        f"- failures: {result.failure_count}",
        f"- warnings: {result.warning_count}",
        "",
        "## Findings",
    ]
    if not result.findings:
        lines.append("- no findings")
    else:
        for item in result.findings:
            lines.append(f"- `{item['code']}` {item['severity']} — {item['message']}")
            lines.append(f"  - {item['evidence']}")
    return "\n".join(lines) + "\n"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate AEE governance docs and artifacts.")
    parser.add_argument("--repo-root", default=str(REPO_DEFAULT))
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero only if validation fails.")
    parser.add_argument("--write-report", action="store_true", help="Write markdown report.")
    parser.add_argument("--report-path", default="Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_REPORT.md")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    result = build_aee_governance_validation(args.repo_root)
    if args.json:
        print(json.dumps(result_to_jsonable_dict(result), sort_keys=True))
    else:
        print(result_to_operator_text(result))

    if args.write_report:
        Path(args.report_path).write_text(result_to_markdown(result), encoding="utf-8")

    if args.strict:
        return 0 if result.status == "PASS" else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
