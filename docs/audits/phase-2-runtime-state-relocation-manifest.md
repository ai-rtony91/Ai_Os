# Phase 2 Runtime State Relocation Manifest

## Purpose

This manifest separates runtime/generated-state candidates from authority/code areas before any physical relocation.

No files are approved for movement by this manifest. Every proposed relocation requires dependency validation and user approval.

## Runtime state that must remain in place for now

| Current path | Proposed path | Dependency risk | Connected systems | Classification | Why safe/unsafe | Validation required before move |
|---|---|---:|---|---|---|---|
| `telemetry/runtime/runtime_state.json` | keep current | high | `scripts/control/Get-AiOsRuntimeStatus.ps1`, `scripts/control/Get-AiOsRuntimeHealth.ps1`, `services/orchestrator/runtimeApiService.js` | KEEP ACTIVE | Unsafe to move; active readers are known | Runtime status, health, and API smoke checks |
| `telemetry/runtime/runtime_heartbeat.json` | keep current | high | Runtime health/status scripts, orchestrator API | KEEP ACTIVE | Unsafe to move; active health dependency | Runtime health check |
| `telemetry/runtime/runtime_process.json` | keep current | high | `scripts/control/Start-AiOsRuntime.ps1`, `Stop-AiOsRuntime.ps1`, status scripts | KEEP ACTIVE | Unsafe to move; process control dependency | Start/stop/status dry validation |
| `telemetry/work_ledger.jsonl` | keep current | high | `services/telemetry/*`, `services/orchestrator/runtimeApiService.js`, telemetry replay | KEEP ACTIVE | Unsafe to move; active ledger dependency | Telemetry replay/API validation |
| `automation/orchestration/work_packets/active/` | keep current | high | Packet advancement, queue displays, worker routing | KEEP ACTIVE | Unsafe to move; active packet state | Packet state/read model validators |
| `automation/orchestration/work_packets/blocked/` | keep current | high | Packet lifecycle | KEEP ACTIVE | Unsafe to move; active packet state | Packet lifecycle validation |
| `automation/orchestration/work_packets/complete/` | keep current until retention policy | medium | Packet history/evidence | KEEP ACTIVE | Moving could break history readers | Packet state display validation |
| `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json` | keep current | high | Approval inbox display/gate flow | KEEP ACTIVE | Unsafe to move; active approval source | Approval inbox validator |
| `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json` | keep current | high | Apply approval gate | KEEP ACTIVE | Unsafe to move; active approval source | Approval gate validator |
| `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json` | keep current | high | Worker address book, router, builder, status | KEEP ACTIVE | Unsafe to move; canonical active registry | Worker registry validators |
| `automation/orchestration/workers/AIOS_WORKER_PROFILES.json` | keep current | high | Packet routing and worker resolution | KEEP ACTIVE | Unsafe to move; active profile source | Worker profile validator |
| `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json` | keep current | high | Inbox, safe execute, completion, state updates | KEEP ACTIVE | Unsafe to move; active worker inbox | Worker inbox validator |

## Generated-state relocation candidates

| Current path | Proposed path | Dependency risk | Connected systems | Classification | Why safe/unsafe | Validation required before move |
|---|---|---:|---|---|---|---|
| `automation/orchestration/workers/*heartbeat.json` | `telemetry/workers/` or generated runtime state area | medium | Stale worker and status scripts | REMOVE/RELOCATE CANDIDATE | Looks generated, but active readers may expect current path | Search references; run worker status/stale checks |
| `automation/orchestration/runtime/logs/supervisor_cycles.jsonl` | `telemetry/runtime/supervisor_cycles.jsonl` | medium | Persistent runtime supervisor | REMOVE/RELOCATE CANDIDATE | Generated audit log; writer path is hardcoded today | Update only after writer/reader validation |
| `telemetry/runtime/runtime_stdout.log` | keep or rotate under `telemetry/runtime/logs/` | medium | Start runtime script | REMOVE/RELOCATE CANDIDATE | Generated log; path is written by control script | Runtime start/status validation |
| `telemetry/runtime/runtime_stderr.log` | keep or rotate under `telemetry/runtime/logs/` | medium | Start runtime script | REMOVE/RELOCATE CANDIDATE | Generated log; path is written by control script | Runtime start/status validation |
| `approval.json` | `automation/orchestration/approval_inbox/` or archive evidence | medium | Unknown | NEEDS USER DECISION | Root state-like file; dependency unknown | Full reference search |
| `completion_report.json` | `validation/` or audit evidence | medium | Unknown | NEEDS USER DECISION | Root report-like artifact | Full reference search and JSON parse |
| `validation_result.json` | `validation/` | medium | Unknown | NEEDS USER DECISION | Root validator output candidate | Full reference search and JSON parse |
| `task_log.json` | `telemetry/` or `logs/` | medium | Unknown | NEEDS USER DECISION | Root runtime/task state candidate | Full reference search and JSON parse |
| `apps/trading_lab/trading_lab/results/` | `apps/trading_lab/data/reports/` or `telemetry/trading_lab/` | medium | Dashboard fixtures and Trading Lab evidence | REMOVE/RELOCATE CANDIDATE | Generated paper evidence, but referenced by dashboard mock data | Reference search, Trading Lab tests, dashboard fixture check |
| `automation/operator/startup_reports/` | `logs/operator/` or `docs/audits/` selected summaries | low | Operator startup evidence | REMOVE/RELOCATE CANDIDATE | Generated reports; dependency unknown | Reference search |
| `automation/operator/layout_profiles/CODEX_CAPTURED_CURRENT.json` | `telemetry/workstation/` or generated layout state | low | Window layout experiments | REMOVE/RELOCATE CANDIDATE | Captured state, not authority | Reference search |
| `.pytest_cache/` | none | low | Pytest cache | REMOVE/RELOCATE CANDIDATE | Generated cache | Delete only after approval |
| `apps/dashboard/node_modules/` | none | low | Dashboard local install | REMOVE/RELOCATE CANDIDATE | Installed dependencies | Confirm lockfile and reinstall path |
| `**/__pycache__/` | none | low | Python runtime cache | REMOVE/RELOCATE CANDIDATE | Generated cache | Delete only after approval |

## Authority areas that must not receive runtime state

| Path | Classification | Rule |
|---|---|---|
| `docs/governance/` | KEEP ACTIVE | Governance docs only |
| `docs/workflows/` | KEEP ACTIVE | Workflow docs only |
| `docs/security/` | KEEP ACTIVE | Security docs only |
| `docs/architecture/` | KEEP ACTIVE | Architecture docs only |
| `docs/audits/` | KEEP ACTIVE | Audit records only; no active runtime state |
| `AGENTS.md` | KEEP ACTIVE | Behavior authority only |
| `README.md` | KEEP ACTIVE | Human front door only |

## Runtime areas that must not become authority

| Path | Classification | Rule |
|---|---|---|
| `telemetry/` | KEEP ACTIVE | Runtime/evidence only |
| `logs/` | NEEDS USER DECISION | Generated logs only |
| `proof/` | KEEP ACTIVE | Evidence only |
| `validation/` | NEEDS USER DECISION | Validator outputs only |
| `automation/orchestration/work_packets/` | KEEP ACTIVE | Packet state only |
| `automation/orchestration/workers/*heartbeat.json` | REMOVE/RELOCATE CANDIDATE | Heartbeat state only |
| `apps/trading_lab/trading_lab/results/` | REMOVE/RELOCATE CANDIDATE | Trading Lab paper output evidence only |

## Safe relocation order

1. Search references for each candidate path.
2. Classify each candidate as active input, generated output, or evidence.
3. Create an explicit approved move manifest.
4. Add compatibility read fallback only if needed and explicitly approved.
5. Move one candidate family at a time.
6. Validate JSON parses for moved JSON.
7. Run affected readers and validators.
8. Run `git diff --check`.
9. Report status before commit approval.

## Stop conditions

Stop and do not move when:

- A path is hardcoded in runtime control scripts.
- A path is hardcoded in orchestrator API services.
- A path is used by packet routing, worker routing, approval gates, or telemetry replay.
- A path has unknown references.
- A path contains paper Trading Lab safety evidence.
- A path may be required for proof or validation continuity.
