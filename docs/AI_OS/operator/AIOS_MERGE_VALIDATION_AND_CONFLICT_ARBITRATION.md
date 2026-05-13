# AI_OS Merge Validation And Conflict Arbitration

## Purpose

This document defines the manual validation and arbitration rules that must happen before any worker branch is merged into the controlled integration lane.

Phase 23 does not create merge automation. It documents the gate.

## Merge Validation Gate

Before any worker branch merge is considered, the operator must verify:

- main branch is clean
- worker report is present
- `files_planned` has been reviewed
- no overlapping planned files exist
- validation commands are listed
- protected root file edits are absent unless explicitly approved
- `files_deleted` is empty unless explicitly approved
- worker branch matches the assigned lane
- worker worktree does not include unrelated edits
- Work Intelligence queue has no relevant `BLOCKED` conflict item

Any failed check stops the merge review.

## Required Evidence

Required evidence before merge review:

- worker ID
- worker lane
- worker branch
- worktree path
- base branch
- report path
- planned files
- validation commands
- validation results
- conflict status

Missing evidence means status `REQUEST_NEW_DRY_RUN` or `BLOCKED`, depending on risk.

## Conflict Arbitration

Conflict arbitration is manual.

The operator reviews:

- planned file overlaps
- lane ownership
- protected root file references
- delete requests
- validator failures
- stale worker reports
- branch drift from main

The operator decides one of the allowed arbitration outcomes.

## Arbitration Outcomes

Allowed outcomes:

- `APPROVE_ONE_WORKER`: one worker keeps ownership; the other worker is paused or revised.
- `SPLIT_SCOPE`: work is divided into non-overlapping files or smaller tasks.
- `DEFER_WORKER`: one worker waits for the current owner to finish.
- `REQUEST_NEW_DRY_RUN`: worker must re-plan with updated scope.
- `BLOCKED`: merge cannot proceed until the conflict is resolved.

No outcome is a commit or push approval.

## Blocked Conditions

Merge review is blocked when:

- main branch is dirty
- worker report is missing
- planned files overlap
- validation commands are missing
- protected root files are planned without approval
- `files_deleted` is not empty without approval
- worker edits outside allowed paths
- broker, OANDA, API key, live execution, or real order logic appears unexpectedly

## Manual Merge Boundary

Phase 23 allows documentation only.

- No automated merge.
- No automated rollback.
- No scripts.
- No dashboard edits.
- No commit.
- No push.

Automation may validate evidence in later phases, but the operator remains the merge authority.

## Validation

Run from the main repo:

```powershell
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1
powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsParallelWorkerReports.ps1
git diff --check
git status --short --branch
```
