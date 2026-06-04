# Phase 17 Next APPLY Sequence

Status: future APPLY planning only

## 17.1 APPLY Automatic Packet Generator

Objective: create a local packet generator that converts a fixture goal into a Codex packet draft.
Allowed paths: `automation/orchestration/execution_pipeline/`, `docs/AI_OS/execution_pipeline/`, `schemas/aios/execution_pipeline/`.
Forbidden paths: runtime, telemetry, approval inbox, locks, memory, Night Supervisor, broker, OANDA, live trading, secrets, `.env`.
Expected files: packet generator script, packet draft fixture, validation report.
Validation: git status, run generator in DRY_RUN and validate-only, parse JSON, forbidden scan.
Commit message: `feat(aios): add execution packet generator preview`.
PR lane: `codex/phase-17-1-packet-generator`.

## 17.2 APPLY Worker Router

Objective: route packet previews to safe worker lanes.
Expected files: router fixture, worker lane taxonomy, validation report.
Validation: lane taxonomy checks, collision rules, Night Supervisor non-interference.
Commit message: `feat(aios): add execution worker router preview`.
PR lane: `codex/phase-17-2-worker-router`.

## 17.3 APPLY Validator Dispatcher

Objective: attach validator chains to packet classes.
Expected files: validator dispatcher preview, validator chain fixtures, schema updates.
Validation: no-write, dirty-tree, forbidden-path, secret, network, trading checks.
Commit message: `feat(aios): add execution validator dispatcher preview`.
PR lane: `codex/phase-17-3-validator-dispatcher`.

## 17.4 APPLY Approval Engine Preview

Objective: generate approval previews without writing to real approval inbox.
Expected files: approval preview runner, approval preview fixtures, validation report.
Validation: approval scope, expiration, risk class, no runtime approval writes.
Commit message: `feat(aios): add approval engine preview`.
PR lane: `codex/phase-17-4-approval-engine-preview`.

## 17.5 APPLY Execution Supervisor Preview

Objective: supervise the full preview lifecycle through clean-state verification.
Expected files: supervisor preview runner, supervisor state fixture, final report.
Validation: lifecycle state checks, blocked/parked/failure recovery states, final git status.
Commit message: `feat(aios): add execution supervisor preview`.
PR lane: `codex/phase-17-5-execution-supervisor-preview`.
