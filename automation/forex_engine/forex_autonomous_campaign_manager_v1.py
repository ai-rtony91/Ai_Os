"""Repo-safe helper for selecting the next FX overnight autonomy stage.

This module has no broker/API interaction, no credential handling, and no order
execution logic. It only reasons about repo-local campaign progression.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import json
import subprocess
import time


CAMPAIGN_ID = "AIOS_FOREX_AUTONOMY_FINISHER_V4"
CAMPAIGN_MODE = "APPLY_VALIDATE_PR_MERGE_CONTINUOUS_MANAGER"
SAFETY_BOUNDARY = (
    "No broker/API access, no credentials, no order execution, no live trading, "
    "no money movement, no scheduler installation, no daemon installation, and "
    "no webhook creation are used."
)

DECISION_STATUS_STAGE_SELECTED = "CAMPAIGN_STAGE_SELECTED"
DECISION_STATUS_BLOCKED = "CAMPAIGN_BLOCKED"
DECISION_STATUS_COMPLETE = "CAMPAIGN_COMPLETE"

NEXT_ACTION_RUN_STAGE = "RUN_SELECTED_STAGE"
NEXT_ACTION_RESOLVE_BLOCKERS = "RESOLVE_CAMPAIGN_BLOCKERS"
NEXT_ACTION_OPEN_FINAL_OWNER_REVIEW = "OPEN_FINAL_OWNER_REVIEW"

ALLOWED_PATHS = (
    "scripts/forex_delivery/Invoke-ForexAutonomousCampaignManager.V1.ps1",
    "automation/forex_engine/forex_autonomous_campaign_manager_v1.py",
    "tests/forex_engine/test_forex_autonomous_campaign_manager_v1.py",
    "Reports/forex_delivery/AIOS_FOREX_AUTONOMY_FINISHER_V4_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_RUNBOOK.md",
    "Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_STATE.json",
    "Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_CHECKPOINT.md",
    "Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_NEXT_CODEX_PROMPT_V1.md",
    "automation/forex_engine/flow2_supervised_demo_evidence_countdown_capture_v1.py",
    "tests/forex_engine/test_flow2_supervised_demo_evidence_countdown_capture_v1.py",
    "Reports/forex_delivery/AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_75_TO_100_OVERNIGHT_CAMPAIGN_MASTER_V2_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_75_TO_100_OVERNIGHT_PACKET_QUEUE_V2.md",
    "Reports/forex_delivery/AIOS_FOREX_75_TO_100_NEXT_CODEX_PACKET_1_V2.md",
    "Reports/forex_delivery/AIOS_FOREX_75_TO_100_NEXT_CODEX_PACKET_2_V2.md",
    "Reports/forex_delivery/AIOS_FOREX_75_TO_100_NEXT_CODEX_PACKET_3_V2.md",
)


@dataclass(frozen=True)
class CampaignStage:
    stage_id: str
    title: str
    status: str
    allowed_paths: tuple[str, ...]
    validators: tuple[str, ...]
    blockers: tuple[str, ...] = ()


@dataclass(frozen=True)
class CampaignState:
    campaign_id: str
    current_branch: str
    head: str
    dirty_files: tuple[str, ...]
    completed_stage_ids: tuple[str, ...]
    active_stage_id: str = ""
    hard_blockers: tuple[str, ...] = ()


@dataclass(frozen=True)
class CampaignDecision:
    status: str
    selected_stage_id: str
    next_action: str
    blockers: tuple[str, ...]
    allowed_paths: tuple[str, ...]
    validators: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "selected_stage_id": self.selected_stage_id,
            "next_action": self.next_action,
            "blockers": list(self.blockers),
            "allowed_paths": list(self.allowed_paths),
            "validators": list(self.validators),
        }


def build_default_forex_campaign_stages() -> tuple[CampaignStage, ...]:
    return (
        CampaignStage(
            stage_id="FLOW2_EVIDENCE_COUNTDOWN_LANDING",
            title="Flow 2 evidence countdown landing",
            status="PENDING",
            allowed_paths=(
                "automation/forex_engine/flow2_supervised_demo_evidence_countdown_capture_v1.py",
                "tests/forex_engine/test_flow2_supervised_demo_evidence_countdown_capture_v1.py",
                "Reports/forex_delivery/AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE_V1_REPORT.md",
                "Reports/forex_delivery/AIOS_FOREX_75_TO_100_OVERNIGHT_CAMPAIGN_MASTER_V2_REPORT.md",
                "Reports/forex_delivery/AIOS_FOREX_75_TO_100_OVERNIGHT_PACKET_QUEUE_V2.md",
                "Reports/forex_delivery/AIOS_FOREX_75_TO_100_NEXT_CODEX_PACKET_1_V2.md",
                "Reports/forex_delivery/AIOS_FOREX_75_TO_100_NEXT_CODEX_PACKET_2_V2.md",
                "Reports/forex_delivery/AIOS_FOREX_75_TO_100_NEXT_CODEX_PACKET_3_V2.md",
            ),
            validators=(
                "python -m py_compile automation/forex_engine/flow2_supervised_demo_evidence_countdown_capture_v1.py",
                "python -m pytest tests/forex_engine/test_flow2_supervised_demo_evidence_countdown_capture_v1.py -q",
            ),
        ),
        CampaignStage(
            stage_id="LIVE_CAPABILITY_GOVERNANCE_GATE",
            title="Live capability governance gate",
            status="PENDING",
            allowed_paths=(
                "scripts/forex_delivery/Invoke-ForexAutonomousCampaignManager.V1.ps1",
                "Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_RUNBOOK.md",
                "Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_STATE.json",
            ),
            validators=(
                "python -m py_compile automation/forex_engine/forex_autonomous_campaign_manager_v1.py",
                "python -m pytest tests/forex_engine/test_forex_autonomous_campaign_manager_v1.py -q",
            ),
        ),
        CampaignStage(
            stage_id="PROFIT_LOOP_ACCELERATION_GATE",
            title="Profit loop acceleration gate",
            status="PENDING",
            allowed_paths=(
                "Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_STATE.json",
                "Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_CHECKPOINT.md",
            ),
            validators=("Manual governance handoff review",),
        ),
        CampaignStage(
            stage_id="BROKER_DEMO_TO_LIVE_GATE_PREFLIGHT_MAP",
            title="Broker demo to live preflight map",
            status="PENDING",
            allowed_paths=(
                "Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_CHECKPOINT.md",
                "Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_NEXT_CODEX_PROMPT_V1.md",
            ),
            validators=("No runtime broker call execution allowed",),
        ),
        CampaignStage(
            stage_id="FINAL_OWNER_REPORT",
            title="Final owner review handoff",
            status="PENDING",
            allowed_paths=(
                "Reports/forex_delivery/AIOS_FOREX_AUTONOMY_FINISHER_V4_REPORT.md",
                "Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_NEXT_CODEX_PROMPT_V1.md",
                "Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_CHECKPOINT.md",
            ),
            validators=("Owner review signoff required",),
        ),
    )


def build_campaign_checkpoint(
    *,
    decision: CampaignDecision,
    state: CampaignState,
    safety_boundary: str = SAFETY_BOUNDARY,
) -> str:
    return f"""# AIOS Forex Autonomy Checkpoint

Campaign ID: {state.campaign_id}
Current branch: {state.current_branch}
Head: {state.head}
Selected stage: {decision.selected_stage_id}
Decision status: {decision.status}
Next action: {decision.next_action}

## Blockers
{_format_as_markdown_list(decision.blockers)}

## Allowed paths
{_format_as_markdown_list(decision.allowed_paths)}

## Validators
{_format_as_markdown_list(decision.validators)}

## Safety boundary
{safety_boundary}
"""


def build_next_codex_prompt(
    *,
    decision: CampaignDecision,
    state: CampaignState,
    mission: str = "AIOS Forex autonomy finisher continuation",
    stop_point: str = "Stop when status is CAMPAIGN_COMPLETE or CAMPAIGN_BLOCKED.",
    validator_chain: str = (
        "python -m py_compile automation/forex_engine/forex_autonomous_campaign_manager_v1.py | "
        "python -m pytest tests/forex_engine/test_forex_autonomous_campaign_manager_v1.py -q | "
        "python -m py_compile automation/forex_engine/flow2_supervised_demo_evidence_countdown_capture_v1.py | "
        "python -m pytest tests/forex_engine/test_flow2_supervised_demo_evidence_countdown_capture_v1.py -q"
    ),
) -> str:
    allowed = "\n".join(f"- {path}" for path in ALLOWED_PATHS)
    forbidden = (
        "- AGENTS.md\\n"
        "- README.md\\n"
        "- WHITEPAPER.md\\n"
        "- RISK_POLICY.md\\n"
        "- docs/architecture/AI_OS_WHITEPAPER.md\\n"
        "- .env\\n"
        "- .env.*\\n"
        "- *.key\\n"
        "- *.pem\\n"
        "- *.p12\\n"
        "- *.pfx\\n"
        "- secrets/*\\n"
        "- credentials/*\\n"
        "- services/*\\n"
        "- apps/*\\n"
        "- telemetry/*\\n"
        "- any broker credential file\\n"
        "- any broker API client\\n"
        "- any live order file\\n"
        "- any scheduler install file\\n"
        "- any daemon install file\\n"
        "- any webhook file\\n"
        "- any file outside ALLOWED PATHS"
    )
    approval_authority = (
        "- preserve current Flow 2 files\\n"
        "- stage-safe edits only\\n"
        "- run required validators\\n"
        "- no broker/API, credentials, order execution, live trading, money movement\\n"
        "- no scheduler/daemon/webhook changes\\n"
    )

    return f"""CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

## IDENTITY MARKER
Project: AI_OS
Repository: ai-rtony91/Ai_Os
Worktree: C:\\\\Dev\\\\Ai.Os
Supervisor identity: ChatGPT planning supervisor
Worker identity: Codex Forex autonomy finisher worker
Packet ID: AIOS_FOREX_AUTONOMY_FINISHER_V4
Mode: {CAMPAIGN_MODE}
Zone: FOREX_AUTONOMOUS_CAMPAIGN_MANAGER
Lane: Forex / autonomy finisher / overnight continuous execution

## ALLOWED PATHS
{allowed}

## FORBIDDEN PATHS
{forbidden}

## APPROVAL AUTHORITY
{approval_authority}

## VALIDATOR CHAIN
{validator_chain}

## STOP POINT
{stop_point}

## MISSION
{mission}

## CURRENT STATE
campaign_id: {state.campaign_id}
current_branch: {state.current_branch}
head: {state.head}
dirty_files: {list(state.dirty_files)}
completed_stage_ids: {list(state.completed_stage_ids)}
active_stage_id: {state.active_stage_id}
selected_stage_id: {decision.selected_stage_id}
next_action: {decision.next_action}

## TASK
Run the next validator and follow repository-safe steps for stage {decision.selected_stage_id}.

## FINAL REPORT FORMAT
AUTONOMY_FINISHER_STATUS:
STAGE_A_FLOW2_PRESERVATION:
STAGE_B_CAMPAIGN_MANAGER:
FILES_CREATED:
FILES_CHANGED:
VALIDATORS_RUN:
VALIDATORS_PASSED:
VALIDATORS_FAILED:
PR_CREATED:
PR_MERGED:
CURRENT_BRANCH:
CURRENT_HEAD:
FINAL_GIT_STATUS:
SAFETY_BOUNDARY:
BROKER_API_ACCESS:
CREDENTIALS_USED:
ORDER_EXECUTION:
LIVE_TRADING:
MONEY_MOVEMENT:
SCHEDULERS_DAEMONS_WEBHOOKS:
NEXT_SAFE_ACTION:
STOP_REASON:
"""


def _format_as_markdown_list(values: tuple[str, ...]) -> str:
    if not values:
        return "- None"
    return "\n".join(f"- {value}" for value in values)


def select_next_campaign_stage(
    campaign_state: CampaignState,
    stages: tuple[CampaignStage, ...] | None = None,
) -> CampaignDecision:
    if stages is None:
        stages = build_default_forex_campaign_stages()

    stage_by_id = {stage.stage_id: stage for stage in stages}

    if campaign_state.hard_blockers:
        return CampaignDecision(
            status=DECISION_STATUS_BLOCKED,
            selected_stage_id="",
            next_action=NEXT_ACTION_RESOLVE_BLOCKERS,
            blockers=campaign_state.hard_blockers,
            allowed_paths=(),
            validators=(),
        )

    unknown_dirty_files = _find_unknown_dirty_files(
        campaign_state.dirty_files,
        allowed_paths=ALLOWED_PATHS,
    )
    if unknown_dirty_files:
        return CampaignDecision(
            status=DECISION_STATUS_BLOCKED,
            selected_stage_id="",
            next_action=NEXT_ACTION_RESOLVE_BLOCKERS,
            blockers=unknown_dirty_files,
            allowed_paths=ALLOWED_PATHS,
            validators=(),
        )

    completed = set(campaign_state.completed_stage_ids)
    if (
        campaign_state.active_stage_id
        and campaign_state.active_stage_id in stage_by_id
        and campaign_state.active_stage_id not in completed
    ):
        active_stage = stage_by_id[campaign_state.active_stage_id]
        return CampaignDecision(
            status=DECISION_STATUS_STAGE_SELECTED,
            selected_stage_id=active_stage.stage_id,
            next_action=NEXT_ACTION_RUN_STAGE,
            blockers=active_stage.blockers,
            allowed_paths=active_stage.allowed_paths,
            validators=active_stage.validators,
        )

    if len(stages) == len(completed):
        return CampaignDecision(
            status=DECISION_STATUS_COMPLETE,
            selected_stage_id="",
            next_action=NEXT_ACTION_OPEN_FINAL_OWNER_REVIEW,
            blockers=(),
            allowed_paths=ALLOWED_PATHS,
            validators=(),
        )

    for stage in stages:
        if stage.stage_id not in completed:
            return CampaignDecision(
                status=DECISION_STATUS_STAGE_SELECTED,
                selected_stage_id=stage.stage_id,
                next_action=NEXT_ACTION_RUN_STAGE,
                blockers=stage.blockers,
                allowed_paths=stage.allowed_paths,
                validators=stage.validators,
            )

    return CampaignDecision(
        status=DECISION_STATUS_COMPLETE,
        selected_stage_id="",
        next_action=NEXT_ACTION_OPEN_FINAL_OWNER_REVIEW,
        blockers=(),
        allowed_paths=ALLOWED_PATHS,
        validators=(),
    )


def _run_git_command(args: tuple[str, ...], repo_root: Path) -> str:
    result = subprocess.run(
        ("git", *args),
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _collect_dirty_files(repo_root: Path) -> tuple[str, ...]:
    porcelain = _run_git_command(("status", "--porcelain=v1"), repo_root)
    if not porcelain:
        return ()

    dirty_files: list[str] = []
    for line in porcelain.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if not path:
            continue
        dirty_files.append(path.replace("\\", "/"))
    return tuple(sorted(dirty_files))


def _is_unknown_dirty_file(path: str, allowed_paths: tuple[str, ...]) -> bool:
    norm_path = path.replace("\\", "/")
    for allowed in allowed_paths:
        if norm_path == allowed:
            return False
        if norm_path.startswith(f"{allowed}/"):
            return False
    return True


def _find_unknown_dirty_files(
    dirty_files: tuple[str, ...],
    allowed_paths: tuple[str, ...],
) -> tuple[str, ...]:
    unknown = tuple(path for path in dirty_files if _is_unknown_dirty_file(path, allowed_paths))
    return unknown


def collect_campaign_state(repo_root: str = "C:\\Dev\\Ai.Os") -> CampaignState:
    root = Path(repo_root).resolve()
    branch = _run_git_command(("branch", "--show-current"), root) or "unknown"
    head = _run_git_command(("rev-parse", "--short", "HEAD"), root) or "unknown"
    dirty_files = _collect_dirty_files(root)
    return CampaignState(
        campaign_id=CAMPAIGN_ID,
        current_branch=branch,
        head=head,
        dirty_files=dirty_files,
        completed_stage_ids=(),
        active_stage_id="",
        hard_blockers=(),
    )


def _read_or_default_state(state_path: Path) -> CampaignState:
    if not state_path.exists():
        return collect_campaign_state()

    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return collect_campaign_state()

    return CampaignState(
        campaign_id=CAMPAIGN_ID,
        current_branch=collect_campaign_state().current_branch,
        head=collect_campaign_state().head,
        dirty_files=_collect_dirty_files(Path("C:\\\\Dev\\\\Ai.Os")),
        completed_stage_ids=tuple(payload.get("completed_stage_ids", ())),
        active_stage_id=payload.get("selected_stage_id", ""),
        hard_blockers=tuple(payload.get("blockers", ())),
    )


def run_manager_cycle(state_path: Path, checkpoint_path: Path, next_prompt_path: Path) -> CampaignDecision:
    current_state = _read_or_default_state(state_path)
    stages = build_default_forex_campaign_stages()
    decision = select_next_campaign_stage(current_state, stages=stages)

    checkpoint = build_campaign_checkpoint(
        decision=decision,
        state=current_state,
        safety_boundary=SAFETY_BOUNDARY,
    )
    next_prompt = build_next_codex_prompt(
        decision=decision,
        state=current_state,
    )

    state_payload = {
        "campaign_id": CAMPAIGN_ID,
        "status": decision.status,
        "selected_stage_id": decision.selected_stage_id,
        "next_action": decision.next_action,
        "completed_stage_ids": list(current_state.completed_stage_ids),
        "blockers": list(decision.blockers),
        "safety_boundary": SAFETY_BOUNDARY,
        "generated_at_note": (
            "Static generated_at_note retained for deterministic evidence; "
            "module does not rely on clock time."
        ),
    }

    state_payload.update({"current_branch": current_state.current_branch, "head": current_state.head})

    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checkpoint_path.write_text(checkpoint, encoding="utf-8")
    next_prompt_path.write_text(next_prompt, encoding="utf-8")

    return decision


def run_campaign_manager(
    repo_root: Path,
    state_path: Path,
    checkpoint_path: Path,
    prompt_path: Path,
    max_cycles: int,
    max_minutes: int,
) -> tuple[CampaignDecision, str]:
    start_time = time.monotonic()
    decision = CampaignDecision(
        status=DECISION_STATUS_COMPLETE,
        selected_stage_id="",
        next_action=NEXT_ACTION_OPEN_FINAL_OWNER_REVIEW,
        blockers=(),
        allowed_paths=ALLOWED_PATHS,
        validators=(),
    )

    stop_reason = "CAMPAIGN_COMPLETE"
    for cycle in range(1, max(max_cycles, 1) + 1):
        if (time.monotonic() - start_time) / 60.0 > max_minutes:
            stop_reason = "MAX_MINUTES_EXCEEDED"
            break

        decision = run_manager_cycle(state_path, checkpoint_path, prompt_path)
        if decision.status != DECISION_STATUS_STAGE_SELECTED:
            stop_reason = {
                DECISION_STATUS_COMPLETE: "CAMPAIGN_COMPLETE",
                DECISION_STATUS_BLOCKED: "CAMPAIGN_BLOCKED",
            }.get(decision.status, "UNKNOWN_STATE")
            break
        if cycle >= max_cycles:
            stop_reason = "MAX_CYCLES_REACHED"
            break

    return decision, stop_reason


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-path", default="Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_STATE.json")
    parser.add_argument("--checkpoint-path", default="Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_CHECKPOINT.md")
    parser.add_argument("--next-prompt-path", default="Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_NEXT_CODEX_PROMPT_V1.md")
    parser.add_argument("--repo-root", default="C:\\Dev\\Ai.Os")
    parser.add_argument("--max-cycles", type=int, default=12)
    parser.add_argument("--max-minutes", type=int, default=480)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-publish", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    _, stop_reason = run_campaign_manager(
        repo_root=Path(args.repo_root).resolve(),
        state_path=Path(args.state_path),
        checkpoint_path=Path(args.checkpoint_path),
        prompt_path=Path(args.next_prompt_path),
        max_cycles=args.max_cycles,
        max_minutes=args.max_minutes,
    )
    # dry-run and no-publish are accepted by interface for safety and future extensibility.
    # behavior is repo-safe in both modes.
    current_state = collect_campaign_state(args.repo_root)
    decision = select_next_campaign_stage(current_state)
    payload = decision.to_dict()
    payload.update(
        {
            "status": decision.status,
            "selected_stage_id": decision.selected_stage_id,
            "next_action": decision.next_action,
            "stop_reason": stop_reason,
            "campaign_id": current_state.campaign_id,
            "current_branch": current_state.current_branch,
            "head": current_state.head,
        }
    )
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
