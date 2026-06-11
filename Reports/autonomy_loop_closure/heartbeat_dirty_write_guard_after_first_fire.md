# Heartbeat Dirty-Write Guard After First Fire

Status: HEARTBEAT DIRTY-WRITE GUARD READY FOR REVIEW

Packet: AIOS-HEARTBEAT-DIRTY-WRITE-GUARD-APPLY-V1
Lane: heartbeat-dirty-write-guard
Mode: APPLY

## Root Cause

The first scheduled-fire proof showed `telemetry/runtime/runtime_heartbeat.json` as the only dirty file. That file is tracked. The current writer was `Write-AiOsRuntimeHeartbeat` in `automation/orchestration/Invoke-AiOsNightCycle.ps1`.

The writer always wrote the active tracked heartbeat path, including observe-only DRY_RUN scheduled runs where `effective_apply` was false. The timestamp update made `main` dirty and caused scheduled-fire validation to fail `git diff --check`.

## Fix Applied

The night-cycle writer now resolves the target heartbeat path before writing:

- observe-only or ineffective APPLY runs write heartbeat evidence to `%TEMP%/AIOS_NIGHT_CYCLE/runtime_heartbeat.<cycle_id>.observe_only.json`;
- effective APPLY runs preserve the active `telemetry/runtime/runtime_heartbeat.json` heartbeat behavior;
- heartbeat schema and active heartbeat functionality are not removed.

This uses fix strategy B from the packet: skip active tracked heartbeat mutation when `effective_apply` is false or `observe_only` is true.

## Tests

Updated `tests/orchestration/test_night_cycle_endurance_contract.py` to prove:

- the night cycle still defines the runtime heartbeat schema;
- the observe-only guard exists;
- observe-only heartbeat evidence is routed to the temp evidence path;
- the old direct active heartbeat write is not used for observe-only/effective_apply false paths;
- no scheduler or task execution is required.

## Safety Status

- No `AIOS_Relay_Nightly` run.
- No Task Scheduler query or mutation.
- No direct night-cycle invocation.
- No manual runtime launch or execution.
- No queue, approval inbox, worker inbox, command queue, or active packet mutation.
- No SOS send.
- No broker action or live trading.
- No credential or secret access.
- No ntfy topic, token, private URL, or secret-like routing value stored.
- No `telemetry/runtime/` mutation by Codex.
- No `telemetry/night_supervisor/` mutation by Codex.
- No dashboard mutation.
- No destructive cleanup.
- No direct push to `main`.
- No merge.
- No PR closure.

## Next Safe Action

Review the code fix in PR, then use a separate approved scheduled-fire retry packet to re-enable or observe the next natural scheduled fire.

Proposed next packet: `automation/orchestration/work_packets/proposed/AIOS-SCHEDULED-FIRE-RETRY-AFTER-HEARTBEAT-GUARD.md`
