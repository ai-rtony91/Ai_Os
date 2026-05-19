# Phase 3 Relocation Safety Matrix

## Purpose

This matrix prepares future relocation batches by classifying candidates as `SAFE`, `NEEDS VALIDATION`, or `BLOCKED`.

No relocation is approved by this file. Physical movement still requires explicit user approval.

## Readiness definitions

- `SAFE`: No active dependency found in this scan. Still requires user approval before delete or move.
- `NEEDS VALIDATION`: No active runtime dependency proven, but evidence/retention/ownership decision is unresolved.
- `BLOCKED`: Active references, active writers, runtime readers, dashboard readers, Trading Lab validators, or source-attribution dependencies exist.

## Relocation matrix

| Current path | Proposed path | Connected systems | Dependency count | Runtime risk | Validation status | Relocation readiness | Required next validation |
|---|---|---|---:|---|---|---|---|
| `telemetry/runtime/runtime_state.json` | keep current | runtime status, runtime health, runtime API, runtime state store | 5+ | high | active reader/writer found | BLOCKED | Runtime API/status/health contract review |
| `telemetry/runtime/runtime_heartbeat.json` | keep current | runtime health/status/API/state store | 5+ | high | active reader/writer found | BLOCKED | Runtime heartbeat contract review |
| `telemetry/runtime/runtime_process.json` | keep current | start/stop/status runtime scripts | 3+ | high | active control dependency found | BLOCKED | Runtime process-control validation |
| `telemetry/work_ledger.jsonl` | keep current | telemetry writer/replay/API/audit | 5+ | high | active telemetry dependency found | BLOCKED | Telemetry replay/API validation |
| `automation/orchestration/work_packets/active/` | keep current | packet advancement, displays, routing | 5+ | high | active packet dependency found | BLOCKED | Packet lifecycle validation |
| `automation/orchestration/work_packets/blocked/` | keep current | packet lifecycle, self-heal | 3+ | high | active packet dependency found | BLOCKED | Packet lifecycle validation |
| `automation/orchestration/work_packets/complete/` | keep current | packet history/evidence | 3+ | medium | active packet history dependency found | BLOCKED | Retention policy plus packet display validation |
| `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json` | keep current | approval inbox/gate/display | 5+ | high | active approval dependency found | BLOCKED | Approval inbox validation |
| `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json` | keep current | apply approval gate | 2+ | high | active approval dependency found | BLOCKED | Approval gate validation |
| `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json` | keep current | worker routing, builder, status, address book | 25+ | high | active worker dependency found | BLOCKED | Worker registry validator |
| `automation/orchestration/workers/AIOS_WORKER_PROFILES.json` | keep current | packet routing, worker resolution | 8+ | high | active worker dependency found | BLOCKED | Worker profile validator |
| `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json` | keep current | inbox, execution, completion, state | 5+ | high | active worker dependency found | BLOCKED | Worker inbox validator |
| `automation/orchestration/workers/*heartbeat.json` | future generated-state area | worker heartbeat scripts and status scripts | 7+ | medium | active heartbeat readers/writers found | BLOCKED | Redesign heartbeat ownership first |
| `automation/orchestration/runtime/logs/supervisor_cycles.jsonl` | future telemetry runtime log area | persistent runtime supervisor writer | 1 active writer | medium | hardcoded writer found | BLOCKED | Change writer path only in approved runtime patch |
| `telemetry/runtime/runtime_stdout.log` | optional `telemetry/runtime/logs/` | runtime start script | 1 active writer + docs | medium | hardcoded writer found | BLOCKED | Runtime start/status validation |
| `telemetry/runtime/runtime_stderr.log` | optional `telemetry/runtime/logs/` | runtime start script | 1 active writer + docs | medium | hardcoded writer found | BLOCKED | Runtime start/status validation |
| `approval.json` | evidence folder or approved deletion | root generated-state candidate | 0 active non-audit refs | medium | JSON_OK | NEEDS VALIDATION | User retention decision |
| `completion_report.json` | `validation/` or evidence folder | root generated-report candidate | 0 active non-audit refs | medium | JSON_OK | NEEDS VALIDATION | User retention decision |
| `validation_result.json` | `validation/` or evidence folder | root validation output candidate | 0 active non-audit refs | medium | JSON_OK | NEEDS VALIDATION | User retention decision |
| `task_log.json` | `telemetry/` or evidence folder | root task-state candidate | audit mention only | medium | JSON_OK | NEEDS VALIDATION | User retention decision |
| `apps/trading_lab/trading_lab/results/` | future evidence/report location | Trading Lab runner, validators, dashboard fixtures | 10+ | high | active references found | BLOCKED | Trading Lab path adapter and validators |
| `automation/operator/startup_reports/` | future operator log/evidence area | governed worker launcher writer | 1 active writer | medium | hardcoded writer found | BLOCKED | Launcher output path approval |
| `automation/operator/layout_profiles/CODEX_CAPTURED_CURRENT.json` | future generated layout state area | layout capture writer | 1 active writer | low | hardcoded writer found | BLOCKED | Layout capture policy |
| `.pytest_cache/` | none | pytest cache | 0 | low | no active dependency required | SAFE | User approval before delete |
| `apps/dashboard/node_modules/` | none | dashboard dependency install | 0 source dependency | low | reinstallable if package metadata retained | SAFE | User approval before delete; keep package files |
| `**/__pycache__/` | none | Python cache | 0 | low | generated cache | SAFE | User approval before delete |

## Duplicate brain relocation matrix

| Current path | Proposed path | Connected systems | Dependency count | Runtime risk | Validation status | Relocation readiness | Required next validation |
|---|---|---|---:|---|---|---|---|
| `docs/AI_OS/system_wizards/` | selected excerpts to canonical docs | operator/agent context | planning/source refs | low runtime, high authority | duplicate authority | NEEDS VALIDATION | File-by-file content comparison |
| `docs/AI_OS/context/` | selected excerpts to canonical docs | source-of-truth, bootstrap, recovery | planning/source refs | low runtime, high authority | duplicate authority | NEEDS VALIDATION | Source-of-truth comparison |
| `docs/AI_OS/operator/` | selected excerpts to `docs/workflows/` | active workflow source attribution | 10+ refs | low runtime, high authority | source dependency | BLOCKED | Replace/accept source attribution first |
| `docs/AI_OS/operator_workflows/` | selected excerpts to `docs/workflows/` | active workflow source attribution | 5+ refs | low runtime, high authority | source dependency | BLOCKED | Replace/accept source attribution first |
| `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md` | `docs/governance/FILE_PLACEMENT_RULES.md` already exists | active governance source attribution | 10+ refs | low runtime, high authority | source dependency | BLOCKED | Compare and certify canonical copy |
| `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md` | `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md` already exists | active governance source attribution | 10+ refs | low runtime, high authority | source dependency | BLOCKED | Compare and certify canonical copy |
| `docs/AI_OS/codex/AIOS_CODEX_ORCHESTRATION_PLAYBOOK.md` | selected excerpts to `AGENTS.md` | context docs and audits | 4+ refs | low runtime, high authority | duplicate authority | NEEDS VALIDATION | Compare against `AGENTS.md` |
| `docs/AI_OS/codex/AGENTS_MD_BACKUP_PHASE15_2_20260513.md` | archive/reference | backup authority source | planning refs | low | historical backup | NEEDS VALIDATION | Confirm root `AGENTS.md` covers current rules |

## Safe relocation candidates

These are the only candidates that appear dependency-safe from this pass:

- `.pytest_cache/`
- `apps/dashboard/node_modules/`
- `**/__pycache__/`

They still require explicit user approval before deletion, and no delete was performed.

## Blocked relocations

Blocked until code/path changes and validators are approved:

- all `telemetry/runtime/*` runtime state/log paths
- `telemetry/work_ledger.jsonl`
- `automation/orchestration/work_packets/`
- `automation/orchestration/approval_inbox/`
- `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`
- `automation/orchestration/workers/AIOS_WORKER_PROFILES.json`
- `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json`
- `automation/orchestration/workers/*heartbeat.json`
- `automation/orchestration/runtime/logs/supervisor_cycles.jsonl`
- `apps/trading_lab/trading_lab/results/`
- `automation/operator/startup_reports/`
- `automation/operator/layout_profiles/CODEX_CAPTURED_CURRENT.json`
- source-attributed duplicate docs in `docs/AI_OS/operator*` and `docs/AI_OS/governance/`

## Next safest relocation batch

The safest physical cleanup batch, after explicit user approval, is cache-only:

1. `.pytest_cache/`
2. `**/__pycache__/`
3. `apps/dashboard/node_modules/` only if dashboard `package.json` and lockfile are retained and reinstall is acceptable.

No runtime, authority, dashboard source, Trading Lab, telemetry, worker, packet, or approval relocation should be attempted before a narrower approved patch.
