"""Bounded bridge from the campaign prompt generator to the existing relay."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping

from automation.orchestration.relay.aios_codex_prompt_consumer_v1 import (
    PROTECTED_FLAGS,
    enqueue_prompt,
)


DEFAULT_FLAGS = {name: False for name in PROTECTED_FLAGS}


def build_next_pr_lifecycle_packet() -> str:
    """Return the unexecuted, approval-gated next handoff packet."""
    return """CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
TOKEN ID: AIOS-GITHUB-PR-LIFECYCLE-CONTROLLER-V1
AI_OS BOOTSTRAP REQUIRED
VALUE: YES
IDENTITY MARKER: AI_OS OWNER-SUPERVISED PR AUTOMATION
SUPERVISOR IDENTITY: HUMAN OWNER ANTHONY
WORKER IDENTITY: CODEX
PACKET ID: AIOS-GITHUB-PR-LIFECYCLE-CONTROLLER-V1
MODE: DRY_RUN
ZONE: LOCAL_REPOSITORY
LANE: PR_LIFECYCLE
WORKTREE: /workspace/Ai_Os
BRANCH: resolve after preflight

ALLOWED PATHS
- automation/orchestration/pr_lifecycle/
- tests/orchestration/
- relay/README.md

FORBIDDEN PATHS
- AGENTS.md
- RISK_POLICY.md
- .git/
- .github/
- credentials/
- secrets/
- broker/

APPROVAL AUTHORITY
Human Owner authorizes read-only design and validation only. Commit, push, PR mutation, merge, and branch deletion require separate approval.

VALIDATOR CHAIN
python -m pytest tests/orchestration -q -p no:cacheprovider
git diff --check
git status --short --branch

STOP POINT
Stop after a read-only design for validated commit creation, PR creation, review, conflict and supersession classification, obsolete PR closure, merge approval, post-merge branch cleanup, refreshed-main continuation, and owner SOS escalation.

MISSION
Design AI_OS GitHub PR Lifecycle Controller V1 without performing protected Git or GitHub actions.

PREFLIGHT
pwd
git status --short --branch
git branch --show-current
git remote -v

FINAL REPORT FORMAT
STATUS:
DESIGN:
PROTECTED ACTIONS NOT PERFORMED:
VALIDATION:
NEXT SAFE ACTION:

END OF PACKET
"""


@dataclass(frozen=True)
class CycleResult:
    status: str
    cycles: int
    prompt_sha256: str = ""
    detail: str = ""


def _task_state(relay_root: Path, task_name: str) -> str:
    for state in ("approvals", "error", "done", "running", "inbox"):
        if (relay_root / state / task_name).exists():
            return state
    return "ambiguous"


def run_self_consuming_cycle(
    *,
    generate: Callable[[], str | None],
    relay_root: Path,
    flags: Mapping[str, object] = DEFAULT_FLAGS,
    invoke_worker: Callable[[], None] | None = None,
    dry_run: bool = False,
    max_cycles: int = 12,
    max_elapsed_minutes: float = 480,
    monotonic: Callable[[], float] = time.monotonic,
) -> CycleResult:
    if max_cycles < 1 or max_elapsed_minutes <= 0:
        raise ValueError("cycle and elapsed limits must be positive")
    start = monotonic()
    previous_digest = ""
    for cycle in range(1, max_cycles + 1):
        if (relay_root / "STOP.flag").exists():
            return CycleResult("STOP_FLAG", cycle - 1, previous_digest)
        if (monotonic() - start) / 60 >= max_elapsed_minutes:
            return CycleResult("MAX_ELAPSED", cycle - 1, previous_digest)
        generated = generate()
        if not generated:
            return CycleResult("WORKFLOW_COMPLETE", cycle - 1, previous_digest)
        prompt_path = Path(generated)
        result = enqueue_prompt(prompt_path, relay_root, flags, dry_run=dry_run)
        digest = str(result["prompt_sha256"] if "prompt_sha256" in result else result["task"]["prompt_sha256"])
        if digest == previous_digest or result["status"] == "DUPLICATE":
            return CycleResult("UNCHANGED_PROMPT", cycle, digest)
        previous_digest = digest
        if result["status"] == "APPROVAL_REQUIRED":
            return CycleResult("APPROVAL_REQUIRED", cycle, digest)
        if dry_run:
            return CycleResult("DRY_RUN", cycle, digest, str(result["target"]))
        if invoke_worker is None:
            return CycleResult("CODEX_RUNTIME_UNAVAILABLE", cycle, digest)
        invoke_worker()
        state = _task_state(relay_root, Path(str(result["target"])).name)
        if state != "done":
            return CycleResult(state.upper(), cycle, digest)
    return CycleResult("MAX_CYCLES", max_cycles, previous_digest)


def _worker(repo_root: Path) -> Callable[[], None] | None:
    shell = shutil.which("pwsh") or shutil.which("powershell")
    codex = shutil.which("codex")
    if not shell or not codex:
        return None
    script = repo_root / "automation/orchestration/relay/Invoke-AiOsRelayWorker.ps1"
    return lambda: subprocess.run(
        [shell, "-NoProfile", "-File", str(script), "-Apply", "-MaxPackets", "1"],
        cwd=repo_root,
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", type=Path, help="Existing generated next-prompt artifact")
    parser.add_argument("--relay-root", type=Path, default=Path("relay"))
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--max-cycles", type=int, default=12)
    parser.add_argument("--max-minutes", type=float, default=480)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--print-next-packet", action="store_true")
    args = parser.parse_args()
    first = True

    def generate() -> str | None:
        nonlocal first
        if not first:
            return str(args.prompt)
        first = False
        return str(args.prompt)

    result = run_self_consuming_cycle(
        generate=generate,
        relay_root=args.relay_root,
        invoke_worker=None if args.dry_run else _worker(args.repo_root),
        dry_run=args.dry_run,
        max_cycles=args.max_cycles,
        max_elapsed_minutes=args.max_minutes,
    )
    print(json.dumps(result.__dict__, indent=2))
    if args.print_next_packet:
        print(build_next_pr_lifecycle_packet())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
