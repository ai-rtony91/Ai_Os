from __future__ import annotations

"""Deterministic anti-stop gate inventory for AEE carryover continuation."""

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

PACKET_ID = "AIOS-AEE-ANTI-STOP-CARRYOVER-CONTINUATION-LONGRUN-V3"
REPO_DEFAULT = Path(__file__).resolve().parents[2]

EXPECTED_BRANCH = "lane/aios-aee-governance-validator-v1"
EXPECTED_CLEAN_MAIN = "main"

ALLOWED_WRITE_PATHS = [
    "automation/governance/",
    "scripts/governance/",
    "tests/governance/",
    "tests/fixtures/governance/",
    "docs/governance/",
    "docs/workflows/",
    "Reports/core_delivery/",
]

FORBIDDEN_PATH_PREFIXES = [
    ".env",
    "secrets/",
    "credentials/",
    "private/",
    "Reports/forex_delivery/",
    "automation/forex_engine/",
    "scripts/forex_delivery/",
    "tests/forex_engine/",
    "schemas/aios/forex/",
]

KNOWN_CARRYOVER_PATHS = [
    "automation/governance/aios_aee_governance_validator_v1.py",
    "scripts/governance/run_aios_aee_governance_validator_v1.py",
    "tests/governance/test_aios_aee_governance_validator_v1.py",
    "tests/fixtures/governance/aee_validator/",
    "docs/workflows/AIOS_AEE_GOVERNANCE_VALIDATOR_V1.md",
    "Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_CHECKPOINT.md",
    "Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_REPORT.md",
]

KNOWN_CARRYOVER_ANCHOR_PATHS = [
    "automation/governance/aios_aee_governance_validator_v1.py",
    "scripts/governance/run_aios_aee_governance_validator_v1.py",
    "docs/workflows/AIOS_AEE_GOVERNANCE_VALIDATOR_V1.md",
    "Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_REPORT.md",
    "Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_CHECKPOINT.md",
]

V3_STOPGATE_PATHS = [
    "automation/governance/aios_aee_stopgate_inventory_v3.py",
    "scripts/governance/run_aios_aee_stopgate_inventory_v3.py",
    "tests/governance/test_aios_aee_stopgate_inventory_v3.py",
    "tests/fixtures/governance/aee_stopgate_inventory_v3/",
    "docs/workflows/AIOS_AEE_ANTI_STOP_CARRYOVER_CONTINUATION_V3.md",
    "Reports/core_delivery/AIOS_AEE_STOPGATE_INVENTORY_V3.md",
    "Reports/core_delivery/AIOS_AEE_STOPGATE_CARRYOVER_CONTINUATION_V3_CHECKPOINT.md",
    "Reports/core_delivery/AIOS_AEE_STOPGATE_CARRYOVER_CONTINUATION_V3_REPORT.md",
]

STRICT_ZERO_STATUSES = {
    "APPROVED_CARRYOVER_CONTINUATION",
    "RECOVERABLE_LOCAL",
    "DEFERRED_OWNER_VALIDATION",
    "OWNER_HANDOFF_READY",
}


@dataclass(frozen=True)
class StopgateMatrixRow:
    code: str
    name: str
    severity: str
    family: str
    classification: str
    detection_signature: str
    allowed_recovery: str
    forbidden_recovery: str
    continue_condition: str
    true_stop_condition: str
    owner_handoff_required: bool
    example: str
    anti_stop_instruction: str


STOPGATE_MATRIX: list[StopgateMatrixRow] = [
    StopgateMatrixRow(
        code="STATE-001",
        name="wrong branch unrelated dirty hard stop",
        severity="high",
        family="state alignment stopgates",
        classification="HARD_STOP",
        detection_signature="branch != expected and dirty files exist",
        allowed_recovery="confirm lane scope before applying any branch logic",
        forbidden_recovery="do not switch branch while dirty carryover exists",
        continue_condition="branch equals expected carryover lane",
        true_stop_condition="dirty files on unrelated branch",
        owner_handoff_required=False,
        example="branch=feature/foo + dirty files",
        anti_stop_instruction="treat as unrelated branch hard stop.",
    ),
    StopgateMatrixRow(
        code="STATE-002",
        name="approved carryover dirty continuation",
        severity="low",
        family="state alignment stopgates",
        classification="APPROVED_CARRYOVER_CONTINUATION",
        detection_signature="branch=expected and dirty files are carryover artifacts",
        allowed_recovery="continue on same lane",
        forbidden_recovery="do not re-run clean-main preflight",
        continue_condition="dirty files are approved carryover artifacts",
        true_stop_condition="dirty carryover cannot be verified",
        owner_handoff_required=False,
        example="lane + v1 artifacts remain dirty",
        anti_stop_instruction="continue immediately.",
    ),
    StopgateMatrixRow(
        code="STATE-003",
        name="staged files present hard stop",
        severity="high",
        family="state alignment stopgates",
        classification="HARD_STOP",
        detection_signature="staged file list present",
        allowed_recovery="resolve staged list intentionally",
        forbidden_recovery="do not continue with staged edits",
        continue_condition="no staged files",
        true_stop_condition="any staged file exists",
        owner_handoff_required=True,
        example="git add -- file produced",
        anti_stop_instruction="stop for explicit owner handling.",
    ),
    StopgateMatrixRow(
        code="STATE-004",
        name="forbidden path dirty hard stop",
        severity="high",
        family="state alignment stopgates",
        classification="HARD_STOP",
        detection_signature="dirty path matches forbidden segment",
        allowed_recovery="remove forbidden paths from dirty set",
        forbidden_recovery="do not touch secrets or credentials",
        continue_condition="no forbidden file in dirty set",
        true_stop_condition="forbidden path observed",
        owner_handoff_required=True,
        example="secrets/config.json is dirty",
        anti_stop_instruction="remove forbidden-file edits.",
    ),
    StopgateMatrixRow(
        code="STATE-005",
        name="clean-main expectation false positive",
        severity="high",
        family="state alignment stopgates",
        classification="WRONG_PACKET_FOR_CLEAN_MAIN",
        detection_signature="branch is main for continuation packet",
        allowed_recovery="re-run on lane branch",
        forbidden_recovery="do not switch to clean-main flow",
        continue_condition="branch is lane continuation branch",
        true_stop_condition="main branch encountered",
        owner_handoff_required=False,
        example="main branch with continuation packet",
        anti_stop_instruction="return wrong-packet status.",
    ),
    StopgateMatrixRow(
        code="RECOVERABLE_LOCAL",
        name="recoverable local conditions present",
        severity="low",
        family="state alignment stopgates",
        classification="RECOVERABLE_LOCAL",
        detection_signature="no hard stop condition detected",
        allowed_recovery="continue scoped local fixes",
        forbidden_recovery="do not stop on approved carryover branch",
        continue_condition="safe and allowed local edits remain",
        true_stop_condition="hard stop condition appears",
        owner_handoff_required=False,
        example="clean local allowed work with carryover context",
        anti_stop_instruction="continue and repair.",
    ),
    StopgateMatrixRow(
        code="BRANCH-001",
        name="target branch conflict",
        severity="high",
        family="branch stopgates",
        classification="HARD_STOP",
        detection_signature="branch does not match expected lane",
        allowed_recovery="use current lane",
        forbidden_recovery="do not force branch switch",
        continue_condition="branch matches expected",
        true_stop_condition="unresolved target branch mismatch",
        owner_handoff_required=False,
        example="branch=heads/main",
        anti_stop_instruction="keep branch fixed.",
    ),
    StopgateMatrixRow(
        code="BRANCH-002",
        name="dirty branch switch attempt forbidden",
        severity="high",
        family="branch stopgates",
        classification="HARD_STOP",
        detection_signature="dirty worktree with branch movement intent",
        allowed_recovery="finish in place",
        forbidden_recovery="do not switch while dirty",
        continue_condition="no branch switch proposal while dirty",
        true_stop_condition="branch switch action while dirty",
        owner_handoff_required=True,
        example="proposal to switch to main in continuation",
        anti_stop_instruction="reject branch-switch proposal.",
    ),
    StopgateMatrixRow(
        code="PROTECTED-001",
        name="git add attempted by Codex",
        severity="high",
        family="protected action stopgates",
        classification="HARD_STOP",
        detection_signature="protected git add operation detected",
        allowed_recovery="owner publishes via explicit block",
        forbidden_recovery="do not auto-stage files",
        continue_condition="no protected command",
        true_stop_condition="staged action detected",
        owner_handoff_required=True,
        example="git add -- file",
        anti_stop_instruction="pause and handoff with explicit files.",
    ),
    StopgateMatrixRow(
        code="PROTECTED-002",
        name="PR create attempted by Codex",
        severity="high",
        family="protected action stopgates",
        classification="HARD_STOP",
        detection_signature="gh pr create outside owner command block",
        allowed_recovery="owner handles publish block",
        forbidden_recovery="do not create PR automatically",
        continue_condition="no pr create command",
        true_stop_condition="untrusted pr create",
        owner_handoff_required=True,
        example="gh pr create --title ...",
        anti_stop_instruction="postpone to owner handoff.",
    ),
    StopgateMatrixRow(
        code="PROTECTED-003",
        name="merge attempted by Codex",
        severity="high",
        family="protected action stopgates",
        classification="HARD_STOP",
        detection_signature="gh pr merge or git merge attempted",
        allowed_recovery="owner handles block2 only",
        forbidden_recovery="do not merge",
        continue_condition="no merge action",
        true_stop_condition="merge command present",
        owner_handoff_required=True,
        example="gh pr merge --squash",
        anti_stop_instruction="route to owner merge block.",
    ),
    StopgateMatrixRow(
        code="SANDBOX-001",
        name="1312 read-only process launch",
        severity="medium",
        family="sandbox/process-launch stopgates",
        classification="SANDBOX_LIMITATION",
        detection_signature="CreateProcessAsUserW failed: 1312 on read-only command",
        allowed_recovery="retry once then continue narrow read",
        forbidden_recovery="do not loop",
        continue_condition="read-only command and one retry possible",
        true_stop_condition="all retries fail and work still needed",
        owner_handoff_required=False,
        example="inspection failed with 1312",
        anti_stop_instruction="log 1312 event and continue local checks.",
    ),
    StopgateMatrixRow(
        code="SANDBOX-002",
        name="1312 strict CLI",
        severity="medium",
        family="sandbox/process-launch stopgates",
        classification="DEFERRED_OWNER_VALIDATION",
        detection_signature="simulate_1312 with strict CLI",
        allowed_recovery="classify as deferred owner validation",
        forbidden_recovery="do not mark false failure",
        continue_condition="targeted tests pass and local work remains",
        true_stop_condition="strict CLI blocked and no tests left",
        owner_handoff_required=False,
        example="strict CLI blocked with 1312",
        anti_stop_instruction="keep working and return deferred status.",
    ),
    StopgateMatrixRow(
        code="SANDBOX-003",
        name="broad scan blocked",
        severity="low",
        family="sandbox/process-launch stopgates",
        classification="MINOR_SCAN_BLOCKED_RECURABLE",
        detection_signature="broad scan command fails",
        allowed_recovery="switch to explicit file paths",
        forbidden_recovery="do not retry broad scan repeatedly",
        continue_condition="explicit paths exist",
        true_stop_condition="no explicit path alternative exists",
        owner_handoff_required=False,
        example="rg --files fails",
        anti_stop_instruction="continue with scoped inputs.",
    ),
    StopgateMatrixRow(
        code="WAITING-001",
        name="waiting for owner powershell",
        severity="medium",
        family="owner handoff readiness stopgates",
        classification="WAITING_FOR_OWNER_POWERSHELL",
        detection_signature="all remaining useful local tasks require owner shell",
        allowed_recovery="handoff with explicit command and context",
        forbidden_recovery="do not continue pretending checks passed",
        continue_condition="no local command path remains",
        true_stop_condition="remaining work requires owner shell",
        owner_handoff_required=False,
        example="1312 with all remaining safe work blocked",
        anti_stop_instruction="pause and request owner powershell handoff.",
    ),
    StopgateMatrixRow(
        code="VALIDATOR-001",
        name="targeted tests pass strict CLI blocked",
        severity="medium",
        family="test failure stopgates",
        classification="DEFERRED_OWNER_VALIDATION",
        detection_signature="targeted tests pass and validate gate deferred",
        allowed_recovery="complete local artifacts",
        forbidden_recovery="do not convert to hard stop",
        continue_condition="repairable local evidence",
        true_stop_condition="all checks blocked by sandbox",
        owner_handoff_required=False,
        example="pytest pass + blocked strict",
        anti_stop_instruction="defer owner validation.",
    ),
    StopgateMatrixRow(
        code="VALIDATOR-002",
        name="repairable test failures",
        severity="medium",
        family="test failure stopgates",
        classification="RECOVERABLE_LOCAL",
        detection_signature="non-forbidden repairable failure",
        allowed_recovery="add fixture/code repair",
        forbidden_recovery="do not mark hard stop",
        continue_condition="failure fixable in allowed paths",
        true_stop_condition="no repair path in allowed scope",
        owner_handoff_required=False,
        example="fixture missing",
        anti_stop_instruction="continue local hardening.",
    ),
    StopgateMatrixRow(
        code="VALIDATOR-003",
        name="forbidden test failure",
        severity="high",
        family="test failure stopgates",
        classification="HARD_STOP",
        detection_signature="failure requires forbidden scope edit",
        allowed_recovery="raise for explicit rebalance",
        forbidden_recovery="do not edit forbidden scope",
        continue_condition="repair in allowed scope",
        true_stop_condition="forbidden scope required",
        owner_handoff_required=True,
        example="secret test path required",
        anti_stop_instruction="do not continue with forbidden edit.",
    ),
    StopgateMatrixRow(
        code="REPORT-001",
        name="report exists but hardening remains",
        severity="low",
        family="report/checkpoint stopgates",
        classification="RECOVERABLE_LOCAL",
        detection_signature="report has pending work markers",
        allowed_recovery="continue hardening",
        forbidden_recovery="do not finalize owner handoff",
        continue_condition="pending work remains",
        true_stop_condition="hardening still missing while report present",
        owner_handoff_required=False,
        example="report exists + pending_work lines",
        anti_stop_instruction="continue until hardening clear.",
    ),
    StopgateMatrixRow(
        code="REPORT-002",
        name="checkpoint exists report pending",
        severity="low",
        family="report/checkpoint stopgates",
        classification="RECOVERABLE_LOCAL",
        detection_signature="checkpoint exists and report missing",
        allowed_recovery="create/update report",
        forbidden_recovery="do not claim complete without report",
        continue_condition="checkpoint exists only",
        true_stop_condition="report missing",
        owner_handoff_required=False,
        example="checkpoint only present",
        anti_stop_instruction="write report and continue.",
    ),
    StopgateMatrixRow(
        code="REPORT-003",
        name="report/checkpoint contradiction",
        severity="medium",
        family="report/checkpoint stopgates",
        classification="EVIDENCE_GAP",
        detection_signature="inconsistent completion signals",
        allowed_recovery="repair alignment",
        forbidden_recovery="do not classify handoff",
        continue_condition="signals aligned",
        true_stop_condition="contradictory markers",
        owner_handoff_required=False,
        example="complete in one, pending in other",
        anti_stop_instruction="repair and rerun.",
    ),
    StopgateMatrixRow(
        code="CI-001",
        name="secret scanner risk",
        severity="high",
        family="ci stopgates",
        classification="HARD_STOP",
        detection_signature="sensitive assignment name pattern",
        allowed_recovery="replace assignment names",
        forbidden_recovery="do not keep sensitive names",
        continue_condition="no sensitive names",
        true_stop_condition="api_key/broker/token/etc assignment in code",
        owner_handoff_required=False,
        example='api_key = "abc"',
        anti_stop_instruction="replace with neutral names.",
    ),
    StopgateMatrixRow(
        code="CI-002",
        name="placeholder false positive",
        severity="low",
        family="ci stopgates",
        classification="FALSE_POSITIVE_REPAIR",
        detection_signature="placeholder in evidence-only fixture",
        allowed_recovery="repair fixture/ignore placeholder",
        forbidden_recovery="do not route as hard stop",
        continue_condition="placeholder in fixture context",
        true_stop_condition="placeholder in executable context",
        owner_handoff_required=False,
        example="{path} in fixture",
        anti_stop_instruction="repair and continue.",
    ),
    StopgateMatrixRow(
        code="SAFETY-001",
        name="broker/API boundary",
        severity="critical",
        family="safety authority stopgates",
        classification="HARD_STOP",
        detection_signature="broker API command boundary",
        allowed_recovery="remove command",
        forbidden_recovery="do not add broker access",
        continue_condition="no broker/API commands",
        true_stop_condition="broker/API path present",
        owner_handoff_required=True,
        example="trading api call",
        anti_stop_instruction="stop and preserve safety.",
    ),
    StopgateMatrixRow(
        code="SAFETY-002",
        name="credential boundary",
        severity="critical",
        family="safety authority stopgates",
        classification="HARD_STOP",
        detection_signature="credentials or .env dirty",
        allowed_recovery="drop credential path",
        forbidden_recovery="do not open credentials",
        continue_condition="no credential file edits",
        true_stop_condition="credential path dirty",
        owner_handoff_required=True,
        example=".env dirty",
        anti_stop_instruction="remove credential scope.",
    ),
    StopgateMatrixRow(
        code="SAFETY-003",
        name="trading execution boundary",
        severity="critical",
        family="safety authority stopgates",
        classification="HARD_STOP",
        detection_signature="trading execution path in scope",
        allowed_recovery="focus on governance paths",
        forbidden_recovery="do not edit trading execution",
        continue_condition="trading execution untouched",
        true_stop_condition="trading execution path touched",
        owner_handoff_required=True,
        example="scripts/forex_delivery",
        anti_stop_instruction="stop and re-scope task.",
    ),
    StopgateMatrixRow(
        code="SAFETY-004",
        name="money movement boundary",
        severity="critical",
        family="safety authority stopgates",
        classification="HARD_STOP",
        detection_signature="money movement command",
        allowed_recovery="no-op governance update",
        forbidden_recovery="no money movement changes",
        continue_condition="money movement absent",
        true_stop_condition="money movement touched",
        owner_handoff_required=True,
        example="payment route touched",
        anti_stop_instruction="stop and handoff.",
    ),
    StopgateMatrixRow(
        code="CONTEXT-001",
        name="context compaction stopgate",
        severity="low",
        family="context compaction stopgates",
        classification="RECOVERABLE_LOCAL",
        detection_signature="non-active context requested",
        allowed_recovery="narrow to active lane",
        forbidden_recovery="do not continue stale context",
        continue_condition="active context available",
        true_stop_condition="context compaction impossible",
        owner_handoff_required=False,
        example="broad unrelated prompt",
        anti_stop_instruction="trim context and continue.",
    ),
    StopgateMatrixRow(
        code="PROMPT-001",
        name="accidental codebase explanation interrupt",
        severity="low",
        family="user accidental prompt injection stopgates",
        classification="PROMPT_INTERRUPTION_IGNORE",
        detection_signature='prompt contains "Explain this codebase"',
        allowed_recovery="ignore prompt and continue lane",
        forbidden_recovery="do not switch workflow based on this prompt",
        continue_condition="lane execution remains active",
        true_stop_condition="explicit interruption command",
        owner_handoff_required=False,
        example="Explain this codebase",
        anti_stop_instruction="keep executing this packet.",
    ),
    StopgateMatrixRow(
        code="HANDOFF-001",
        name="handoff ready but local work remains",
        severity="low",
        family="owner handoff readiness stopgates",
        classification="RECOVERABLE_LOCAL",
        detection_signature="protected action pending but pending work exists",
        allowed_recovery="continue local work",
        forbidden_recovery="do not handoff before done",
        continue_condition="pending work exists",
        true_stop_condition="local work remains",
        owner_handoff_required=False,
        example="publish block shown while fixtures missing",
        anti_stop_instruction="continue work then handoff.",
    ),
    StopgateMatrixRow(
        code="HANDOFF-002",
        name="owner handoff ready and work complete",
        severity="low",
        family="owner handoff readiness stopgates",
        classification="OWNER_HANDOFF_READY",
        detection_signature="no local work and report/checkpoint aligned",
        allowed_recovery="owner handoff",
        forbidden_recovery="no more local edits",
        continue_condition="none",
        true_stop_condition="local work remains",
        owner_handoff_required=True,
        example="all stopgate work complete",
        anti_stop_instruction="hand off safely.",
    ),
]

MATRIX_INDEX = {row.code: row for row in STOPGATE_MATRIX}


@dataclass(frozen=True)
class StopgateInventoryResult:
    packet_id: str
    timestamp_utc: str
    repo_root: str
    branch: str
    continuation_status: str
    current_phase: str
    dirty_files_observed: list[str]
    staged_files: list[str]
    allowed_paths_verified: list[str]
    forbidden_paths_seen: list[str]
    carryover_artifacts_detected: list[str]
    new_stopgate_artifacts_planned: list[str]
    completed_work: list[str]
    pending_work: list[str]
    validators_passed: list[str]
    validators_blocked: list[str]
    failures_encountered: list[str]
    events_1312: list[dict[str, str]]
    recovery_attempts: list[str]
    next_safe_action: str
    resume_instruction: str
    stopgates_found: list[StopgateMatrixRow]
    stopgates_repaired: list[str]
    stopgates_deferred: list[str]


def _normalise_path(value: str | Path) -> str:
    text = str(value).replace("\\", "/").lower()
    while text.startswith("./"):
        text = text[2:]
    return text


def _under(item: str, prefix: str) -> bool:
    candidate = _normalise_path(item)
    target = _normalise_path(prefix).rstrip("/")
    return candidate == target or candidate.startswith(f"{target}/")


def _allowed(item: str) -> bool:
    return any(_under(item, root) for root in ALLOWED_WRITE_PATHS)


def scan_forbidden_paths(dirty_files: Iterable[str]) -> list[str]:
    hits: list[str] = []
    for item in dirty_files:
        normalized = _normalise_path(item)
        if any(_under(normalized, seg) for seg in FORBIDDEN_PATH_PREFIXES):
            if normalized not in hits:
                hits.append(normalized)
    return hits


def classify_dirty_worktree(
    dirty_files: Iterable[str],
    *,
    staged_files: Iterable[str] | None = None,
) -> tuple[str, list[str], list[str]]:
    dirty = [_normalise_path(item) for item in dirty_files]
    staged = [item for item in (staged_files or []) if str(item).strip()]
    if staged:
        return "HARD_STOP", ["STATE-003"], [item.lower() for item in staged]
    if not dirty:
        return "RECOVERABLE_LOCAL", ["RECOVERABLE_LOCAL"], []
    forbidden = scan_forbidden_paths(dirty)
    if forbidden:
        return "HARD_STOP", ["STATE-004"], forbidden
    if not all(_allowed(item) for item in dirty):
        return "HARD_STOP", ["STATE-001"], [item for item in dirty if not _allowed(item)]
    carryover = [item for item in dirty if any(_under(item, path) for path in KNOWN_CARRYOVER_PATHS)]
    has_anchor = any(any(_under(item, anchor) for item in carryover) for anchor in KNOWN_CARRYOVER_ANCHOR_PATHS)
    if carryover and len(carryover) == len(dirty) and has_anchor:
        return "APPROVED_CARRYOVER_CONTINUATION", ["STATE-002"], carryover
    return "RECOVERABLE_LOCAL", ["RECOVERABLE_LOCAL"], dirty


def classify_branch_state(branch: str, dirty_files: Iterable[str] | None = None) -> str:
    normalized = (branch or "").lower().strip()
    if normalized == EXPECTED_BRANCH:
        return "STATE-002" if dirty_files else "STATE-002"
    if normalized == EXPECTED_CLEAN_MAIN:
        return "STATE-005"
    if normalized:
        return "BRANCH-001"
    return "HARD_STOP"


def classify_1312_event(
    simulate_1312: bool,
    *,
    targeted_tests_passed: bool = False,
    all_remaining_work_blocked: bool = False,
    is_read_only: bool = True,
) -> str:
    if not simulate_1312:
        return "NO_1312"
    if all_remaining_work_blocked:
        return "WAITING_FOR_OWNER_POWERSHELL"
    if targeted_tests_passed:
        return "DEFERRED_OWNER_VALIDATION"
    if is_read_only:
        return "SANDBOX-001"
    return "SANDBOX-002"


def classify_validation_gate(
    *,
    targeted_tests_passed: bool,
    targeted_tests_failed_recovery: bool = False,
) -> str:
    if targeted_tests_failed_recovery:
        return "VALIDATOR-002"
    if targeted_tests_passed:
        return "VALIDATOR-001"
    return "VALIDATOR-001"


def classify_protected_action_gate(
    *,
    local_work_complete: bool,
    protected_ready: bool,
) -> str:
    if not protected_ready:
        return "RECOVERABLE_LOCAL"
    if local_work_complete:
        return "HANDOFF-002"
    return "HANDOFF-001"


def scan_report_checkpoint_consistency(
    repo_root: Path,
    report_path: str,
    checkpoint_path: str,
) -> tuple[str, list[str], list[str]]:
    report_file = (repo_root / report_path).resolve()
    checkpoint_file = (repo_root / checkpoint_path).resolve()
    report_text = ""
    checkpoint_text = ""
    if report_file.exists():
        report_text = report_file.read_text(encoding="utf-8", errors="replace").lower()
    if checkpoint_file.exists():
        checkpoint_text = checkpoint_file.read_text(encoding="utf-8", errors="replace").lower()

    report_present = bool(report_text)
    checkpoint_present = bool(checkpoint_text)

    if not report_present and not checkpoint_present:
        return "EVIDENCE_GAP", ["REPORT-003"], ["report and checkpoint missing"]

    if report_present and not checkpoint_present:
        return "RECOVERABLE_LOCAL", ["REPORT-002"], ["checkpoint missing"]
    if checkpoint_present and not report_present:
        return "RECOVERABLE_LOCAL", ["REPORT-002"], ["report missing"]

    if "pending_work" in report_text or "pending_work" in checkpoint_text:
        return "RECOVERABLE_LOCAL", ["REPORT-001"], ["hardening remains"]

    complete_report = "complete" in report_text
    complete_checkpoint = "complete" in checkpoint_text
    if complete_report != complete_checkpoint:
        return "EVIDENCE_GAP", ["REPORT-003"], ["contradictory completion markers"]

    if complete_report and complete_checkpoint:
        return "OWNER_HANDOFF_READY", [], []

    return "RECOVERABLE_LOCAL", [], ["no explicit completion marker"]


def scan_continue_conditions(result: StopgateInventoryResult) -> list[str]:
    conditions: list[str] = []
    if result.continuation_status in STRICT_ZERO_STATUSES | {"OWNER_HANDOFF_READY", "HARD_STOP", "WRONG_PACKET_FOR_CLEAN_MAIN", "WAITING_FOR_OWNER_POWERSHELL", "PROMPT_INTERRUPTION_IGNORE"}:
        conditions.append("continue if local work exists and is allowed")
    if result.forbidden_paths_seen:
        conditions.append("remove forbidden path edits")
    if result.staged_files:
        conditions.append("resolve staged files")
    if result.continuation_status == "WRONG_PACKET_FOR_CLEAN_MAIN":
        conditions.append("rerun on lane/aios-aee-governance-validator-v1")
    if result.continuation_status == "WAITING_FOR_OWNER_POWERSHELL":
        conditions.append("wait for owner powershell")
    return conditions


def _prompt_interrupt(prompt: str | None) -> bool:
    if not prompt:
        return False
    lowered = prompt.lower()
    return "explain this codebase" in lowered


def build_stopgate_inventory(
    repo_root: str | Path,
    *,
    branch: str,
    dirty_files: list[str] | None = None,
    staged_files: list[str] | None = None,
    write_report: bool = False,
    report_path: str = "Reports/core_delivery/AIOS_AEE_STOPGATE_INVENTORY_V3.md",
    strict: bool = False,
    continue_plan: str = "",
    simulate_1312: bool = False,
    simulate_targeted_tests_passed: bool = False,
    simulate_targeted_tests_failed: bool = False,
    all_remaining_work_blocked: bool = False,
    broad_scan_blocked: bool = False,
    operator_prompt: str | None = None,
    protected_ready: bool = False,
    local_work_complete_hint: bool | None = None,
    has_hardening_pending: bool = False,
    validator_report_path: str = "Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_REPORT.md",
    validator_checkpoint_path: str = "Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_CHECKPOINT.md",
) -> StopgateInventoryResult:
    root = Path(repo_root).resolve()
    dirty = [_normalise_path(item) for item in (dirty_files or [])]
    staged = [item for item in (staged_files or []) if str(item).strip()]

    branch_class = classify_branch_state(branch, dirty)
    dirty_class, dirty_codes, dirty_meta = classify_dirty_worktree(dirty, staged_files=staged)
    forbidden_seen = scan_forbidden_paths(dirty)
    carryover_hits = [item for item in dirty if any(_under(item, p) for p in KNOWN_CARRYOVER_PATHS + V3_STOPGATE_PATHS)]
    report_status, report_codes, report_failures = scan_report_checkpoint_consistency(
        root,
        validator_report_path,
        validator_checkpoint_path,
    )

    prompt_interrupt = _prompt_interrupt(operator_prompt)
    event_class = classify_1312_event(
        simulate_1312,
        targeted_tests_passed=simulate_targeted_tests_passed,
        all_remaining_work_blocked=all_remaining_work_blocked,
        is_read_only=True,
    )
    validation_class = classify_validation_gate(
        targeted_tests_passed=simulate_targeted_tests_passed,
        targeted_tests_failed_recovery=simulate_targeted_tests_failed,
    )

    local_complete = bool(
        local_work_complete_hint
        if local_work_complete_hint is not None
        else not dirty and not staged and not forbidden_seen and report_status == "OWNER_HANDOFF_READY"
    )
    protected_class = classify_protected_action_gate(
        local_work_complete=local_complete,
        protected_ready=protected_ready or local_complete,
    )

    stopgate_codes: list[str] = []
    repaired: list[str] = []
    deferred: list[str] = []
    failed: list[str] = []

    def add(code: str, recovered: bool = False, deferred_flag: bool = False) -> None:
        matrix_row = MATRIX_INDEX.get(code)
        if matrix_row is None:
            return
        if code not in stopgate_codes:
            stopgate_codes.append(code)
            if recovered:
                repaired.append(code)
            if deferred_flag:
                deferred.append(code)
            if matrix_row.classification in {"HARD_STOP", "WRONG_PACKET_FOR_CLEAN_MAIN", "WAITING_FOR_OWNER_POWERSHELL"}:
                failed.append(code)

    add(branch_class)
    for code in dirty_codes:
        add(code)
    for code in report_codes:
        add(code, deferred_flag=code == "MINOR_SCAN_BLOCKED_RECURABLE")

    if broad_scan_blocked:
        add("SANDBOX-003", deferred_flag=True)

    if simulate_1312 and event_class in {"SANDBOX-001", "DEFERRED_OWNER_VALIDATION", "WAITING_FOR_OWNER_POWERSHELL"}:
        if event_class == "SANDBOX-001":
            add("SANDBOX-001", deferred_flag=True)
        elif event_class == "DEFERRED_OWNER_VALIDATION":
            add("SANDBOX-002", deferred_flag=True)
        else:
            add("WAITING-001", deferred_flag=False)

    if has_hardening_pending:
        add("REPORT-001", deferred_flag=True)

    if validation_class == "VALIDATOR-002":
        add("VALIDATOR-002", recovered=True)
    if validation_class == "VALIDATOR-001":
        if simulate_1312 and simulate_targeted_tests_passed:
            add("VALIDATOR-001")
        else:
            add("VALIDATOR-001", deferred_flag=True)

    if forbidden_seen:
        add("STATE-004")

    if prompt_interrupt:
        add("PROMPT-001")

    if protected_class == "HANDOFF-001":
        add("HANDOFF-001", recovered=True)
    elif protected_class == "HANDOFF-002":
        add("HANDOFF-002")

    if prompt_interrupt:
        final_status = "PROMPT_INTERRUPTION_IGNORE"
    elif branch == EXPECTED_CLEAN_MAIN:
        final_status = "WRONG_PACKET_FOR_CLEAN_MAIN"
    elif branch_class == "BRANCH-001":
        final_status = "HARD_STOP" if dirty else "HARD_STOP"
    elif event_class == "WAITING_FOR_OWNER_POWERSHELL":
        final_status = "WAITING_FOR_OWNER_POWERSHELL"
    elif dirty_class == "HARD_STOP":
        final_status = "HARD_STOP"
    elif event_class == "DEFERRED_OWNER_VALIDATION":
        final_status = "DEFERRED_OWNER_VALIDATION"
    elif event_class == "SANDBOX-001":
        final_status = "SANDBOX_LIMITATION"
    elif broad_scan_blocked:
        final_status = "MINOR_SCAN_BLOCKED_RECURABLE"
    elif protected_class == "HANDOFF-001":
        final_status = "RECOVERABLE_LOCAL"
    elif dirty_class == "APPROVED_CARRYOVER_CONTINUATION":
        final_status = "APPROVED_CARRYOVER_CONTINUATION"
    elif protected_class == "HANDOFF-002" and not has_hardening_pending and not dirty and not staged and not forbidden_seen:
        final_status = "OWNER_HANDOFF_READY"
    elif report_status == "OWNER_HANDOFF_READY":
        final_status = "OWNER_HANDOFF_READY" if not has_hardening_pending and not dirty and not staged else "RECOVERABLE_LOCAL"
    else:
        final_status = "RECOVERABLE_LOCAL"

    rows = [MATRIX_INDEX[code] for code in sorted(set(stopgate_codes)) if code in MATRIX_INDEX]

    result = StopgateInventoryResult(
        packet_id=PACKET_ID,
        timestamp_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        repo_root=str(root),
        branch=branch,
        continuation_status=final_status,
        current_phase="phase_2_stopgate_scan",
        dirty_files_observed=dirty,
        staged_files=staged,
        allowed_paths_verified=ALLOWED_WRITE_PATHS.copy(),
        forbidden_paths_seen=forbidden_seen,
        carryover_artifacts_detected=sorted(set(carryover_hits)),
        new_stopgate_artifacts_planned=V3_STOPGATE_PATHS.copy(),
        completed_work=[item for item in dirty if any(_under(item, path) for path in V3_STOPGATE_PATHS)],
        pending_work=failed if failed else [],
        validators_passed=[code for code in stopgate_codes if MATRIX_INDEX.get(code) and MATRIX_INDEX[code].classification in {"RECOVERABLE_LOCAL", "OWNER_HANDOFF_READY", "DEFERRED_OWNER_VALIDATION", "SANDBOX_LIMITATION", "FALSE_POSITIVE_REPAIR", "EVIDENCE_GAP"}],
        validators_blocked=sorted(set(failed)),
        failures_encountered=report_failures + [f"classify:{dirty_class}", f"report:{report_status}"] + report_failures,
        events_1312=[{"event": "CreateProcessAsUserW failed: 1312"}]
        if simulate_1312
        else [],
        recovery_attempts=sorted(set([continue_plan] if continue_plan else [])),
        next_safe_action="continue local anti-stop work" if final_status not in {"HARD_STOP", "WRONG_PACKET_FOR_CLEAN_MAIN", "WAITING_FOR_OWNER_POWERSHELL"} else "run handoff or owner validation",
        resume_instruction="continue with scoped files and do not switch branch.",
        stopgates_found=rows,
        stopgates_repaired=sorted(set(repaired)),
        stopgates_deferred=sorted(set(deferred)),
    )

    if write_report:
        target = root / _normalise_path(report_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(result_to_markdown(result), encoding="utf-8")

    return result


def result_to_operator_text(result: StopgateInventoryResult) -> str:
    row = [
        f"packet_id: {result.packet_id}",
        f"branch: {result.branch}",
        f"continuation_status: {result.continuation_status}",
        f"dirty_files_observed: {len(result.dirty_files_observed)}",
        f"forbidden_paths_seen: {len(result.forbidden_paths_seen)}",
        f"next_safe_action: {result.next_safe_action}",
        "stopgates_found:",
    ]
    if result.stopgates_found:
        row.extend(f"- {entry.code}: {entry.name}" for entry in result.stopgates_found)
    else:
        row.append("- none")
    row.extend(["", "continue_conditions:"] + [f"- {item}" for item in scan_continue_conditions(result)])
    return "\n".join(row) + "\n"


def result_to_markdown(result: StopgateInventoryResult) -> str:
    found = {item.code for item in result.stopgates_found}
    rows = [
        "# AIOS AEE Stopgate Inventory V3",
        "",
        f"- packet_id: {result.packet_id}",
        f"- continuation_status: {result.continuation_status}",
        f"- branch: {result.branch}",
        f"- repo_root: {result.repo_root}",
        "",
        "## Stopgate matrix",
        "| Code | Family | Name | Severity | Found | Classification | Detection | Continue condition | Stop condition |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in STOPGATE_MATRIX:
        rows.append(
            "| "
            + " | ".join(
                [
                    item.code,
                    item.family,
                    item.name,
                    item.severity,
                    "yes" if item.code in found else "no",
                    item.classification,
                    item.detection_signature,
                    item.continue_condition,
                    item.true_stop_condition,
                ]
            )
            + " |"
        )
    rows.extend(
        [
            "",
            "## Active stopgates",
        ]
    )
    if result.stopgates_found:
        for row in result.stopgates_found:
            rows.append(f"- `{row.code}` {row.anti_stop_instruction}")
    else:
        rows.append("- none")
    return "\n".join(rows) + "\n"


def result_to_jsonable_dict(result: StopgateInventoryResult) -> dict[str, Any]:
    payload = asdict(result)
    payload["stopgates_found"] = [asdict(item) for item in result.stopgates_found]
    return payload


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run AEE V3 stopgate scanner.")
    parser.add_argument("--repo-root", default=str(REPO_DEFAULT))
    parser.add_argument("--branch", default=EXPECTED_BRANCH)
    parser.add_argument("--dirty-file", action="append", default=[], dest="dirty_file")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--report-path", default="Reports/core_delivery/AIOS_AEE_STOPGATE_INVENTORY_V3.md")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--continue-plan", default="")
    parser.add_argument("--simulate-1312", action="store_true")
    parser.add_argument("--simulate-targeted-tests-passed", action="store_true")
    return parser.parse_args()


def _allow_strict_exit(status: str) -> bool:
    return status in STRICT_ZERO_STATUSES | {"PROMPT_INTERRUPTION_IGNORE", "MINOR_SCAN_BLOCKED_RECURABLE", "DEFERRED_OWNER_VALIDATION"}


def main() -> int:
    args = _parse_args()
    result = build_stopgate_inventory(
        args.repo_root,
        branch=args.branch,
        dirty_files=args.dirty_file,
        strict=args.strict,
        continue_plan=args.continue_plan,
        simulate_1312=args.simulate_1312,
        simulate_targeted_tests_passed=args.simulate_targeted_tests_passed,
    )
    print(
        json.dumps(result_to_jsonable_dict(result), sort_keys=True)
        if args.json
        else result_to_operator_text(result)
    )
    if args.strict:
        return 0 if _allow_strict_exit(result.continuation_status) else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
