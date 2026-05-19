# Phase 195 Final Reaper Unblock Archive Plan

Branch: `phase-189-high-risk-doctrine-review`
Date: 2026-05-19

## Current Counts

- `docs/AI_OS`: 443 tracked files
- `archive/docs_aios_legacy`: 327 tracked files
- `docs/concepts`: 6 tracked files
- `docs/workflows`: 2 tracked files
- `docs/governance`: 2 tracked files
- `docs/security`: 5 tracked files
- `docs/audits`: 42 tracked files
- Root files directly under `docs/AI_OS`: 19 tracked files

## Folder Classification Table

| Folder | Count | Classification | Live Wires | Canonical Destination | Action |
| --- | ---: | --- | ---: | --- | --- |
| `agent_runtime` | 24 | KEEP ACTIVE, active runtime fixture/model | 46 | Future split to concepts plus active fixture location | Do not move |
| `telemetry` | 23 | KEEP ACTIVE, active planning/source docs | 27 | Future `docs/concepts/aios-telemetry-data-model-concepts.md` | Do not move |
| `operator` | 23 | KEEP ACTIVE, active operator references | 14 | `docs/workflows/aios-operator-workflows.md` later | Needs blocker phase |
| `governance` | 22 | KEEP ACTIVE, authority docs | 4 | `docs/governance` after explicit governance phase | Do not move |
| `security` | 21 | KEEP ACTIVE, security/privacy authority | 6 | `docs/security` after explicit security phase | Do not move |
| `audits` | 14 | MIXED, audit source and older drafts | 13 | `docs/audits` | Split later |
| `roadmap` | 13 | MIXED, roadmap planning | 2 | `docs/roadmap` | Split later |
| `change_control` | 12 | KEEP ACTIVE, dashboard mock references | 8 | `docs/workflows` or `docs/governance` later | Needs blocker phase |
| `llm` | 12 | MIXED, LLM doctrine | 2 | `docs/concepts` or `docs/security` | Canonicalize first |
| `productization` | 11 | MIXED, product planning | 1 | `docs/roadmap` or `docs/concepts` | Canonicalize first |
| `signal_intelligence` | 11 | KEEP ACTIVE, validators reference it | 10 | Future concept/spec docs | Needs blocker phase |
| `system_wizards` | 10 | PROMOTE candidate, no active-area refs found | 0 | `docs/concepts` or `docs/workflows` | Inspect and extract first |
| `multi_agent` | 10 | KEEP ACTIVE, validators and fixtures | 13 | Future agent runtime concept | Needs blocker phase |
| `problem_resolution` | 10 | KEEP ACTIVE, dashboard mock references | 3 | `docs/workflows` | Needs blocker phase |
| `operations` | 10 | PROMOTE candidate, no active-area refs found | 0 | `docs/workflows` | Inspect and extract first |
| `brokers` | 10 | DO NOT TOUCH, broker boundary area | 1 | `docs/security` or `docs/specs` only after broker-boundary review | Do not move |
| `agents` | 9 | KEEP ACTIVE, validators reference it | 6 | Future multi-agent concept | Needs blocker phase |
| `reporting` | 8 | KEEP ACTIVE, validators reference it | 18 | Future reporting concept/spec | Needs blocker phase |
| `strategy_registry` | 8 | KEEP ACTIVE, backtesting validators | 7 | `docs/specs` later | Needs blocker phase |
| `backtesting` | 8 | KEEP ACTIVE, backtesting validators | 7 | `docs/specs` later | Needs blocker phase |
| `tools` | 8 | KEEP ACTIVE, tool validators | 4 | `docs/specs` later | Needs blocker phase |
| `context` | 7 | PROMOTE candidate, no active-area refs found | 0 | `docs/concepts` | Inspect and extract first |
| `risk_controls` | 7 | DO NOT TOUCH, trading safety boundary | 5 | `docs/security` or `docs/specs` only after safety review | Do not move |
| `analytics` | 7 | KEEP ACTIVE, status validators | 19 | `docs/specs` later | Needs blocker phase |
| `observability` | 7 | KEEP ACTIVE, production validators | 5 | `docs/specs` or `docs/architecture` | Needs blocker phase |
| `azure` | 7 | KEEP ACTIVE, Azure boundary validator | 5 | `docs/infrastructure` or `docs/security` | Needs blocker phase |
| `index` | 6 | KEEP ACTIVE, documentation validators | 6 | `docs/governance` or `docs/audits` | Needs blocker phase |
| `trading` | 6 | DO NOT TOUCH, trading boundary area | 18 | Separate trading safety review only | Do not move |
| `validators` | 6 | KEEP ACTIVE, dashboard mock/status refs | 6 | `docs/specs` or `docs/workflows` | Needs blocker phase |
| `execution` | 6 | DO NOT TOUCH, live execution safety boundary | 5 | Separate execution safety review only | Do not move |
| `readiness` | 5 | KEEP ACTIVE, readiness validators | 6 | `docs/workflows` | Needs blocker phase |
| `mobile` | 5 | PROMOTE candidate, no active-area refs found | 0 | `docs/roadmap` or `docs/specs` | Inspect and extract first |
| `operator_workflows` | 5 | KEEP ACTIVE, dashboard fixtures | 12 | `docs/workflows/aios-operator-workflows.md` later | Needs blocker phase |
| `product` | 4 | MIXED, low active references | 0 | `docs/roadmap` or `docs/concepts` | Inspect first |
| `router` | 4 | KEEP ACTIVE, router validators | 9 | `docs/workflows` | Needs blocker phase |
| `metrics` | 4 | KEEP ACTIVE, analytics validators | 4 | `docs/specs` | Needs blocker phase |
| `broker_adapters` | 4 | DO NOT TOUCH, broker boundary area | 0 | Separate broker-boundary review only | Do not move |
| `work_intelligence` | 4 | KEEP ACTIVE, work intelligence automation | 4 | `docs/concepts` later | Needs blocker phase |
| `compliance` | 4 | DO NOT TOUCH, compliance authority | 0 | `docs/security` or compliance docs after review | Do not move |
| `monetization` | 4 | PROMOTE candidate, no active-area refs found | 0 | `docs/roadmap` or `docs/concepts` | Inspect and extract first |
| `codex` | 4 | KEEP ACTIVE, codex validator | 1 | `docs/workflows` or `docs/governance` | Needs blocker phase |
| `automation` | 4 | KEEP ACTIVE, writer/status validators | 12 | `docs/workflows` or `docs/specs` | Needs blocker phase |
| `legal` | 4 | DO NOT TOUCH, legal placeholder area | 0 | Legal/compliance review only | Do not move |
| `runtime` | 3 | PROMOTE candidate, no active-area refs found | 0 | `docs/architecture` | Inspect and extract first |
| `runbooks` | 3 | KEEP ACTIVE, status references | 2 | `docs/workflows` | Needs blocker phase |
| `approval` | 3 | KEEP ACTIVE, approval validators | 5 | `docs/workflows` or `docs/governance` | Needs blocker phase |
| `secrets` | 3 | DO NOT TOUCH, secrets boundary area | 2 | `docs/security` only after explicit review | Do not move |
| `mean_machine` | 3 | KEEP ACTIVE, status validators | 8 | `docs/concepts` later | Needs blocker phase |
| `source_control` | 2 | KEEP ACTIVE, source-control validators | 2 | `docs/workflows` or `docs/governance` | Needs blocker phase |
| `startup` | 2 | KEEP ACTIVE, startup validators | 2 | `docs/workflows` | Needs blocker phase |
| `architecture` | 2 | PROMOTE candidate, no active-area refs found | 0 | `docs/architecture` | Inspect and extract first |
| `interface` | 2 | PROMOTE candidate, canonical reference exists | 0 | `docs/workflows` or `docs/specs` | Inspect and extract first |
| `trader` | 2 | DO NOT TOUCH, trading-adjacent | 0 | Separate trading review only | Do not move |
| `cicd` | 2 | PROMOTE candidate, no active-area refs found | 0 | `docs/workflows` or `docs/governance` | Inspect and extract first |
| `production` | 2 | KEEP ACTIVE, master validator | 1 | `docs/architecture` | Needs blocker phase |
| `devops` | 1 | KEEP ACTIVE, dashboard mock references | 2 | `docs/workflows` | Needs blocker phase |
| Root `docs/AI_OS/*.md` / `.txt` | 19 | MIXED stale draft docs | 0 | Existing canonical docs or new concepts | Delete-candidate review later |

## Archived Already

- `archive/docs_aios_legacy/autonomous`
- `archive/docs_aios_legacy/backfill`
- `archive/docs_aios_legacy/bootstrap_engine`
- `archive/docs_aios_legacy/checkpoints`
- `archive/docs_aios_legacy/dashboard`
- `archive/docs_aios_legacy/dispatcher`
- `archive/docs_aios_legacy/morning_brief`
- `archive/docs_aios_legacy/orchestration`
- `archive/docs_aios_legacy/progress`
- `archive/docs_aios_legacy/roadmaps`
- `archive/docs_aios_legacy/writers`

## Not Archived Yet

The remaining `docs/AI_OS` folders are listed in the classification table. High-risk active folders include `agent_runtime`, `operator`, `operator_workflows`, `governance`, `security`, and `telemetry`.

## True Live Wires

Representative true live wires found in active areas:

- `automation/agent_runtime/Test-AiOsAgentRuntimeReadiness.DRY_RUN.ps1` references `docs\AI_OS\agent_runtime`.
  - Recommended fix: do not repoint until an approved active runtime fixture/model destination exists.
  - Safe now: NO.
- `apps/dashboard/mock-data/aios-orchestration-control-room.example.json` references `docs/AI_OS/agent_runtime` JSON fixtures.
  - Recommended fix: keep active until agent runtime split is designed.
  - Safe now: NO.
- `automation/status/Test-AiOsLifetimeDevelopmentTelemetry.DRY_RUN.ps1` references `docs\AI_OS\telemetry` evidence/storage contracts.
  - Recommended fix: canonicalize telemetry data model first, then decide whether validators should move.
  - Safe now: NO.
- `automation/status/Test-AiOsTelemetryReportingPersistenceReadiness.DRY_RUN.ps1` references multiple `docs/AI_OS/telemetry` boundary docs.
  - Recommended fix: telemetry canonicalization phase.
  - Safe now: NO.
- `apps/dashboard/mock-data/aios-apply-routing-v1.example.json`, `aios-session-resume-state-v1.example.json`, and `aios-morning-execution-packet-v1.example.json` reference `docs/AI_OS/operator_workflows`.
  - Recommended fix: operator workflow blocker-retirement phase using `docs/workflows/aios-operator-workflows.md` only after fixture semantics are reviewed.
  - Safe now: NO.
- `automation/router/Test-AiOsRouterCommandMap.DRY_RUN.ps1` and `automation/router/Test-AiOsWorkflowRegistry.DRY_RUN.ps1` reference `docs/AI_OS/router` and `docs/AI_OS/operator`.
  - Recommended fix: router/operator canonical workflow phase.
  - Safe now: NO.
- `automation/backtesting/*` references `docs/AI_OS/backtesting` and `docs/AI_OS/strategy_registry`.
  - Recommended fix: create backtesting/spec canonical docs first.
  - Safe now: NO.
- `automation/execution_safety/*` references `docs/AI_OS/execution`, `docs/AI_OS/brokers`, and `docs/AI_OS/risk_controls`.
  - Recommended fix: separate trading/execution safety review only.
  - Safe now: NO.
- `automation/status/*Analytics*` references `docs/AI_OS/analytics` and `docs/AI_OS/metrics`.
  - Recommended fix: analytics/metrics spec canonicalization phase.
  - Safe now: NO.
- `automation/status/*Writer*` references `docs/AI_OS/automation` after writers archive cleanup.
  - Recommended fix: writer automation concept/workflow review.
  - Safe now: NO.

## Soft Historical References

Soft references exist in `docs/audits`, `docs/concepts`, `docs/specs`, `docs/roadmap`, and `docs/infrastructure` for already archived folders such as dashboard, dispatcher, orchestration, writers, bootstrap_engine, and autonomous. These references preserve historical provenance and do not block archive by themselves.

## Safe Archive Candidates

No folder was archived in this pass.

Potential future candidates with no active-area references found during this pass:

- `docs/AI_OS/system_wizards`
- `docs/AI_OS/operations`
- `docs/AI_OS/context`
- `docs/AI_OS/mobile`
- `docs/AI_OS/monetization`
- `docs/AI_OS/runtime`
- `docs/AI_OS/architecture`
- `docs/AI_OS/interface`
- `docs/AI_OS/cicd`

These are not archived now because useful concepts have not yet been extracted and the pass did not perform file-level review for each folder.

## Unsafe To Move Tonight

- `docs/AI_OS/agent_runtime`
- `docs/AI_OS/telemetry`
- `docs/AI_OS/operator`
- `docs/AI_OS/operator_workflows`
- `docs/AI_OS/governance`
- `docs/AI_OS/security`
- `docs/AI_OS/execution`
- `docs/AI_OS/brokers`
- `docs/AI_OS/broker_adapters`
- `docs/AI_OS/risk_controls`
- `docs/AI_OS/trading`
- `docs/AI_OS/secrets`
- `docs/AI_OS/legal`
- `docs/AI_OS/compliance`

## Canonicalization Needed

- Agent runtime: split doctrine into concepts while keeping active JSON fixtures in a reviewed active location.
- Telemetry: create or update `docs/concepts/aios-telemetry-data-model-concepts.md`.
- Operator/operator workflows/router: consolidate into `docs/workflows/aios-operator-workflows.md` only after dashboard fixtures and router validators are reviewed.
- Backtesting/strategy registry: create `docs/specs` canonical material.
- Analytics/metrics/reporting/observability: create data/reporting spec docs.
- Multi-agent/agents/LLM/work intelligence: create concept docs before any move.
- Low-reference folders: inspect and extract concepts before archive.

## Delete Candidates Later

No deletion was performed.

Root-level `docs/AI_OS` draft files with no active-area references are delete-candidates after preservation review:

- `docs/AI_OS/AGENT_ROLE_ARCHITECTURE_DRAFT.md`
- `docs/AI_OS/AIOS_PROGRESS_MODEL_CORRECTION_DRAFT.md`
- `docs/AI_OS/AUTOMATION_HELPER_DRY_RUN_REQUIREMENTS_DRAFT.md`
- `docs/AI_OS/AUTOMATION_HELPER_LAYER_PLAN_DRAFT.md`
- `docs/AI_OS/DASHBOARD_OPERATOR_INTERFACE_PLAN_DRAFT.md`
- `docs/AI_OS/DUPLICATE_ARCHIVE_HANDLING_POLICY_DRAFT.md`
- `docs/AI_OS/EVIDENCE_FOLDER_PLAN_DRAFT.md`
- `docs/AI_OS/FILE_CLASSIFICATION_DECISION_RULES_DRAFT.md`
- `docs/AI_OS/LLM_TOOL_PLACEMENT_PLAN_DRAFT.md`
- `docs/AI_OS/MODE_BASED_LAUNCH_RULES_DRAFT.md`
- `docs/AI_OS/MORNING_BRIEF_WORKFLOW_PLAN_DRAFT.md`
- `docs/AI_OS/MORNING_LAUNCH_SAFETY_RULES_DRAFT.md`
- `docs/AI_OS/PROTECTED_FILE_APPROVAL_RULES_DRAFT.md`
- `docs/AI_OS/SCREEN_RECORDING_EVIDENCE_POLICY_DRAFT.md`
- `docs/AI_OS/SCREEN_RECORDING_READINESS_CHECKLIST_DRAFT.md`
- `docs/AI_OS/TELEMETRY_FIELDS_DRAFT.md`

Risk level: medium. Useful content must be preserved in canonical docs first. Safe delete requires another active scan.

Archive delete-candidates for later review:

- `archive/docs_aios_legacy/roadmaps`
- `archive/docs_aios_legacy/backfill`
- `archive/docs_aios_legacy/progress`
- `archive/docs_aios_legacy/checkpoints`
- `archive/docs_aios_legacy/morning_brief`

Risk level: medium. These may be stale generated lineage, but no archive content should be deleted without a separate retention review.

## Actions Performed

- Created `docs/audits/phase-195-final-reaper-unblock-archive-plan.md`.
- No folders moved.
- No files deleted.
- No references repointed.
- No APPLY scripts run.

## Validation

- `git status --short -uall`: expected to show this audit file as untracked before staging.
- `git diff --stat`: no tracked-file diff expected before staging.
- `git diff --name-status`: no tracked-file diff expected before staging.
- `git diff --check`: PASS expected.
- PowerShell parser checks: not required; no `.ps1` files changed.
- JSON parse checks: not required; no `.json` files changed.
- Delete-only check: no delete-only entries expected.
- Final `docs/AI_OS` count: 443 tracked files.
- Final `archive/docs_aios_legacy` count: 327 tracked files.

## Recommended Next Commit Message

`docs: map final AI_OS cleanup blockers`
