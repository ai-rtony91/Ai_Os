# AI_OS Canonical Ownership Boundaries

## Purpose

This document defines the Phase 2 proposed ownership boundaries for AI_OS_V2.

It is governance only. It does not move, delete, rename, archive, or rewrite files.

## Canonical authority owners

| Owner | Canonical scope | Classification | Rule |
|---|---|---|---|
| `README.md` | Human front door | KEEP ACTIVE | Project overview, current mission, and repo orientation only |
| `AGENTS.md` | AI/tool behavior | KEEP ACTIVE | Single active behavior authority for Codex and AI coding agents |
| `docs/governance/` | Rules, doctrine, ownership | KEEP ACTIVE | Repo rules, ownership, source-of-truth maps, placement rules |
| `docs/governance/aios-identity-and-lane-governance.md` | Identity and lane governance | KEEP ACTIVE | Canonical Human Owner, Business GPT, Claude Chat, Codex East, Claude Code West, temporary worker, validator, lock, packet, and stop-point identity spine |
| `docs/workflows/` | Operator/development workflows | KEEP ACTIVE | Workflow instructions and safe operating sequences |
| `docs/security/` | Access and safety boundaries | KEEP ACTIVE | Secrets, credentials, approval, privacy, access, no-live-trading boundaries |
| `docs/architecture/` | System architecture | KEEP ACTIVE | Durable architecture and runtime design |
| `docs/audits/` | Audit trail and cleanup decisions | KEEP ACTIVE | Inspection results, classification manifests, and cleanup decision records |

Authority rule:

No file under `docs/AI_OS/`, `automation/`, `telemetry/`, `logs/`, `proof/`, `validation/`, `work_packets/`, or app-generated result folders should act as active authority unless explicitly promoted into one of the canonical owners above.

## Canonical runtime owners

| Owner | Canonical scope | Classification | Rule |
|---|---|---|---|
| `services/runtime/` | Runtime engine code | KEEP ACTIVE | Runtime execution code only |
| `services/dispatcher/` | Dispatcher and packet runtime code | KEEP ACTIVE | Dispatcher code only |
| `services/orchestrator/` | Runtime API service | KEEP ACTIVE | API service code and package metadata only |
| `services/policy/` | Policy enforcement code | KEEP ACTIVE | Policy code only |
| `services/telemetry/` | Telemetry code | KEEP ACTIVE | Telemetry models, replay, writers, and visibility builders |
| `scripts/control/` | Runtime control wrappers | KEEP ACTIVE | Start/stop/status/health commands only |
| `automation/orchestration/` | Orchestration machinery and state | KEEP ACTIVE | Worker, packet, approval, validator, supervisor, and control-loop machinery |
| `automation/orchestration/locks/` | Lock registry and conflict checks | KEEP ACTIVE | File-lock evidence, lock naming, and path conflict policy |
| `automation/orchestration/validators/` | Orchestration validator source | KEEP ACTIVE | DRY_RUN validators and validator-chain configuration for orchestration packets |

Runtime rule:

Runtime code must not be mixed with source-of-truth docs. Runtime state must not be promoted into governance or workflow authority.

## Canonical generated-state owners

| Owner | Canonical scope | Classification | Rule |
|---|---|---|---|
| `telemetry/runtime/` | Runtime state, heartbeat, process records, runtime logs | KEEP ACTIVE | Active runtime artifacts; preserve until retention policy exists |
| `telemetry/work_ledger.jsonl` | Work telemetry ledger | KEEP ACTIVE | Active ledger; do not relocate without API and replay validation |
| `automation/orchestration/work_packets/` | Packet lifecycle state | KEEP ACTIVE | Active/blocked/complete packet state; do not move without packet validators |
| `automation/orchestration/workers/` | Worker registry, profiles, inbox, worker runtime state | KEEP ACTIVE | Registry/profile/inbox active; heartbeat files are generated-state candidates |
| `automation/orchestration/approval_inbox/` | Approval inbox and apply gate state | KEEP ACTIVE | Active approval state |
| `proof/` | Proof/evidence artifacts | KEEP ACTIVE | Evidence only, not authority |
| `logs/` | Log artifacts | NEEDS USER DECISION | Generated logs; retention policy required |
| `validation/` | Validation outputs | NEEDS USER DECISION | Output only; source validators live elsewhere |
| `apps/trading_lab/trading_lab/results/` | Trading Lab paper result artifacts | REMOVE/RELOCATE CANDIDATE | Evidence/generated outputs; retention decision required |

Generated-state rule:

Generated artifacts may be active evidence, but they are not active authority. Any relocation requires a manifest and validation of all readers.

## Canonical app owners

| Owner | Canonical scope | Classification | Rule |
|---|---|---|---|
| `apps/dashboard/` | Dashboard application | KEEP ACTIVE | UI source, package metadata, and wired fixtures |
| `apps/dashboard/mock-data/` | Dashboard fixtures | NEEDS USER DECISION | Split wired fixtures from stale/mock-only fixtures before cleanup |
| `apps/trading_lab/` | Trading Lab app | KEEP ACTIVE | Paper-only app package, data, tests, and docs |
| `aios/modules/trader/` | Paper trader module | NEEDS USER DECISION | Currently tested by `tests/trader/`; canonical long-term role undecided |

App rule:

Dashboard and Trading Lab cleanup must not alter runtime wiring, assets, safety boundaries, paper-only behavior, or package/import paths without validation.

## Canonical archive/reference owners

| Owner | Canonical scope | Classification | Rule |
|---|---|---|---|
| `archive/` | Historical/reference material | ARCHIVE ONLY | Reference only; not active authority |
| `docs/AI_OS/` | CLEAN-era source material pending classification | MERGE INTO CANONICAL | Source material only unless explicitly promoted |
| `internal/source-artifacts/` | Imported source artifacts | ARCHIVE ONLY | Reference only |
| `inputs/` | Imported input/source material | ARCHIVE ONLY | Reference only |
| `automation/operator/legacy_imports/` | Legacy imported automation | ARCHIVE ONLY | Reference only unless dependency scan proves active use |

Archive rule:

Archive/reference areas must not drive live runtime, startup, approvals, or Trading Lab behavior.

## Prohibited ownership mixing

| Pattern | Classification | Boundary |
|---|---|---|
| Authority docs inside runtime state folders | REMOVE/RELOCATE CANDIDATE | Move into canonical docs only after approval |
| Runtime JSON state at repo root | REMOVE/RELOCATE CANDIDATE | Relocate only after reader validation |
| Generated logs inside authority folders | REMOVE/RELOCATE CANDIDATE | Relocate to generated-state owner after approval |
| CLEAN-era brain files acting as current instructions | MERGE INTO CANONICAL | Merge selected content, then retire as active authority |
| Dashboard mock data referencing historical paths as live paths | NEEDS USER DECISION | Classify wired versus stale fixtures first |

## Phase 2 stop conditions

Stop before moving or rewriting when:

- A file is read by `aios.ps1`.
- A file is read by `scripts/control/`.
- A file is read by `services/orchestrator/runtimeApiService.js`.
- A file is read by `automation/orchestration/workers/`, `work_packets/`, or `approval_inbox/`.
- A file participates in Trading Lab paper-only safety tests.
- A file is a protected root governance file.
- A file may contain generated state that is still evidence.
