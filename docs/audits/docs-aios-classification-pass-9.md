# docs/AI_OS Classification - Pass 9

Date: 2026-05-19
Branch: phase-82-copy-paste-reduction-runner
Mode: REPORT ONLY

## Purpose

Classify `docs/AI_OS` before any cleanup move/delete pass. No files were moved, deleted, renamed, or rewritten. This report is a decision aid for MAIN CONTROL.

## Inspection Summary

- Tracked files under `docs/AI_OS`: 770
- Top-level subfolders under `docs/AI_OS`: 70
- Root-level tracked files under `docs/AI_OS`: 19
- Markdown files: 684
- JSON files: 25
- `README_FOLDER_PURPOSE.txt` files: 61
- Files matching generated/planning patterns such as `_DRAFT`, `DRY_RUN`, `PHASE_`, `STAGE`, `CHECKPOINT`, `REPORT`, `SNAPSHOT`, `LEDGER`, `STATUS`, or `PLAN`: 531

## Top-Level Folder Counts

Largest tracked folders:

| Count | Folder |
| ---: | --- |
| 127 | `docs/AI_OS/dashboard` |
| 57 | `docs/AI_OS/dispatcher` |
| 49 | `docs/AI_OS/orchestration` |
| 24 | `docs/AI_OS/agent_runtime` |
| 23 | `docs/AI_OS/operator` |
| 23 | `docs/AI_OS/telemetry` |
| 23 | `docs/AI_OS/writers` |
| 22 | `docs/AI_OS/governance` |
| 21 | `docs/AI_OS/security` |
| 19 | `docs/AI_OS/bootstrap_engine` |
| 17 | `docs/AI_OS/autonomous` |
| 14 | `docs/AI_OS/audits` |
| 13 | `docs/AI_OS/roadmap` |
| 12 | `docs/AI_OS/change_control` |
| 12 | `docs/AI_OS/llm` |
| 11 | `docs/AI_OS/checkpoints` |
| 11 | `docs/AI_OS/productization` |
| 11 | `docs/AI_OS/signal_intelligence` |
| 10 | `docs/AI_OS/brokers` |
| 10 | `docs/AI_OS/multi_agent` |
| 10 | `docs/AI_OS/operations` |
| 10 | `docs/AI_OS/problem_resolution` |
| 10 | `docs/AI_OS/system_wizards` |

Largest second-level folders:

| Count | Folder |
| ---: | --- |
| 40 | `docs/AI_OS/dispatcher/runtime` |
| 10 | `docs/AI_OS/security/secure_access` |
| 8 | `docs/AI_OS/brokers/oanda` |
| 8 | `docs/AI_OS/security/phase_15_secure_access` |
| 5 | `docs/AI_OS/dashboard/sidebar` |

## Naming Pattern Findings

The dominant pattern is a generated planning swarm:

- many `_DRAFT.md` files,
- many `PHASE_*` and `STAGE*` files,
- many dry-run, plan, status, report, checkpoint, fixture, and schema drafts,
- many topic folders with only one to four files,
- many duplicate topic families across `operator`, `operator_workflows`, `operations`, `orchestration`, `dispatcher`, `runtime`, `automation`, and `autonomous`.

This suggests `docs/AI_OS` is still acting as a mixed active-docs, roadmap, implementation-plan, generated-report, and historical-memory area.

## KEEP ACTIVE Recommendations

Keep active, but eventually relocate or promote into canonical `docs/*` folders:

### Architecture

- `docs/AI_OS/architecture/SYSTEM_LEVEL_AI_WIZARDS.md`
- `docs/AI_OS/orchestration/AI_OS_ORCHESTRATION_MODEL.md`
- `docs/AI_OS/orchestration/AIOS_WORK_PACKETS.md`
- `docs/AI_OS/orchestration/AIOS_WORKTREE_LANES.md`
- `docs/AI_OS/orchestration/AIOS_WORKSPACE_BOOTSTRAP.md`
- `docs/AI_OS/dispatcher/runtime/RUNTIME_SOURCE_OF_TRUTH_MAP.md`
- `docs/AI_OS/dispatcher/runtime/RUNTIME_API_CONTRACT.md`
- `docs/AI_OS/dispatcher/runtime/RUNTIME_PACKET_AND_LOCK_MODEL.md`
- `docs/AI_OS/dispatcher/runtime/RUNTIME_WORKER_LIFECYCLE_MODEL.md`

Recommended destination later:

- `docs/architecture/`
- `docs/infrastructure/`

### Governance and Safety

- `docs/AI_OS/AGENTS.md`
- `docs/AI_OS/WORKER_GOVERNANCE.md`
- `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md`
- `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md`
- `docs/AI_OS/governance/AIOS_SYSTEM_WIDE_SAFETY_MATRIX_DRAFT.md`
- `docs/AI_OS/governance/AIOS_SECRET_HANDLING_MATRIX_DRAFT.md`
- `docs/AI_OS/governance/AIOS_BROKER_LIVE_TRADING_BLOCK_MATRIX_DRAFT.md`
- `docs/AI_OS/governance/AIOS_DESTRUCTIVE_ACTION_BLOCK_MATRIX_DRAFT.md`
- `docs/AI_OS/governance/AIOS_DOCUMENTATION_PROMOTION_CRITERIA_DRAFT.md`
- `docs/AI_OS/security/secure_access/*`

Recommended destination later:

- `docs/governance/`
- `docs/security/`

### Operator Workflow and Runbooks

- `docs/AI_OS/operator/AIOS_OPERATOR_PREFERENCES_AND_WORKFLOW_CANONICAL.md`
- `docs/AI_OS/operator/AIOS_MORNING_OPERATOR_STARTUP_FLOW.md`
- `docs/AI_OS/operator/AIOS_FILE_OWNERSHIP_AND_COLLISION_PREVENTION.md`
- `docs/AI_OS/operator/AIOS_MERGE_VALIDATION_AND_CONFLICT_ARBITRATION.md`
- `docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md`
- `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md`
- `docs/AI_OS/operator_workflows/AIOS_SAFE_SESSION_RESUME_STANDARD.md`
- `docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md`
- `docs/AI_OS/runbooks/REPO_HEALTH_VERIFICATION_CHAIN_DRAFT.md`

Recommended destination later:

- `docs/workflows/`
- `docs/runbooks/`

### Source Control / Validation

- `docs/AI_OS/source_control/AIOS_STAGE93_SOURCE_CONTROL_ROLLBACK_DRAFT.md`
- `docs/AI_OS/dispatcher/runtime/validators/*`
- `docs/AI_OS/dispatcher/runtime/commit_packages/EXACT_FILE_COMMIT_RULES.md`
- `docs/AI_OS/dispatcher/runtime/approval/APPROVAL_RUNTIME_MODEL.md`

Recommended destination later:

- `docs/workflows/`
- `docs/infrastructure/`

## ROADMAP / CONCEPT EXTRACTION Recommendations

These folders contain useful ideas, but should not remain as many active docs. Extract durable ideas into `docs/roadmap/` or `docs/concepts/`, then archive the source swarm.

| Folder/topic | Why extract |
| --- | --- |
| `docs/AI_OS/dashboard` | 127 files with many widget, mock, panel, layout, and wiring drafts. Extract one dashboard product spec, one data contract index, and one UI roadmap. |
| `docs/AI_OS/bootstrap_engine` | Useful concept for new-project inference and scaffold proposal, but mostly draft planning docs. Extract to concepts. |
| `docs/AI_OS/autonomous` | Useful autonomy boundaries and stop conditions. Extract one autonomous-safety concept and one future roadmap item. |
| `docs/AI_OS/agent_runtime` | Useful agent runtime model, but overlaps with dispatcher/orchestration. Extract into one runtime architecture note. |
| `docs/AI_OS/multi_agent`, `docs/AI_OS/agents`, `docs/AI_OS/llm` | Useful role separation and tool placement concepts. Extract to agent governance/concepts. |
| `docs/AI_OS/telemetry`, `docs/AI_OS/analytics`, `docs/AI_OS/metrics`, `docs/AI_OS/reporting`, `docs/AI_OS/work_intelligence` | Useful measurement ideas. Extract one telemetry/data model and one analytics roadmap. |
| `docs/AI_OS/product`, `docs/AI_OS/productization`, `docs/AI_OS/monetization`, `docs/AI_OS/mobile` | Product future ideas. Extract to roadmap/concepts, not active system docs. |
| `docs/AI_OS/backtesting`, `docs/AI_OS/trading`, `docs/AI_OS/trader`, `docs/AI_OS/brokers`, `docs/AI_OS/broker_adapters` | Useful Trading Lab ideas, but should be subordinate to paper-only Trading Lab docs and safety boundaries. Extract carefully; do not promote live broker content. |
| `docs/AI_OS/roadmap` and `docs/AI_OS/roadmaps` | Duplicate roadmap folders. Consolidate into one `docs/roadmap/` later. |

## ARCHIVE CANDIDATE Recommendations

Archive after extracting useful ideas:

- Most `docs/AI_OS/dashboard/*_DRAFT.md` and fixture drafts after creating a single dashboard source-of-truth spec.
- Most `docs/AI_OS/orchestration/PHASE_16_*` and `PHASE_15_*` implementation phase docs after current orchestration docs are promoted to `docs/architecture` or `docs/workflows`.
- `docs/AI_OS/checkpoints/*`
- `docs/AI_OS/progress/*`
- `docs/AI_OS/audits/AIOS_STAGE*`, if replaced by current `docs/audits/*` cleanup reports.
- `docs/AI_OS/backfill/*`
- `docs/AI_OS/morning_brief/*` after extracting one workflow if still wanted.
- `docs/AI_OS/writers/*` after deciding whether writer chains remain part of active AI_OS.
- Duplicate secure access generation set under `docs/AI_OS/security/phase_15_secure_access/` if `docs/AI_OS/security/secure_access/` is chosen as canonical.

Candidate archive destination later:

- `archive/docs_aios_legacy/`

## DELETE CANDIDATE LATER Recommendations

Do not delete in the next pass. Mark for later review after archive and extraction:

- Repeated tiny `_DRAFT.md` files that only restate an obvious rule.
- Duplicate timestamped files such as `*_DRAFT_2026-05-07_153925.md` after confirming the untimestamped version has the same useful content.
- Low-value `README_FOLDER_PURPOSE.txt` files in folders that will be archived entirely.
- Fixture JSON files under docs that duplicate app mock data or automation schemas.
- Stale status/report/checkpoint docs superseded by current audit reports.
- Empty-shell docs with no durable decision, procedure, or architecture.

## HUMAN REVIEW Items

These need MAIN CONTROL decisions before move/archive:

- `docs/AI_OS/dashboard`: decide whether docs should describe the real `apps/dashboard` implementation or remain product ideation.
- `docs/AI_OS/dispatcher` vs `docs/AI_OS/orchestration`: decide the canonical vocabulary. The repo should not have dispatcher, orchestration, runtime, automation, and operator as separate brains.
- `docs/AI_OS/security/secure_access` vs `docs/AI_OS/security/phase_15_secure_access`: likely duplicate lineage.
- `docs/AI_OS/brokers`, `docs/AI_OS/broker_adapters`, `docs/AI_OS/trading`, `docs/AI_OS/trader`, `docs/AI_OS/backtesting`: confirm paper-only role before promoting anything.
- Root-level `docs/AI_OS/*_DRAFT.md`: many look like governance concepts; decide whether to extract or archive as planning history.
- `docs/AI_OS/claude`, `docs/AI_OS/codex`, and agent role docs: decide if these belong under `docs/governance/agents/` or archive.

## Proposed Clean Docs Structure

Recommended target shape:

```text
docs/
  architecture/
    AI_OS_SYSTEM_ARCHITECTURE.md
    ORCHESTRATION_RUNTIME_MODEL.md
    DASHBOARD_ARCHITECTURE.md
  workflows/
    OPERATOR_WORKFLOW.md
    APPLY_APPROVAL_WORKFLOW.md
    COMMIT_AND_PR_WORKFLOW.md
    SAFE_SESSION_RESUME.md
  governance/
    AI_OS_DOCTRINE.md
    AGENT_GOVERNANCE.md
    FILE_PLACEMENT_RULES.md
    SAFETY_MATRIX.md
  infrastructure/
    RUNTIME_SOURCE_OF_TRUTH_MAP.md
    VALIDATOR_CHAIN.md
    WORK_PACKET_SCHEMA.md
  security/
    SECURE_ACCESS_MODEL.md
    SECRET_HANDLING.md
    BROKER_LIVE_TRADING_BLOCKS.md
  roadmap/
    AI_OS_ROADMAP.md
    DASHBOARD_ROADMAP.md
    TELEMETRY_ROADMAP.md
  concepts/
    AUTONOMY_BOUNDARIES.md
    BOOTSTRAP_ENGINE_CONCEPT.md
    MULTI_AGENT_CONCEPTS.md
  audits/
    current cleanup reports only
```

## What Not To Touch

Do not touch in the next cleanup pass without separate approval:

- active app source or app docs under `apps/`
- `archive/`
- root governance files
- `.github/`
- `automation/`
- `services/`, `scripts/`, `aios/`, `schemas/`, `tests/`
- live broker/OANDA/webhook/trading materials
- `docs/AI_OS/trading_laboratory` because it has already been moved to archive

## Exact Next Pass Recommendation

Run a DRY_RUN extraction plan before moving files:

1. Create a canonical promotion list for 10 to 20 active docs.
2. Propose new destination names under `docs/architecture`, `docs/workflows`, `docs/governance`, `docs/infrastructure`, `docs/security`, `docs/roadmap`, and `docs/concepts`.
3. Propose `archive/docs_aios_legacy/` grouping for the remaining generated/planning swarm.
4. Do not move anything until MAIN CONTROL approves the exact file list.

Suggested next pass title:

`AI_OS DOCS PASS 10 - PROMOTION AND ARCHIVE PLAN FOR docs/AI_OS`

## Validation

Required validation for this report:

```powershell
git status --short
git diff --stat
```

Expected result:

- only `docs/audits/docs-aios-classification-pass-9.md` is changed,
- no moves,
- no deletes,
- no edits outside `docs/audits`.
