# Worker Registry Canonical Map

Date: 2026-06-01
Packet: AIOS-P22

## 1. Canonical Profile Store

Canonical file: `automation/orchestration/workers/AIOS_WORKER_PROFILES.json`

This file defines worker profile authority for orchestration assignment, including `owns_paths`, lane identity, overlap rules, and apply gate expectations. Packet-assigned workers such as `dispatcher` and `codex_worker_1` must resolve here before they are treated as valid orchestration worker identities.

## 2. Runtime State Store

Runtime file: `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`

This file tracks runtime worker state such as `supervisor_loop`, `pr_gate`, validator, health, and daemon-style workers. These are runtime state records, not packet assignment profiles.

## 3. Window Identity Store

Window file: `automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json`

This file identifies operator/window-level worker slots for UI and local session coordination. It is not the orchestration execution profile store and should not be used to resolve active packet `assigned_worker` values.

Canonical replacement for orchestration worker authority: `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`.
The operator/window registry remains an active legacy-mixed dependency until an operator dependency review reroutes consumers safely.

## 4. Superseded Stub

Superseded file: `automation/orchestration/workers/WORKER_REGISTRY.json`

This file was never populated and remains empty. Do not add new workers to it. Worker profiles live in `AIOS_WORKER_PROFILES.json`; runtime worker state lives in `AIOS_WORKER_REGISTRY.json`.

Canonical replacement: `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`.
