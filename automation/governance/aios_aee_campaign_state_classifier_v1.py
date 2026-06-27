from __future__ import annotations

"""Campaign state classifier for AIOS AEE compound execution."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

PACKET_ID = "AIOS-AEE-COMPOUND-SPARK-LONGRUN-IMPLEMENTATION-CAMPAIGN-V1"
TARGET_BRANCH = "lane/aios-aee-governance-validator-v1"
CLEAN_MAIN_BRANCH = "main"

ALLOWED_WRITE_PATHS: list[str] = [
    "automation/governance/",
    "scripts/governance/",
    "tests/governance/",
    "tests/fixtures/governance/",
    "docs/governance/",
    "docs/workflows/",
    "Reports/core_delivery/",
]

FORBIDDEN_PATH_PREFIXES: list[str] = [
    ".env",
    ".env/",
    "secrets/",
    "credentials/",
    "private/",
    "Reports/forex_delivery/",
    "automation/forex_engine/",
    "scripts/forex_delivery/",
    "tests/forex_engine/",
    "schemas/aios/forex/",
]

KNOWN_V1_V3_CARRYOVER_PATHS: list[str] = [
    "automation/governance/aios_aee_governance_validator_v1.py",
    "automation/governance/aios_aee_stopgate_inventory_v3.py",
    "scripts/governance/run_aios_aee_governance_validator_v1.py",
    "scripts/governance/run_aios_aee_stopgate_inventory_v3.py",
    "tests/governance/test_aios_aee_governance_validator_v1.py",
    "tests/governance/test_aios_aee_stopgate_inventory_v3.py",
    "tests/fixtures/governance/aee_validator/",
    "tests/fixtures/governance/aee_stopgate_inventory_v3/",
    "docs/workflows/AIOS_AEE_GOVERNANCE_VALIDATOR_V1.md",
    "docs/workflows/AIOS_AEE_ANTI_STOP_CARRYOVER_CONTINUATION_V3.md",
    "Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_CHECKPOINT.md",
    "Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_REPORT.md",
    "Reports/core_delivery/AIOS_AEE_STOPGATE_INVENTORY_V3.md",
    "Reports/core_delivery/AIOS_AEE_STOPGATE_CARRYOVER_CONTINUATION_V3_CHECKPOINT.md",
    "Reports/core_delivery/AIOS_AEE_STOPGATE_CARRYOVER_CONTINUATION_V3_REPORT.md",
]

KNOWN_COMPOUND_PATHS: list[str] = [
    "automation/governance/aios_aee_campaign_state_classifier_v1.py",
    "automation/governance/aios_aee_validator_execution_planner_v1.py",
    "automation/governance/aios_aee_owner_handoff_builder_v1.py",
    "automation/governance/aios_aee_static_ci_guard_v1.py",
    "automation/governance/aios_aee_campaign_metrics_v1.py",
    "scripts/governance/run_aios_aee_compound_campaign_v1.py",
    "tests/governance/test_aios_aee_compound_campaign_v1.py",
    "tests/fixtures/governance/aee_compound_campaign_v1/",
    "docs/workflows/AIOS_AEE_COMPOUND_SPARK_LONGRUN_CAMPAIGN_V1.md",
    "Reports/core_delivery/AIOS_AEE_COMPOUND_SPARK_LONGRUN_CAMPAIGN_V1_CHECKPOINT.md",
    "Reports/core_delivery/AIOS_AEE_COMPOUND_SPARK_LONGRUN_CAMPAIGN_V1_REPORT.md",
]

PROMPT_REVIEW_PATTERNS = (
    "explain this codebase",
    "search this codebase",
    "run /review",
    "review this codebase",
)
PROMPT_STOP_PATTERNS = ("cancel", "hard stop", "stop now", "stop packet")


def _normalise(value: str | Path) -> str:
    text = str(value).replace("\\", "/").strip().lower()
    while text.startswith("./"):
        text = text[2:]
    return text


def _under(candidate: str, prefix: str) -> bool:
    candidate_norm = _normalise(candidate)
    prefix_norm = _normalise(prefix).rstrip("/")
    return candidate_norm == prefix_norm or candidate_norm.startswith(prefix_norm + "/")


def _coerce_items(items: Iterable[str] | None) -> list[str]:
    return [_normalise(item) for item in (items or []) if str(item).strip()]


@dataclass(frozen=True)
class CampaignStateClassifierResult:
    packet_id: str
    branch: str
    continuation_status: str
    dirty_files_observed: list[str]
    staged_files_observed: list[str]
    carryover_artifacts: list[str]
    allowed_dirty_files: list[str]
    noncarryover_dirty_files: list[str]
    forbidden_paths_seen: list[str]
    prompt_status: str
    summary: list[str]
    next_safe_action: str
    resume_instruction: str
    timestamp_utc: str


def classify_forbidden_paths(dirty_files: Iterable[str]) -> list[str]:
    found: list[str] = []
    for path in _coerce_items(dirty_files):
        if any(_under(path, forbidden) for forbidden in FORBIDDEN_PATH_PREFIXES):
            if path not in found:
                found.append(path)
    return found


def classify_staged_files(staged_files: Iterable[str] | None) -> tuple[str, list[str]]:
    staged = _coerce_items(staged_files)
    if not staged:
        return "RECOVERABLE_LOCAL", []
    return "HARD_STOP", staged


def classify_dirty_files(
    dirty_files: Iterable[str] | None,
    *,
    require_compound: bool = False,
) -> tuple[str, list[str], list[str], list[str], list[str]]:
    dirty = _coerce_items(dirty_files)
    if not dirty:
        return "RECOVERABLE_LOCAL", [], [], [], []

    forbidden = classify_forbidden_paths(dirty)
    if forbidden:
        return "HARD_STOP", [], [], [], forbidden

    allowed = [path for path in dirty if any(_under(path, prefix) for prefix in ALLOWED_WRITE_PATHS)]
    if not allowed:
        return "HARD_STOP", [], [], list(dirty), forbidden

    carryover_hits = [path for path in dirty if any(_under(path, prefix) for prefix in KNOWN_V1_V3_CARRYOVER_PATHS)]
    compound_hits = [path for path in dirty if any(_under(path, prefix) for prefix in KNOWN_COMPOUND_PATHS)]
    noncarryover = [path for path in dirty if path not in carryover_hits and path not in compound_hits]

    if require_compound and not compound_hits:
        return "APPROVED_CARRYOVER_CONTINUATION", carryover_hits, allowed, noncarryover, forbidden
    if compound_hits and not noncarryover:
        return "APPROVED_COMPOUND_CARRYOVER_CONTINUATION", carryover_hits + compound_hits, allowed, noncarryover, forbidden
    if carryover_hits and not noncarryover:
        return "APPROVED_CARRYOVER_CONTINUATION", carryover_hits, allowed, noncarryover, forbidden
    return "RECOVERABLE_LOCAL", carryover_hits + compound_hits, allowed, noncarryover, forbidden


def classify_branch(branch: str | None, dirty_files: Iterable[str] | None = None) -> str:
    current = _normalise(branch or "")
    if current == CLEAN_MAIN_BRANCH:
        return "WRONG_PACKET_FOR_CLEAN_MAIN"
    if current != _normalise(TARGET_BRANCH):
        return "HARD_STOP"
    return "APPROVED_CARRYOVER_CONTINUATION" if dirty_files and any(_coerce_items(dirty_files)) else "RECOVERABLE_LOCAL"


def classify_prompt_interruption(prompt: str | None) -> str:
    if not prompt:
        return ""
    lower_prompt = prompt.lower()
    if any(token in lower_prompt for token in PROMPT_STOP_PATTERNS):
        return "HARD_STOP"
    if any(token in lower_prompt for token in PROMPT_REVIEW_PATTERNS):
        return "PROMPT_INTERRUPTION_REVIEW_QUEUE"
    return ""


def classify_owner_handoff_state(
    *,
    local_work_complete: bool,
    forbidden_paths: Sequence[str],
    staged_files: Sequence[str],
    deferred_validation: bool,
) -> str:
    if deferred_validation:
        return "DEFERRED_OWNER_VALIDATION"
    if local_work_complete and not forbidden_paths and not staged_files:
        return "OWNER_HANDOFF_READY"
    return "RECOVERABLE_LOCAL"


def _build_result(
    branch: str,
    status: str,
    dirty: list[str],
    staged: list[str],
    carryover_artifacts: list[str],
    allowed_dirty: list[str],
    noncarryover: list[str],
    forbidden_paths: list[str],
    prompt_status: str,
    summary: list[str],
    next_safe_action: str,
    resume_instruction: str,
) -> CampaignStateClassifierResult:
    return CampaignStateClassifierResult(
        packet_id=PACKET_ID,
        branch=branch,
        continuation_status=status,
        dirty_files_observed=dirty,
        staged_files_observed=staged,
        carryover_artifacts=carryover_artifacts,
        allowed_dirty_files=allowed_dirty,
        noncarryover_dirty_files=noncarryover,
        forbidden_paths_seen=forbidden_paths,
        prompt_status=prompt_status,
        summary=summary,
        next_safe_action=next_safe_action,
        resume_instruction=resume_instruction,
        timestamp_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    )


def classify_campaign_state(
    *,
    branch: str,
    dirty_files: Sequence[str] | None = None,
    staged_files: Sequence[str] | None = None,
    operator_prompt: str | None = None,
    local_work_complete: bool = False,
    simulate_1312: bool = False,
    targeted_tests_passed: bool = False,
    all_remaining_work_blocked: bool = False,
    broad_scan_blocked: bool = False,
    deferred_validation: bool = False,
) -> CampaignStateClassifierResult:
    dirty = _coerce_items(dirty_files)
    staged = _coerce_items(staged_files)

    dirty_status, carryover_hits, allowed_dirty, noncarryover_dirty, forbidden_paths = classify_dirty_files(
        dirty,
        require_compound=False,
    )
    branch_status = classify_branch(branch, dirty_files=dirty)
    if branch_status == "WRONG_PACKET_FOR_CLEAN_MAIN":
        return _build_result(
            branch=branch,
            status="WRONG_PACKET_FOR_CLEAN_MAIN",
            dirty=dirty,
            staged=staged,
            carryover_artifacts=carryover_hits,
            allowed_dirty=allowed_dirty,
            noncarryover=noncarryover_dirty,
            forbidden_paths=forbidden_paths,
            prompt_status="",
            summary=[
                "clean-main preflight intentionally bypassed because this is the approved carryover packet lane."
            ],
            next_safe_action="run only on lane/aios-aee-governance-validator-v1.",
            resume_instruction="stop now and align branch.",
        )

    if branch_status == "HARD_STOP":
        return _build_result(
            branch=branch,
            status="HARD_STOP",
            dirty=dirty,
            staged=staged,
            carryover_artifacts=carryover_hits,
            allowed_dirty=allowed_dirty,
            noncarryover=noncarryover_dirty,
            forbidden_paths=forbidden_paths,
            prompt_status="",
            summary=["branch does not match expected campaign lane."],
            next_safe_action="keep to this lane until carryover tasks finish.",
            resume_instruction="do not switch to unrelated branches.",
        )

    prompt_status = classify_prompt_interruption(operator_prompt)
    if prompt_status == "HARD_STOP":
        return _build_result(
            branch=branch,
            status="HARD_STOP",
            dirty=dirty,
            staged=staged,
            carryover_artifacts=carryover_hits,
            allowed_dirty=allowed_dirty,
            noncarryover=noncarryover_dirty,
            forbidden_paths=forbidden_paths,
            prompt_status=prompt_status,
            summary=["operator explicitly requested stop."],
            next_safe_action="pause and wait for Owner confirmation.",
            resume_instruction="do not continue while stop prompt remains active.",
        )
    if prompt_status == "PROMPT_INTERRUPTION_REVIEW_QUEUE":
        return _build_result(
            branch=branch,
            status="PROMPT_INTERRUPTION_REVIEW_QUEUE",
            dirty=dirty,
            staged=staged,
            carryover_artifacts=carryover_hits,
            allowed_dirty=allowed_dirty,
            noncarryover=noncarryover_dirty,
            forbidden_paths=forbidden_paths,
            prompt_status=prompt_status,
            summary=["accidental review/analysis prompt queued; campaign scope unchanged."],
            next_safe_action="record prompt interruption and continue.",
            resume_instruction="continue this packet unless explicit stop arrives.",
        )

    staged_status, staged_failures = classify_staged_files(staged)
    if staged_status == "HARD_STOP":
        return _build_result(
            branch=branch,
            status="HARD_STOP",
            dirty=dirty,
            staged=staged_failures,
            carryover_artifacts=carryover_hits,
            allowed_dirty=allowed_dirty,
            noncarryover=noncarryover_dirty,
            forbidden_paths=forbidden_paths,
            prompt_status=prompt_status,
            summary=["staged file list must be empty for local execution."],
            next_safe_action="keep staged files out of local execution.",
            resume_instruction="owner may handoff only when ready.",
        )

    if forbidden_paths:
        return _build_result(
            branch=branch,
            status="HARD_STOP",
            dirty=dirty,
            staged=staged,
            carryover_artifacts=carryover_hits,
            allowed_dirty=allowed_dirty,
            noncarryover=noncarryover_dirty,
            forbidden_paths=forbidden_paths,
            prompt_status=prompt_status,
            summary=["forbidden path present in dirty list."],
            next_safe_action="remove forbidden entries and continue.",
            resume_instruction="keep all remaining edits inside allowed paths.",
        )

    if broad_scan_blocked:
        return _build_result(
            branch=branch,
            status="MINOR_SCAN_BLOCKED_RECOVERABLE",
            dirty=dirty,
            staged=staged,
            carryover_artifacts=carryover_hits,
            allowed_dirty=allowed_dirty,
            noncarryover=noncarryover_dirty,
            forbidden_paths=forbidden_paths,
            prompt_status=prompt_status,
            summary=["scan command was blocked; continue with explicit file targets."],
            next_safe_action="avoid broad scans and continue.",
            resume_instruction="use explicit known paths for next command.",
        )

    if simulate_1312:
        if all_remaining_work_blocked:
            return _build_result(
                branch=branch,
                status="SANDBOX_LIMITATION",
                dirty=dirty,
                staged=staged,
                carryover_artifacts=carryover_hits,
                allowed_dirty=allowed_dirty,
                noncarryover=noncarryover_dirty,
                forbidden_paths=forbidden_paths,
                prompt_status=prompt_status,
                summary=["remaining commands are blocked by 1312."],
                next_safe_action="record owner validation request and defer.",
                resume_instruction="wait for owner PowerShell validation pass.",
            )
        if targeted_tests_passed or deferred_validation:
            return _build_result(
                branch=branch,
                status="DEFERRED_OWNER_VALIDATION",
                dirty=dirty,
                staged=staged,
                carryover_artifacts=carryover_hits,
                allowed_dirty=allowed_dirty,
                noncarryover=noncarryover_dirty,
                forbidden_paths=forbidden_paths,
                prompt_status=prompt_status,
                summary=["strict CLI is deferred for owner validation."],
                next_safe_action="finish remaining local work and hand off.",
                resume_instruction="no protected command execution by Codex.",
            )
        return _build_result(
            branch=branch,
            status="RECOVERABLE_LOCAL",
            dirty=dirty,
            staged=staged,
            carryover_artifacts=carryover_hits,
            allowed_dirty=allowed_dirty,
            noncarryover=noncarryover_dirty,
            forbidden_paths=forbidden_paths,
            prompt_status=prompt_status,
            summary=["1312 observed; retry once for read-only command."],
            next_safe_action="continue with explicit commands and one retry path.",
            resume_instruction="do not continue unbounded command retries.",
        )

    handoff_status = classify_owner_handoff_state(
        local_work_complete=local_work_complete,
        forbidden_paths=forbidden_paths,
        staged_files=staged,
        deferred_validation=deferred_validation,
    )
    if handoff_status == "OWNER_HANDOFF_READY":
        return _build_result(
            branch=branch,
            status="OWNER_HANDOFF_READY",
            dirty=dirty,
            staged=staged,
            carryover_artifacts=carryover_hits,
            allowed_dirty=allowed_dirty,
            noncarryover=noncarryover_dirty,
            forbidden_paths=forbidden_paths,
            prompt_status="",
            summary=["local campaign work completed; handoff is ready."],
            next_safe_action="generate owner publish/check and merge/sync blocks.",
            resume_instruction="owner executes protected commands only.",
        )

    if dirty_status in {"APPROVED_COMPOUND_CARRYOVER_CONTINUATION", "APPROVED_CARRYOVER_CONTINUATION"}:
        return _build_result(
            branch=branch,
            status=dirty_status,
            dirty=dirty,
            staged=staged,
            carryover_artifacts=carryover_hits,
            allowed_dirty=allowed_dirty,
            noncarryover=noncarryover_dirty,
            forbidden_paths=forbidden_paths,
            prompt_status=prompt_status,
            summary=["approved continuation state observed."],
            next_safe_action="continue required work tracks.",
            resume_instruction="maintain explicit known-path edits.",
        )

    return _build_result(
        branch=branch,
        status="RECOVERABLE_LOCAL",
        dirty=dirty,
        staged=staged,
        carryover_artifacts=carryover_hits,
        allowed_dirty=allowed_dirty,
        noncarryover=noncarryover_dirty,
        forbidden_paths=forbidden_paths,
        prompt_status=prompt_status,
        summary=["no hard stop and no explicit owner handoff condition."],
        next_safe_action="continue local implementation tracks.",
        resume_instruction="preserve approved-carryover continuation artifacts.",
    )


def result_to_jsonable_dict(result: CampaignStateClassifierResult) -> dict[str, object]:
    return asdict(result)


def result_to_markdown(result: CampaignStateClassifierResult) -> str:
    lines = [
        "# AIOS AEE Campaign State Classifier",
        "",
        f"packet_id: {result.packet_id}",
        f"branch: {result.branch}",
        f"continuation_status: {result.continuation_status}",
        f"timestamp_utc: {result.timestamp_utc}",
        "",
        f"dirty_files: {len(result.dirty_files_observed)}",
        f"staged_files: {len(result.staged_files_observed)}",
        f"forbidden_paths_seen: {len(result.forbidden_paths_seen)}",
        "",
        "summary:",
    ]
    lines.extend(f"- {item}" for item in result.summary)
    lines.extend(
        [
            "",
            f"next_safe_action: {result.next_safe_action}",
            f"resume_instruction: {result.resume_instruction}",
        ]
    )
    return "\n".join(lines) + "\n"


def result_to_operator_text(result: CampaignStateClassifierResult) -> str:
    return (
        f"status={result.continuation_status}, branch={result.branch}, "
        f"dirty={len(result.dirty_files_observed)}, staged={len(result.staged_files_observed)}, "
        f"forbidden={len(result.forbidden_paths_seen)}"
    )

