# Phase 5B Canonical Doc Compare

Status: compare-only audit
Branch: `v2/aios`
Scope: selected `docs/AI_OS` CLEAN-era sources compared against current V2 canonical docs.

This audit does not move, delete, rename, merge, or edit source/canonical documents. It identifies whether useful CLEAN-era content still needs to be pulled into active V2 authority later.

## Executive Summary

The five canonical V2 files exist and already cover the core authority from their CLEAN-era source files. The main active conflict is structural: several source files still frame `docs/AI_OS/` as an active or canonical planning root, while V2 canonical docs place active authority under `docs/governance/` and `docs/workflows/`.

Most pairs need no full merge. The only selective merge candidates are granular ownership/approval details from the CLEAN-era ownership map and explicit worker lane/validator details from the worker branch/lane rules source.

## Compare Matrix

| Pair | Source exists | Canonical exists | Recommendation | Risk |
|---|---:|---:|---|---|
| File placement rules | yes | yes | canonical already stronger | high |
| Repo folder ownership map | yes | yes | merge specific section later | high |
| APPLY routing chain | yes | yes | canonical already stronger | low |
| Safe session resume | yes | yes | no merge needed | low |
| Worker branch and lane rules | yes | yes | merge specific section later | medium |

## Pair 1: File Placement Rules

| Field | Detail |
|---|---|
| Source | `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md` |
| Canonical | `docs/governance/FILE_PLACEMENT_RULES.md` |
| Source exists | yes |
| Canonical exists | yes |
| Recommendation | canonical already stronger |
| Risk level | high |

### Overlap Summary

Both files define where project material belongs: documentation, scripts, reports, dashboard code, backend code, broker/OANDA planning, telemetry planning, and blocked execution paths.

### Canonical Already Covers Well

- `docs/` as the V2 active documentation home.
- `automation/`, `apps/dashboard/`, `services/`, and `agent/` implementation ownership.
- Broker/OANDA/API/webhook/live trading blocks.
- Telemetry as docs-only until approved.
- Fail-closed handling for unknown placement.
- Blocked-action matrix for sensitive execution paths.

### Useful Source Content Missing From Canonical

- Some legacy topic examples are more explicit in the source, including legal, compliance, monetization, mobile, and broker adapter planning buckets.
- Source has stronger prompt-level wording around rejecting misplaced prompts.

### Conflicting Guidance

- Source treats `docs/AI_OS/` as the primary documentation destination.
- Canonical treats `docs/` as the active V2 documentation root and `docs/AI_OS/` as legacy/CLEAN-era material pending classification.

### Stale/Legacy Guidance In Source

- `docs/AI_OS/` as active authority.
- CLEAN-era placement language that predates V2 canonical governance.

### Decision

No broad merge needed. Canonical is the active authority. If desired, later extract only missing topic examples into the canonical file after confirming they still match V2 ownership.

## Pair 2: Repo Folder Ownership Map

| Field | Detail |
|---|---|
| Source | `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md` |
| Canonical | `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md` |
| Source exists | yes |
| Canonical exists | yes |
| Recommendation | merge specific section later |
| Risk level | high |

### Overlap Summary

Both files define folder ownership and boundaries for documentation, automation, reports, dashboard, backend services, agent runtime, telemetry, Trading Lab, broker planning, legal/compliance/monetization, and cleanup governance.

### Canonical Already Covers Well

- V2 ownership split between `docs/`, `automation/`, `Reports/`, `apps/dashboard/`, `services/`, `agent/`, and governance/security/spec roots.
- `docs/AI_OS/` as legacy active planning source only until repointed.
- Archive-before-delete cleanup doctrine.
- Topic ownership for telemetry, Trading Lab, broker planning, and dashboard specs.

### Useful Source Content Missing From Canonical

- The source has a more granular ownership table with related folders, current status, recommended correction, approval-needed state, and risk.
- Source explicitly separates automation, report generation, future backend, telemetry planning, telemetry scripts, broker adapters, and audit reports in one operational table.

### Conflicting Guidance

- Source presents `docs/AI_OS/` as the canonical planning root.
- Canonical presents `docs/` as active V2 authority and `docs/AI_OS/` as legacy pending repointing.

### Stale/Legacy Guidance In Source

- CLEAN-era folder authority assumptions.
- Some future-path labels appear older than the current V2 spine.

### Decision

Merge specific section later. Do not replace the canonical file with the source. Extract only useful table columns or ownership notes into the V2 map after validating against current runtime and governance boundaries.

## Pair 3: APPLY Routing Chain

| Field | Detail |
|---|---|
| Source | `docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md` |
| Canonical | `docs/workflows/APPLY_ROUTING_CHAIN.md` |
| Source exists | yes |
| Canonical exists | yes |
| Recommendation | canonical already stronger |
| Risk level | low |

### Overlap Summary

Both files define the DRY_RUN to APPLY chain, required evidence, blocked conditions, and a non-automation statement.

### Canonical Already Covers Well

- DRY_RUN, validation, approval request, APPLY candidate, exact-file evidence, and review package chain.
- Required evidence fields.
- Protected-file and live trading blockers.
- Explicit no stage/commit/push/merge/run-broker statement.

### Useful Source Content Missing From Canonical

- Source has fuller state definitions for each routing step.
- Source uses the phrase `merge-ready package`; canonical uses the safer `review package`.

### Conflicting Guidance

- No material conflict.
- The source term `merge-ready package` may imply stronger readiness than V2 intends.

### Stale/Legacy Guidance In Source

- CLEAN-era wording around merge readiness.

### Decision

No broad merge needed. Canonical is cleaner and safer. If a later workflow update needs definitions, selectively add short state definitions without restoring `merge-ready package` wording.

## Pair 4: Safe Session Resume

| Field | Detail |
|---|---|
| Source | `docs/AI_OS/operator_workflows/AIOS_SAFE_SESSION_RESUME_STANDARD.md` |
| Canonical | `docs/workflows/SAFE_SESSION_RESUME.md` |
| Source exists | yes |
| Canonical exists | yes |
| Recommendation | no merge needed |
| Risk level | low |

### Overlap Summary

Both files define review-only resume behavior after pause, crash, restart, or new chat. They cover resume evidence, allowed restoration, blocked restoration, stale state, invalid data, and next safe action.

### Canonical Already Covers Well

- Review-only resume behavior.
- Pending approvals and next safe action in resume evidence.
- Blocks active execution, autonomous APPLY, automatic commit/push, merge execution, background worker state, broker execution, OANDA, API keys, and live trading.
- `STALE`, `UNKNOWN`, and `INVALID DATA` handling.

### Useful Source Content Missing From Canonical

- Source explicitly lists `unfinished APPLY packages`.
- Source has a standalone `Next Safe Action` section.

### Conflicting Guidance

- No material conflict.

### Stale/Legacy Guidance In Source

- None material. Source is mostly superseded by canonical wording.

### Decision

No merge needed. Canonical already captures the operational behavior. `unfinished APPLY packages` can remain implicit under pending approvals/review state unless the user wants stricter resume packet fields later.

## Pair 5: Worker Branch And Lane Rules

| Field | Detail |
|---|---|
| Source | `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md` |
| Canonical | `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` |
| Source exists | yes |
| Canonical exists | yes |
| Recommendation | merge specific section later |
| Risk level | medium |

### Overlap Summary

Both files define worker branch naming, lane metadata, allowed/blocked path behavior, collision handling, and safety limits around branch/worktree/commit/push/merge activity.

### Canonical Already Covers Well

- Branch naming pattern.
- Required metadata before APPLY review.
- Worker path ownership.
- Secret, credential, broker, webhook, live execution, and trading execution blocks.
- Collision handling and stale worker review.
- Clear statement that it does not create branches, worktrees, commits, pushes, or merges.

### Useful Source Content Missing From Canonical

- Explicit allowed worker lane list:
  - Work Intelligence
  - Operator Orchestration
  - Dashboard UI
  - Trading Lab
  - Validators
  - Reports
  - Mock Data
- Validation commands:
  - `powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1`
  - `powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsParallelWorkerReports.ps1`
  - `git diff --check`
  - `git status --short --branch`
- Source examples of branch names.

### Conflicting Guidance

- No direct conflict, but explicit allowed lanes could become stale if worker lanes are now defined elsewhere.

### Stale/Legacy Guidance In Source

- Validator paths may be stale and require existence/runtime validation before promotion.
- Allowed lane list may be incomplete for current V2.

### Decision

Merge specific section later only after validation. Candidate merge content is the allowed lane list, branch examples, and validator command references if the scripts still exist and remain the intended validation chain.

## Merge Candidates Found

| Candidate | Source | Proposed target | Reason | User decision |
|---|---|---|---|---|
| Granular ownership table fields | `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md` | `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md` | Source has operational columns not fully represented in canonical. | Decide whether canonical should stay concise or include detailed table columns. |
| Worker allowed lane list | `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md` | `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` | Canonical does not enumerate approved worker lanes. | Validate lane list against current worker system before merge. |
| Worker validator commands | `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md` | `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` | Source names concrete validators. | Validate scripts exist and remain authoritative before merge. |
| APPLY state definitions | `docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md` | `docs/workflows/APPLY_ROUTING_CHAIN.md` | Source has fuller step definitions. | Optional; avoid restoring `merge-ready package` wording. |

## Conflicts Found

| Conflict | Affected pairs | Recommendation |
|---|---|---|
| `docs/AI_OS/` as active/canonical planning root vs V2 `docs/` active authority | File placement rules, repo folder ownership map | Keep canonical V2 authority. Treat source as CLEAN-era material. |
| `merge-ready package` wording vs canonical `review package` wording | APPLY routing chain | Keep canonical `review package` wording. |
| Explicit worker lane list may be stale | Worker branch and lane rules | Validate before promotion. |

## Docs Needing User Decision

| Document | Decision needed |
|---|---|
| `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md` | Should the canonical file absorb the source's detailed ownership table fields, or stay concise? |
| `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` | Should V2 define an explicit allowed worker lane list here, or in a separate worker registry/governance file? |
| `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` | Should the source validator commands be promoted after script existence and authority validation? |

## Recommended Next Safe Step

Run a focused validation pass for only the merge candidates:

1. Confirm the worker validator scripts exist.
2. Confirm whether worker lane names are currently referenced by automation, worker reports, or orchestration.
3. Decide whether ownership-map detail belongs in `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md` or a separate audit/appendix.
4. If approved, prepare a narrow Phase 5C merge plan with exact sections only.

## Explicitly Untouched

- Source CLEAN-era docs were not edited.
- Canonical V2 docs were not edited.
- Runtime, orchestration, dashboard, trading, telemetry, archive, and launcher paths were not touched.
- No files were moved, deleted, renamed, committed, pushed, or staged.
