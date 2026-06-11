"""AI_OS decision-to-packet drafter (observe-only).

The gap-to-goal classifier emits goal CANDIDATES. The next-action decider may
recommend PROPOSE_NEXT_GOAL. Nothing on main turns an approved candidate into a
governed work-packet draft. This module closes that arrow: it renders one goal
candidate into a CODEX-ONLY PROMPT packet DRAFT shaped to satisfy the governance
validator's required sections.

Safety posture:
  * Observe-only. Produces DRAFT text. Optionally writes ONE .md draft under an
    allowed reports area. It NEVER writes into work_packets/, NEVER mutates packet
    or approval state, NEVER commits/pushes/merges, NEVER executes.
  * DRY_RUN mode only. The draft always declares MODE: DRY_RUN-FIRST, attaches the
    full forbidden-paths safety set, and states that commit/push/merge each need a
    separate explicit Human Owner approval.
  * Path honesty. The classifier deliberately does not auto-scope allowed paths. If
    the caller does not supply concrete allowed_paths, the draft is emitted with a
    conservative derived path and marked DRAFT_NEEDS_PATH_CONFIRMATION (never
    "ready"), so the completeness reviewer gates it. No unresolved <TOKEN>
    placeholders are ever emitted (they would, correctly, fail governance).

Pure standard library. No network. No mutation beyond an explicit draft write.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


SCHEMA = "AIOS_PACKET_DRAFT.v1"
DEFAULT_SUBDIR = Path("Reports") / "self_build_drafts"

# Always-attached forbidden paths (mirrors the governed packet safety boundary).
FORBIDDEN_PATHS = [
    "AGENTS.md", "RISK_POLICY.md", "README.md", "WHITEPAPER.md", "ARCHITECTURE.md",
    ".github/", ".githooks/", ".git/",
    "automation/orchestration/approval_inbox/", "automation/orchestration/work_packets/",
    "automation/orchestration/coordination_spine/", "automation/orchestration/autonomy_loop/",
    "automation/orchestration/packet_runner/", "automation/orchestration/scheduler/",
    "secrets/", "credentials/", ".env", ".env.*",
    "broker/", "OANDA/", "live_trading/", "webhooks/",
]

STRICT_PACKET_FIELDS = [
    "packet_id",
    "objective",
    "allowed_paths",
    "forbidden_paths",
    "approval_authority",
    "validator_chain",
    "stop_point",
    "mission",
    "preflight",
    "final_report_format",
]

PROTECTED_OUTPUT_MARKERS = [
    "automation/orchestration/work_packets/",
    "automation/orchestration/workers/inbox/",
    "automation/orchestration/workers/aios_worker_inbox.json",
    "automation/orchestration/command_queue/",
    "automation/orchestration/approval_inbox/",
    "telemetry/runtime/",
    "services/runtime/",
    "services/dispatcher/",
    "services/orchestrator/",
    "services/policy/",
    "apps/trading_lab/",
    "aios/modules/trader/",
    "broker/",
    "live_trading/",
    "secrets/",
    "credentials/",
    ".env",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slug(text: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", text or "").strip("-").upper()
    return s[:60] or "GAP"


def _clean_paths(paths: Any) -> list[str]:
    out: list[str] = []
    for p in paths or []:
        s = str(p).strip().strip("`").replace("\\", "/").strip()
        if s and s not in out:
            out.append(s)
    return out


def _is_valid_candidate(goal: Any) -> bool:
    return (
        isinstance(goal, dict)
        and isinstance(goal.get("objective"), str)
        and bool(goal.get("objective"))
    )


def _missing_strict_packet_fields(request: dict) -> list[str]:
    missing: list[str] = []
    for field in STRICT_PACKET_FIELDS:
        value = request.get(field)
        if value is None or value == "" or value == []:
            missing.append(field)
    return missing


def draft_codex_packet_from_request(request: Any, *, now: Optional[str] = None) -> dict[str, object]:
    """Strict packet-draft entry point that fails closed on missing governance fields."""
    if not isinstance(request, dict):
        return {
            "schema": SCHEMA,
            "status": "BLOCKED_MALFORMED_REQUEST",
            "missing": list(STRICT_PACKET_FIELDS),
            "draft_text": "",
            "observe_only": True,
        }

    missing = _missing_strict_packet_fields(request)
    if missing:
        return {
            "schema": SCHEMA,
            "status": "BLOCKED_MISSING_REQUIRED_INPUTS",
            "missing": missing,
            "draft_text": "",
            "observe_only": True,
        }

    goal = {
        "objective": request["objective"],
        "target_area": request.get("target_area") or "Reports/self_build_drafts",
        "allowed_paths": request["allowed_paths"],
        "worker_preference": request.get("worker_identity") or "Codex East",
        "protected_action_expected": bool(request.get("protected_action_expected", False)),
        "source_gap": request.get("mission") or request["objective"],
    }
    return build_packet_draft(
        goal,
        allowed_paths=list(request["allowed_paths"]),
        supervisor=str(request.get("supervisor_identity") or "ChatGPT Personal"),
        worker_identity=str(request.get("worker_identity") or "Codex East"),
        now=now,
    )


def build_packet_draft(
    goal: dict,
    *,
    allowed_paths: Optional[list[str]] = None,
    supervisor: str = "Codex West",
    worker_identity: Optional[str] = None,
    now: Optional[str] = None,
) -> dict[str, object]:
    """Render one goal candidate into a governed packet DRAFT. Raises ValueError if malformed."""
    if not _is_valid_candidate(goal):
        raise ValueError("malformed goal candidate: requires non-empty 'objective'")
    now = now or _now()

    objective = str(goal["objective"]).strip()
    target_area = str(goal.get("target_area") or _slug(objective).lower())
    urgency = str(goal.get("urgency") or "MEDIUM")
    protected = bool(goal.get("protected_action_expected"))
    worker = worker_identity or str(goal.get("worker_preference") or "Codex East")
    packet_id = "AIOS-DRAFT-" + _slug(objective)

    # Path scoping honesty: explicit paths -> ready-shaped; otherwise derive + flag.
    explicit = _clean_paths(allowed_paths if allowed_paths is not None else goal.get("allowed_paths"))
    if explicit:
        allowed = explicit
        path_status = "SCOPED"
    else:
        # conservative, concrete derived path (never an unresolved placeholder token)
        derived = target_area.rstrip("/") + "/"
        allowed = [derived, "tests/orchestration/", "Reports/self_build_drafts/"]
        path_status = "NEEDS_PATH_CONFIRMATION"

    missing: list[str] = []
    if path_status == "NEEDS_PATH_CONFIRMATION":
        missing.append("operator-confirmed ALLOWED PATHS (auto-derived from target_area)")

    status = "DRAFT_READY_FOR_COMPLETENESS_REVIEW" if not missing else "DRAFT_NEEDS_PATH_CONFIRMATION"

    draft_text = _render(
        packet_id=packet_id, objective=objective, urgency=urgency, protected=protected,
        supervisor=supervisor, worker=worker, allowed=allowed, now=now,
        source_gap=str(goal.get("source_gap") or objective), path_status=path_status,
    )

    return {
        "schema": SCHEMA,
        "generated_at": now,
        "packet_id": packet_id,
        "status": status,
        "path_status": path_status,
        "protected_action_expected": protected,
        "missing": missing,
        "allowed_paths": allowed,
        "forbidden_paths": list(FORBIDDEN_PATHS),
        "worker_identity": worker,
        "draft_text": draft_text,
        "observe_only": True,
        "safe_next_action": (
            "Run the packet completeness review on this draft. It is a DRAFT only; it "
            "is not an approval and authorizes no APPLY, commit, push, or merge."
        ),
    }


def _render(*, packet_id, objective, urgency, protected, supervisor, worker, allowed, now, source_gap, path_status) -> str:
    allowed_block = "\n".join(f"- `{p}`" for p in allowed)
    forbidden_block = "\n".join(f"- `{p}`" for p in FORBIDDEN_PATHS)
    protected_line = (
        "PROTECTED ACTION EXPECTED: yes. This gap touches a protected surface "
        "(scheduler/SOS/approval/merge/push/secret/broker/live). It must not be auto-run."
        if protected else
        "PROTECTED ACTION EXPECTED: not detected by keyword scan. Treat all protected "
        "gates as still in force regardless."
    )
    return f"""CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED
Before processing this task, read and follow:
1. AGENTS.md
2. RISK_POLICY.md
3. README.md
4. operator instruction
If unavailable, stop and report missing AI_OS context.

IDENTITY MARKER: AI_OS_PACKET_DRAFT_MACHINE_GENERATED

SUPERVISOR IDENTITY: {supervisor}

PACKET ID: {packet_id}

MODE: DRY_RUN-FIRST

ZONE: self-build drafting lane

WORKER IDENTITY: {worker}

LANE: AI_OS_SELFBUILD_DRAFT

WORKTREE: C:\\Dev\\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

PATH SCOPING STATUS: {path_status}

SOURCE GAP:
{source_gap}

OBJECTIVE (definition of done):
{objective}. Additive-only, DRY_RUN-first, no mutation, with a STOP before APPLY.

MISSION:
Implement, DRY_RUN-first and only after explicit APPLY approval, the objective
above. Phase 1 produces design plus a preview diff plan, then STOPS for Human
Owner approval. {protected_line}

ALLOWED PATHS:
{allowed_block}

FORBIDDEN PATHS:
{forbidden_block}

HARD LIMITS (a violation fails this packet):
- Additive-only inside the allowed write boundary. Read-only over the rest of the repo.
- DRY_RUN default. APPLY is a separate explicit approval naming this packet ID.
- No live trading, broker, secrets, scheduler registration, or webhook behavior.
- Do not weaken validators, approvals, locks, or Human Owner authority.

APPROVAL AUTHORITY:
Anthony Meza the Human Owner must approve before APPLY. A validator PASS is evidence
only. This draft does not state that the Human Owner approves commit, push, or merge.
Each of commit, push, and merge requires a separate explicit Human Owner approval
naming this packet ID. Approval does not transfer between actions.

PREFLIGHT (read-only, before any APPLY work):
- pwd
- git status --short --branch
- git branch --show-current
- git remote -v
- Read AGENTS.md
- Read RISK_POLICY.md
- Confirm the working tree is clear of operator local self-build work

VALIDATOR CHAIN:
- python automation/validators/aios_governance_validator.py --input <this packet>
- python -m py_compile <new files> in Phase 2
- python -m pytest tests/orchestration in Phase 2
- git diff --check

STOP POINT:
Stop after producing the Phase 1 design and preview diff plan. Stop immediately if
preflight state does not match this packet, if a forbidden path would be touched, if
validation fails, or if APPLY approval is not explicit.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
VALIDATION:
COLLISION CHECK:
REMAINING DIRTY FILES:
SAFE NEXT ACTION:
STATUS: COMPLETE, NO COMMIT, NO PUSH

GENERATED: {now} (machine draft; observe-only; not an approval)
"""


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp_name, path)
    except Exception:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise


def write_draft(
    result: dict,
    *,
    output_dir: Optional[Path] = None,
    repo_root: Optional[Path] = None,
    overwrite: bool = False,
) -> dict[str, object]:
    """Atomically write the draft .md. Never writes into work_packets/. Never overwrites by default."""
    if output_dir is not None:
        target_dir = Path(output_dir)
    else:
        base = Path(repo_root) if repo_root else Path.cwd()
        target_dir = base / DEFAULT_SUBDIR

    normalized_target = (str(target_dir).replace("\\", "/").rstrip("/") + "/").lower()

    # Hard guard: refuse to write into protected state, runtime, credential, broker, or trading lanes.
    if any(marker in normalized_target for marker in PROTECTED_OUTPUT_MARKERS):
        return {"written": False, "status": "BLOCKED_FORBIDDEN_DIR", "md_path": None}

    md_path = target_dir / f"{result['packet_id']}.md"
    if md_path.exists() and not overwrite:
        return {"written": False, "status": "SKIPPED_EXISTS", "md_path": str(md_path)}

    _atomic_write_text(md_path, str(result["draft_text"]))
    return {"written": True, "status": "WRITTEN", "md_path": str(md_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a goal candidate into a governed packet DRAFT (observe-only).")
    parser.add_argument("--candidate", required=True, help="path to a goal-candidate JSON (single goal or classifier output)")
    parser.add_argument("--index", type=int, default=0, help="if classifier output, which goal index to draft")
    parser.add_argument("--allowed-path", action="append", default=None, help="explicit allowed path (repeatable)")
    parser.add_argument("--out", default=None, help="optional output dir for the .md draft")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    data = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
    goal = data["goals"][args.index] if isinstance(data, dict) and "goals" in data else data
    result = build_packet_draft(goal, allowed_paths=args.allowed_path)
    if args.out:
        result["_write_result"] = write_draft(result, output_dir=Path(args.out), overwrite=args.overwrite)
    print(json.dumps({k: v for k, v in result.items() if k != "draft_text"}, indent=2, sort_keys=True))
    print("\n----- DRAFT -----\n")
    print(result["draft_text"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
