# AI_OS File Ownership And Collision Prevention

## Purpose

This document defines file ownership rules for supervised Codex worker lanes. The goal is to prevent multiple workers from touching the same file during one APPLY cycle.

## Ownership Principle

Each file must have one owner per APPLY cycle.

Ownership is declared through worker report evidence before APPLY. A worker does not own a file until its `files_planned` entry is reviewed by the integration lane.

## Lane Ownership Rules

Default ownership rules:

- `Work Intelligence`: `automation/work_intelligence/`, `docs/AI_OS/work_intelligence/`, `Reports/work_intelligence/`
- `Operator Orchestration`: `automation/operator/`, `docs/AI_OS/operator/`, `Reports/operator/`
- `Dashboard UI`: `apps/dashboard/`
- `Trading Lab`: `docs/AI_OS/trading_laboratory/`, `automation/trading_lab/`
- `Validators`: validator scripts and validation documentation assigned by the operator
- `Reports`: `Reports/checkpoints/`, `Reports/daily/`, report-only documentation
- `Mock Data`: `apps/dashboard/mock-data/`

If ownership cannot be determined from path evidence, status is `OWNER_REQUIRED`.

## Planned File Declaration

Workers must declare planned files before APPLY using `files_planned` in their worker report.

Worker reports must also include:

- worker identity
- lane
- mode
- files deleted
- validation commands
- summary

An empty or missing `files_planned` list is not proof that a worker owns no files; it means ownership evidence is incomplete and must be reviewed.

## Conflict States

Allowed ownership states:

- `REVIEW`: Evidence exists but operator review is still needed.
- `BLOCKED`: A collision, protected file, delete request, or lane mismatch prevents progression.
- `OWNER_REQUIRED`: The correct owner lane cannot be determined.
- `SAFE_TO_PROCEED`: Evidence supports one owner and no collision for the file.

`SAFE_TO_PROCEED` is not APPLY approval. It only means the ownership evidence is clean.

## Collision Prevention Rules

- One owner per file per APPLY cycle.
- Overlapping planned files become `BLOCKED`.
- Protected root files require explicit operator approval.
- Dashboard files require `Dashboard UI` lane ownership.
- Trading files require `Trading Lab` lane ownership.
- Validator files require `Validators` lane ownership unless explicitly assigned by the operator.
- Worker report files are evidence only and must not be edited by conflict resolution logic.

## Blocked Examples

Blocked examples:

- Worker 1 and Worker 2 both plan `automation/work_intelligence/Invoke-AiOsWorkIntelligenceScan.ps1`.
- A non-dashboard lane plans `apps/dashboard/AIOS_STATIC_PREVIEW.html`.
- A worker plans `README.md` without explicit protected-file approval.
- A worker report includes files in `files_deleted`.

## Operator Resolution

The operator resolves ownership conflicts manually.

Resolution options:

- assign the file to one worker
- split the task into non-overlapping files
- defer one worker
- request a new DRY_RUN
- mark the work blocked until scope is clarified

No automated process may auto-resolve conflicts.

## Safety

This document creates no scripts, launches no workers, edits no dashboard files, performs no APPLY work, commits nothing, and pushes nothing.

## Validation

Run from the main repo:

```powershell
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1
powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsParallelWorkerReports.ps1
git diff --check
git status --short --branch
```
