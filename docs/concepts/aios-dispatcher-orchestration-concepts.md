# AI_OS Dispatcher and Orchestration Concepts

Status: canonical concept summary extracted from legacy `docs/AI_OS/dispatcher` and `docs/AI_OS/orchestration`

Last reviewed: Phase 93 dispatcher/orchestration reference retirement

## Purpose

This document summarizes dispatcher and orchestration concepts from legacy `docs/AI_OS`. It is a bridge document for human review and architecture continuity, not an automation spec.

## Terminology

Current working interpretation:

- Orchestration is the broader control model.
- Dispatcher is a subsystem concept for packet routing and runtime state.
- Operator control remains above both.

This terminology is not fully settled. MAIN CONTROL should decide whether `dispatcher` remains an active subsystem name or becomes historical vocabulary.

## Core Concepts

The useful concepts are:

- work packets define units of work,
- queues/folders hold packet state,
- worker registry defines available worker roles,
- locks prevent overlapping file ownership,
- approval inbox records human-gated decisions,
- validators check safety before and after APPLY,
- commit packages recommend exact-file staging,
- summaries show status but should not own truth.

Additional durable ideas extracted during Phase 92:

- dispatcher packets need explicit lifecycle states: queued, locked, waiting approval, approved, blocked, retryable, and complete,
- dead-letter handling should separate retryable packets from poison packets and keep recovery human-readable,
- worker leases and heartbeats are runtime safety tools, not permission to run uncontrolled background work,
- runtime rebuild should derive state from checked-in registries, queues, ledgers, and reports instead of hidden process memory,
- assignment locks should fail closed when file ownership overlaps or stale lock evidence is unclear,
- validator chains should produce clear PASS, FAIL, BLOCKED, or REVIEW_REQUIRED results before commit readiness,
- recovery and resume should preserve operator control after interrupted APPLY or partial runtime state,
- display scripts are acceptable when they expose state without mutating protected paths.

## What Became Canonical

Recent cleanup made these canonical in `automation/orchestration`:

- worker registry under `workers/`,
- work packets under `work_packets/`,
- command queue under `command_queue/`,
- approval inbox under `approval_inbox/`,
- validators under `validators/`,
- commit packages under `commit_packages/`,
- control and health summaries under dedicated subfolders.

Old root fallback examples were archived to `archive/orchestration_legacy/root_examples/`.

## Active Reference Status

Phase 92 found active references from automation into both legacy doc trees. Phase 93 retired the references that were in the allowed edit scope by redirecting them to canonical docs.

Retired dispatcher references:

- `automation/dispatcher/validators/Test-AIOSDispatcherDryRun.ps1`
- `automation/operator/Test-AIOSCodexWindowSnapshot.DRY_RUN.ps1`

Retired orchestration references in allowed files:

- `automation/operator/Test-AiOsWorkflowOrchestrator.DRY_RUN.ps1`
- `automation/operator/Test-AiOsWorkerAutoRouting.DRY_RUN.ps1`
- `automation/operator/Test-AiOsPhase3State.DRY_RUN.ps1`
- root metadata/example files under `automation/orchestration/*.json` that were in scope for this phase.

Remaining blockers are outside Phase 93 allowed edits. They are listed in `docs/audits/phase-93-dispatcher-orchestration-reference-retirement.md`.

## Current Doctrine

Orchestration should:

- be display-first and approval-gated,
- keep worker boundaries clear,
- avoid overlapping edits,
- require validators before commit readiness,
- keep commit and push manual unless separately approved.

Orchestration should not:

- launch uncontrolled workers,
- run background loops without approval,
- hide state in generated reports,
- bypass human approval,
- touch broker/live trading paths.

## automation/orchestration Classification

Phase 92 classification:

- Active code: `bootstrap/`, `supervisor/`, `runtime/`, `workers/`, `work_packets/`, `validators/`, `validator_chain_runner/`, `approval_detection/`, `approval_processor/`, `approval_runner/`, `advancement/`, `router/`, `queue_runner/`, `command_queue/`, `locks/`, `clean_state/`, `commit_packages/`, `control/`, `health/`, `mission_control/`, `terminal_workstations/`, `git/`, `guard/`, `pr_gates/`, root DRY_RUN scripts, root display scripts, and root PR helper scripts.
- Active examples/state: `workers/*.json`, `workers/*heartbeat.json`, `work_packets/active/*.json`, `queue/*.json`, `approval_inbox/*.json`, `command_queue/*.json`, `locks/FILE_LOCK_REGISTRY_001.json`, `memory/AIOS_RUNTIME_MEMORY.json`, `claims/WORKER_CLAIM_REGISTRY_001.json`, `policy/AIOS_WORKER_SAFETY_POLICY.json`, and `operator/AIOS_OPERATOR_RULES.json`.
- Stale examples: root `*.v1.example.json`, root `*.example.json`, subfolder `*.example.json`, `task_cards/WORKER-*-TASK.md`, and old v1 display/example files that still mirror earlier orchestration plans.
- Logs/temp/generated candidates: `reports/*.csv`, `reports/ORCHESTRATION_STATUS_SNAPSHOT_001.md`, `PR_BODY_LAST_GENERATED.md`, `workers/logs/*.log`, generated status/check reports, and completed or blocked historical work packet JSON.
- Future cleanup targets: split generated runtime state from checked-in examples, retire v1 examples after references move to canonical docs, decide whether heartbeat files belong in source control, and archive old task cards after active packet routing is confirmed.

## Planned/Future Ideas

- one front-door operator loop,
- clearer packet lifecycle,
- consolidated validator chain,
- archive of v1 examples after direct dependencies are removed,
- dashboard visibility into orchestration state.

## Human-Review Items

- Decide dispatcher vs orchestration vocabulary.
- Decide whether v1 examples are fixtures, canonical docs, or archive candidates.
- Decide how much state belongs in `automation/orchestration` versus reports.
- Decide which display scripts remain active operator commands.
