# AI_OS Worker Governance

## Purpose

Worker governance keeps multi-worker AI_OS work visible before APPLY, commit, push, or merge.

This layer is read-only by default. It reports worktree lanes, branch ownership, file-scope overlap, and merge readiness for MAIN CONTROL review.

## Safety Boundaries

- No live trading.
- No broker connection.
- No API keys or secrets.
- No runtime execution edits.
- No dashboard UI edits.
- No policy engine edits.
- No telemetry internals edits.
- No commits, pushes, or merges from these governance checks.

## Governance Checks

Run from the active AI_OS repo worktree.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\workers\Get-AiOsWorkerLanes.ps1
```

Shows registered lanes, git worktrees, unregistered worktrees, dirty worktrees, and MAIN CONTROL next action.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\workers\Test-AiOsWorkerIsolation.ps1 -ProposedPaths "docs/AI_OS/WORKER_GOVERNANCE.md"
```

Checks proposed paths and current dirty files against protected paths and active lock registry evidence.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\workers\Get-AiOsMergeReadiness.ps1
```

Reports whether the current branch is ready for PR or merge review. It does not create, push, or merge anything.

## MAIN CONTROL Rule

MAIN CONTROL owns final approval for:

- APPLY permission.
- Selective staging.
- Commit.
- Push.
- PR creation.
- Merge.

Worker lanes may inspect and report. Worker lanes must not assume ownership of files that overlap another lane, active lock, protected root file, dashboard asset, secret path, broker path, or live trading path.

## Stale Lane Review

A stale lane is any worker branch or worktree that lacks recent operator evidence, has unmerged work, has dirty files, or is missing from the lane registry.

Stale lane review should answer:

- Does the worktree still exist?
- Does the branch still exist?
- Is the worktree clean?
- Is the lane represented in the lane registry?
- Does it overlap another active worker's file scope?
- Is it safe to close, merge, or leave parked?

Closing, deleting, pruning, or renaming a stale lane requires explicit operator approval.

## Merge Readiness

Merge readiness requires:

- Current branch is not `main`.
- Worktree is clean.
- `git diff --check` passes.
- Protected files are not included unless explicitly approved.
- File-scope isolation has no blockers.
- Relevant validators have passed.
- CI status is reviewed before merge.

The governance scripts report readiness only. They do not replace human approval.

## Next Safe Action

Run the lane report first, then isolation check for proposed paths, then merge readiness only after APPLY work is complete and validated.
