# Proposed Request Packet: Heartbeat Dirty-Write Guard After First Scheduled Fire

Status: PROPOSED / REVIEW-ONLY / NOT EXECUTABLE

This file is not an executable Codex packet. It does not authorize running `AIOS_Relay_Nightly`, querying or changing the scheduled task, invoking the night-cycle script, launching runtime, executing runtime, mutating queues, sending SOS, touching broker or live-trading paths, accessing credentials, storing secrets, deleting files, pushing to `main`, merging, or closing a PR.

## Purpose

Request a future, separate APPLY lane to fix or normalize `telemetry/runtime/runtime_heartbeat.json` write behavior so the next natural scheduled-fire validation can leave the active repo clean.

## Source Evidence

- First-fire proof report: `Reports/autonomy_loop_closure/first_scheduled_fire_proof_after_scheduler_enable.json`
- Human-readable first-fire proof: `Reports/autonomy_loop_closure/first_scheduled_fire_proof_after_scheduler_enable.md`
- Night report: `telemetry/night_supervisor/reports/night_summary_2026-06-11.json`

## Problem Statement

The first natural scheduled-fire proof showed:

- Scheduler fire: `PASS`
- AI_OS reached: `PASS`
- Safety gates held: `PASS`
- Supervisor status: `BLOCKED`
- Execution result: `FAIL`
- Validator status: `FAIL`
- Dirty file: `telemetry/runtime/runtime_heartbeat.json`

The immediate failure class is `CONTROLLED_VALIDATOR_BLOCK`: the scheduled run reached AI_OS and stopped safely because validator automation detected the heartbeat dirty-write behavior.

## Future APPLY Lane Requirements

Any future heartbeat guard packet must include:

- `CODEX-ONLY PROMPT`
- `AI_OS EXECUTION TOKEN`
- `AI_OS BOOTSTRAP REQUIRED`
- identity marker
- supervisor identity
- packet ID
- mode: `APPLY`
- zone
- worker identity
- lane
- worktree
- branch
- exact allowed paths
- exact forbidden paths
- explicit Anthony approval
- validator chain
- stop point
- mission
- preflight
- final report format

The future APPLY lane must inspect the current owner of heartbeat writes before editing. It must choose the smallest safe fix that prevents scheduled-fire validation from leaving `telemetry/runtime/runtime_heartbeat.json` dirty on `main`.

Acceptable fix directions to evaluate:

- make the heartbeat write idempotent when content would not materially change;
- write scheduled-run heartbeat evidence to an approved sandbox/report path instead of active runtime state during DRY_RUN validation;
- normalize or restore the heartbeat file before validator `git diff --check` runs, only if that does not hide meaningful runtime state;
- update the validator flow so expected heartbeat writes are handled without leaving the repo dirty.

## Required Forbidden Boundaries

The future packet must explicitly forbid:

- running `AIOS_Relay_Nightly`;
- querying or changing the scheduled task unless separately approved;
- invoking the night-cycle script directly;
- manual runtime launch;
- manual runtime execution;
- active packet, approval, worker inbox, or command queue mutation unless separately approved;
- SOS send by Codex;
- broker action;
- live trading;
- credential access;
- secret storage;
- ntfy topic, token, private URL, or secret-like routing storage;
- destructive cleanup;
- direct push to `main`;
- merge;
- PR closure.

## Required Validation

The future APPLY lane must validate at minimum:

- `git diff --check`
- JSON parse for any JSON file it changes
- PowerShell parse for any PowerShell file it changes
- `git status --short --branch`
- forbidden path check proving no queue, approval inbox, worker inbox, command queue, broker, live trading, secret, dashboard, or unrelated telemetry files changed

## Stop Point

Stop after producing the heartbeat dirty-write guard fix, validation evidence, and final report. Do not run the scheduled task or runtime to prove the next fire unless Anthony separately approves a later first-fire validation packet.

## Safe Next Action

Create a future executable APPLY packet that targets only the heartbeat writer or validator logic responsible for `telemetry/runtime/runtime_heartbeat.json` dirty-write behavior.
