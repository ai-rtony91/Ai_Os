# Phase 5A docs/AI_OS Pick-and-Pull Plan

## 1. Executive summary

`docs/AI_OS/` is CLEAN-era source material, not active V2 authority by default.

The folder contains high-value safety, workflow, governance, security, and architecture material, but it also contains duplicate brains, historical drafts, phase-specific plans, source-of-truth duplicates, current-state/checkpoint files, and generated-looking status/audit material.

Phase 5A does not move, delete, rename, or rewrite any `docs/AI_OS/` files. It defines what should be extracted into active V2 authority and what should remain reference-only until approved.

Canonical V2 targets:

- `README.md`
- `AGENTS.md`
- `docs/governance/`
- `docs/workflows/`
- `docs/security/`
- `docs/architecture/`
- `docs/audits/`

## 2. docs/AI_OS structure overview

High-density zones observed:

| Current path | Proposed V2 role | Classification | Reason | Risk level | Recommended action |
|---|---|---|---|---|---|
| `docs/AI_OS/agent_runtime/` | Source for runtime/agent architecture | MERGE INTO CANONICAL | 24 files; likely useful but mixed plans/status/schema docs | high | Extract durable architecture into `docs/architecture/`; classify status/schema files separately |
| `docs/AI_OS/operator/` | Source for workflow authority | MERGE INTO CANONICAL | 23 files; overlaps `docs/workflows/` | high | Compare against canonical workflows before archive proposal |
| `docs/AI_OS/governance/` | Source for governance authority | MERGE INTO CANONICAL | 22 files; overlaps `docs/governance/` | high | Extract only current rules into governance docs |
| `docs/AI_OS/audits/` | Historical audit/reference material | ARCHIVE ONLY | Prior audit outputs, not current authority | low | Keep as reference unless a summary is needed |
| `docs/AI_OS/telemetry/` | Source for telemetry doctrine/specs | MERGE INTO CANONICAL | Contains telemetry contracts/roadmaps | medium | Extract selected durable rules to `docs/architecture/` or `docs/specs/` |
| `docs/AI_OS/roadmap/` | Historical roadmap source | ARCHIVE ONLY | Phase/dated roadmap material | low | Reference only unless current roadmap gaps exist |
| `docs/AI_OS/llm/` | Source for assistant boundaries | MERGE INTO CANONICAL | Contains AI assistant/input/output boundaries | medium | Extract safety boundaries to `AGENTS.md` or `docs/security/` if still current |
| `docs/AI_OS/change_control/` | Source for governance/workflows | MERGE INTO CANONICAL | Contains commit/change boundaries | medium | Merge selected rules into governance/workflow docs |
| `docs/AI_OS/security/` and subfolders | Source for security authority | MERGE INTO CANONICAL | Access/credential docs may still matter | high | Extract into `docs/security/` after dependency review |
| `docs/AI_OS/system_wizards/` | Duplicate brain/source context | MERGE INTO CANONICAL | Start-here/current-state/checkpoint stack | high | Extract only durable current rules, then mark source reference-only |

## 3. Major duplicate-brain zones

| Current path | Proposed V2 role | Classification | Reason | Risk level | Recommended action |
|---|---|---|---|---|---|
| `docs/AI_OS/system_wizards/00_START_HERE_AI_OS_CONTEXT_PACK.md` | Source for `AGENTS.md` and `docs/workflows/` | MERGE INTO CANONICAL | Start-here brain duplicates active rules | high | Compare with root `AGENTS.md`; extract only missing durable rules |
| `docs/AI_OS/system_wizards/START_HERE_AI_OS_CONTEXT_PACK.md` | Source comparison only | MERGE INTO CANONICAL | Duplicate start-here file | high | Diff against `00_START_HERE...`; keep only unique current content |
| `docs/AI_OS/system_wizards/01_CURRENT_STATE.md` | Audit/checkpoint source | MERGE INTO CANONICAL | Current-state file can masquerade as active truth | medium | Extract durable facts into `docs/audits/`; do not keep active |
| `docs/AI_OS/system_wizards/02_CHECKPOINT.md` | Audit/checkpoint source | MERGE INTO CANONICAL | Checkpoint context may be stale | medium | Compare with `proof/` and `checkpoints/` before any archive proposal |
| `docs/AI_OS/context/AIOS_REPO_SOURCE_OF_TRUTH_MAP.md` | Source for `docs/governance/source-of-truth-map.md` | MERGE INTO CANONICAL | Duplicate authority map | high | Merge verified facts only |
| `docs/AI_OS/context/AIOS_OPERATOR_QUICKSTART.md` | Source for `docs/workflows/OPERATOR_WORKFLOW.md` | MERGE INTO CANONICAL | Operator quickstart duplicate | medium | Extract current operator steps only |
| `docs/AI_OS/context/AIOS_NEW_CHAT_BOOTSTRAP_SEQUENCE.md` | Source for resume/bootstrap workflow | MERGE INTO CANONICAL | Bootstrap instructions duplicate active workflow | medium | Extract only if still used |
| `docs/AI_OS/operator/AIOS_OPERATOR_PREFERENCES_AND_WORKFLOW_CANONICAL.md` | Source for `docs/workflows/OPERATOR_WORKFLOW.md` | MERGE INTO CANONICAL | Name says canonical but path is not V2 canonical | high | Compare with active workflow docs |
| `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md` | Source for `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` | MERGE INTO CANONICAL | Duplicate worker lane authority | high | Certify canonical workflow file before retiring source |
| `docs/AI_OS/codex/AIOS_CODEX_ORCHESTRATION_PLAYBOOK.md` | Source for `AGENTS.md` | MERGE INTO CANONICAL | Duplicate Codex instruction stack | high | Extract only missing active behavior rules |
| `docs/AI_OS/codex/AGENTS_MD_BACKUP_PHASE15_2_20260513.md` | Historical backup | ARCHIVE ONLY | Backup must not act as current authority | medium | Keep reference-only after root `AGENTS.md` review |

## 4. High-value source-material docs worth extracting

| Current path | Proposed V2 role | Classification | Reason | Risk level | Recommended action |
|---|---|---|---|---|---|
| `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md` | `docs/governance/FILE_PLACEMENT_RULES.md` | MERGE INTO CANONICAL | Core file-placement rules already source-attributed by canonical doc | high | Compare and certify canonical copy |
| `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md` | `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md` | MERGE INTO CANONICAL | Core ownership map already source-attributed by canonical doc | high | Compare and certify canonical copy |
| `docs/AI_OS/governance/AIOS_APPROVAL_REQUIRED_MATRIX_DRAFT.md` | `docs/governance/` or `docs/security/` | MERGE INTO CANONICAL | Approval boundaries are safety-critical | high | Extract stable approval rules |
| `docs/AI_OS/governance/AIOS_BLOCKED_ACTION_MATRIX_DRAFT.md` | `AGENTS.md` and `docs/security/` | MERGE INTO CANONICAL | Blocked actions protect runtime/trading safety | high | Extract current blocked action rules |
| `docs/AI_OS/governance/AIOS_DESTRUCTIVE_ACTION_BLOCK_MATRIX_DRAFT.md` | `AGENTS.md` and `docs/governance/` | MERGE INTO CANONICAL | Destructive-action policy is core governance | high | Extract current destructive-action rules |
| `docs/AI_OS/governance/AIOS_SECRET_HANDLING_MATRIX_DRAFT.md` | `docs/security/` | MERGE INTO CANONICAL | Secret-handling rules are important | high | Extract into security docs if not already covered |
| `docs/AI_OS/security/AIOS_PRIVACY_CREDENTIAL_EXCLUSION_CHECKLIST_DRAFT.md` | `docs/security/PRIVACY_CREDENTIAL_EXCLUSION_CHECKLIST.md` | MERGE INTO CANONICAL | Credential exclusion is active safety concern | high | Compare with canonical security checklist |
| `docs/AI_OS/security/secure_access/AIOS_ACCESS_MODEL_OVERVIEW.md` | `docs/security/ACCESS_MODEL_OVERVIEW.md` | MERGE INTO CANONICAL | Access model may be current source | medium | Compare and extract stable access rules |
| `docs/AI_OS/trading/AIOS_EXECUTION_BLOCKING_CONTRACT_DRAFT.md` | `docs/security/` and Trading Lab docs | MERGE INTO CANONICAL | No-live-execution boundary is critical | high | Preserve blocked live execution rules |
| `docs/AI_OS/risk_controls/AIOS_BLOCKED_LIVE_EXECUTION_RULES_DRAFT.md` | `docs/security/` and Trading Lab docs | MERGE INTO CANONICAL | Trading safety boundary | high | Extract into canonical safety docs |
| `docs/AI_OS/brokers/oanda/OANDA_NO_LIVE_EXECUTION_RULES_DRAFT.md` | `docs/security/` reference section | MERGE INTO CANONICAL | Broker/no-live boundary | high | Extract safety boundary without enabling broker integration |
| `docs/AI_OS/architecture/SYSTEM_LEVEL_AI_WIZARDS.md` | `docs/architecture/` | MERGE INTO CANONICAL | Architecture source material | medium | Extract durable architecture only |
| `docs/AI_OS/operations/RUNTIME_CONTROL_RUNBOOK.md` | `docs/workflows/` or `docs/architecture/` | MERGE INTO CANONICAL | May document active runtime controls | high | Validate against `scripts/control/` before merge |
| `docs/AI_OS/reporting/AIOS_REPORTING_AND_CHECKPOINT_STANDARD.md` | `docs/workflows/` | MERGE INTO CANONICAL | Reporting/checkpoint standard may still matter | medium | Extract into workflow/reporting guidance |

## 5. Docs likely safe as archive-only

| Current path | Proposed V2 role | Classification | Reason | Risk level | Recommended action |
|---|---|---|---|---|---|
| `docs/AI_OS/audits/` | Historical reference | ARCHIVE ONLY | Prior audit artifacts, not active authority | low | Keep reference-only |
| `docs/AI_OS/roadmap/AIOS_MASTER_STRATEGIC_ORDER_ROADMAP_*` | Historical roadmap reference | ARCHIVE ONLY | Dated/phase-specific roadmap outputs | low | Keep reference-only |
| `docs/AI_OS/codex/AGENTS_MD_BACKUP_PHASE15_2_20260513.md` | Historical backup | ARCHIVE ONLY | Backup copy should not govern current behavior | medium | Mark reference-only after `AGENTS.md` confirmation |
| `docs/AI_OS/mobile/*_2026-05-07_153925.md` | Historical duplicate snapshot | ARCHIVE ONLY | Timestamped duplicates | low | Reference only |
| `docs/AI_OS/broker_adapters/*_2026-05-07_153925.md` | Historical duplicate snapshot | ARCHIVE ONLY | Timestamped duplicates | low | Reference only |
| `docs/AI_OS/brokers/oanda/*_2026-05-07_153925.md` | Historical duplicate snapshot | ARCHIVE ONLY | Timestamped duplicates | low | Reference only after non-dated safety docs are reviewed |
| `docs/AI_OS/productization/*_DRAFT.md` | Productization source/reference | ARCHIVE ONLY | Not current runtime authority | low | Reference only unless productization resumes |
| `docs/AI_OS/legal/*PLACEHOLDER_DRAFT.md` | Placeholder legal docs | ARCHIVE ONLY | Placeholder content should not be active authority | medium | User decision before any legal promotion |

## 6. Docs that appear stale/draft/generated

| Current path | Proposed V2 role | Classification | Reason | Risk level | Recommended action |
|---|---|---|---|---|---|
| `docs/AI_OS/**/*_DRAFT.md` | Reference/source material | ARCHIVE ONLY | 232 draft-style markdown files observed | medium | Do not treat as active unless explicitly promoted |
| `docs/AI_OS/**/*_DRY_RUN.md` | Audit/source material | ARCHIVE ONLY | Dry-run docs are evidence/planning, not authority | low | Reference only |
| `docs/AI_OS/*FIXTURE_DRAFT.json` | Fixture/source material | REMOVE/RELOCATE CANDIDATE | Generated-looking fixtures should not live in authority docs | medium | Classify later; do not move in Phase 5A |
| `docs/AI_OS/agent_runtime/*STATUS*.json` | Runtime/status source material | REMOVE/RELOCATE CANDIDATE | Status JSON is not authority | medium | Validate before relocation |
| `docs/AI_OS/analytics/*VARIANTS_DRAFT.json` | Draft fixture/source material | REMOVE/RELOCATE CANDIDATE | Generated-looking JSON fixture | low | Classify later |
| `docs/AI_OS/index/*VALIDATION_DRAFT.md` | Historical validation/index source | ARCHIVE ONLY | Validation drafts should not be active maps | low | Reference only |

## 7. Docs requiring dependency validation before relocation

| Current path | Proposed V2 role | Classification | Reason | Risk level | Recommended action |
|---|---|---|---|---|---|
| `docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md` | Source for `docs/workflows/PARALLEL_CODEX_WORKFLOW.md` | MERGE INTO CANONICAL | Canonical doc currently source-attributed to this file | high | Compare and replace source attribution before archive proposal |
| `docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md` | Source for `docs/workflows/APPLY_ROUTING_CHAIN.md` | MERGE INTO CANONICAL | Canonical doc currently source-attributed to this file | high | Compare and certify canonical copy |
| `docs/AI_OS/operator_workflows/AIOS_SAFE_SESSION_RESUME_STANDARD.md` | Source for `docs/workflows/SAFE_SESSION_RESUME.md` | MERGE INTO CANONICAL | Canonical doc currently source-attributed to this file | high | Compare and certify canonical copy |
| `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md` | Source for `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` | MERGE INTO CANONICAL | Canonical doc currently source-attributed to this file | high | Compare and certify canonical copy |
| `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md` | Source for `docs/governance/FILE_PLACEMENT_RULES.md` | MERGE INTO CANONICAL | Canonical doc currently source-attributed to this file | high | Compare and certify canonical copy |
| `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md` | Source for `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md` | MERGE INTO CANONICAL | Canonical doc currently source-attributed to this file | high | Compare and certify canonical copy |
| `docs/AI_OS/operations/RUNTIME_CONTROL_RUNBOOK.md` | Source for runtime workflow docs | NEEDS USER DECISION | May refer to active runtime paths | high | Validate against `scripts/control/` |
| `docs/AI_OS/operations/MAIN_CONTROL_OPERATING_MODEL.md` | Source for operator/control docs | NEEDS USER DECISION | May describe active control loop | high | Validate against `aios.ps1` and orchestration scripts |
| `docs/AI_OS/interface/WINDOWS_TERMINAL_PROFILES_DRAFT.md` | Source for workstation docs | NEEDS USER DECISION | Root launcher prints this path as reference | medium | Validate whether still used before archive proposal |

## 8. Recommended canonical merge targets

| Current path | Proposed V2 role | Classification | Reason | Risk level | Recommended action |
|---|---|---|---|---|---|
| `docs/AI_OS/codex/AIOS_CODEX_ORCHESTRATION_PLAYBOOK.md` | `AGENTS.md` | MERGE INTO CANONICAL | AI/tool behavior belongs in root agent authority | high | Extract missing current rules only |
| `docs/AI_OS/agents/*ROLE_DRAFT.md` | `AGENTS.md` or `docs/governance/agent-roles.md` | MERGE INTO CANONICAL | Role definitions duplicate AI/tool authority | medium | Merge only if roles remain active |
| `docs/AI_OS/operator/*WORKFLOW*.md` | `docs/workflows/` | MERGE INTO CANONICAL | Operator workflow authority belongs in canonical workflows | high | Merge deltas only |
| `docs/AI_OS/operator_workflows/*.md` | `docs/workflows/` | MERGE INTO CANONICAL | Workflow duplicates | high | Merge deltas only |
| `docs/AI_OS/governance/*.md` | `docs/governance/` | MERGE INTO CANONICAL | Governance belongs in canonical governance | high | Merge stable rules only |
| `docs/AI_OS/security/**/*.md` | `docs/security/` | MERGE INTO CANONICAL | Security/access docs belong in canonical security | high | Merge current rules; do not expose secrets |
| `docs/AI_OS/trading/*.md` | `docs/security/` and Trading Lab docs | MERGE INTO CANONICAL | Trading safety boundaries must be preserved | high | Merge no-live-execution rules |
| `docs/AI_OS/architecture/SYSTEM_LEVEL_AI_WIZARDS.md` | `docs/architecture/` | MERGE INTO CANONICAL | Architecture belongs in canonical architecture | medium | Merge durable architecture only |
| `docs/AI_OS/reporting/AIOS_REPORTING_AND_CHECKPOINT_STANDARD.md` | `docs/workflows/` | MERGE INTO CANONICAL | Reporting/checkpoint workflow belongs in workflows | medium | Merge reporting rules |

## 9. Recommended archive targets

| Current path | Proposed V2 role | Classification | Reason | Risk level | Recommended action |
|---|---|---|---|---|---|
| `docs/AI_OS/audits/` | Historical reference | ARCHIVE ONLY | Audit records should not act as current instructions | low | Keep reference-only |
| `docs/AI_OS/roadmap/` | Historical roadmap reference | ARCHIVE ONLY | Most files are dated/phase planning | low | Keep reference-only unless user resumes old roadmap |
| `docs/AI_OS/legal/` | Placeholder/reference | ARCHIVE ONLY | Placeholder legal docs should not be active | medium | User review required before any legal use |
| `docs/AI_OS/monetization/` | Product reference | ARCHIVE ONLY | Not active runtime/governance | low | Reference only |
| `docs/AI_OS/mobile/` | Product/mobile reference | ARCHIVE ONLY | Not active V2 authority | low | Reference only |
| `docs/AI_OS/productization/` | Productization reference | ARCHIVE ONLY | Not current active authority | low | Reference only |
| `docs/AI_OS/production/` | Historical production-hardening reference | ARCHIVE ONLY | Could be aspirational, not active runtime | medium | Reference only unless production work resumes |

## 10. User decision conflicts

| Current path | Proposed V2 role | Classification | Reason | Risk level | Recommended action |
|---|---|---|---|---|---|
| `docs/AI_OS/claude/CLAUDE_DELEGATION_STANDARD.md` | `AGENTS.md` or archive/reference | NEEDS USER DECISION | Claude workflow may or may not remain active | medium | User decides whether Claude role survives |
| `docs/AI_OS/llm/AI_OS_ASSISTANT_CONSOLE_BACKEND_PLAN.md` | Architecture or archive/reference | NEEDS USER DECISION | Assistant backend may be future product, not current authority | medium | User decides if active roadmap item |
| `docs/AI_OS/secrets/` | `docs/security/` or archive/reference | NEEDS USER DECISION | Security-sensitive topic; must avoid secrets | high | Inspect carefully before promotion |
| `docs/AI_OS/interface/WINDOWS_TERMINAL_PROFILES_DRAFT.md` | Workstation workflow or archive/reference | NEEDS USER DECISION | Referenced by `aios.ps1` layout text | medium | Decide if workstation profiles remain active |
| `docs/AI_OS/operations/` | `docs/workflows/` or `docs/architecture/` | NEEDS USER DECISION | Some files may map to active runtime controls | high | Validate against runtime scripts before extraction |
| `docs/AI_OS/signal_intelligence/AIOS_SIGNAL_INTELLIGENCE_SOURCE_OF_TRUTH.md` | Trading Lab docs or archive/reference | NEEDS USER DECISION | Name says source of truth, but target path is not canonical | high | Decide if signal intelligence is active V2 scope |
| `docs/AI_OS/product/AIOS_TRADING_LAB_METHODOLOGY_AND_EXECUTION_ROADMAP.md` | Trading Lab roadmap or archive/reference | NEEDS USER DECISION | May affect Trading Lab direction | medium | User decides if current |

## 11. First safe extraction batch

Recommended first extraction batch is comparison/certification only, not movement:

| Current path | Proposed V2 role | Classification | Reason | Risk level | Recommended action |
|---|---|---|---|---|---|
| `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md` | Certify `docs/governance/FILE_PLACEMENT_RULES.md` | MERGE INTO CANONICAL | Canonical doc already exists and cites this source | high | Compare, add certification note to audit only |
| `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md` | Certify `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md` | MERGE INTO CANONICAL | Canonical doc already exists and cites this source | high | Compare, add certification note to audit only |
| `docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md` | Certify `docs/workflows/APPLY_ROUTING_CHAIN.md` | MERGE INTO CANONICAL | Canonical doc already exists and cites this source | high | Compare before source retirement |
| `docs/AI_OS/operator_workflows/AIOS_SAFE_SESSION_RESUME_STANDARD.md` | Certify `docs/workflows/SAFE_SESSION_RESUME.md` | MERGE INTO CANONICAL | Canonical doc already exists and cites this source | high | Compare before source retirement |
| `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md` | Certify `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` | MERGE INTO CANONICAL | Canonical doc already exists and cites this source | high | Compare before source retirement |

First safe edit batch after approval:

1. Create a comparison audit for the five files above.
2. Do not edit the source files.
3. If canonical files already fully contain the source rules, mark source files archive-ready in an audit.
4. If canonical files are missing current safety rules, propose a narrow canonical-doc merge.

## 12. Explicitly untouched systems

The Phase 5A plan does not touch:

- runtime code
- orchestration code
- worker registry/state
- packet state
- approvals
- telemetry
- dashboard source
- Trading Lab source/results
- `aios/modules/trader/`
- launchers
- services
- `scripts/control/`
- `docs/AI_OS/` source files
- `archive/`
- `.git/`
- `.codex_worktrees/`
- `node_modules/`

No commit or push is part of this phase.
