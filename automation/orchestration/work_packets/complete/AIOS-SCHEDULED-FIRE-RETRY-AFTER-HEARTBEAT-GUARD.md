# Proposed Request Packet: Scheduled Fire Retry After Heartbeat Guard

Status: PROPOSED / REVIEW-ONLY / NOT EXECUTABLE

This file is not an executable Codex packet. It does not authorize running `AIOS_Relay_Nightly`, querying or changing the scheduled task, enabling or disabling the scheduled task, invoking the night-cycle script, launching runtime, executing runtime, mutating queues, sending SOS, touching broker or live-trading paths, accessing credentials, storing secrets, deleting files, pushing to `main`, merging, or closing a PR.

## Purpose

Request a future, separate human-approved evidence lane to retry the natural scheduled-fire proof after the heartbeat dirty-write guard lands.

## Source Evidence

- First-fire proof: `Reports/autonomy_loop_closure/first_scheduled_fire_proof_after_scheduler_enable.json`
- Heartbeat guard report: `Reports/autonomy_loop_closure/heartbeat_dirty_write_guard_after_first_fire.json`
- Guarded writer: `automation/orchestration/Invoke-AiOsNightCycle.ps1`

## Retry Preconditions

A future retry packet must confirm:

- the heartbeat guard PR is merged to `main`;
- `main` is clean and synced with `origin/main`;
- `telemetry/runtime/runtime_heartbeat.json` is clean before retry observation;
- Anthony explicitly approves any Task Scheduler enablement or observation step required for the retry;
- no scheduler run or night-cycle invocation is performed manually by Codex.

## Required Future Packet Fields

Any future retry packet must include:

- `CODEX-ONLY PROMPT`
- `AI_OS EXECUTION TOKEN`
- `AI_OS BOOTSTRAP REQUIRED`
- identity marker
- supervisor identity
- packet ID
- mode
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

## Required Forbidden Boundaries

The future packet must explicitly forbid:

- manual task run by Codex;
- direct night-cycle invocation by Codex;
- manual runtime launch;
- manual runtime execution;
- queue mutation unless separately approved;
- approval inbox, worker inbox, command queue, or active packet mutation unless separately approved;
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

## Retry Evidence Minimum

The future retry lane must record:

- task state evidence supplied or explicitly approved for collection;
- night report evidence after the natural scheduled fire;
- whether AI_OS was reached;
- whether `telemetry/runtime/runtime_heartbeat.json` stayed clean;
- whether `git diff --check` passed;
- whether forbidden write attempts remained zero;
- whether broker/live trading, credentials, secrets, queue mutation, SOS, dashboard mutation, and destructive cleanup remained blocked.

## Stop Point

Stop after recording retry evidence and validation. Do not perform scheduler enablement, scheduler disablement, manual task run, runtime launch, commit, push, PR creation, merge, or PR closure unless the future packet separately and explicitly authorizes that exact action.

## Safe Next Action

After this heartbeat guard PR is reviewed and merged, prepare a new tokenized scheduled-fire retry evidence packet with exact Task Scheduler approval boundaries.
