# Phase 5E docs/AI_OS Leftover Classification

Status: classification only
Branch: `v2/aios`
Scope: `docs/AI_OS/` compared against active V2 authority in `AGENTS.md`, `docs/governance/`, `docs/workflows/`, `docs/security/`, and `docs/architecture/`.

This audit does not edit, move, delete, rename, archive, commit, or push files. It classifies remaining CLEAN-era source material after Phase 5D canonical workflow promotion.

## Executive Summary

`docs/AI_OS/` remains a large CLEAN-era source-material tree. It contains useful doctrine, but it should not act as active V2 authority by default.

Current V2 authority is:

- `AGENTS.md` for AI/tool behavior.
- `docs/governance/` for ownership, placement, runtime boundaries, source-of-truth rules, and operational doctrine.
- `docs/workflows/` for operator, APPLY, resume, parallel worker, and branch/lane workflows.
- `docs/security/` for access, approval, privacy, and credential exclusion.
- `docs/architecture/` for durable runtime and agent architecture.

The highest-risk leftover zones are duplicate brains in `docs/AI_OS/system_wizards/`, `docs/AI_OS/context/`, `docs/AI_OS/operator/`, `docs/AI_OS/operator_workflows/`, `docs/AI_OS/governance/`, `docs/AI_OS/codex/`, and `docs/AI_OS/AGENTS.md`.

## docs/AI_OS Folder Overview

| Area | File count observed | Proposed role | Classification | Reason |
|---|---:|---|---|---|
| `docs/AI_OS/system_wizards/` | 10 | Historical start/current/checkpoint brain source | MERGE INTO CANONICAL | Contains start-here, current-state, checkpoint, architecture, guardrail docs. |
| `docs/AI_OS/context/` | 7 | Historical context/source map source | MERGE INTO CANONICAL | Duplicates current source-of-truth and operator bootstrap authority. |
| `docs/AI_OS/operator/` | 23 | Operator workflow source material | MERGE INTO CANONICAL | Some workflows remain worth mining, but canonical workflows now live in `docs/workflows/`. |
| `docs/AI_OS/operator_workflows/` | 5 | Workflow source material | ARCHIVE ONLY after validation | APPLY and safe resume are absorbed; morning/fatigue/roadmap need triage. |
| `docs/AI_OS/governance/` | 22 | Governance source material | MERGE INTO CANONICAL | Some safety matrices may still be useful; placement/ownership already absorbed. |
| `docs/AI_OS/codex/`, `docs/AI_OS/claude/`, `docs/AI_OS/agents/` | 14 | AI assistant role source material | NEEDS USER DECISION | Root `AGENTS.md` is authority; non-Codex assistant roles may or may not be retained. |
| `docs/AI_OS/security/` | 21 | Security source material | MERGE INTO CANONICAL | Secure access and credential exclusion may contain details not fully promoted. |
| `docs/AI_OS/brokers/`, `docs/AI_OS/broker_adapters/`, `docs/AI_OS/execution/`, `docs/AI_OS/risk_controls/`, `docs/AI_OS/trading/` | 33 | Trading/broker safety source material | MERGE INTO CANONICAL | Preserve no-live-trading and paper-only boundaries before archive. |
| `docs/AI_OS/telemetry/`, `docs/AI_OS/observability/`, `docs/AI_OS/analytics/`, `docs/AI_OS/metrics/`, `docs/AI_OS/reporting/` | 49 | Telemetry/reporting source material | MERGE INTO CANONICAL | Useful for specs/security/workflows; not runtime authority. |
| `docs/AI_OS/agent_runtime/`, `docs/AI_OS/multi_agent/`, `docs/AI_OS/runtime/`, `docs/AI_OS/operations/`, `docs/AI_OS/work_intelligence/` | 51 | Agent/runtime/orchestration source material | MERGE INTO CANONICAL | Compare against `docs/architecture/` and runtime boundary governance before archive. |
| `docs/AI_OS/audits/`, `docs/AI_OS/roadmap/`, `docs/AI_OS/readiness/`, `docs/AI_OS/production/` | 34 | Historical audit/readiness records | ARCHIVE ONLY | Mostly phase-specific historical reports and drafts. |
| `docs/AI_OS/legal/`, `docs/AI_OS/compliance/`, `docs/AI_OS/monetization/`, `docs/AI_OS/productization/`, `docs/AI_OS/mobile/`, `docs/AI_OS/azure/` | 35 | Product/commercial/deployment planning source | NEEDS USER DECISION | Useful later, but not core authority for current V2 stabilization. |
| `docs/AI_OS/problem_resolution/`, `docs/AI_OS/change_control/`, `docs/AI_OS/validators/`, `docs/AI_OS/runbooks/`, `docs/AI_OS/router/` | 35 | Workflow/tooling source material | MERGE INTO CANONICAL | May inform future workflow/spec docs; avoid duplicate active workflow authority. |
| `docs/AI_OS/**/*_DRAFT.md` | many | Draft source material | ARCHIVE ONLY by default | Drafts are not active authority unless explicitly promoted. |
| `docs/AI_OS/**/README_FOLDER_PURPOSE.txt` | many | Folder-note artifacts | REMOVE/RELOCATE CANDIDATE | Generated/organizer-style notes; keep until archive plan approved. |

## Duplicate Authority Left Behind

| Current path | Canonical authority | Classification | Recommendation |
|---|---|---|---|
| `docs/AI_OS/AGENTS.md` | `AGENTS.md` | ARCHIVE ONLY | Do not treat as active AI/tool behavior authority. |
| `docs/AI_OS/system_wizards/00_START_HERE_AI_OS_CONTEXT_PACK.md` | `README.md`, `AGENTS.md`, `docs/workflows/OPERATOR_WORKFLOW.md` | MERGE INTO CANONICAL | Mine only missing durable startup doctrine; then archive. |
| `docs/AI_OS/system_wizards/START_HERE_AI_OS_CONTEXT_PACK.md` | Same as above | MERGE INTO CANONICAL | Compare with `00_START_HERE`; likely duplicate brain. |
| `docs/AI_OS/system_wizards/01_CURRENT_STATE.md` | `docs/audits/`, current git/status evidence | ARCHIVE ONLY | Current-state docs become stale quickly. |
| `docs/AI_OS/system_wizards/02_CHECKPOINT.md` | `docs/audits/`, commit history | ARCHIVE ONLY | Historical checkpoint, not live authority. |
| `docs/AI_OS/system_wizards/03_ARCHITECTURE_LOCK.md` | `docs/architecture/` | MERGE INTO CANONICAL | Mine architecture constraints only if still true. |
| `docs/AI_OS/system_wizards/04_AGENT_ROLES.md` | `AGENTS.md`, possible future `docs/governance/agent-roles.md` | NEEDS USER DECISION | Agent role model may be useful, but root AGENTS remains authority. |
| `docs/AI_OS/system_wizards/05_RULES_AND_GUARDRAILS.md` | `AGENTS.md`, `docs/security/`, `docs/governance/` | MERGE INTO CANONICAL | Safety-critical; compare before archive. |
| `docs/AI_OS/system_wizards/06_PROJECT_PATHS.md` | `docs/governance/source-of-truth-map.md`, `docs/governance/runtime-ownership-map.md` | ARCHIVE ONLY after validation | Path authority is dangerous if stale. |
| `docs/AI_OS/context/AIOS_REPO_SOURCE_OF_TRUTH_MAP.md` | `docs/governance/source-of-truth-map.md` | ARCHIVE ONLY | Source-of-truth role already absorbed into canonical V2 map. |
| `docs/AI_OS/context/AIOS_OPERATOR_QUICKSTART.md` | `docs/workflows/OPERATOR_WORKFLOW.md` | MERGE INTO CANONICAL | Mine only missing beginner-safe operator steps. |
| `docs/AI_OS/context/AIOS_NEW_CHAT_BOOTSTRAP_SEQUENCE.md` | `docs/workflows/SAFE_SESSION_RESUME.md` | MERGE INTO CANONICAL | Mine recovery/bootstrap details only. |
| `docs/AI_OS/context/AIOS_MINIMAL_RECOVERY_CONTEXT_PACKET.md` | `docs/workflows/SAFE_SESSION_RESUME.md` | MERGE INTO CANONICAL | Mine useful resume packet fields only. |
| `docs/AI_OS/operator/AIOS_OPERATOR_PREFERENCES_AND_WORKFLOW_CANONICAL.md` | `docs/workflows/OPERATOR_WORKFLOW.md` | NEEDS USER DECISION | Name says canonical but path is not V2 canonical. |
| `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md` | `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` | ARCHIVE ONLY | Phase 5D promoted allowed lanes and validation commands. |
| `docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md` | `docs/workflows/APPLY_ROUTING_CHAIN.md` | ARCHIVE ONLY | Phase 5D promoted useful state definitions with V2 wording. |
| `docs/AI_OS/operator_workflows/AIOS_SAFE_SESSION_RESUME_STANDARD.md` | `docs/workflows/SAFE_SESSION_RESUME.md` | ARCHIVE ONLY | Phase 5B found no merge needed. |
| `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md` | `docs/governance/FILE_PLACEMENT_RULES.md` | ARCHIVE ONLY | Phase 5B found canonical stronger. |
| `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md` | `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md` | NEEDS USER DECISION | Only optional operational review fields remain unpromoted. |
| `docs/AI_OS/codex/AIOS_CODEX_ORCHESTRATION_PLAYBOOK.md` | `AGENTS.md`, `docs/workflows/` | MERGE INTO CANONICAL | Mine only missing Codex workflow constraints. |
| `docs/AI_OS/codex/AGENTS_MD_BACKUP_PHASE15_2_20260513.md` | `AGENTS.md` | ARCHIVE ONLY | Backup authority must not be active. |

## Docs Already Absorbed Into V2

| CLEAN-era source | Absorbed by | Status |
|---|---|---|
| `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md` | `docs/governance/FILE_PLACEMENT_RULES.md` | Canonical already stronger. |
| `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md` | `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md` | Core ownership absorbed; optional review fields remain. |
| `docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md` | `docs/workflows/APPLY_ROUTING_CHAIN.md` | Useful state definitions promoted in Phase 5D; `merge-ready package` rejected. |
| `docs/AI_OS/operator_workflows/AIOS_SAFE_SESSION_RESUME_STANDARD.md` | `docs/workflows/SAFE_SESSION_RESUME.md` | Canonical already covers behavior. |
| `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md` | `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` | Allowed lanes and validation commands promoted in Phase 5D. |
| `docs/AI_OS/security/secure_access/AIOS_ACCESS_MODEL_OVERVIEW.md` | `docs/security/ACCESS_MODEL_OVERVIEW.md` | Likely absorbed; verify any remaining secure-access details before archive batch. |
| `docs/AI_OS/security/AIOS_PRIVACY_CREDENTIAL_EXCLUSION_CHECKLIST_DRAFT.md` | `docs/security/PRIVACY_CREDENTIAL_EXCLUSION_CHECKLIST.md` | Likely absorbed; compare before archive. |

## Docs Still Worth Mining

| Current path or area | Proposed canonical target | Classification | Why it is worth mining |
|---|---|---|---|
| `docs/AI_OS/system_wizards/05_RULES_AND_GUARDRAILS.md` | `AGENTS.md`, `docs/security/`, `docs/governance/` | MERGE INTO CANONICAL | Safety-critical guardrails may contain unpromoted constraints. |
| `docs/AI_OS/codex/AIOS_CODEX_ORCHESTRATION_PLAYBOOK.md` | `AGENTS.md`, `docs/workflows/` | MERGE INTO CANONICAL | May contain Codex-specific workflow constraints. |
| `docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md` | `docs/workflows/PARALLEL_CODEX_WORKFLOW.md` | MERGE INTO CANONICAL | Parallel worker details may still differ from canonical workflow. |
| `docs/AI_OS/operator/AIOS_APPLY_APPROVAL_WORKFLOW_DRAFT.md` | `docs/workflows/APPLY_ROUTING_CHAIN.md`, `docs/security/approval-model.md` | MERGE INTO CANONICAL | Approval safety is critical; mine exact gate rules only. |
| `docs/AI_OS/operator/AIOS_COMMIT_PUSH_WORKFLOW_DRAFT.md` | `docs/workflows/`, `AGENTS.md` | MERGE INTO CANONICAL | Commit/push is protected; mine only user-control safeguards. |
| `docs/AI_OS/operator/AIOS_FILE_OWNERSHIP_AND_COLLISION_PREVENTION.md` | `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md`, `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md` | MERGE INTO CANONICAL | May add lane ownership detail not yet canonical. |
| `docs/AI_OS/change_control/` | `docs/workflows/`, `docs/security/approval-model.md` | MERGE INTO CANONICAL | Change request, scope, commit package, UI/dashboard/trading boundaries are valuable. |
| `docs/AI_OS/problem_resolution/` | `docs/workflows/` | MERGE INTO CANONICAL | Repair flow, rollback, collision, validator routing may become a canonical repair workflow. |
| `docs/AI_OS/validators/` | `docs/workflows/`, `schemas/`, `tests/` | MERGE INTO CANONICAL | Validator naming/status/packet standards may support automation readiness. |
| `docs/AI_OS/operations/` | `docs/architecture/`, `docs/workflows/` | MERGE INTO CANONICAL | Queue, packet lifecycle, runtime control, merge order, observability docs may be operationally valuable. |
| `docs/AI_OS/agent_runtime/` | `docs/architecture/AGENT_RUNTIME_ARCHITECTURE.md` | MERGE INTO CANONICAL | Agent runtime schemas/state machine may align with architecture. |
| `docs/AI_OS/telemetry/` | `docs/security/`, `docs/specs/`, `docs/architecture/` | MERGE INTO CANONICAL | Local-only telemetry, retention, schema, replay, and privacy rules matter. |
| `docs/AI_OS/brokers/`, `docs/AI_OS/execution/`, `docs/AI_OS/risk_controls/`, `docs/AI_OS/trading/` | `docs/security/`, `docs/architecture/`, Trading Lab docs | MERGE INTO CANONICAL | Preserve no-live-trading, paper-only, broker boundary, and execution block rules. |
| `docs/AI_OS/product/AIOS_PRODUCT_PHILOSOPHY_AND_MVP_ARCHITECTURE.md` | `docs/roadmap/`, `docs/architecture/` | MERGE INTO CANONICAL | Contains clear V2 product framing and Trading Lab boundary language. |

## Archive-Only Candidates

| Current path or pattern | Classification | Reason |
|---|---|---|
| `docs/AI_OS/**/*_DRAFT.md` | ARCHIVE ONLY by default | Drafts are not active authority unless explicitly promoted. |
| `docs/AI_OS/**/*_DRY_RUN.md` | ARCHIVE ONLY | Historical DRY_RUN records, not live authority. |
| `docs/AI_OS/**/*_APPLY_*.md` | ARCHIVE ONLY | Historical apply records, not current authority. |
| `docs/AI_OS/**/*_2026-*.md` | ARCHIVE ONLY | Timestamped snapshots are historical. |
| `docs/AI_OS/audits/` | ARCHIVE ONLY | CLEAN-era audit records; V2 audit trail now lives in `docs/audits/`. |
| `docs/AI_OS/roadmap/` | ARCHIVE ONLY after product review | Old roadmap drafts should not steer current V2 unless promoted. |
| `docs/AI_OS/readiness/` | ARCHIVE ONLY | Readiness drafts are historical phase records. |
| `docs/AI_OS/production/` | ARCHIVE ONLY | Production-hardening draft material; not current runtime authority. |
| `docs/AI_OS/codex/AGENTS_MD_BACKUP_PHASE15_2_20260513.md` | ARCHIVE ONLY | Backup of active authority. |
| `docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md` | ARCHIVE ONLY | Absorbed into canonical workflow. |
| `docs/AI_OS/operator_workflows/AIOS_SAFE_SESSION_RESUME_STANDARD.md` | ARCHIVE ONLY | Absorbed into canonical workflow. |
| `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md` | ARCHIVE ONLY | Absorbed into canonical workflow. |
| `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md` | ARCHIVE ONLY | Canonical placement rules are stronger. |

## Remove/Relocate Candidates

These are not approved for deletion or movement. They are candidates for later cleanup manifests only.

| Current path or pattern | Classification | Reason |
|---|---|---|
| `docs/AI_OS/**/README_FOLDER_PURPOSE.txt` | REMOVE/RELOCATE CANDIDATE | Folder-organizer artifacts; not durable authority. |
| `docs/AI_OS/agent_runtime/*.json` | REMOVE/RELOCATE CANDIDATE | Looks like schema/state/runtime validation material mixed into docs. |
| `docs/AI_OS/multi_agent/*.json` | REMOVE/RELOCATE CANDIDATE | Structured agent matrices belong in schemas/specs if active. |
| `docs/AI_OS/problem_resolution/PROBLEM_TO_OWNER_MAP.json` | REMOVE/RELOCATE CANDIDATE | Could become schema/spec or archive depending on use. |
| `docs/AI_OS/change_control/*.json` | REMOVE/RELOCATE CANDIDATE | Structured ledgers/maps should not remain hidden authority in legacy docs. |
| `docs/AI_OS/analytics/*.json` | REMOVE/RELOCATE CANDIDATE | Fixture/schema drafts should move to specs/schemas or archive after validation. |
| `docs/AI_OS/tools/*.json` | REMOVE/RELOCATE CANDIDATE | Tool boundary matrix may belong in specs/governance if active. |

## User Decisions Needed

1. Should `docs/AI_OS/operator/AIOS_OPERATOR_PREFERENCES_AND_WORKFLOW_CANONICAL.md` be mined into `docs/workflows/OPERATOR_WORKFLOW.md`, or archived despite its `CANONICAL` name?
2. Should AI assistant role docs under `docs/AI_OS/agents/`, `docs/AI_OS/codex/`, `docs/AI_OS/claude/`, and `docs/AI_OS/llm/` collapse into `AGENTS.md`, or should V2 keep separate role docs?
3. Should Trading Lab methodology docs under `docs/AI_OS/product/`, `docs/AI_OS/trading/`, `docs/AI_OS/execution/`, and `docs/AI_OS/risk_controls/` become a canonical Trading Lab architecture/security pack?
4. Should telemetry schemas and privacy drafts under `docs/AI_OS/telemetry/` move toward `docs/specs/` and `docs/security/`, or remain archive-only until runtime telemetry stabilizes?
5. Should JSON files inside `docs/AI_OS/` be treated as historical fixtures, active schemas, or relocation candidates into `schemas/`?
6. Should `README_FOLDER_PURPOSE.txt` files be archived, removed, or regenerated later under a V2 folder-purpose standard?

## Recommended First Archive Batch

No archive action is approved by this file. If the user approves a future archive pass, start with files already absorbed and low-risk historical artifacts:

1. `docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md`
2. `docs/AI_OS/operator_workflows/AIOS_SAFE_SESSION_RESUME_STANDARD.md`
3. `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md`
4. `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md`
5. `docs/AI_OS/codex/AGENTS_MD_BACKUP_PHASE15_2_20260513.md`
6. Timestamped duplicate drafts such as `*_2026-*.md`
7. Historical `*_DRY_RUN.md` and `*_APPLY_*.md` records after confirming no active references.

Required validation before any archive move:

- Search references to each path.
- Confirm canonical target contains promoted content.
- Use `git mv` only after explicit approval.
- Run `git diff --check`.
- Run `git status --short --branch`.

## Protected Non-Actions

- No `docs/AI_OS/` files were edited.
- No canonical docs were edited by this classification.
- No files were moved, deleted, renamed, archived, staged, committed, or pushed.
- Runtime, orchestration, worker state, packet state, approval state, telemetry, dashboard source, Trading Lab, broker paths, launchers, archive, `.git`, `.codex_worktrees`, `node_modules`, and cache folders were not touched.
