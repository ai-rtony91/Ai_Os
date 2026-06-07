> Deprecated duplicate / reference-only HRQ-001 document.
>
> Current canonical workflow authority lives in `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md`.
> This file `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md` is retained only as historical/source evidence until references are reviewed.
> Do not treat this file as active workflow authority.
> Do not delete or archive this file without a separate approved retirement APPLY packet.

> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS authority. Current operating authority is `AGENTS.md`; current front-door authority is `README.md`; current source-of-truth mapping lives in `docs/governance/source-of-truth-map.md`; current active-system mapping lives in `docs/audits/active-system-map.md`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved canonical document explicitly promotes them.

# AI_OS Worker Branch And Lane Rules

## Purpose

This document defines branch naming and lane metadata rules for supervised Codex workers. It supports isolated worktree operation while keeping the main repo as the controlled integration lane.

## Branch Naming

Recommended branch format:

```text
worker/<lane>/<phase>-<short-task>
```

Examples:

```text
worker/work-intelligence/phase-21-branch-rules
worker/operator-orchestration/phase-22-file-ownership
worker/dashboard-ui/phase-15-centerpiece-review
```

Branch names should be lowercase, short, and descriptive. Use hyphens instead of spaces. Do not include secrets, API keys, ticket tokens, or private data in branch names.

## Required Worker Metadata

Each worker lane should declare:

- `worker_id`
- `worker_lane`
- `branch_name`
- `base_branch`
- `worktree_path`
- `allowed_paths`
- `blocked_paths`
- `report_path`
- `validation_commands`

This metadata must be available before a worker moves from DRY_RUN planning to scoped APPLY review.

## Allowed Worker Lanes

Allowed worker lanes are:

- `Work Intelligence`
- `Operator Orchestration`
- `Dashboard UI`
- `Trading Lab`
- `Validators`
- `Reports`
- `Mock Data`

Any lane outside this list is `UNKNOWN` until the operator approves and documents it.

## Path Rules

Workers must stay inside their declared `allowed_paths`.

Workers must not edit:

- protected root files
- files outside their allowed lane
- secrets, credentials, API keys, broker tokens, private keys, or recovery keys
- dashboard files unless assigned to `Dashboard UI`
- trading execution logic
- broker, OANDA, live execution, or real order paths

Workers must declare planned files before APPLY.

## Report Rules

Each worker report must include planned files and validation commands. The integration lane checks those reports before any merge or APPLY review.

If two workers declare the same planned file, Work Intelligence marks the collision as a blocked conflict. The operator must resolve ownership before work continues.

## Safety

This document does not create branches, create worktrees, launch workers, merge code, rollback code, commit, or push. It defines rules only.

## Validation

Run from the main repo:

```powershell
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1
powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsParallelWorkerReports.ps1
git diff --check
git status --short --branch
```
