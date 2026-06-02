# AI_OS Worker Branch And Lane Rules

Status: canonical workflow
Source material: `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md`

`docs/AI_OS/**` is reference/source material only. Current workflow authority lives in `docs/workflows/` unless a specific rule is promoted through governance.

## Purpose

This document defines branch and lane metadata rules for supervised AI_OS worker activity. It supports isolation and collision prevention; it does not create branches, worktrees, commits, pushes, or merges.

## Branch Naming

Recommended branch pattern:

```text
worker/<lane>/<phase>-<short-task>
```

Branch names must be lowercase, short, descriptive, and free of secrets, tokens, account identifiers, or private data.

West branch naming must remain PR-lane compliant and packet-scoped. Recommended West branch pattern:

```text
west/<packet-id>-<short-topic>
```

Example:

```text
west/PKT-WEST-DOCS-001-architecture-map
```

Codex East governance APPLY branches may use packet-specific East branch names when executing approved governance hardening:

```text
east/<packet-id>-<short-topic>
```

## Required Lane Metadata

Before APPLY review, each lane should declare:

- worker ID.
- supervisor identity.
- zone.
- worker lane.
- branch name.
- base branch.
- worktree path.
- allowed paths.
- blocked paths.
- packet ID.
- lock ID when shared paths or APPLY work are involved.
- approval authority.
- report path.
- validation commands.
- stop point.

## Allowed Worker Lanes

Allowed worker lanes are:

- Work Intelligence
- Operator Orchestration
- Dashboard UI
- Trading Lab
- Validators
- Reports
- Mock Data
- Codex East
- Claude Code West
- Command Control
- Validator Lane
- Codex Worker 1
- Codex Worker 2
- Codex Worker 3
- Codex Worker 4
- Codex Worker 5
- Codex Worker 6

Any lane outside this list is `UNKNOWN` until the operator approves and documents it.

## Safe 8-Window Parallel Map

Main Control and Claude Reviewer do not create file ownership by themselves. Main Control owns command, approval, and protected-action decisions. Claude Reviewer is read-only unless a separate APPLY packet assigns exact files.

Six Codex worker windows may run in parallel only when each packet resolves to a unique `worker_id` in `automation/orchestration/workers/AIOS_WORKER_PROFILES.json` and declares non-overlapping allowed paths. Window titles and presentation markers from `automation/window_identity/AIOS_WORKER_REGISTRY.json` are display-only and do not grant file ownership.

Default non-overlap guidance:

| Worker | Default lane | Default boundary |
|---|---|---|
| `codex_worker_1` | worker registry / orchestration ownership | `automation/orchestration/workers/` plus assigned worker ownership governance docs |
| `codex_worker_2` | workflow docs | assigned `docs/workflows/` files |
| `codex_worker_3` | governance docs | assigned `docs/governance/` files |
| `codex_worker_4` | validators and schemas | assigned `automation/orchestration/validators/` and `schemas/` files |
| `codex_worker_5` | dashboard UI | assigned `apps/dashboard/` UI files only |
| `codex_worker_6` | audits and reports | assigned `docs/audits/` and reporting files only |

Trading Lab, runtime, scheduler, approval mutation, active packet-state mutation, commit, push, merge, reset, clean, delete, broker, OANDA, API-key, secret, and live trading authority are never implied by this map.

## Worker Identity Names

Packet-scoped worker identities must use the canonical identity spine:

- `EAST_OCC_##` for East worksite packet execution.
- `WEST_OCC_##` for West worksite packet execution or refinement.
- `VALIDATOR_##` for validator/check/evidence lanes.

Permanent supervisor identities are `Human Owner`, `Business GPT`, `Claude Chat`, `Codex East`, and `Claude Code West`.

## Claude Code West Lane Boundary

Claude Code West is a governed, limited, DRY_RUN-first inspection/refinement lane. It is not autonomous and does not own runtime, orchestration, governance, main-branch, broker, OANDA, API-key, live-order, or real-money execution authority.

Proposed West path classes must be packet-scoped and may include `docs/concepts/`, `docs/architecture/`, `docs/roadmap/`, `docs/specs/`, `docs/standards/` after classification, and tightly scoped `apps/dashboard/` UI work.

Shared or approval-required West paths include `docs/governance/`, `docs/workflows/`, `docs/security/`, `schemas/aios/orchestration/`, and `apps/dashboard/mock-data/`.

Forbidden West paths include `automation/orchestration/`, `automation/operator/`, `services/`, `telemetry/`, `scripts/`, root authority files except approved pointer changes, trading execution paths, broker/OANDA/API-key/live-order paths, and `aios/modules/trader/` until Human Owner decision.

West worktree doctrine remains proposed until an approved packet names the exact branch, worktree path, allowed paths, forbidden paths, validator chain, lock plan, approval authority, and stop point.

## Path Ownership

Workers must stay inside declared allowed paths and must not edit:

- protected root files.
- files outside their assigned lane.
- secrets, credentials, API keys, broker tokens, private keys, or recovery keys.
- dashboard files unless assigned to a dashboard lane.
- trading execution logic.
- broker, OANDA, webhook, live execution, or real order paths.

## Collision Handling

If two workers declare the same planned file, the conflict is blocked until the operator assigns ownership. Stale worker state must be reviewed before resuming.

East and West workers must not edit the same file tree at the same time. Cross-zone edits require explicit reassignment, matching allowed paths, lock review, validator review, and Human Owner approval when APPLY is involved.

No lock, packet, validator, or worker claim may be treated as authority when its identity fields are missing or placeholder-only.

## Validation

Worker branch and lane reviews may use:

```powershell
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1
powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsParallelWorkerReports.ps1
git diff --check
git status --short --branch
automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1
```

These commands validate evidence only. They do not approve APPLY, create branches, create worktrees, stage files, commit, push, merge, or change runtime state.
