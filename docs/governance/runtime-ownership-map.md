# AI_OS Runtime Ownership Map

## Purpose

This document proposes ownership boundaries for AI_OS runtime, authority, generated state, operator tooling, and reference-only material.

This is a planning/control document only. It does not approve restructuring.

## Ownership model

AI_OS should use one owner per responsibility:

- Root files own project identity and top-level rules.
- `docs/` owns active documentation authority.
- `apps/` owns user-facing applications.
- `services/` owns backend/runtime service code.
- `automation/` owns orchestration machinery and operator automation.
- `scripts/` owns simple operator/developer command wrappers.
- `schemas/` owns structured contracts.
- `tests/` owns validation.
- `telemetry/`, `logs/`, `proof/`, `validation/`, and `checkpoints/` own evidence/runtime outputs, not authority.
- `archive/` owns historical reference only.
- `docs/AI_OS/` is CLEAN-era source material pending merge/archive classification.

## Active runtime folders

| Folder | Proposed owner | Connected systems | Dependency risk | Classification | Boundary |
|---|---|---|---|---|---|
| `services/runtime/` | Runtime service owner | Runtime bootstrap, automation dispatcher/executor/handlers, event bus | high | KEEP ACTIVE | Runtime code only; no docs authority or generated reports |
| `services/dispatcher/` | Dispatcher service owner | Packet queue, resume, restoration, execution graph | high | KEEP ACTIVE | Dispatcher code only; no operator docs |
| `services/policy/` | Policy service owner | Approval requirements, capability policy, telemetry | high | KEEP ACTIVE | Policy code only; no secrets |
| `services/telemetry/` | Telemetry service owner | Telemetry writer, replay, runtime visibility, audit replay | high | KEEP ACTIVE | Telemetry code only; runtime ledgers live under `telemetry/` |
| `services/orchestrator/` | Runtime API owner | Express API, runtime data adapter | high | KEEP ACTIVE | API code and package metadata only |
| `automation/orchestration/` | Orchestration runtime owner | Workers, packets, approvals, validators, supervisor, control loop | high | KEEP ACTIVE | Orchestration state and tools; consolidate cautiously |
| `automation/intake/` | Goal intake owner | Runtime loop intake and recommendation chain | medium | KEEP ACTIVE | Goal intake scripts only |
| `automation/runtime/` | Runtime support owner | Path registry/state support scripts | high | KEEP ACTIVE | Runtime support tooling; no docs authority |
| `scripts/control/` | Runtime control wrapper owner | Start/stop/status/health runtime scripts | high | KEEP ACTIVE | Thin operator control wrappers |

## Authority/docs folders

| Folder | Proposed owner | Connected systems | Dependency risk | Classification | Boundary |
|---|---|---|---|---|---|
| `docs/governance/` | Governance owner | Source-of-truth map, ownership, doctrine, placement rules | high | KEEP ACTIVE | Active repo rules and ownership only |
| `docs/workflows/` | Workflow owner | Operator workflows, apply routing, resume, worker lane rules | high | KEEP ACTIVE | Active workflows only |
| `docs/security/` | Security owner | Access, credentials, approval/security boundaries | high | KEEP ACTIVE | Active security docs only |
| `docs/architecture/` | Architecture owner | System and agent runtime architecture | medium | KEEP ACTIVE | Durable architecture only |
| `docs/specs/` | Specification owner | API, automation, dashboard contracts | medium | KEEP ACTIVE | Active specs only |
| `docs/audits/` | Audit owner | Cleanup records, decisions, inspection reports | medium | KEEP ACTIVE | Audit history, not operational commands |
| `docs/concepts/` | Concept source owner | Design concepts | low | MERGE INTO CANONICAL | Concept material pending promotion |
| `docs/roadmap/` | Roadmap owner | Product/build planning | low | KEEP ACTIVE | Directional planning, not runtime authority |
| `docs/AI_OS/` | CLEAN-era source owner | Prior docs, drafts, authority duplicates | high | MERGE INTO CANONICAL | Source material only unless promoted |

## Generated-state folders

| Folder or path | Proposed owner | Connected systems | Dependency risk | Classification | Boundary |
|---|---|---|---|---|---|
| `telemetry/runtime/` | Runtime state owner | Runtime status, heartbeat, process, stdout/stderr logs | high | KEEP ACTIVE | Runtime state only; no source authority |
| `telemetry/work_ledger.jsonl` | Telemetry ledger owner | Telemetry replay, orchestrator runtime API | high | KEEP ACTIVE | Append-style event ledger; retention policy needed |
| `logs/` | Log owner | Unknown/generated logs | medium | NEEDS USER DECISION | Logs only; no active authority |
| `proof/` | Proof/evidence owner | `checkpoints/verify_success.ps1` and proof verification | high | KEEP ACTIVE | Evidence only; no source authority |
| `validation/` | Validation output owner | Validator outputs | medium | NEEDS USER DECISION | Output only; no active authority |
| `checkpoints/` | Checkpoint/proof owner | Proof bundle and verify success script | high | KEEP ACTIVE | Checkpoint tools/evidence; no duplicate brain docs |
| `automation/orchestration/work_packets/active/` | Active packet state owner | Packet advancement, dispatcher queue display | high | KEEP ACTIVE | Active runtime state |
| `automation/orchestration/work_packets/blocked/` | Blocked packet state owner | Packet lifecycle | high | KEEP ACTIVE | Blocked runtime state |
| `automation/orchestration/work_packets/complete/` | Completed packet state owner | Evidence/history | medium | KEEP ACTIVE | Completed runtime state pending archive policy |
| `automation/orchestration/workers/*heartbeat.json` | Worker heartbeat owner | Worker status/stale worker tooling | medium | REMOVE/RELOCATE CANDIDATE | Runtime state; relocate when safe |
| `apps/trading_lab/trading_lab/results/` | Trading Lab evidence owner | Paper runner/API output, dashboard fixture references | medium | REMOVE/RELOCATE CANDIDATE | Generated/evidence outputs; retention decision required |
| Root `approval.json`, `completion_report.json`, `validation_result.json`, `task_log.json` | Root generated-state candidates | Unknown | medium | NEEDS USER DECISION | Should not remain root authority |

## Operator tooling folders

| Folder | Proposed owner | Connected systems | Dependency risk | Classification | Boundary |
|---|---|---|---|---|---|
| `scripts/` | Simple command wrapper owner | Control, runtime, telemetry, validation, worker helpers | medium | KEEP ACTIVE | Thin scripts only; avoid becoming second orchestration system |
| `scripts/runtime/` | Runtime launcher wrapper owner | Runtime start helpers | medium | KEEP ACTIVE | Wrapper only |
| `scripts/telemetry/` | Telemetry helper owner | Audit timeline and telemetry event writers | medium | KEEP ACTIVE | Helper scripts only |
| `scripts/validation/` | Validation helper owner | Clean-state check launcher | medium | KEEP ACTIVE | Validation wrappers only |
| `scripts/workers/` | Worker helper owner | Worker isolation/lane/merge readiness checks | medium | KEEP ACTIVE | Worker checks only |
| `automation/operator/` | Operator automation owner candidate | Morning operations, worker launchers, layout profiles, legacy imports | high | NEEDS USER DECISION | Split active launchers from legacy experiments |
| `automation/startup/` | Startup automation owner candidate | Morning brief/state/workflow | medium | NEEDS USER DECISION | Decide relationship to `automation/operator/` |
| `automation/windows_workstation/` | Local workstation launcher owner | Morning workspace launcher, presets, layouts | medium | KEEP ACTIVE | Local workstation launch only |
| `automation/window_identity/` | Window identity owner | Worker layout and identity registry | medium | NEEDS USER DECISION | Decide separation from orchestration worker registry |
| `automation/mission_control/` | Mission planning owner | `aios.ps1 -Mode mission/runner` | medium | KEEP ACTIVE | Mission planning only |

## Archive/reference-only folders

| Folder | Proposed owner | Connected systems | Dependency risk | Classification | Boundary |
|---|---|---|---|---|---|
| `archive/` | Historical reference owner | Reference only | low | ARCHIVE ONLY | Never active authority |
| `internal/source-artifacts/` | Source artifact owner | Imported PDFs/text | low | ARCHIVE ONLY | Reference only |
| `inputs/` | Source input owner | Imported source materials | low | ARCHIVE ONLY | Reference only |
| `automation/operator/legacy_imports/` | Legacy import owner | Unknown legacy scripts | medium | ARCHIVE ONLY | Reference only unless dependency found |
| `docs/AI_OS/**/*_DRAFT.md` | CLEAN-era draft owner | Prior planning material | medium | ARCHIVE ONLY | Not active authority unless promoted |

## Folders that should never contain active authority

| Folder or pattern | Classification | Reason |
|---|---|---|
| `archive/` | ARCHIVE ONLY | Historical/reference only |
| `.codex_worktrees/` | ARCHIVE ONLY | Worktree material, not active repo authority |
| `node_modules/` | REMOVE/RELOCATE CANDIDATE | Installed dependencies |
| `__pycache__/` | REMOVE/RELOCATE CANDIDATE | Generated cache |
| `.pytest_cache/` | REMOVE/RELOCATE CANDIDATE | Generated test cache |
| `telemetry/runtime/` | KEEP ACTIVE | Runtime state only, not docs authority |
| `logs/` | NEEDS USER DECISION | Logs/evidence only |
| `proof/` | KEEP ACTIVE | Proof/evidence only |
| `validation/` | NEEDS USER DECISION | Validator output only |
| `apps/trading_lab/trading_lab/results/` | REMOVE/RELOCATE CANDIDATE | Paper output evidence only |
| `automation/orchestration/workers/*heartbeat.json` | REMOVE/RELOCATE CANDIDATE | Runtime heartbeat state only |

## Folders that should never contain runtime artifacts

| Folder | Classification | Reason |
|---|---|---|
| `docs/governance/` | KEEP ACTIVE | Governance docs only |
| `docs/workflows/` | KEEP ACTIVE | Workflow docs only |
| `docs/security/` | KEEP ACTIVE | Security docs only |
| `docs/architecture/` | KEEP ACTIVE | Architecture docs only |
| `docs/specs/` | KEEP ACTIVE | Specs only |
| `docs/concepts/` | MERGE INTO CANONICAL | Concepts only |
| Root protected governance files | KEEP ACTIVE | Authority/log files, not runtime state |
| `schemas/` | KEEP ACTIVE | Contracts only |
| `tests/` | KEEP ACTIVE | Test code only |

## Proposed AI_OS ownership boundaries

| Responsibility | Proposed canonical owner | Secondary/source areas | Notes |
|---|---|---|---|
| Human entry point | `README.md` | `docs/roadmap/`, `docs/audits/` | Root front door only |
| AI/tool behavior | `AGENTS.md` | `docs/AI_OS/codex/`, `docs/AI_OS/agents/`, `docs/AI_OS/claude/` | Merge selected rules, then archive duplicates |
| Governance | `docs/governance/` | `docs/AI_OS/governance/`, `docs/AI_OS/index/` | One source of truth per topic |
| Workflows | `docs/workflows/` | `docs/AI_OS/operator/`, `docs/AI_OS/operator_workflows/`, `docs/AI_OS/system_wizards/` | One workflow doc per job |
| Security | `docs/security/` and `SECURITY.md` | `docs/AI_OS/security/`, `docs/AI_OS/brokers/`, `docs/AI_OS/execution/` | Preserve no-live-trading boundaries |
| Architecture | `docs/architecture/` | `docs/AI_OS/architecture/`, `docs/infrastructure/`, `docs/concepts/` | Durable architecture only |
| Dashboard app | `apps/dashboard/` | `apps/dashboard/mock-data/` | UI source plus fixtures; split wired/stale fixtures later |
| Trading Lab app | `apps/trading_lab/` | `aios/modules/trader/` | User decision needed for canonical package |
| Runtime service | `services/runtime/` | `scripts/control/`, `telemetry/runtime/` | Code in services, state in telemetry |
| Orchestrator API | `services/orchestrator/` | `telemetry/runtime/`, `telemetry/work_ledger.jsonl` | API reads runtime state; dashboard not confirmed wired |
| Orchestration automation | `automation/orchestration/` | `scripts/`, `automation/operator/` | Active but unconsolidated |
| Worker state | `automation/orchestration/workers/` | `automation/window_identity/` | Registry split needs decision |
| Packet state | `automation/orchestration/work_packets/` | `work_packets/` | Canonical runtime packet path appears under `automation/orchestration/` |
| Telemetry evidence | `telemetry/` | `services/telemetry/` | Ledger/state outputs, not authority |
| Validation | `tests/`, `automation/orchestration/validators/`, `scripts/validation/` | `validation/` outputs | Test code separate from validator output |

## What is actually wired versus what only looks important

Actually wired or directly referenced:

- `aios.ps1`
- `automation/session/Start-AiOsDailyFlow.ps1`
- `automation/session/Resume-AiOsSession.ps1`
- `automation/intake/Start-AiOsRuntimeLoop.ps1`
- `automation/orchestration/runtime/Start-AiOsPersistentRuntimeSupervisor.ps1`
- `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`
- `automation/orchestration/workers/AIOS_WORKER_PROFILES.json`
- `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json`
- `automation/orchestration/work_packets/`
- `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json`
- `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json`
- `services/orchestrator/index.js`
- `services/orchestrator/runtimeApiService.js`
- `services/runtime/runtimeBootstrap.js`
- `telemetry/runtime/*`
- `telemetry/work_ledger.jsonl`
- `apps/dashboard/src/App.jsx`
- `apps/dashboard/mock-data/aios-runtime-visibility-v1.example.json`
- `apps/trading_lab/trading_lab/cli.py`
- `aios/modules/trader/` through `tests/trader/`

Looks important but requires classification:

- Most `docs/AI_OS/` files
- Most `apps/dashboard/mock-data/*.example.json`
- Root runtime/report JSON files
- `automation/operator/` subtrees
- `work_packets/` top-level folder
- `approvals/` top-level folder
- `logs/`, `validation/`, `uploads/`

Duplicate-brain retention markings:

- `docs/AI_OS/**` is source/reference material pending file-by-file merge/archive classification; do not treat it as active authority by default.
- Root `work_packets/**` is not active queue authority; decide retention or migration before any archive move.
- Root `approvals/**` is not active approval authority; decide retention or migration before any archive move.
- `automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json` is compatibility evidence until adapter-first use is fully proven and retirement is approved.
- `automation/orchestration/*.example.json` files require fixture ownership review before archive.
- Current duplicate-brain delete readiness has 0 safe delete candidates.

Historical/reference by default:

- `archive/`
- `internal/source-artifacts/`
- `inputs/`
- `automation/operator/legacy_imports/`
- `docs/AI_OS/**/*_DRAFT.md`

## Dangerous removal list

Do not remove or relocate these without a dependency-specific validator:

- `aios.ps1`
- `automation/session/`
- `automation/intake/`
- `automation/orchestration/README.md`
- `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`
- `automation/orchestration/workers/AIOS_WORKER_PROFILES.json`
- `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json`
- `automation/orchestration/work_packets/`
- `automation/orchestration/approval_inbox/`
- `automation/orchestration/validators/`
- `scripts/control/`
- `services/runtime/`
- `services/dispatcher/`
- `services/orchestrator/`
- `services/telemetry/`
- `telemetry/work_ledger.jsonl`
- `telemetry/runtime/`
- `apps/dashboard/src/`
- `apps/dashboard/package.json`
- `apps/trading_lab/trading_lab/`
- `aios/modules/trader/`
- `tests/trader/`

## Open ownership questions

1. Which Trading Lab package is canonical: `apps/trading_lab/trading_lab/` or `aios/modules/trader/`?
2. Should `work_packets/` at repo root survive, or should all packet runtime state live under `automation/orchestration/work_packets/`?
3. Should `approvals/` at repo root survive, or should approval runtime state live under `automation/orchestration/approval_inbox/`?
4. Should `automation/operator/` remain active after `automation/orchestration/` becomes canonical?
5. Should dashboard connect to `services/orchestrator` APIs, or remain local fixture-driven for now?
6. What retention policy should apply to `telemetry/`, `logs/`, `proof/`, `validation/`, and Trading Lab result outputs?
