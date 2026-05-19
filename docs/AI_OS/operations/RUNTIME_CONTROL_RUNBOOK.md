# Runtime Control Runbook

Status: CURRENT
Mode: Operations documentation

## Purpose

This runbook documents the actual runtime controls available from `scripts/control` and the runtime bootstrap under `services/runtime`.

Runtime control is local-first. It writes local state and heartbeat files. It does not approve APPLY, stage files, commit, push, merge, connect brokers, use API keys, or place orders.

## Runtime Startup

Foreground or bounded startup:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\control\Start-AiOsRuntime.ps1 -Once
powershell -ExecutionPolicy Bypass -File scripts\control\Start-AiOsRuntime.ps1 -MaxTicks 3
```

Background startup:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\control\Start-AiOsRuntime.ps1 -Background
```

Optional clean-state gate:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\control\Start-AiOsRuntime.ps1 -RequireCleanState
```

## Runtime Shutdown

Preview stop status:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\control\Stop-AiOsRuntime.ps1
```

Stop a recorded background runtime:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\control\Stop-AiOsRuntime.ps1 -Force
```

If the runtime is running in the foreground, stop it with `Ctrl+C` in that terminal.

## Runtime Status

```powershell
powershell -ExecutionPolicy Bypass -File scripts\control\Get-AiOsRuntimeStatus.ps1
```

This reads:

- `telemetry/runtime/runtime_state.json`
- `telemetry/runtime/runtime_heartbeat.json`
- `telemetry/runtime/runtime_process.json`

## Runtime Health

```powershell
powershell -ExecutionPolicy Bypass -File scripts\control\Get-AiOsRuntimeHealth.ps1
```

This checks:

- runtime state
- runtime heartbeat freshness
- automation queue counts
- telemetry ledger parse health

## Runtime Internals

The Node runtime starts at:

- `services/runtime/runtimeBootstrap.js`

Runtime startup restores packets from telemetry, writes runtime state, writes heartbeat, emits heartbeat ticks, and shuts down on bounded completion or signal.

The TypeScript runtime loop model in `services/runtime` connects:

- telemetry replay
- dispatcher state rebuild
- resume planning
- scheduling
- supervisor evaluation
- backpressure
- remediation planning

## Runtime State Files

Runtime writes local operational state under:

```text
telemetry/runtime/
```

Important files:

- `runtime_state.json`
- `runtime_heartbeat.json`
- `runtime_process.json`
- `runtime_stdout.log`
- `runtime_stderr.log`

## Stop Conditions

Stop runtime work when:

- heartbeat is missing or stale
- runtime state is missing and runtime is expected to be active
- runtime status is `degraded`, `blocked`, or `failed`
- telemetry ledger has invalid JSON lines
- queue state is not understood
- a recovery action would resume APPLY, release locks, or reassign packets without approval

## Next Safe Action

Check status and health before starting or stopping runtime work.
