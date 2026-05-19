# docs/AI_OS Promotion and Archive Plan - Pass 10

Date: 2026-05-19
Branch: phase-82-copy-paste-reduction-runner
Mode: REPORT ONLY

## Purpose

Create an exact promotion, extraction, archive, and delete-candidate plan for `docs/AI_OS`. This pass did not move, delete, rename, or rewrite any `docs/AI_OS` files.

## Current docs/AI_OS Summary

- Tracked files under `docs/AI_OS`: 770
- Top-level subfolders under `docs/AI_OS`: 70
- Generated/planning pattern matches: 531 files
- Largest folders:
  - `docs/AI_OS/dashboard`: 127
  - `docs/AI_OS/dispatcher`: 57
  - `docs/AI_OS/orchestration`: 49
  - `docs/AI_OS/agent_runtime`: 24
  - `docs/AI_OS/operator`: 23
  - `docs/AI_OS/telemetry`: 23
  - `docs/AI_OS/writers`: 23
  - `docs/AI_OS/governance`: 22
  - `docs/AI_OS/security`: 21
  - `docs/AI_OS/bootstrap_engine`: 19

## KEEP ACTIVE / PROMOTE

These should remain active by being promoted into compact canonical docs. Promotion should create new docs first, then archive source swarms later.

### To `docs/architecture/`

- `docs/AI_OS/architecture/SYSTEM_LEVEL_AI_WIZARDS.md` -> `docs/architecture/AI_OS_SYSTEM_ARCHITECTURE.md`
- `docs/AI_OS/orchestration/AI_OS_ORCHESTRATION_MODEL.md` -> `docs/architecture/ORCHESTRATION_MODEL.md`
- `docs/AI_OS/dispatcher/runtime/RUNTIME_SOURCE_OF_TRUTH_MAP.md` -> `docs/architecture/RUNTIME_SOURCE_OF_TRUTH_MAP.md`
- `docs/AI_OS/dispatcher/runtime/RUNTIME_API_CONTRACT.md` -> `docs/architecture/RUNTIME_API_CONTRACT.md`
- `docs/AI_OS/dispatcher/runtime/RUNTIME_PACKET_AND_LOCK_MODEL.md` -> `docs/architecture/WORK_PACKET_AND_LOCK_MODEL.md`
- `docs/AI_OS/dispatcher/runtime/RUNTIME_WORKER_LIFECYCLE_MODEL.md` -> `docs/architecture/WORKER_LIFECYCLE_MODEL.md`
- Extract from `docs/AI_OS/dashboard/*` -> `docs/architecture/DASHBOARD_ARCHITECTURE.md`

### To `docs/workflows/`

- `docs/AI_OS/operator/AIOS_OPERATOR_PREFERENCES_AND_WORKFLOW_CANONICAL.md` -> `docs/workflows/OPERATOR_WORKFLOW.md`
- `docs/AI_OS/operator/AIOS_MORNING_OPERATOR_STARTUP_FLOW.md` -> `docs/workflows/MORNING_STARTUP_WORKFLOW.md`
- `docs/AI_OS/operator/AIOS_FILE_OWNERSHIP_AND_COLLISION_PREVENTION.md` -> `docs/workflows/FILE_OWNERSHIP_AND_COLLISION_PREVENTION.md`
- `docs/AI_OS/operator/AIOS_MERGE_VALIDATION_AND_CONFLICT_ARBITRATION.md` -> `docs/workflows/MERGE_VALIDATION_AND_CONFLICT_ARBITRATION.md`
- `docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md` -> `docs/workflows/PARALLEL_CODEX_WORKFLOW.md`
- `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md` -> `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md`
- `docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md` -> `docs/workflows/APPLY_ROUTING_CHAIN.md`
- `docs/AI_OS/operator_workflows/AIOS_SAFE_SESSION_RESUME_STANDARD.md` -> `docs/workflows/SAFE_SESSION_RESUME.md`
- `docs/AI_OS/runbooks/REPO_HEALTH_VERIFICATION_CHAIN_DRAFT.md` -> `docs/workflows/REPO_HEALTH_VERIFICATION_CHAIN.md`

### To `docs/governance/`

- `docs/AI_OS/AGENTS.md` -> `docs/governance/AGENT_RULES.md`
- `docs/AI_OS/WORKER_GOVERNANCE.md` -> `docs/governance/WORKER_GOVERNANCE.md`
- `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md` -> `docs/governance/FILE_PLACEMENT_RULES.md`
- `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md` -> `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md`
- Extract from `docs/AI_OS/governance/AIOS_SYSTEM_WIDE_SAFETY_MATRIX_DRAFT.md` -> `docs/governance/SAFETY_MATRIX.md`
- Extract from `docs/AI_OS/governance/AIOS_SECRET_HANDLING_MATRIX_DRAFT.md` -> `docs/governance/SECRET_HANDLING.md`
- Extract from `docs/AI_OS/governance/AIOS_BROKER_LIVE_TRADING_BLOCK_MATRIX_DRAFT.md` -> `docs/governance/BROKER_LIVE_TRADING_BLOCKS.md`
- Extract from `docs/AI_OS/governance/AIOS_DOCUMENTATION_PROMOTION_CRITERIA_DRAFT.md` -> `docs/governance/DOCUMENTATION_PROMOTION_CRITERIA.md`

### To `docs/infrastructure/`

- `docs/AI_OS/orchestration/AIOS_WORK_PACKETS.md` -> `docs/infrastructure/WORK_PACKETS.md`
- `docs/AI_OS/orchestration/AIOS_WORKTREE_LANES.md` -> `docs/infrastructure/WORKTREE_LANES.md`
- `docs/AI_OS/orchestration/AIOS_WORKSPACE_BOOTSTRAP.md` -> `docs/infrastructure/WORKSPACE_BOOTSTRAP.md`
- `docs/AI_OS/dispatcher/runtime/validators/VALIDATOR_STAGE_MATRIX.md` -> `docs/infrastructure/VALIDATOR_STAGE_MATRIX.md`
- `docs/AI_OS/dispatcher/runtime/validators/VALIDATOR_IMPLEMENTATION_PLAN.md` -> `docs/infrastructure/VALIDATOR_CHAIN.md`
- `docs/AI_OS/dispatcher/runtime/commit_packages/EXACT_FILE_COMMIT_RULES.md` -> `docs/infrastructure/EXACT_FILE_COMMIT_RULES.md`
- `docs/AI_OS/dispatcher/runtime/approval/APPROVAL_RUNTIME_MODEL.md` -> `docs/infrastructure/APPROVAL_RUNTIME_MODEL.md`

### To `docs/security/`

- `docs/AI_OS/security/secure_access/AIOS_ACCESS_MODEL_OVERVIEW.md` -> `docs/security/ACCESS_MODEL_OVERVIEW.md`
- `docs/AI_OS/security/secure_access/AIOS_ADMIN_ZONE_REAUTH_RULES.md` -> `docs/security/ADMIN_ZONE_REAUTH_RULES.md`
- `docs/AI_OS/security/secure_access/GITHUB_REPO_IDENTITY_BOUNDARY.md` -> `docs/security/GITHUB_REPO_IDENTITY_BOUNDARY.md`
- `docs/AI_OS/security/secure_access/SECURE_ACCESS_SETUP_CHECKLIST_TEMPLATE.md` -> `docs/security/SECURE_ACCESS_SETUP_CHECKLIST.md`
- Extract from `docs/AI_OS/security/AIOS_PRIVACY_CREDENTIAL_EXCLUSION_CHECKLIST_DRAFT.md` -> `docs/security/PRIVACY_CREDENTIAL_EXCLUSION_CHECKLIST.md`

### To `docs/decisions/`

- Extract canonical vocabulary decision from `docs/AI_OS/dispatcher` vs `docs/AI_OS/orchestration` -> `docs/decisions/AI_OS_DISPATCHER_ORCHESTRATION_TERMINOLOGY.md`
- Extract dashboard active-vs-ideation decision from `docs/AI_OS/dashboard` -> `docs/decisions/DASHBOARD_DOCS_PROMOTION_DECISION.md`
- Extract secure-access lineage decision from `docs/AI_OS/security/secure_access` and `docs/AI_OS/security/phase_15_secure_access` -> `docs/decisions/SECURE_ACCESS_DOCS_CANONICAL_LINEAGE.md`

## PROMOTE / EXTRACT LIST

These folders are too large or noisy to promote directly. Extract compact summaries first.

| Source | Extract into | Notes |
| --- | --- | --- |
| `docs/AI_OS/dashboard` | `docs/architecture/DASHBOARD_ARCHITECTURE.md`, `docs/roadmap/DASHBOARD_ROADMAP.md`, `docs/concepts/DASHBOARD_WIDGET_CONCEPTS.md` | 127 files. Extract UI architecture, data contract, widget roadmap, and safety boundaries. |
| `docs/AI_OS/dispatcher` | `docs/architecture/RUNTIME_SOURCE_OF_TRUTH_MAP.md`, `docs/infrastructure/VALIDATOR_CHAIN.md`, `docs/workflows/PACKET_LIFECYCLE_WORKFLOW.md` | 57 files. Promote runtime source-of-truth and validator concepts. |
| `docs/AI_OS/orchestration` | `docs/architecture/ORCHESTRATION_MODEL.md`, `docs/infrastructure/WORK_PACKETS.md`, `docs/workflows/OPERATOR_ORCHESTRATION_WORKFLOW.md` | 49 files. Promote stable model docs; archive phase docs later. |
| `docs/AI_OS/operator` | `docs/workflows/OPERATOR_WORKFLOW.md` plus focused workflow docs | Keep stable operator procedures; archive draft variants. |
| `docs/AI_OS/operator_workflows` | `docs/workflows/` | Fold into operator workflow set. |
| `docs/AI_OS/governance` | `docs/governance/` | Promote rules, ownership, safety matrices, and promotion criteria. |
| `docs/AI_OS/security` | `docs/security/` | Prefer `secure_access` over `phase_15_secure_access` unless human review says otherwise. |
| `docs/AI_OS/source_control` | `docs/workflows/SOURCE_CONTROL_ROLLBACK.md` | Promote rollback workflow if still valid. |
| `docs/AI_OS/runbooks` | `docs/workflows/` or `docs/runbooks/` | Promote repo health chain and archive coverage-gap draft. |
| `docs/AI_OS/architecture` | `docs/architecture/` | Promote system architecture doc. |
| `docs/AI_OS/roadmap`, `docs/AI_OS/roadmaps` | `docs/roadmap/AI_OS_ROADMAP.md` | Merge duplicate roadmap folders into one roadmap. |
| `docs/AI_OS/product`, `docs/AI_OS/productization` | `docs/roadmap/PRODUCTIZATION_ROADMAP.md`, `docs/concepts/PRODUCT_BOUNDARIES.md` | Extract product boundaries; do not imply live trading productization. |

## ARCHIVE CANDIDATE LIST

Move later to `archive/docs_aios_legacy/` only after Pass 11 summaries exist.

### Folder-based candidates

- `docs/AI_OS/checkpoints/`
- `docs/AI_OS/progress/`
- `docs/AI_OS/backfill/`
- `docs/AI_OS/morning_brief/`
- `docs/AI_OS/writers/`
- `docs/AI_OS/bootstrap_engine/`
- `docs/AI_OS/autonomous/`
- `docs/AI_OS/agent_runtime/` after runtime architecture extraction
- `docs/AI_OS/analytics/`
- `docs/AI_OS/metrics/`
- `docs/AI_OS/reporting/`
- `docs/AI_OS/work_intelligence/`
- `docs/AI_OS/mobile/`
- `docs/AI_OS/monetization/`
- `docs/AI_OS/productization/` after productization summary
- `docs/AI_OS/roadmaps/` after roadmap merge
- `docs/AI_OS/security/phase_15_secure_access/` if `secure_access` is approved as canonical
- `docs/AI_OS/dashboard/` after dashboard summary docs are created
- `docs/AI_OS/orchestration/PHASE_*` files after canonical orchestration docs are promoted

### Pattern-based candidates

- `docs/AI_OS/**/*_DRAFT.md`
- `docs/AI_OS/**/*_DRY_RUN.md`
- `docs/AI_OS/**/PHASE_*.md`
- `docs/AI_OS/**/STAGE*.md`
- `docs/AI_OS/**/*CHECKPOINT*.md`
- `docs/AI_OS/**/*STATUS*.md`
- `docs/AI_OS/**/*REPORT*.md`
- `docs/AI_OS/**/*LEDGER*.md`
- timestamped duplicates such as `*_2026-05-07_153925.md`

## DELETE CANDIDATE LATER LIST

Do not delete in Pass 11 or Pass 12. Consider deletion only after archived content has been reviewed.

- `README_FOLDER_PURPOSE.txt` files inside folders that are archived wholesale.
- Duplicate timestamped drafts when an untimestamped version has the same useful content.
- Fixture JSON under docs that duplicates real app mock data or schemas:
  - `docs/AI_OS/dashboard/*FIXTURE*.json`
  - `docs/AI_OS/analytics/*FIXTURE*.json`
- Repeated tiny rule drafts that are fully absorbed into canonical governance docs.
- Stale stage/status/checkpoint reports superseded by current `docs/audits/` reports.
- Empty shell docs with no durable decision, architecture, workflow, or governance content.

## HUMAN REVIEW LIST

- `docs/AI_OS/dashboard`: decide active implementation docs vs product ideation before archiving.
- `docs/AI_OS/dispatcher` and `docs/AI_OS/orchestration`: decide whether "dispatcher" is a subsystem under orchestration or a legacy name.
- `docs/AI_OS/security/secure_access` vs `docs/AI_OS/security/phase_15_secure_access`: choose canonical lineage.
- `docs/AI_OS/brokers`, `docs/AI_OS/broker_adapters`, `docs/AI_OS/trading`, `docs/AI_OS/trader`, `docs/AI_OS/backtesting`: confirm paper-only status and avoid live broker implications.
- `docs/AI_OS/agents`, `docs/AI_OS/multi_agent`, `docs/AI_OS/llm`, `docs/AI_OS/codex`, `docs/AI_OS/claude`: decide one agent governance location.
- Root-level `docs/AI_OS/*_DRAFT.md`: decide whether to extract into governance/concepts or archive as planning history.

## Proposed Clean Active Docs Target Tree

```text
docs/
  architecture/
    AI_OS_SYSTEM_ARCHITECTURE.md
    ORCHESTRATION_MODEL.md
    RUNTIME_SOURCE_OF_TRUTH_MAP.md
    DASHBOARD_ARCHITECTURE.md
  workflows/
    OPERATOR_WORKFLOW.md
    MORNING_STARTUP_WORKFLOW.md
    APPLY_ROUTING_CHAIN.md
    SAFE_SESSION_RESUME.md
    COMMIT_AND_PR_WORKFLOW.md
  governance/
    AGENT_RULES.md
    WORKER_GOVERNANCE.md
    FILE_PLACEMENT_RULES.md
    SAFETY_MATRIX.md
    SECRET_HANDLING.md
    BROKER_LIVE_TRADING_BLOCKS.md
  infrastructure/
    WORK_PACKETS.md
    VALIDATOR_CHAIN.md
    EXACT_FILE_COMMIT_RULES.md
    APPROVAL_RUNTIME_MODEL.md
  security/
    ACCESS_MODEL_OVERVIEW.md
    ADMIN_ZONE_REAUTH_RULES.md
    GITHUB_REPO_IDENTITY_BOUNDARY.md
    SECURE_ACCESS_SETUP_CHECKLIST.md
  audits/
    current cleanup reports only
  decisions/
    AI_OS_DISPATCHER_ORCHESTRATION_TERMINOLOGY.md
    DASHBOARD_DOCS_PROMOTION_DECISION.md
    SECURE_ACCESS_DOCS_CANONICAL_LINEAGE.md
  roadmap/
    AI_OS_ROADMAP.md
    DASHBOARD_ROADMAP.md
    PRODUCTIZATION_ROADMAP.md
  concepts/
    AUTONOMY_BOUNDARIES.md
    BOOTSTRAP_ENGINE_CONCEPT.md
    MULTI_AGENT_CONCEPTS.md
    DASHBOARD_WIDGET_CONCEPTS.md
```

## Proposed Pass 11

Smallest useful next move: create compact summary docs only. Do not archive hundreds of files yet.

Allowed Pass 11 outputs:

- `docs/architecture/AI_OS_SYSTEM_ARCHITECTURE.md`
- `docs/architecture/ORCHESTRATION_MODEL.md`
- `docs/architecture/RUNTIME_SOURCE_OF_TRUTH_MAP.md`
- `docs/architecture/DASHBOARD_ARCHITECTURE.md`
- `docs/workflows/OPERATOR_WORKFLOW.md`
- `docs/workflows/APPLY_ROUTING_CHAIN.md`
- `docs/governance/SAFETY_MATRIX.md`
- `docs/security/ACCESS_MODEL_OVERVIEW.md`
- `docs/roadmap/AI_OS_ROADMAP.md`
- `docs/concepts/AUTONOMY_BOUNDARIES.md`
- `docs/decisions/AI_OS_DISPATCHER_ORCHESTRATION_TERMINOLOGY.md`

Pass 11 should read from `docs/AI_OS` and write only compact canonical docs. No archive moves.

## Proposed Pass 12

First actual archive batch should be folder-based and limited to clearly generated/historical groups.

Recommended Pass 12 archive batch:

- `docs/AI_OS/checkpoints/` -> `archive/docs_aios_legacy/checkpoints/`
- `docs/AI_OS/progress/` -> `archive/docs_aios_legacy/progress/`
- `docs/AI_OS/backfill/` -> `archive/docs_aios_legacy/backfill/`
- `docs/AI_OS/morning_brief/` -> `archive/docs_aios_legacy/morning_brief/`
- `docs/AI_OS/roadmaps/` -> `archive/docs_aios_legacy/roadmaps_duplicate/` after `docs/roadmap/AI_OS_ROADMAP.md` exists
- `docs/AI_OS/security/phase_15_secure_access/` -> `archive/docs_aios_legacy/security_phase_15_secure_access/` after secure-access decision

Do not include `dashboard`, `dispatcher`, or `orchestration` in the first archive batch. Those need compact summaries and reference review first.

## Risk Controls

- Preserve ideas before archive by creating compact summaries first.
- Avoid touching app/code paths; this plan is docs-only.
- Keep paper-only trading boundary explicit when extracting broker/trading docs.
- Avoid breaking references by scanning docs and scripts before any move.
- Use folder-based archive batches, not hundreds of individual file decisions.
- Do not delete in the archive pass; deletion can only happen after human review of archived material.
- Keep `docs/AI_OS/trading_laboratory` out of scope because it has already been moved to archive.

## Validation

Required validation:

```powershell
git status --short
git diff --stat
```

Expected:

- only `docs/audits/docs-aios-promotion-archive-plan-pass-10.md` changed,
- no moves,
- no deletes,
- no edits outside `docs/audits`.
