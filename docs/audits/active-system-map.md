# AI_OS Active System Map

## Executive summary

This map identifies the active launch, runtime, worker, dashboard, Trading Lab, authority, and generated-state surfaces observed in AI_OS_V2.

This is a planning document only. It does not approve moves, deletes, renames, archive actions, launcher rewrites, runtime rewrites, or CLEAN-to-V2 replacements.

Highest-risk active dependency zones:

- Root shortcut: `aios.ps1`
- Orchestration runtime: `automation/orchestration/`
- Runtime telemetry state: `telemetry/runtime/` and `telemetry/work_ledger.jsonl`
- Worker registry/inbox/packet state: `automation/orchestration/workers/`, `automation/orchestration/work_packets/`
- Dashboard runtime visibility fixture/API split: `apps/dashboard/mock-data/` versus `services/orchestrator/`
- Trading Lab package split: `apps/trading_lab/trading_lab/` versus `aios/modules/trader/`
- Authority split: root docs and `docs/{governance,workflows,security,architecture}` versus `docs/AI_OS/`

Recommended principle for reconstruction:

Map dependencies first, then promote one canonical path per job. Do not remove duplicate-looking files until launcher and import references are verified.

## Active startup chain

| Current path | Role | Connected systems | Dependency risk | Classification | Recommendation |
|---|---|---|---|---|---|
| `aios.ps1` | Root operator shortcut and mode router | `automation/session/`, `automation/operator/`, `automation/orchestration/`, `automation/intake/`, `automation/mission_control/`, `checkpoints/verify_success.ps1` | high | KEEP ACTIVE | Treat as primary launch map until a replacement is approved |
| `automation/session/Start-AiOsDailyFlow.ps1` | Daily flow launcher | Starts session, resume, runtime loop, self-heal, worker inbox, optional worker preview/swarm | high | KEEP ACTIVE | Keep; classify called scripts before editing |
| `automation/session/Start-AiOsSession.ps1` | Session initializer | Runtime memory/session state under orchestration memory | medium | KEEP ACTIVE | Keep active pending memory/state ownership decision |
| `automation/session/Resume-AiOsSession.ps1` | Resume launcher | `automation/orchestration/memory/AIOS_RUNTIME_MEMORY.json`, next-step resolver, blocker resolver | medium | KEEP ACTIVE | Keep active; memory file is runtime state |
| `automation/windows_workstation/Launch-AiOsMorningWorkspace.ps1` | Morning workspace launcher | Delegates to `automation/window_identity/Open-AiOsWorkerWindowLayout.ps1` | medium | KEEP ACTIVE | Keep active; no window/terminal rewrites yet |
| `automation/window_identity/Open-AiOsWorkerWindowLayout.ps1` | Worker window layout launcher | Window identity registry/layout files | medium | KEEP ACTIVE | Keep active if local workstation flow is retained |
| `automation/operator/Start-AiOsMorningOperations.ps1` | Morning operations launcher | Called by `aios.ps1 -Mode morning` | high | KEEP ACTIVE | Keep active until operator layer is consolidated |
| `automation/startup/Start-AiOsMorningWorkflow.ps1` | Startup workflow candidate | Startup brief/state scripts | medium | NEEDS USER DECISION | Decide whether this supersedes or complements operator morning scripts |
| `apps/dashboard/package.json` | Dashboard dev/build launcher source | Vite scripts: `dev`, `build`, `lint`, `preview` | medium | KEEP ACTIVE | Keep active for dashboard app |
| `services/orchestrator/index.js` | Runtime API server entry | Express API on port 5050, runtime status/queue/audit/health/visibility/control endpoints | high | KEEP ACTIVE | Keep active; dashboard is not yet confirmed wired to it |

## Active orchestration chain

| Current path | Role | Connected systems | Dependency risk | Classification | Recommendation |
|---|---|---|---|---|---|
| `automation/orchestration/README.md` | Current orchestration boundary and canonical path map | Worker registry, profiles, inbox, packets, command queue, approval inbox, validators, commit packages | high | KEEP ACTIVE | Treat as active map, but not sole authority over root rules |
| `automation/orchestration/clean_state_gate.ps1` | Clean-state preflight gate | Git/status and safe launch decision flow | high | KEEP ACTIVE | Keep active; do not bypass |
| `automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1` | Runtime health validator | `aios.ps1 status`, status/control displays | high | KEEP ACTIVE | Keep active |
| `automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1` | Next action recommender | Runtime loop and status chain | medium | KEEP ACTIVE | Keep active |
| `automation/orchestration/work_packets/` | Work packet lifecycle root | Route/create/move/get packet scripts, active/blocked/complete/template folders | high | KEEP ACTIVE | Keep; classify packet JSON as runtime state versus examples |
| `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json` | Command queue state | Command queue add/get scripts | medium | KEEP ACTIVE | Keep active if command queue remains canonical |
| `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json` | Approval inbox state | Approval display and apply gate flow | high | KEEP ACTIVE | Keep active; protect from blind removal |
| `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json` | Approval gate state | Apply approval checks | high | KEEP ACTIVE | Keep active |
| `automation/orchestration/validators/` | Validator chain | Commit/package/apply safety checks | high | KEEP ACTIVE | Keep active |
| `automation/orchestration/commit_packages/` | Commit package planning | Commit package previews and recommendations | medium | KEEP ACTIVE | Keep active; no commit automation without approval |

## Active runtime chain

| Current path | Role | Connected systems | Dependency risk | Classification | Recommendation |
|---|---|---|---|---|---|
| `scripts/control/Start-AiOsRuntime.ps1` | Starts Node runtime bootstrap | `services/runtime/runtimeBootstrap.js`, `telemetry/runtime/runtime_process.json`, stdout/stderr logs | high | KEEP ACTIVE | Keep as runtime control entry |
| `scripts/control/Stop-AiOsRuntime.ps1` | Stops recorded runtime process | `telemetry/runtime/runtime_process.json` | high | KEEP ACTIVE | Keep; do not edit process semantics |
| `scripts/control/Get-AiOsRuntimeStatus.ps1` | Reads runtime state | `telemetry/runtime/runtime_state.json`, `runtime_heartbeat.json`, `runtime_process.json` | high | KEEP ACTIVE | Keep active |
| `scripts/control/Get-AiOsRuntimeHealth.ps1` | Reads runtime health | `telemetry/runtime/*`, `telemetry/work_ledger.jsonl` | high | KEEP ACTIVE | Keep active |
| `services/runtime/runtimeBootstrap.js` | Node runtime bootstrap | Runtime state/heartbeat/process via control scripts | high | KEEP ACTIVE | Keep active |
| `services/runtime/` | Runtime implementation | Dispatcher/executor/handlers/backpressure/event bus | high | KEEP ACTIVE | Keep active |
| `services/dispatcher/` | Dispatcher implementation | Packet queue, restoration, resume, execution graph, telemetry | high | KEEP ACTIVE | Keep active |
| `services/policy/policyEngine.ts` | Policy enforcement | Telemetry writer, approval requirements, runtime remediation capability | high | KEEP ACTIVE | Keep active |
| `services/telemetry/` | Telemetry model/replay/visibility | `telemetry/work_ledger.jsonl`, runtime visibility, audit replay | high | KEEP ACTIVE | Keep active |
| `automation/intake/Start-AiOsRuntimeLoop.ps1` | Goal intake runtime loop | Goal intake, action recommendation, runtime health | high | KEEP ACTIVE | Keep active |
| `automation/orchestration/runtime/Start-AiOsPersistentRuntimeSupervisor.ps1` | Repeated supervisor cycle launcher | Path registry, runtime self-route, packet advancement, supervisor cycle logs | high | KEEP ACTIVE | Keep active; writes audit log |
| `automation/orchestration/runtime/Invoke-AiOsRuntimeSelfRoute.ps1` | Runtime self-routing | Supervisor loop | high | KEEP ACTIVE | Keep active |
| `automation/orchestration/runtime/Invoke-AiOsRuntimePacketAdvancement.ps1` | Packet advancement | `automation/orchestration/work_packets/active` | high | KEEP ACTIVE | Keep active; movement semantics are dangerous to change |

## Active dashboard chain

| Current path | Role | Connected systems | Dependency risk | Classification | Recommendation |
|---|---|---|---|---|---|
| `apps/dashboard/src/App.jsx` | Current React dashboard entry | Imports `../mock-data/aios-runtime-visibility-v1.example.json` | medium | KEEP ACTIVE | Keep; current UI is fixture-driven |
| `apps/dashboard/mock-data/aios-runtime-visibility-v1.example.json` | Wired dashboard runtime fixture | Dashboard runtime page | medium | KEEP ACTIVE | Keep until API wiring replaces it |
| `apps/dashboard/mock-data/` | Dashboard fixtures and planning data | Many mock data files; not all imported by current UI | medium | NEEDS USER DECISION | Split wired fixtures from historical/mock-only fixtures later |
| `services/orchestrator/index.js` | Runtime API server | `/api/runtime/status`, `/queue`, `/audit`, `/health`, `/visibility`, `/control` | high | KEEP ACTIVE | Keep; candidate future dashboard data source |
| `services/orchestrator/runtimeApiService.js` | Runtime API data adapter | Reads `telemetry/runtime/*` and `telemetry/work_ledger.jsonl` | high | KEEP ACTIVE | Keep; protect telemetry contracts |
| `apps/dashboard/assets/` | Dashboard assets | Protected by repo rules | medium | NEEDS USER DECISION | Do not touch unless explicitly allowed |
| `apps/dashboard/node_modules/` | Installed dependencies | Dashboard local install | low | REMOVE/RELOCATE CANDIDATE | Remove only after approval; do not inspect/edit manually |

## Active worker chain

| Current path | Role | Connected systems | Dependency risk | Classification | Recommendation |
|---|---|---|---|---|---|
| `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json` | Canonical worker registry per orchestration README | Worker address book, router, builder, inbox, status scripts | high | KEEP ACTIVE | Keep active |
| `automation/orchestration/workers/AIOS_WORKER_PROFILES.json` | Worker capability/profile source | Packet routing, worker resolution, bootstrap checks | high | KEEP ACTIVE | Keep active |
| `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json` | Worker inbox state | Inbox display, safe execute, completion, state updates | high | KEEP ACTIVE | Keep active |
| `automation/orchestration/workers/Get-AiOsWorkerAddressBook.ps1` | Worker registry/address display | Orchestration worker registry plus window identity registry | medium | KEEP ACTIVE | Keep active; note dual registry dependency |
| `automation/window_identity/AIOS_WORKER_REGISTRY.json` | Window identity worker registry | Address book bridge and local window identity tooling | medium | NEEDS USER DECISION | Decide if this remains separate from orchestration registry |
| `automation/orchestration/workers/*heartbeat.json` | Worker heartbeat artifacts | Stale worker/status displays | medium | REMOVE/RELOCATE CANDIDATE | Runtime state; relocate or regenerate after approval |
| `scripts/write-worker-heartbeat.ps1` | Legacy/simple heartbeat writer | `workers/` or configured worker heartbeat dir | medium | NEEDS USER DECISION | Compare with orchestration worker heartbeat model |
| `scripts/detect-stale-workers.ps1` | Legacy/simple stale worker detector | Heartbeat JSON files | medium | NEEDS USER DECISION | Keep only if still used by active workflow |
| `automation/operator/worker_queue/` | Operator worker queue | Operator UI/launcher experiments | medium | NEEDS USER DECISION | Classify against orchestration inbox before cleanup |

## Trading Lab isolation map

| Current path | Role | Connected systems | Dependency risk | Classification | Recommendation |
|---|---|---|---|---|---|
| `apps/trading_lab/README.md` | Trading Lab safety and CLI guide | Paper-only CLI, SQLite, local webhooks | high | KEEP ACTIVE | Keep active |
| `apps/trading_lab/trading_lab/cli.py` | Typer CLI | init-db, import-file, backtest, walk-forward, serve-webhooks, report | high | KEEP ACTIVE | Keep active; `serve-webhooks` is local paper-only but high-sensitivity |
| `apps/trading_lab/trading_lab/` | Trading Lab app package | Backtest, ingest, execution, bot, runner, server, strategies | high | KEEP ACTIVE | Keep active |
| `apps/trading_lab/trading_lab/execution/` | Paper execution/risk layer | Live broker stub and paper risk gates | high | KEEP ACTIVE | Dangerous to touch; preserve live-disabled behavior |
| `apps/trading_lab/trading_lab/results/` | Paper output artifacts | Dashboard mock-data references and paper runner evidence | medium | REMOVE/RELOCATE CANDIDATE | Treat as generated/evidence until retention decision |
| `aios/modules/trader/` | Separate paper trader module | Tests import `aios.modules.trader.*`; local paper broker/risk/routes | high | KEEP ACTIVE | Keep active until canonical package decision |
| `tests/trader/` | Safety tests for `aios/modules/trader` | Paper route preview and payload tests | high | KEEP ACTIVE | Keep active |
| `automation/trading_lab/` | Trading Lab validators/automation | Paper handoff, route workflow, latency validators | high | KEEP ACTIVE | Keep active |
| `docs/AI_OS/brokers/`, `docs/AI_OS/execution/`, `docs/AI_OS/trading/` | Trading safety source material | No-live and broker boundary docs | high | MERGE INTO CANONICAL | Preserve safety rules; do not activate broker execution |

Dangerous Trading Lab boundaries:

- Do not enable broker connections.
- Do not add API keys or credentials.
- Do not convert paper webhook/server paths into real external execution.
- Do not weaken live execution status checks.
- Do not remove tests that assert paper-only and blocked live execution behavior.

## Active authority map

| Current path | Role | Connected systems | Dependency risk | Classification | Recommendation |
|---|---|---|---|---|---|
| `AGENTS.md` | AI/tool behavior authority | All Codex/agent work | high | KEEP ACTIVE | Single active AI behavior authority |
| `README.md` | Human front door | Project orientation | medium | KEEP ACTIVE | Keep active; refresh later |
| `docs/governance/` | Governance authority | Repo rules, ownership, doctrine | high | KEEP ACTIVE | Canonical governance |
| `docs/workflows/` | Workflow authority | Operator/development workflows | high | KEEP ACTIVE | Canonical workflows |
| `docs/security/` | Security authority | Access, credentials, approvals | high | KEEP ACTIVE | Canonical security docs |
| `docs/architecture/` | Architecture authority | System architecture | medium | KEEP ACTIVE | Canonical architecture |
| `docs/audits/` | Audit trail | Cleanup decisions and history | medium | KEEP ACTIVE | Records decisions; not day-to-day command authority |
| `docs/governance/source-of-truth-map.md` | Proposed V2 authority map | Current planning layer | high | KEEP ACTIVE | Keep as planning authority pending approval |
| `docs/governance/runtime-ownership-map.md` | Proposed V2 runtime ownership map | This mapping pass | high | KEEP ACTIVE | Use for future cleanup boundaries |

## Duplicate authority map

| Current path | Role | Connected systems | Dependency risk | Classification | Recommendation |
|---|---|---|---|---|---|
| `docs/AI_OS/context/AIOS_REPO_SOURCE_OF_TRUTH_MAP.md` | CLEAN-era source-of-truth map | Root/docs authority | high | MERGE INTO CANONICAL | Merge selected current facts into `docs/governance/source-of-truth-map.md` |
| `docs/AI_OS/system_wizards/00_START_HERE_AI_OS_CONTEXT_PACK.md` | Start-here brain | Operator/agent bootstrapping | high | MERGE INTO CANONICAL | Merge durable rules into `AGENTS.md`/workflows, then archive |
| `docs/AI_OS/system_wizards/START_HERE_AI_OS_CONTEXT_PACK.md` | Duplicate start-here brain | Operator/agent bootstrapping | high | MERGE INTO CANONICAL | Compare against `00_` version before archive |
| `docs/AI_OS/system_wizards/01_CURRENT_STATE.md` | Current-state brain | Session context | medium | MERGE INTO CANONICAL | Convert durable facts to audit/status docs |
| `docs/AI_OS/system_wizards/02_CHECKPOINT.md` | Checkpoint brain | Session context | medium | MERGE INTO CANONICAL | Convert to audit/checkpoint record |
| `docs/AI_OS/operator/` | Operator workflow duplicates | Workflows, launch rules, lane rules | high | MERGE INTO CANONICAL | Merge into `docs/workflows/` |
| `docs/AI_OS/operator_workflows/` | Operator workflow duplicates | Morning/session/apply routing | high | MERGE INTO CANONICAL | Merge into `docs/workflows/` |
| `docs/AI_OS/codex/` | Codex instruction duplicates | Root `AGENTS.md` | high | MERGE INTO CANONICAL | Root `AGENTS.md` remains authority |
| `docs/AI_OS/claude/` | Claude delegation instructions | Optional reviewer workflow | medium | NEEDS USER DECISION | Keep only if Claude remains part of V2 |
| `docs/AI_OS/governance/` | Governance duplicates | `docs/governance/` | high | MERGE INTO CANONICAL | Promote selected current rules |
| `docs/AI_OS/index/` | Index/ownership/source maps | Governance map | high | MERGE INTO CANONICAL | Merge selected facts |

## Runtime/generated-state map

| Current path | Role | Connected systems | Dependency risk | Classification | Recommendation |
|---|---|---|---|---|---|
| `telemetry/runtime/runtime_state.json` | Runtime state | Control scripts and orchestrator API | high | KEEP ACTIVE | Runtime artifact; do not delete while runtime flow depends on it |
| `telemetry/runtime/runtime_heartbeat.json` | Runtime heartbeat | Health/status scripts and orchestrator API | high | KEEP ACTIVE | Runtime artifact; do not delete blindly |
| `telemetry/runtime/runtime_process.json` | Runtime process record | Start/stop/status scripts | high | KEEP ACTIVE | Runtime artifact; protect |
| `telemetry/runtime/runtime_stdout.log`, `runtime_stderr.log` | Runtime logs | Start runtime script | medium | REMOVE/RELOCATE CANDIDATE | Generated logs; retention decision needed |
| `telemetry/work_ledger.jsonl` | Telemetry ledger | Services telemetry replay/API | high | KEEP ACTIVE | Treat as active ledger until retention policy exists |
| `automation/orchestration/runtime/logs/supervisor_cycles.jsonl` | Supervisor cycle audit log | Persistent supervisor | medium | KEEP ACTIVE | Runtime audit artifact |
| `automation/orchestration/work_packets/active/` | Active packet state | Runtime packet advancement and display tools | high | KEEP ACTIVE | Active state; dangerous to move |
| `automation/orchestration/work_packets/blocked/` | Blocked packet state | Packet lifecycle | high | KEEP ACTIVE | Active state; dangerous to move |
| `automation/orchestration/work_packets/complete/` | Completed packet state | Packet lifecycle/evidence | medium | KEEP ACTIVE | Retain until archival policy exists |
| `automation/orchestration/workers/*heartbeat.json` | Worker heartbeat state | Worker stale/status tools | medium | REMOVE/RELOCATE CANDIDATE | Generated runtime state; relocate later |
| `approval.json`, `completion_report.json`, `validation_result.json`, `task_log.json` | Root runtime/report artifacts | Unknown | medium | NEEDS USER DECISION | Classify before relocation/removal |
| `apps/trading_lab/trading_lab/results/` | Paper Trading Lab outputs | Dashboard fixtures and evidence | medium | REMOVE/RELOCATE CANDIDATE | Generated/evidence; do not delete without retention decision |
| `apps/dashboard/mock-data/*.example.json` | Dashboard fixtures | Some wired, many mock-only | medium | NEEDS USER DECISION | Split wired fixture set from old mock library |

## Dangerous-to-touch areas

| Current path | Role | Connected systems | Dependency risk | Classification | Recommendation |
|---|---|---|---|---|---|
| `aios.ps1` | Root launch router | Most operator workflows | high | KEEP ACTIVE | Do not rewrite until replacement is tested |
| `scripts/control/` | Runtime process control | Node runtime and telemetry runtime state | high | KEEP ACTIVE | Do not rewrite without validation |
| `services/runtime/` | Runtime engine | Runtime loop/automation handlers | high | KEEP ACTIVE | Do not touch in cleanup pass |
| `services/dispatcher/` | Dispatcher engine | Packet restoration/resume/queue | high | KEEP ACTIVE | Do not touch in cleanup pass |
| `automation/orchestration/work_packets/` | Packet state machine | Runtime/supervisor/worker scripts | high | KEEP ACTIVE | Do not move/delete blindly |
| `automation/orchestration/workers/` | Worker registry/inbox/heartbeats | Worker launch/status/supervisor | high | KEEP ACTIVE | Do not consolidate without dependency tests |
| `automation/orchestration/approval_inbox/` | Approval gate state | Apply/approval workflow | high | KEEP ACTIVE | Protect |
| `apps/trading_lab/trading_lab/execution/` | Paper execution boundary | Trading safety | high | KEEP ACTIVE | Do not weaken blocked live execution |
| `aios/modules/trader/` | Tested paper trader module | `tests/trader/` | high | KEEP ACTIVE | Do not remove until canonical package decision |
| `apps/dashboard/src/` | Active dashboard source | Vite app | high | KEEP ACTIVE | Do not change in mapping pass |
| `.github/` | GitHub workflows/config | CI/repo automation | high | NEEDS USER DECISION | Do not touch per rule |

## Likely stale areas

| Current path | Role | Connected systems | Dependency risk | Classification | Recommendation |
|---|---|---|---|---|---|
| `docs/AI_OS/**/*_DRAFT.md` | CLEAN-era drafts | Unknown references | medium | ARCHIVE ONLY | Treat as source material unless promoted |
| `docs/AI_OS/codex/AGENTS_MD_BACKUP_PHASE15_2_20260513.md` | Backup of authority file | Root `AGENTS.md` | medium | ARCHIVE ONLY | Archive after confirming root authority |
| `automation/operator/legacy_imports/` | Legacy imported scripts | Unknown | medium | ARCHIVE ONLY | Reference only unless launcher dependency found |
| `apps/dashboard/mock-data/agent-workbench.example.json` | Old mock registry | References non-existing/old `docs/AI_OS/trading_laboratory/` paths | medium | NEEDS USER DECISION | Candidate for fixture cleanup after dashboard source inventory |
| `internal/source-artifacts/` | Imported source artifacts | Unknown | low | ARCHIVE ONLY | Reference only |
| `inputs/` | Source inputs | Unknown | low | ARCHIVE ONLY | Reference only |
| `automation/operator/layout_profiles/CODEX_CAPTURED_CURRENT.json` | Captured layout snapshot | Window layout experiments | low | REMOVE/RELOCATE CANDIDATE | Generated state candidate |

## Recommended protected zones

- Protected authority: `AGENTS.md`, `README.md`, protected root governance logs.
- Protected runtime: `scripts/control/`, `services/runtime/`, `services/dispatcher/`, `services/policy/`, `services/telemetry/`.
- Protected orchestration: `automation/orchestration/work_packets/`, `automation/orchestration/workers/`, `automation/orchestration/approval_inbox/`, `automation/orchestration/validators/`.
- Protected Trading Lab: `apps/trading_lab/trading_lab/execution/`, `apps/trading_lab/trading_lab/ingest/`, `aios/modules/trader/`, `tests/trader/`, `automation/trading_lab/`.
- Protected dashboard: `apps/dashboard/src/`, `apps/dashboard/package.json`, wired fixture `apps/dashboard/mock-data/aios-runtime-visibility-v1.example.json`, and `apps/dashboard/assets/` unless explicitly approved.
- Protected evidence until retention policy: `telemetry/`, `proof/`, `logs/`, `validation/`, `checkpoints/`, `apps/trading_lab/trading_lab/results/`.

## Recommended future cleanup order

1. Freeze authority: keep root `AGENTS.md` and proposed V2 docs authority map.
2. Create a full file-by-file `docs/AI_OS/` classification table.
3. Identify all launcher references from `aios.ps1`, `automation/session/`, `automation/operator/`, `automation/orchestration/`, and `scripts/control/`.
4. Decide canonical Trading Lab package path.
5. Decide canonical worker registry and whether window identity registry remains separate.
6. Split dashboard mock-data into wired fixtures, future fixtures, stale fixtures, and generated outputs.
7. Define telemetry/runtime retention policy.
8. Prepare approved merge-only docs batch.
9. Prepare approved relocate-only runtime/generated-state batch.
10. Prepare approved archive/remove batch after backups and validation.

## Known unknowns

- Whether `apps/trading_lab/trading_lab/` or `aios/modules/trader/` should be the canonical long-term paper trading package.
- Whether `automation/operator/` is active operator tooling, legacy experiment space, or both.
- Whether `automation/window_identity/AIOS_WORKER_REGISTRY.json` should remain separate from `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`.
- Whether dashboard should remain fixture-driven or connect to `services/orchestrator` runtime API.
- Whether root runtime/report JSON files are evidence, stale generated state, or active inputs.
- Whether old `docs/AI_OS/trading_laboratory/` paths referenced by dashboard mock data exist only historically.
- Whether `packages/`, `tools/`, and `agents/` should be introduced later as V2 top-level folders.

## Explicit non-actions

- No files moved.
- No files deleted.
- No files renamed.
- No archive changes made.
- No launcher rewrites made.
- No runtime code changes made.
- No trading logic changes made.
- No dashboard code changes made.
- No GitHub workflow changes made.
- No commits or pushes made.
