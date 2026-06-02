# Worker Registry Canonical Map

Date: 2026-06-01
Packet: AIOS-P22

## 1. Canonical Profile Store

Canonical file: `automation/orchestration/workers/AIOS_WORKER_PROFILES.json`

This file defines worker profile authority for orchestration assignment, including `owns_paths`, lane identity, overlap rules, and apply gate expectations. Packet-assigned workers such as `dispatcher` and `codex_worker_1` must resolve here before they are treated as valid orchestration worker identities.

For parallel human-supervised work, this file is the only worker ownership source. A Codex window may display any local title, but it does not own files until its `worker_id`, lane, allowed paths, blocked paths, and stop point resolve through this profile store and the current packet.

## 2. Runtime State Store

Runtime file: `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`

This file tracks runtime worker state such as `supervisor_loop`, `pr_gate`, validator, health, and daemon-style workers. These are runtime state records, not packet assignment profiles.

## 3. Window Identity Store

Window file: `automation/window_identity/AIOS_WORKER_REGISTRY.json`

This file identifies operator/window-level worker slots for UI and local session coordination. It is not the orchestration execution profile store and should not be used to resolve active packet `assigned_worker` values.

Canonical replacement for orchestration worker authority: `automation/orchestration/workers/AIOS_WORKER_PROFILES.json`.
The window identity registry is presentation-only. It may show Main Control, Claude Reviewer, and Codex worker labels, but it must not grant APPLY, queue mutation, runtime launch, commit, push, merge, scheduler, trading, broker, OANDA, API-key, or secret authority.

Historical compatibility evidence may still exist at `automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json`. Keep it until adapter-first registry use is fully proven and Human Owner retirement approval is granted.

## 4. Safe 8-Window Ownership Map

The safe 8-window operating map is:

| Window | Canonical role | Ownership rule |
|---|---|---|
| Main Control | Human command and final approval lane | No file ownership by default; reviews status, approvals, validator evidence, and protected actions |
| Claude Reviewer | Read-only architecture/risk reviewer | No file edits unless a separate APPLY packet assigns exact files |
| Codex Worker 1 | East orchestration worker registry lane | Packet-scoped ownership only for `automation/orchestration/workers/` and related worker ownership governance files |
| Codex Worker 2 | Workflow lane | Packet-scoped ownership only for assigned `docs/workflows/` files |
| Codex Worker 3 | Governance lane | Packet-scoped ownership only for assigned `docs/governance/` files |
| Codex Worker 4 | Validator/schema lane | Packet-scoped ownership only for assigned validator and schema files |
| Codex Worker 5 | Dashboard UI lane | Packet-scoped UI ownership only; no runtime, telemetry persistence, broker, or trading execution authority |
| Codex Worker 6 | Audit/reporting lane | Packet-scoped ownership only for assigned audit/reporting files |

Trading Lab, runtime, scheduler, approval mutation, and active packet-state mutation remain unassigned unless a separate packet explicitly grants a bounded lane and Human Owner approval.

## 5. Superseded Stub

Superseded file: `automation/orchestration/workers/WORKER_REGISTRY.json`

This file was never populated and remains empty. Do not add new workers to it. Worker profiles live in `AIOS_WORKER_PROFILES.json`; runtime worker state lives in `AIOS_WORKER_REGISTRY.json`.

Canonical replacement: `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`.
