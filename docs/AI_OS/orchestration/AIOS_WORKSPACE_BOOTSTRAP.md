# AI_OS Workspace Bootstrap

Issue #60 defines a preview-first lane restore system for AI_OS worktrees.

Source of truth:

```text
automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json
```

Session state example:

```text
automation/orchestration/terminal_workstations/AIOS_SESSION_STATE.example.json
```

Operator rulebook:

```text
docs/AI_OS/orchestration/AIOS_OPERATOR_RULEBOOK.md
automation/orchestration/operator/AIOS_OPERATOR_RULES.json
```

Daily Start route:

```text
docs/AI_OS/orchestration/AIOS_DAILY_START.md
automation/orchestration/bootstrap/Start-AiOsDay.ps1
automation/orchestration/bootstrap/Resolve-AiOsWorkspaceIntent.ps1
automation/orchestration/supervisor/Resolve-AiOsSupervisorAssignment.DRY_RUN.ps1
```

Primary one-command workflow:

```text
docs/AI_OS/orchestration/AIOS_ONE_COMMAND_WORKFLOW.md
automation/orchestration/bootstrap/Start-AiOsWork.ps1
```

Work packets:

```text
docs/AI_OS/orchestration/AIOS_WORK_PACKETS.md
automation/orchestration/work_packets/
```

Worker profiles:

```text
docs/AI_OS/orchestration/AIOS_WORKER_PROFILES.md
automation/orchestration/workers/AIOS_WORKER_PROFILES.json
automation/orchestration/workers/Get-AiOsWorkerProfiles.ps1
automation/orchestration/workers/Resolve-AiOsNeededWorkers.DRY_RUN.ps1
automation/orchestration/workers/Resolve-AiOsWorkerForPacket.DRY_RUN.ps1
```

## Lane Model

Each lane records:

- `lane_id`
- `display_title`
- `window_title`
- `tab_title`
- `path`
- `branch`
- `role`
- `emoji_marker`
- `truth_source`

`truth_source` must be `path_and_branch`.

Required user-facing lane titles:

- `CONTROL · main`
- `CREATE · codex`
- `SAVE · git`
- `ROUTE · dispatch`
- `CHECK · audit`
- `WATCH · state`
- `RULEBOOK · codex`

Do not put `filter` in user-facing names.

CONTROL must be the leftmost lane in workspace launches and restores.

Do not use generic shell titles:

- `Windows PowerShell`
- `PowerShell`
- filesystem folder names such as `aios-worker-*`
- branch names such as `phase-*`

## Truth Rule

Trust the prompt path and Git branch, not a stale terminal or tab title after `cd`.

Window titles and tab titles are operator labels only. The path and branch printed by the scripts are the source of truth for work location.

## Git And Codex Split

Git lanes are for status, diffs, validators, and commit package review. They do not start the assistant.

Codex lanes are manual work lanes. The scripts print the correct worktree and branch so the operator can start the assistant by hand after confirming the prompt and scope.

Codex lanes must never auto-run Codex. When an intent selects a Codex lane, bootstrap prints:

```text
Manual Codex lane needed: <title>
Command: cd <path>; codex
```

The bootstrap layer opens PowerShell only when `-LaunchManualShells` is passed. Preview mode is the default.

`-LaunchManualShells` opens selected lanes as Windows Terminal tabs and respects `-MaxWindows`.

Launch policy:

```text
launch_policy: windows_terminal_tab_only
fallback_policy: print_manual_command
```

The preferred launch model is one Windows Terminal window with multiple named tabs. Each tab uses `wt -w 0 new-tab` and the locked registry `tab_title`. If `wt.exe` is unavailable, scripts print manual PowerShell commands instead of opening separate PowerShell windows.

Each launched shell immediately runs:

```text
automation/orchestration/bootstrap/Set-AiOsTerminalIdentity.ps1
```

The helper reapplies the locked registry `tab_title` and `window_title` after `Set-Location`, then prints:

```text
ACTIVE LANE:
lane_id:
display_title:
path:
branch:
truth_source:
```

Codex lanes may open as shell tabs, but the scripts must never run `codex`. A Codex lane tab prints the manual command only:

```text
Manual Codex lane needed: <title>
Command: cd <path>; codex
```

## Intent Router

`Start-AiOsWorkspace.ps1` accepts a plain language intent:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -Preview -Intent "queue dispatcher automation"
```

Preview is the default behavior. `-Preview` may still be passed for clarity.

The intent router selects locked registry `lane_id` values only. The lane registry remains the source of truth for:

- `lane_id`
- `display_title`
- `window_title`
- `tab_title`
- `role`
- `path`
- `branch`

The router must not create titles, rename windows outside the registry, or invent lane names. Bootstrap resolves selected `lane_id` values against:

```text
automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json
```

Then it prints the existing registry titles. Path and branch remain the operational truth source.

Intent keyword mapping by `lane_id`:

- `queue`, `dispatcher`, `packet`, `routing` selects `route_dispatch` and `watch_state`
- `validation`, `audit`, `cleanup`, `check` selects `check_audit`
- `bootstrap`, `workspace`, `lane`, `window`, `session` selects `save_git`
- `codex`, `edit`, `feature`, `implement` selects `create_codex` as manual instruction only
- `rulebook`, `operator`, `rules`, `memory`, `instructions` selects `rulebook_codex` as manual instruction only
- no matched keyword selects `main_control` and `save_git`

`CONTROL · main` is always included in preview output.

Intent examples:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -Preview -Intent "queue dispatcher automation"
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -Preview -Intent "validation cleanup audit"
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -Preview -Intent "edit feature with codex"
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -Preview -Intent "operator rulebook memory"
```

Manual tab launch example:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -LaunchManualShells -Intent "queue dispatcher automation" -MaxWindows 3
```

Intent preview output includes:

- `Intent:`
- `Selected lanes:`
- `Manual Codex instructions:`
- `Validators suggested:`
- `Next safe action:`

## Daily Start

`Start-AiOsDay.ps1` connects the Rulebook, Intent Router, and Supervisor route for the start of a work session.

Preview command:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsDay.ps1 -Intent "complete brainstem daily start route" -MaxTabs 3
```

Daily Start prints CONTROL git status, workspace intent route, supervisor assignment preview, work packet summary, worker profile resolution, guard check recommendation, later save/PR command, suggested lanes, suggested validators, and a `WHERE TO RUN NEXT` block.

Manual launch remains explicit:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsDay.ps1 -Intent "complete brainstem daily start route" -MaxTabs 3 -LaunchManualShells
```

It opens Windows Terminal tabs only, does not start Codex, does not commit, does not push, does not create scheduled/startup tasks, and does not touch broker/API/live trading.

## One Command Workflow

`Start-AiOsWork.ps1` is the preferred operator entrypoint. It runs status, validator, packet state, packet routing, Daily Start, worker profile resolution, branch/PR awareness, main freshness checks, and then prints one chosen next safe action with exact guard, Codex, validator, and save preview commands.

The cockpit output is intentionally compact:

- `STATUS`
- `PACKETS`
- `WORKER`
- `GUARD`
- `NEXT COMMAND`
- `STOP CONDITION`

Preview command:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWork.ps1 -Intent "choose next AI_OS work"
```

## Supervisor Planner

Supervisor assignment preview:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\supervisor\Resolve-AiOsSupervisorAssignment.DRY_RUN.ps1 -Intent "complete brainstem daily start route"
```

The planner answers what workers are needed, what each worker does, what lane each worker uses, what files are in scope, what validators run, what approval is required, and the exact next safe action.

## Work Packets

Work packets persist assignments as small JSON files:

```text
automation/orchestration/work_packets/
```

Packet commands:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\work_packets\Get-AiOsWorkPacketState.ps1
powershell -ExecutionPolicy Bypass -File automation\orchestration\work_packets\Route-AiOsWorkPacket.DRY_RUN.ps1
```

The ROUTE lane acts as packet dispatcher. The WATCH lane acts as packet state observer. CONTROL remains the root lane.

Worker profiles connect packets to standing worker IDs. Packet routing must flag unknown `owner_lane` or `assigned_worker` values before work continues.

## Start Commands

Preview workspace:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -Preview
```

Open selected lane tabs manually:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -LaunchManualShells
```

Open selected intent lane tabs manually:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -LaunchManualShells -Intent "workspace session check" -MaxWindows 3
```

Preview one lane:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Open-AiOsLane.ps1 -LaneId save_git -Preview
```

Open one lane tab manually:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Open-AiOsLane.ps1 -LaneId save_git -LaunchManualShells
```

## Workspace Checkpoints

Workspace checkpoints preserve the current lane identity model for tomorrow's restore flow.

Checkpoint example:

```text
automation/orchestration/terminal_workstations/AIOS_WORKSPACE_CHECKPOINT.example.json
```

Checkpoint save preview:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Save-AiOsWorkspaceCheckpoint.ps1 -Preview
```

Checkpoint save apply:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Save-AiOsWorkspaceCheckpoint.ps1 -Apply
```

Checkpoint restore preview:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Restore-AiOsWorkspaceCheckpoint.ps1 -Preview
```

Checkpoint restore tab launch:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Restore-AiOsWorkspaceCheckpoint.ps1 -LaunchManualShells -MaxWindows 3
```

Checkpoints store:

- `checkpoint_id`
- `created_at`
- `active_workspace`
- `active_worktree`
- `active_branch`
- `launch_policy`
- `fallback_policy`
- lane identity fields from the registry
- `last_commands`
- `pending_workorders`
- `last_validator_status`
- `next_safe_action`

Restore resolves checkpoint `lane_id` values back through the locked registry and prints exactly what would reopen. Path and branch remain the operational truth source.

## Session Save And Restore

Preview session metadata:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Save-AiOsSession.ps1 -Preview
```

Write session metadata:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Save-AiOsSession.ps1 -Apply
```

Restore preview:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Restore-AiOsSession.ps1 -Preview
```

Restore manual shells:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Restore-AiOsSession.ps1 -LaunchManualShells
```

## Preview Versus Launch

Preview mode prints:

- `git worktree list`
- `lane_id`, `display_title`, `window_title`, `tab_title`, `emoji_marker`, and `truth_source`
- path and branch
- last session commands
- next safe action

Launch mode opens Windows Terminal tabs only. It does not mutate Git state, does not start assistant tooling, and does not run background launch hooks.

## Copy Markers

Report scripts print copy markers:

```text
COPY START — <script>
COPY END — <script>
```

Marker-enabled scripts:

- `Start-AiOsWorkspace.ps1`
- `Start-AiOsDay.ps1`
- `Open-AiOsLane.ps1`
- `Set-AiOsTerminalIdentity.ps1`
- `Save-AiOsSession.ps1`
- `Restore-AiOsSession.ps1`
- `Save-AiOsWorkspaceCheckpoint.ps1`
- `Restore-AiOsWorkspaceCheckpoint.ps1`
- `Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1`

## Operator Workflow

1. Run the validator:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1
```

2. Preview the workspace:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -Preview
```

3. Confirm the intended lane, path, and branch.

4. Open lane shells only if the preview is correct:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -LaunchManualShells
```

5. Start any assistant session manually in the correct lane after reading the role and branch.

6. Save session metadata when the work state changes:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Save-AiOsSession.ps1 -Apply
```

7. Restore by preview first:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Restore-AiOsSession.ps1 -Preview
```
