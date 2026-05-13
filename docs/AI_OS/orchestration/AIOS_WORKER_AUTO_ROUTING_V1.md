# AI_OS Worker Auto-Routing V1

## Purpose

Worker auto-routing connects the workflow orchestrator to the 8-window DRY_RUN launcher.

The operator runs the orchestrator once. The orchestrator writes the normal operator packet and also writes one worker routing packet:

```text
Reports/operator/AIOS_WORKER_ROUTING_PACKET.json
```

The launcher reads that routing packet so each worker window receives its role, lane, allowed paths, blocked paths, task, report path, validation commands, and stop condition without manual prompt copy and paste.

## Routing Packet Fields

Each worker route includes:

- `worker_id`
- `label`
- `lane`
- `allowed_paths`
- `blocked_paths`
- `dry_run_task`
- `report_path`
- `validation_commands`
- `stop_condition`

Worker 8 remains review-only with `DRY_RUN_ONLY_REVIEW_ONLY`.

## Launcher Behavior

`Start-AiOsParallelDryRunCrew.ps1` checks for:

```text
Reports/operator/AIOS_WORKER_ROUTING_PACKET.json
```

If the routing packet exists, the launcher uses it.

If the routing packet is missing, the launcher falls back to:

```text
automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json
```

## Codex Prompt Delivery

If Codex launch is enabled, each worker receives its assigned routing task inside the worker prompt.

Because the Codex prompt argument name is still `UNKNOWN`, the launcher passes the prompt through:

```powershell
$env:AIOS_CODEX_WORKER_PROMPT
```

## Safety Boundary

Auto-routing is DRY_RUN only.

It does not grant permission to APPLY, commit, push, stage files, connect brokers, use API keys, store secrets, or enable live trading.

Every worker stop condition remains:

```text
Produce DRY_RUN report only. No APPLY, no commit, no push.
```

## Validation

Run:

```powershell
powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsWorkerAutoRouting.DRY_RUN.ps1
powershell -ExecutionPolicy Bypass -File automation/operator/Invoke-AiOsWorkflowOrchestrator.ps1
git diff --check
git status --short --branch
```

The launcher can be tested manually after reviewing the routing packet:

```powershell
powershell -ExecutionPolicy Bypass -File automation/operator/Start-AiOsParallelDryRunCrew.ps1
```
