# AI_OS Worker Profiles

Worker profiles connect intent, work packets, supervisor planning, guard checks, and save automation without opening every possible worker.

## Files

```text
automation/orchestration/workers/AIOS_WORKER_PROFILES.json
automation/orchestration/workers/Get-AiOsWorkerProfiles.ps1
automation/orchestration/workers/Resolve-AiOsNeededWorkers.DRY_RUN.ps1
automation/orchestration/workers/Resolve-AiOsWorkerForPacket.DRY_RUN.ps1
```

## Fields

Each worker profile contains:

- `worker_id`
- `display_title`
- `worker_type`
- `default_path`
- `default_branch`
- `owns_paths`
- `blocked_paths`
- `can_run_parallel_with`
- `cannot_overlap_with`
- `launch_policy`
- `codex_policy`
- `guard_policy`
- `save_policy`
- `safety_notes`

## Standing Workers

- `main_control`
- `create_codex`
- `save_git`
- `route_dispatch`
- `check_audit`
- `watch_state`
- `rulebook_codex`
- `brainstem_codex`
- `safety_codex`
- `orchestration_codex`
- `forex_sim_codex`
- `risk_codex`
- `strategy_codex`

Forex workers are profiles only for now. They are not active trading workers, do not add secrets, and do not enable broker/API/live trading.

## Connector Flow

Daily Start answers:

1. What work packets exist.
2. Which packet should be worked next.
3. Which standing worker profile owns it.
4. Which path and branch should be used.
5. Which validator should run.
6. Which guard check applies.
7. Which save/PR command will be used later.

## Commands

List profiles:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\workers\Get-AiOsWorkerProfiles.ps1
```

Resolve needed workers:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\workers\Resolve-AiOsNeededWorkers.DRY_RUN.ps1 -Intent "resume AI_OS orchestration"
```

Resolve a worker for one packet:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\workers\Resolve-AiOsWorkerForPacket.DRY_RUN.ps1 -PacketId "brainstem-daily-start"
```

## Rules

- Do not open all workers by default.
- Resolve workers from intent or active work packets.
- One writer per overlapping file zone.
- CONTROL remains fixed root.
- Codex workers are manual only.
- Git/save worker handles save/PR automation.
- No secrets.
- No background services, daemons, or scheduled tasks.

## Next Safe Action

WHERE: visible tab/window `SAVE · git`

Path: repo root

Run:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1
```
