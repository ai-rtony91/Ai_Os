# Runtime Boundary Enforcement

## Purpose

This document hardens AI_OS runtime ownership boundaries before relocation.

It is governance only. It does not change runtime code, launchers, telemetry, packet routing, dashboard code, or Trading Lab code.

## Enforcement principles

1. Runtime code owns behavior.
2. Runtime state owns current machine state.
3. Authority docs own rules.
4. Audit docs own decisions and evidence summaries.
5. CLEAN-era docs are source material unless promoted.
6. Generated files are not authority.
7. No runtime path moves without reader/writer validation.

## Runtime-critical paths

| Path | Owner | Boundary | Enforcement status |
|---|---|---|---|
| `aios.ps1` | root operator shortcut | Launch routing | Do not rewrite without full launcher validation |
| `scripts/control/` | runtime control wrappers | Start/stop/status/health | Do not change paths without runtime validation |
| `services/runtime/` | runtime engine | Runtime behavior | Do not mix generated state or authority docs |
| `services/dispatcher/` | dispatcher engine | Packet dispatch/resume/restoration | Do not change packet contracts without validators |
| `services/orchestrator/` | runtime API | API reads telemetry/runtime state | Do not change source paths without API validation |
| `services/telemetry/` | telemetry code | Ledger parsing, replay, visibility | Do not move ledger without replay validation |
| `automation/orchestration/` | orchestration machinery | Workers, packets, approvals, validators | Do not consolidate by directory name alone |
| `telemetry/runtime/` | runtime state | State, heartbeat, process, runtime logs | Runtime state only; not authority |
| `telemetry/work_ledger.jsonl` | telemetry ledger | Work/event ledger | Preserve path until replay/API migration exists |

## Authority boundaries

| Path | Owner | Must contain | Must not contain |
|---|---|---|---|
| `AGENTS.md` | AI/tool behavior authority | Agent rules, safety rules, workflow constraints | Runtime state, generated logs, duplicate historical context |
| `README.md` | Human front door | Project identity and orientation | Runtime output, generated reports |
| `docs/governance/` | Governance authority | Ownership, doctrine, source-of-truth maps | Runtime state, telemetry outputs |
| `docs/workflows/` | Workflow authority | Operator/developer workflows | Packet state, worker heartbeat files |
| `docs/security/` | Security authority | Access, secrets, approval, safety boundaries | Credentials, runtime state |
| `docs/architecture/` | Architecture authority | Durable architecture | Runtime outputs |
| `docs/audits/` | Audit records | Decisions, validation reports, manifests | Active runtime state |

## Generated-state boundaries

| Path | Owner | Enforcement rule |
|---|---|---|
| `telemetry/runtime/` | Runtime state | Keep current until runtime readers/writers are migrated together |
| `telemetry/work_ledger.jsonl` | Telemetry ledger | Keep current until replay/API migration exists |
| `automation/orchestration/work_packets/` | Packet state | Keep current until packet lifecycle validators pass on a new path |
| `automation/orchestration/workers/*heartbeat.json` | Worker heartbeat state | Do not move until worker heartbeat scripts are updated together |
| `apps/trading_lab/trading_lab/results/` | Trading Lab paper evidence | Do not move until runner, validators, and dashboard fixtures support new path |
| root generated JSON artifacts | Root generated-state candidates | Do not delete without retention decision |
| `logs/` | Logs | Logs only; not authority |
| `validation/` | Validator output | Output only; source validators live elsewhere |
| `proof/` | Proof evidence | Evidence only; not authority |

## Duplicate-brain enforcement

| Source area | Enforcement rule | Current status |
|---|---|---|
| `docs/AI_OS/system_wizards/` | Source material only until merged | NEEDS VALIDATION |
| `docs/AI_OS/context/` | Source material only until merged | NEEDS VALIDATION |
| `docs/AI_OS/operator/` | Not active workflow authority once canonical docs are certified | BLOCKED by source attribution |
| `docs/AI_OS/operator_workflows/` | Not active workflow authority once canonical docs are certified | BLOCKED by source attribution |
| `docs/AI_OS/governance/` | Not active governance authority once canonical docs are certified | BLOCKED by source attribution |
| `docs/AI_OS/codex/` | Not active AI/tool authority once `AGENTS.md` is certified | NEEDS VALIDATION |

## Required validators before relocation

| Relocation family | Required validation |
|---|---|
| Runtime state/logs | Runtime start/status/health and orchestrator API checks |
| Telemetry ledger | Telemetry replay and runtime visibility checks |
| Worker registry/profile/inbox | Worker registry/profile/inbox validators |
| Worker heartbeat files | Worker status, stale-worker detection, heartbeat writer loop |
| Packet state | Packet lifecycle, route, move, state display validators |
| Approval state | Approval inbox and apply gate validators |
| Trading Lab results | Trading Lab runner validators, paper safety tests, dashboard fixture check |
| Duplicate brain docs | Canonical doc comparison and source-attribution replacement |
| Root generated JSON | JSON parse, reference search, user retention decision |

## Enforcement stop conditions

Stop and classify `BLOCKED` when:

- A hardcoded path is found in runtime, orchestration, dashboard, or Trading Lab code.
- A generated file is used by a validator, dashboard fixture, or API adapter.
- A duplicate doc is cited as the source for an active canonical doc.
- A Trading Lab file participates in default paper/simulation or broker-gate safety checks.
- A file may be proof, telemetry, or audit evidence and no retention policy exists.

## Approved Phase 3 outcome

Phase 3 may produce validation reports, dependency maps, relocation matrices, and boundary enforcement docs only.

Phase 3 does not approve:

- deletes
- moves
- renames
- archive actions
- launcher rewrites
- runtime rewrites
- dashboard rewrites
- Trading Lab rewrites
- telemetry path changes
- packet path changes
