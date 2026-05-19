# Phase 3 Dependency Validation

## Purpose

Phase 3 validates references before any relocation, archive, rename, delete, or canonical merge.

No files were moved, deleted, renamed, archived, or rewritten during this validation.

## Validation method

Active areas searched:

- root files
- `docs/`
- `automation/`
- `scripts/`
- `services/`
- `apps/`
- `aios/`
- `tests/`
- `telemetry/`
- `proof/`
- `validation/`

Excluded by rule:

- `.git/`
- `.codex_worktrees/`
- `archive/`
- `node_modules/`
- `__pycache__/`

## Runtime dependency validation

| Candidate | Observed references | Connected systems | Runtime risk | Validation status | Relocation readiness | Recommendation |
|---|---:|---|---|---|---|---|
| `telemetry/runtime/runtime_state.json` | 5+ | `scripts/control/Get-AiOsRuntimeStatus.ps1`, `scripts/control/Get-AiOsRuntimeHealth.ps1`, `services/runtime/runtimeStateStore.js`, `services/orchestrator/runtimeApiService.js`, path registry docs | high | dependency-unsafe | BLOCKED | Keep current |
| `telemetry/runtime/runtime_heartbeat.json` | 5+ | runtime status, runtime health, runtime state store, orchestrator API, runtime runbooks | high | dependency-unsafe | BLOCKED | Keep current |
| `telemetry/runtime/runtime_process.json` | 3+ | runtime start/stop/status control scripts | high | dependency-unsafe | BLOCKED | Keep current |
| `telemetry/work_ledger.jsonl` | 5+ | telemetry writer, telemetry replay, automation audit replay, orchestrator API, runtime health | high | dependency-unsafe | BLOCKED | Keep current |
| `automation/orchestration/work_packets/active/` | 5+ | packet advancement, self-heal, queue display, worker routing, status displays | high | dependency-unsafe | BLOCKED | Keep current |
| `automation/orchestration/work_packets/blocked/` | 3+ | self-heal, packet lifecycle, queue state | high | dependency-unsafe | BLOCKED | Keep current |
| `automation/orchestration/work_packets/complete/` | 3+ | packet lifecycle, evidence, state display | medium | dependency-unsafe | BLOCKED | Keep current until retention policy exists |
| `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json` | 5+ | approval display, approval gate, orchestration README, supervisor examples | high | dependency-unsafe | BLOCKED | Keep current |
| `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json` | 2+ | apply approval gate and approval inbox flow | high | dependency-unsafe | BLOCKED | Keep current |
| `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json` | 25+ | worker router, builder, launcher, address book, sync, status scripts, docs | high | dependency-unsafe | BLOCKED | Keep current |
| `automation/orchestration/workers/AIOS_WORKER_PROFILES.json` | 8+ | packet routing, worker resolution, bootstrap checks, docs | high | dependency-unsafe | BLOCKED | Keep current |
| `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json` | 5+ | inbox display, add item, safe execute, completion, task state | high | dependency-unsafe | BLOCKED | Keep current |

## Generated state validation

| Candidate | Observed references | Connected systems | Runtime risk | Validation status | Relocation readiness | Recommendation |
|---|---:|---|---|---|---|---|
| `automation/orchestration/workers/*heartbeat.json` | 7+ | `scripts/write-worker-heartbeat.ps1`, `scripts/heartbeat-loop.ps1`, `scripts/show-worker-status.ps1`, `scripts/detect-stale-workers.ps1`, `scripts/mark-worker-offline.ps1`, orchestration concepts/docs | medium | dependency-unsafe | BLOCKED | Do not relocate until worker heartbeat owner is redesigned |
| `automation/orchestration/runtime/logs/supervisor_cycles.jsonl` | 1 active writer | `automation/orchestration/runtime/Start-AiOsPersistentRuntimeSupervisor.ps1` | medium | dependency-unsafe | BLOCKED | Keep until writer path is changed by approved runtime patch |
| `telemetry/runtime/runtime_stdout.log` | 1 active writer + docs | `scripts/control/Start-AiOsRuntime.ps1`, runtime docs | medium | dependency-unsafe | BLOCKED | Keep current |
| `telemetry/runtime/runtime_stderr.log` | 1 active writer + docs | `scripts/control/Start-AiOsRuntime.ps1`, runtime docs | medium | dependency-unsafe | BLOCKED | Keep current |
| `approval.json` | no active non-audit reference found | root generated-state candidate | medium | JSON_OK, dependency-safe from scan | NEEDS VALIDATION | User decision: retain as evidence, relocate, or remove after approval |
| `completion_report.json` | no active non-audit reference found | root generated report candidate | medium | JSON_OK, dependency-safe from scan | NEEDS VALIDATION | User decision: retain as evidence, relocate, or remove after approval |
| `validation_result.json` | no active non-audit reference found | root validation output candidate | medium | JSON_OK, dependency-safe from scan | NEEDS VALIDATION | User decision: retain as evidence, relocate, or remove after approval |
| `task_log.json` | referenced by existing audit as root tracked entry only | root task-state candidate | medium | JSON_OK, no active reader found | NEEDS VALIDATION | User decision: retain as evidence, relocate, or remove after approval |
| `apps/trading_lab/trading_lab/results/` | 10+ | Trading Lab runner, Trading Lab validators, dashboard mock data, replay outputs | high | dependency-unsafe | BLOCKED | Do not relocate until Trading Lab result path adapter is approved |
| `automation/operator/startup_reports/` | 1 active writer | `automation/operator/Start-AIOSGovernedWorkerLauncher.ps1` | medium | dependency-unsafe | BLOCKED | Keep current until launcher output path is approved |
| `automation/operator/layout_profiles/CODEX_CAPTURED_CURRENT.json` | 1 active writer + file itself | `automation/operator/Capture-AIOSCodexWindowLayout.ps1` | low | dependency-unsafe | BLOCKED | Keep current until layout capture policy is approved |
| `.pytest_cache/` | no active reference required | pytest cache | low | dependency-safe | SAFE | Delete candidate after explicit approval only |
| `apps/dashboard/node_modules/` | dependency install folder | dashboard local dependencies | low | dependency-safe if lockfile is retained | SAFE | Delete candidate after explicit approval only |
| `**/__pycache__/` | Python cache | Python runtime cache | low | dependency-safe | SAFE | Delete candidate after explicit approval only |

## Duplicate brain dependency validation

| Candidate | Observed references | Connected systems | Authority risk | Validation status | Relocation readiness | Recommendation |
|---|---:|---|---|---|---|---|
| `docs/AI_OS/system_wizards/00_START_HERE_AI_OS_CONTEXT_PACK.md` | source file plus Phase 2/3 planning refs | operator/agent context | high | duplicate authority | NEEDS VALIDATION | Compare against `AGENTS.md` and workflows before archive proposal |
| `docs/AI_OS/system_wizards/START_HERE_AI_OS_CONTEXT_PACK.md` | source file plus planning refs | operator/agent context | high | duplicate authority | NEEDS VALIDATION | Diff against `00_` version |
| `docs/AI_OS/system_wizards/01_CURRENT_STATE.md` | source file plus planning refs | session/current-state context | medium | likely historical | NEEDS VALIDATION | Convert durable facts to audit if needed |
| `docs/AI_OS/system_wizards/02_CHECKPOINT.md` | source file plus planning refs | checkpoint context | medium | likely historical | NEEDS VALIDATION | Compare with `checkpoints/` and `proof/` |
| `docs/AI_OS/system_wizards/03_ARCHITECTURE_LOCK.md` | source file plus planning refs | architecture context | medium | duplicate authority | NEEDS VALIDATION | Compare with `docs/architecture/` |
| `docs/AI_OS/system_wizards/04_AGENT_ROLES.md` | source file plus planning refs | agent role context | medium | duplicate authority | NEEDS VALIDATION | Compare with `AGENTS.md` |
| `docs/AI_OS/system_wizards/05_RULES_AND_GUARDRAILS.md` | source file plus planning refs | safety context | high | duplicate safety authority | NEEDS VALIDATION | Compare with `AGENTS.md`, `RISK_POLICY.md`, `docs/security/` |
| `docs/AI_OS/system_wizards/06_PROJECT_PATHS.md` | source file plus planning refs | path context | high | stale path risk | NEEDS VALIDATION | Validate every path before retaining |
| `docs/AI_OS/system_wizards/07_DAILY_REPORT_PROMPT.md` | source file plus planning refs | reporting prompt | low | likely historical | NEEDS VALIDATION | Compare with active reporting rules |
| `docs/AI_OS/context/AIOS_REPO_SOURCE_OF_TRUTH_MAP.md` | 4+ | prior source-of-truth map, current planning maps | high | duplicate authority | NEEDS VALIDATION | Merge verified facts only into `docs/governance/source-of-truth-map.md` |
| `docs/AI_OS/context/AIOS_OPERATOR_QUICKSTART.md` | source file plus planning refs | operator quickstart | medium | duplicate authority | NEEDS VALIDATION | Compare with `docs/workflows/OPERATOR_WORKFLOW.md` |
| `docs/AI_OS/context/AIOS_NEW_CHAT_BOOTSTRAP_SEQUENCE.md` | source file references Codex playbook and operator preferences | chat bootstrap context | medium | duplicate authority | NEEDS VALIDATION | Treat as historical unless user keeps new-chat bootstrap workflow |
| `docs/AI_OS/context/AIOS_MINIMAL_RECOVERY_CONTEXT_PACKET.md` | references operator preferences and Codex playbook | recovery context | medium | duplicate authority | NEEDS VALIDATION | Merge only active recovery facts |
| `docs/AI_OS/context/AIOS_PROJECT_ASSUMPTIONS_AND_DEFAULTS.md` | source file plus planning refs | assumptions/defaults | medium | stale assumption risk | NEEDS VALIDATION | Verify or label UNKNOWN |
| `docs/AI_OS/context/AIOS_CHATGPT_MEMORY_EXTERNALIZATION.md` | source file plus planning refs | memory/process doc | low | process-specific | NEEDS VALIDATION | User decision |
| `docs/AI_OS/operator/AIOS_OPERATOR_PREFERENCES_AND_WORKFLOW_CANONICAL.md` | referenced by context docs and prior audits | operator workflow | high | duplicate authority | NEEDS VALIDATION | Merge only deltas into `docs/workflows/OPERATOR_WORKFLOW.md` |
| `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md` | referenced by `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md`, audits, operations index | worker lane rules | high | source dependency | NEEDS VALIDATION | Do not archive until source attribution is replaced or accepted |
| `docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md` | referenced by `docs/workflows/PARALLEL_CODEX_WORKFLOW.md` and audits | parallel workflow | high | source dependency | NEEDS VALIDATION | Compare and preserve canonical workflow |
| `docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md` | referenced by `docs/workflows/APPLY_ROUTING_CHAIN.md` and audits | apply routing | high | source dependency | NEEDS VALIDATION | Compare and preserve approval rules |
| `docs/AI_OS/operator_workflows/AIOS_SAFE_SESSION_RESUME_STANDARD.md` | referenced by `docs/workflows/SAFE_SESSION_RESUME.md` and audits | resume workflow | high | source dependency | NEEDS VALIDATION | Compare and preserve resume rules |
| `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md` | referenced by `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md` and audits | folder ownership | high | source dependency | NEEDS VALIDATION | Compare before source retirement |
| `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md` | referenced by `docs/governance/FILE_PLACEMENT_RULES.md` and audits | placement rules | high | source dependency | NEEDS VALIDATION | Compare before source retirement |
| `docs/AI_OS/codex/AIOS_CODEX_ORCHESTRATION_PLAYBOOK.md` | referenced by context docs and planning/audits | Codex behavior | high | duplicate authority | NEEDS VALIDATION | Merge active rules into `AGENTS.md` only after review |
| `docs/AI_OS/codex/PHASE_15_2_CODEX_PERSISTENT_INSTRUCTION_LAYER.md` | source file plus planning refs | phase-specific instruction layer | medium | likely historical | NEEDS VALIDATION | Archive proposal after user review |
| `docs/AI_OS/codex/AGENTS_MD_BACKUP_PHASE15_2_20260513.md` | source file plus planning refs | backup of authority | medium | historical backup | NEEDS VALIDATION | Archive proposal after confirming root `AGENTS.md` |

## Validation conclusions

- Runtime-critical files are not ready for relocation.
- Worker registry/profile/inbox paths are heavily referenced and must remain stable.
- Worker heartbeat files are generated, but current scripts still read/write heartbeat patterns.
- Trading Lab result outputs are generated/evidence, but active validators and dashboard fixtures reference them.
- Root JSON artifacts parse cleanly and no active readers were found in this scan; relocation still needs user retention decision.
- CLEAN-era brain files are not directly runtime-critical, but several are still source-attributed by canonical V2 docs.

## Blockers

- Source attribution in canonical docs still points to `docs/AI_OS/` for several workflow/governance files.
- Runtime output paths are hardcoded in control scripts and orchestrator API code.
- Trading Lab result output paths are hardcoded in runner, validators, and dashboard fixtures.
- Worker heartbeat relocation would break simple worker scripts unless those scripts are updated together.

## Explicit non-actions

- No files moved.
- No files deleted.
- No files renamed.
- No launchers modified.
- No runtime code modified.
- No dashboard code modified.
- No Trading Lab code modified.
- No telemetry runtime state modified.
