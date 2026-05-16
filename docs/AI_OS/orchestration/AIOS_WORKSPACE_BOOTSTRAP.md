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
- `BOOTSTRAP · git`
- `BOOTSTRAP · codex`
- `VALIDATE · audit`
- `DISPATCH · queue`
- `STATE · monitor`

Do not put `filter` in user-facing names.

## Truth Rule

Trust the prompt path and Git branch, not a stale terminal or tab title after `cd`.

Window titles and tab titles are operator labels only. The path and branch printed by the scripts are the source of truth for work location.

## Git And Codex Split

Git lanes are for status, diffs, validators, and commit package review. They do not start the assistant.

Codex lanes are manual work lanes. The scripts print the correct worktree and branch so the operator can start the assistant by hand after confirming the prompt and scope.

The bootstrap layer opens PowerShell only when `-LaunchManualShells` is passed. Preview mode is the default.

## Start Commands

Preview workspace:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -Preview
```

Open all lane shells manually:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -LaunchManualShells
```

Preview one lane:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Open-AiOsLane.ps1 -LaneId bootstrap_git -Preview
```

Open one lane shell manually:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Open-AiOsLane.ps1 -LaneId bootstrap_git -LaunchManualShells
```

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

Launch mode opens PowerShell shells only. It does not mutate Git state, does not start assistant tooling, and does not run background launch hooks.

## Copy Markers

Report scripts print copy markers:

```text
COPY START — <script>
COPY END — <script>
```

Marker-enabled scripts:

- `Start-AiOsWorkspace.ps1`
- `Open-AiOsLane.ps1`
- `Save-AiOsSession.ps1`
- `Restore-AiOsSession.ps1`
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
