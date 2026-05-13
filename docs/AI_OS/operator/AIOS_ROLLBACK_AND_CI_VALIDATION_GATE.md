# AI_OS Rollback And CI Validation Gate

## 1. Purpose

Phase 24 defines the manual rollback and local CI-style validation gate for AI_OS operator orchestration.

The goal is to protect the main integration lane before worker merges, approved package commits, and pushes. This document is a foundation plan only. It creates no automation that runs commands.

Rollback is not a panic button. It is a controlled return to the last known good state.

## 2. Scope

This gate applies to:

- worker branch review
- worker report review
- approved APPLY package review
- exact-file commit package review
- push readiness review
- recovery planning after failed validation

This gate does not approve a merge, commit, push, or rollback by itself.

## 3. Main Repo Integration Lane

The main repo is the controlled integration lane.

Rules:

- No worker branch is merged until evidence is reviewed.
- No commit is approved until validation evidence is clean.
- No push is allowed until the repo validates clean.
- Main should not receive direct worker edits once isolated worktree workflow is active.
- Worker reports are evidence, not approval.
- The human operator remains the approval authority.

## 4. Required Validation Before Commit

Before any commit package is considered, run:

```powershell
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1
powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsParallelWorkerReports.ps1
git diff --check
git status --short --branch
```

Commit review is blocked if any validator fails or if unexpected files appear.

## 5. Required Validation Before Push

Before push, repeat or verify the same gate:

```powershell
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1
powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsParallelWorkerReports.ps1
git diff --check
git status --short --branch
```

Push remains manual. Push is not allowed until validation passes and the operator approves the push.

## 6. Rollback Evidence

Rollback review must record:

- `last_known_good_commit`
- `files_changed`
- `worker_branch`
- `validation_result`
- `rollback_reason`
- `operator_decision`
- `timestamp`
- `recovery_action`

If any field is missing, the rollback review is incomplete.

## 7. Blocked Conditions

The gate blocks merge, commit, or push when any of these are present:

- validator failure
- dirty main branch before merge
- unapproved protected root edits
- files_deleted without approval
- worker file conflicts
- missing worker report
- invalid worker report JSON
- overlapping planned files
- missing validation commands
- secret/API key evidence
- broker/OANDA/live execution evidence
- dashboard edits from non-dashboard lane
- trading edits from non-Trading Lab lane

Blocked means stop, report the condition, and ask the operator for a recovery decision.

## 8. Manual Rollback Procedure

Manual rollback procedure:

1. Identify `last_known_good_commit`.
2. List `files_changed`.
3. Identify the worker branch or package that introduced the issue.
4. Record failed validation output.
5. Record `rollback_reason`.
6. Ask the operator for the recovery action.
7. Execute only the approved recovery action.
8. Re-run validation commands.
9. Record the result.

No reset, clean, checkout, branch deletion, merge revert, or force push is automatic.

## 9. Local CI-Style Gate

The local CI-style gate is a repeatable manual validation sequence.

It checks:

- Work Intelligence scanner validity
- worker report and file ownership validity
- whitespace/diff cleanliness
- current branch and worktree state

This gate is local-only and evidence-based.

## 10. What This Does Not Automate

This document does not automate:

- merge
- rollback
- commit
- push
- git staging
- worker launch
- dashboard update
- broker/OANDA/API/live execution behavior
- protected root file changes

Rollback is manual for now.
Merge is manual for now.
Commit is manual for now.
Push is manual for now.

## 11. Operator Checklist

- Confirm branch and repo path.
- Confirm worker report exists and parses.
- Confirm no overlapping planned files.
- Confirm no unapproved protected root edits.
- Confirm no file deletion without approval.
- Confirm no unexpected broker/OANDA/live execution evidence.
- Run required validation commands.
- Review output before commit.
- Approve exact-file staging only if clean.
- Approve push only after commit and final validation.

## 12. Validation Commands

Run from the active repo root:

```powershell
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1
powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsParallelWorkerReports.ps1
git diff --check
git status --short --branch
```
