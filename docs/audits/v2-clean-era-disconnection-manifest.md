# V2 CLEAN-Era Disconnection Manifest

## Executive summary

AI_OS_V2 has a usable modern repo spine, but active authority is still diluted by CLEAN-era source material, draft documents, generated state, and overlapping workflow/agent instructions.

This manifest is a planning layer only. It does not approve file moves, deletes, renames, rewrites, or mass replacement of CLEAN-era references. Its purpose is to classify the repo before any cleanup execution.

Recommended canonical V2 brain:

- `README.md` = human front door
- `AGENTS.md` = AI/tool behavior authority
- `docs/governance/` = repo rules, ownership, doctrine
- `docs/workflows/` = operator and development workflows
- `docs/security/` = access and safety boundaries
- `docs/architecture/` = system architecture
- `docs/audits/` = audit trail and cleanup decisions

`docs/AI_OS/` should be treated as CLEAN-era source material unless a specific file is explicitly promoted into the V2 authority map.

## What V2 currently uses as active authority

| Current path | Proposed V2 role | Classification | Reason | Risk level | Recommended action |
|---|---|---|---|---|---|
| `README.md` | Human front door and project overview | KEEP ACTIVE | Root project entry point | medium | Keep active; later refresh content after approval |
| `AGENTS.md` | AI/tool behavior authority | KEEP ACTIVE | Current Codex and agent operating rules live here | high | Keep as single active AI behavior source |
| `SECURITY.md` | Root security overview | KEEP ACTIVE | Standard repo security entry | medium | Keep active and align with `docs/security/` |
| `CHANGELOG.md` | Change history | KEEP ACTIVE | Standard repo history file | low | Keep active |
| `docs/governance/` | Repo rules, ownership, doctrine | KEEP ACTIVE | Matches target V2 structure | high | Promote as canonical governance area |
| `docs/workflows/` | Operator and development workflows | KEEP ACTIVE | Matches target V2 structure | high | Promote as canonical workflow area |
| `docs/security/` | Access and safety boundaries | KEEP ACTIVE | Matches target V2 structure | high | Promote as canonical security area |
| `docs/architecture/` | System architecture | KEEP ACTIVE | Matches target V2 structure | medium | Promote as canonical architecture area |
| `docs/audits/` | Audit records and cleanup decisions | KEEP ACTIVE | Correct place for cleanup trail | low | Keep active as history, not operating authority |
| `apps/` | User-facing applications | KEEP ACTIVE | Contains dashboard and Trading Lab app | high | Keep active |
| `services/` | Backend/runtime services | KEEP ACTIVE | Contains dispatcher, runtime, telemetry, policy services | high | Keep active |
| `scripts/` | Operator/developer helper scripts | KEEP ACTIVE | Contains control, runtime, telemetry, validation helpers | medium | Keep active; later de-duplicate with `automation/` |
| `automation/` | Orchestration and operator automation | KEEP ACTIVE | Contains active orchestration tooling and launchers | high | Keep active but classify subtrees before cleanup |
| `schemas/` | Validation/data contracts | KEEP ACTIVE | Contains orchestration schemas | medium | Keep active |
| `tests/` | Validation tests | KEEP ACTIVE | Contains Trading Lab paper-route tests | medium | Keep active |

## What `docs/AI_OS` appears to represent

`docs/AI_OS/` appears to be a large CLEAN-era knowledge base and working-document area. It includes drafts, source-of-truth maps, role definitions, context packs, operator workflows, trading boundaries, telemetry plans, governance matrices, and audit material.

Default V2 treatment:

| Current path | Proposed V2 role | Classification | Reason | Risk level | Recommended action |
|---|---|---|---|---|---|
| `docs/AI_OS/` | CLEAN-era source material | MERGE INTO CANONICAL | Contains useful source material but too many active-looking authorities | high | Freeze as source material until classified |
| `docs/AI_OS/context/` | Source material for governance/workflow docs | MERGE INTO CANONICAL | Contains source-of-truth and quickstart brain files | high | Extract current rules into canonical V2 docs |
| `docs/AI_OS/system_wizards/` | Source material for operator bootstrap | MERGE INTO CANONICAL | Contains start-here, current-state, checkpoint brain files | high | Merge selected rules, then mark archive-only |
| `docs/AI_OS/operator/` | Source material for `docs/workflows/` | MERGE INTO CANONICAL | Overlaps with active workflow authority | high | Merge current workflow rules into `docs/workflows/` |
| `docs/AI_OS/codex/` | Source material for `AGENTS.md` and governance | MERGE INTO CANONICAL | Overlaps with root AI/tool behavior authority | high | Extract only active Codex rules |
| `docs/AI_OS/claude/` | Source material for agent role policy | MERGE INTO CANONICAL | Useful only if Claude delegation remains active | medium | User decision before promotion |
| `docs/AI_OS/governance/` | Source material for `docs/governance/` | MERGE INTO CANONICAL | Duplicates governance authority | high | Promote selected current docs only |
| `docs/AI_OS/security/` | Source material for `docs/security/` | MERGE INTO CANONICAL | Duplicates security authority | high | Promote selected current docs only |
| `docs/AI_OS/**/*_DRAFT.md` | Historical draft material | ARCHIVE ONLY | Draft suffix means not active authority by default | medium | Archive after merge review |

## Likely active files and folders

| Current path | Proposed V2 role | Classification | Reason | Risk level | Recommended action |
|---|---|---|---|---|---|
| `apps/dashboard/` | Dashboard app | KEEP ACTIVE | User-facing control plane | high | Keep active; do not touch `apps/dashboard/assets/` without approval |
| `apps/trading_lab/` | Paper-only Trading Lab app | KEEP ACTIVE | First production vertical | high | Keep active; preserve no-live-trading boundary |
| `services/dispatcher/` | Dispatcher service code | KEEP ACTIVE | Runtime orchestration code | high | Keep active |
| `services/runtime/` | Runtime service code | KEEP ACTIVE | Runtime loop and automation execution code | high | Keep active |
| `services/telemetry/` | Telemetry service code | KEEP ACTIVE | Local telemetry/replay/readout code | medium | Keep active |
| `services/policy/` | Policy engine | KEEP ACTIVE | Safety/approval policy code | high | Keep active |
| `automation/orchestration/` | Main automation orchestration layer | KEEP ACTIVE | Contains validator chain, queue, workers, control loop | high | Keep active but reduce duplicates later |
| `automation/windows_workstation/` | Local workspace launcher layer | KEEP ACTIVE | OMEN/local workstation workflow support | medium | Keep active if still used |
| `automation/startup/` | Morning/startup automation | KEEP ACTIVE | Active startup workflow scripts | medium | Keep active pending workflow consolidation |
| `scripts/control/` | Runtime control commands | KEEP ACTIVE | Standard helper script location | medium | Keep active |
| `scripts/validation/` | Validation launcher scripts | KEEP ACTIVE | Clean-state validation launcher exists here | medium | Keep active |
| `schemas/aios/orchestration/` | Orchestration schemas | KEEP ACTIVE | Structured validation contracts | medium | Keep active |
| `tests/trader/` | Paper-route tests | KEEP ACTIVE | Validates paper-only trading behavior | high | Keep active |

## CLEAN-era source material

| Current path | Proposed V2 role | Classification | Reason | Risk level | Recommended action |
|---|---|---|---|---|---|
| `docs/AI_OS/agent_runtime/` | Source for agent runtime docs | MERGE INTO CANONICAL | Contains active-looking plans, status, schemas, and summaries | high | Split durable docs from generated/status files |
| `docs/AI_OS/agents/` | Source for agent role docs | MERGE INTO CANONICAL | Contains role drafts for ChatGPT, Codex, Claude, human operator | medium | Merge into a single agent role/governance doc |
| `docs/AI_OS/index/` | Source for source-of-truth and ownership maps | MERGE INTO CANONICAL | Overlaps with governance and this manifest | high | Extract into `docs/governance/` |
| `docs/AI_OS/operator_workflows/` | Source for workflow authority | MERGE INTO CANONICAL | Overlaps with `docs/workflows/` | high | Merge selected current workflows |
| `docs/AI_OS/change_control/` | Source for governance/workflow rules | MERGE INTO CANONICAL | Contains change boundaries and safe apply checklist | medium | Promote only current rules |
| `docs/AI_OS/reporting/` | Source for reporting standards | MERGE INTO CANONICAL | Overlaps root logs and audit requirements | medium | Merge into workflow/governance docs |
| `docs/AI_OS/telemetry/` | Source for telemetry docs | MERGE INTO CANONICAL | Useful for local telemetry roadmap | medium | Merge into `docs/architecture/` or `docs/specs/` |
| `docs/AI_OS/trading/` | Source for Trading Lab safety docs | MERGE INTO CANONICAL | Contains no-live-execution boundaries | high | Merge into `docs/security/` and Trading Lab docs |
| `docs/AI_OS/brokers/` | Broker boundary source docs | MERGE INTO CANONICAL | Contains OANDA/sandbox/no-live policy drafts | high | Preserve safety content; do not wire broker execution |

## Archive-only files and folders

| Current path | Proposed V2 role | Classification | Reason | Risk level | Recommended action |
|---|---|---|---|---|---|
| `docs/AI_OS/audits/` | Historical CLEAN-era audit material | ARCHIVE ONLY | Prior audit trail, not active authority | low | Keep as reference or move under archive after approval |
| `docs/audits/phase-*.md` | Historical cleanup records | ARCHIVE ONLY | Useful history, not live instructions | low | Keep in audits unless user wants archive split |
| `automation/operator/legacy_imports/` | Historical legacy script imports | ARCHIVE ONLY | Explicitly named legacy | medium | Archive after confirming no active launcher calls it |
| `internal/source-artifacts/` | Imported/source artifacts | ARCHIVE ONLY | Source material, not active repo authority | low | Archive after approval |
| `inputs/` | Imported source inputs | ARCHIVE ONLY | Looks like source/input material | low | Archive after approval |

## Generated/runtime/noise candidates

| Current path | Proposed V2 role | Classification | Reason | Risk level | Recommended action |
|---|---|---|---|---|---|
| `.pytest_cache/` | None | REMOVE/DELETE CANDIDATE AFTER APPROVAL | Test cache | low | Delete after approval |
| `apps/dashboard/node_modules/` | None | REMOVE/DELETE CANDIDATE AFTER APPROVAL | Installed dependencies | low | Delete after approval if package lock exists |
| `**/__pycache__/` | None | REMOVE/DELETE CANDIDATE AFTER APPROVAL | Python cache | low | Delete after approval |
| `approval.json` | Runtime state or archive evidence | REMOVE/DELETE CANDIDATE AFTER APPROVAL | Root runtime-like state | medium | Classify before removal |
| `completion_report.json` | Runtime state or archive evidence | REMOVE/DELETE CANDIDATE AFTER APPROVAL | Generated report-like file | medium | Classify before removal |
| `validation_result.json` | Runtime state or archive evidence | REMOVE/DELETE CANDIDATE AFTER APPROVAL | Generated validator result | medium | Classify before removal |
| `task_log.json` | Runtime state or telemetry evidence | REMOVE/DELETE CANDIDATE AFTER APPROVAL | Generated task state | medium | Classify before removal |
| `automation/orchestration/workers/*heartbeat.json` | Runtime state | REMOVE/DELETE CANDIDATE AFTER APPROVAL | Worker heartbeat artifacts | medium | Move to runtime state or delete after approval |
| `automation/operator/startup_reports/` | Audit evidence or generated state | REMOVE/DELETE CANDIDATE AFTER APPROVAL | Generated startup reports | low | Move to audit evidence or delete after approval |
| `apps/trading_lab/trading_lab/results/` | Test evidence or generated output | REMOVE/DELETE CANDIDATE AFTER APPROVAL | Paper signal output artifacts | medium | Archive as evidence or remove after approval |

## Brain files and folders

| Current path | Proposed V2 role | Classification | Reason | Risk level | Recommended action |
|---|---|---|---|---|---|
| `AGENTS.md` | Canonical active V2 AI/tool brain | KEEP ACTIVE | Root authority for Codex/agents | high | Keep as active authority |
| `README.md` | Canonical human entry point | KEEP ACTIVE | Root front door | medium | Keep active; later refresh |
| `docs/AI_OS/system_wizards/00_START_HERE_AI_OS_CONTEXT_PACK.md` | Source for `AGENTS.md` and workflows | MERGE INTO CANONICAL | Start-here brain duplicate | high | Merge current rules then archive |
| `docs/AI_OS/system_wizards/START_HERE_AI_OS_CONTEXT_PACK.md` | Source for `AGENTS.md` and workflows | MERGE INTO CANONICAL | Duplicate start-here brain | high | Compare with `00_` file before archive |
| `docs/AI_OS/system_wizards/01_CURRENT_STATE.md` | Audit/checkpoint source | MERGE INTO CANONICAL | Current-state brain duplicate | medium | Convert durable facts to audit/checkpoint |
| `docs/AI_OS/system_wizards/02_CHECKPOINT.md` | Audit/checkpoint source | MERGE INTO CANONICAL | Checkpoint brain duplicate | medium | Move durable state into audits after approval |
| `docs/AI_OS/context/AIOS_REPO_SOURCE_OF_TRUTH_MAP.md` | Source for V2 source-of-truth map | MERGE INTO CANONICAL | Duplicate source-of-truth map | high | Merge into `docs/governance/source-of-truth-map.md` |
| `docs/AI_OS/context/AIOS_OPERATOR_QUICKSTART.md` | Source for operator workflow | MERGE INTO CANONICAL | Quickstart overlaps `docs/workflows/` | medium | Merge into canonical workflow |
| `docs/AI_OS/context/AIOS_NEW_CHAT_BOOTSTRAP_SEQUENCE.md` | Source for session workflow | MERGE INTO CANONICAL | Bootstrap brain duplicate | medium | Merge into `docs/workflows/SAFE_SESSION_RESUME.md` |
| `docs/AI_OS/codex/AIOS_CODEX_ORCHESTRATION_PLAYBOOK.md` | Source for `AGENTS.md` or governance | MERGE INTO CANONICAL | Codex instruction duplicate | high | Extract current instructions only |
| `docs/AI_OS/codex/AGENTS_MD_BACKUP_PHASE15_2_20260513.md` | Historical backup | ARCHIVE ONLY | Backup of root authority | medium | Archive after confirming root `AGENTS.md` is current |
| `docs/AI_OS/claude/CLAUDE_DELEGATION_STANDARD.md` | Optional agent-role reference | NEEDS USER DECISION | May be active only if Claude workflow remains | medium | Decide whether Claude remains in V2 authority |
| `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` | Canonical workflow candidate | KEEP ACTIVE | Already in active V2 workflow folder | medium | Keep active pending consolidation |
| `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md` | Source for workflow doc | MERGE INTO CANONICAL | Duplicate worker lane rules | high | Compare and merge into `docs/workflows/` |
| `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md` | Canonical ownership map candidate | KEEP ACTIVE | Already in active governance folder | high | Keep active |
| `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md` | Source for ownership map | MERGE INTO CANONICAL | Duplicate ownership authority | high | Compare and merge into `docs/governance/` |

## User decision items

| Current path | Proposed V2 role | Classification | Reason | Risk level | Recommended action |
|---|---|---|---|---|---|
| `agent/` | `agents/` or archive | NEEDS USER DECISION | Target structure prefers `agents/`, but current path may be referenced | medium | Decide whether to keep, promote to `agents/`, or archive |
| `aios/modules/trader/` | Shared package or legacy Trading Lab source | NEEDS USER DECISION | Overlaps with `apps/trading_lab/trading_lab/` | high | Pick one canonical paper Trading Lab code path |
| `apps/trading_lab/trading_lab/` | Canonical Trading Lab package candidate | NEEDS USER DECISION | Active app package, but overlaps with `aios/modules/trader/` | high | Decide canonical Python package path |
| `automation/operator/` | Active operator layer or legacy experiments | NEEDS USER DECISION | Contains active-looking scripts and legacy subfolders | high | Classify launcher dependencies before cleanup |
| `automation/orchestration/Sync-AiOsMain.CLEANUP.ps1` | Cleanup helper or stale launcher | NEEDS USER DECISION | Name suggests cleanup operation | medium | Inspect content and decide whether it survives |
| `work_packets/` | Active queue data or examples only | NEEDS USER DECISION | Contains schemas, examples, approvals, state | medium | Decide active runtime location |
| `telemetry/work_ledger.jsonl` | Active ledger or generated state | NEEDS USER DECISION | Could be audit-critical telemetry | medium | Decide retention policy |
| `logs/`, `proof/`, `validation/`, `checkpoints/` | Evidence/runtime folders | NEEDS USER DECISION | May contain operator-critical evidence | medium | Decide what is active evidence versus generated noise |

## Known blockers

- `docs/AI_OS/` contains many active-looking instructions and drafts that duplicate V2 canonical areas.
- Root `README.md` appears stale and should not be trusted as fully current until refreshed.
- Multiple workflow layers exist: `docs/workflows/`, `docs/AI_OS/operator/`, `docs/AI_OS/operator_workflows/`, `automation/operator/`, and `automation/orchestration/`.
- Multiple worker registries and heartbeat/state files exist across automation folders.
- Trading Lab code appears in both `apps/trading_lab/trading_lab/` and `aios/modules/trader/`.
- Generated state appears at repo root and inside active automation folders.
- `archive/` is reference-only and was not inspected for cleanup execution.

## Safe disconnection order

1. Freeze authority: declare `AGENTS.md`, `README.md`, and canonical `docs/` folders as proposed active V2 authority.
2. Create and review source-of-truth map before editing old docs.
3. Classify `docs/AI_OS/` by topic: governance, workflows, security, architecture, runtime, trading, audit.
4. Merge only selected durable rules from `docs/AI_OS/` into canonical V2 docs.
5. After merge approval, mark duplicate CLEAN-era brain files archive-only.
6. Classify generated/runtime state separately from source docs.
7. Confirm canonical Trading Lab package path.
8. Confirm canonical automation path: `scripts/` for helpers, `automation/` for orchestration.
9. Create explicit move/delete manifests.
10. Execute only approved batches with validation.

## First safe edit batch proposal

No cleanup execution is approved by this manifest.

Recommended next batch after user approval:

1. Update `README.md` to reflect V2 project identity and current active spine.
2. Update `docs/governance/source-of-truth-map.md` after user decisions.
3. Create a `docs/audits/v2-docs-ai-os-classification-table.md` listing every `docs/AI_OS/` file by classification.
4. Create a `docs/audits/v2-generated-state-candidate-manifest.md` listing generated/runtime files before deletion approval.
5. Run `git diff --check` after edits.

## Explicit list of things not touched

- No files moved.
- No files deleted.
- No files renamed.
- No launchers changed.
- No runtime code changed.
- No trading logic changed.
- No broker config touched.
- No secrets, keys, credentials, or private tokens touched.
- No GitHub workflow files touched.
- No `.git/` content touched.
- No `.codex_worktrees/` content touched.
- No `archive/` content moved or edited.
- No `node_modules/` content touched.
- No `__pycache__/` content touched.
- No commit created.
- No push performed.
