# AI_OS Guard Safety Wrapper

`Invoke-AiOsGuard.ps1` is a lightweight preview-only guard for risky AI_OS operator actions.

It prevents common mistakes before the operator proceeds:

- wrong path
- wrong branch
- wrong lane
- git save or merge from `main` without explicit allowance
- Codex worker activity from `main_control`
- commands that require `-Apply` but were started without `-Apply`
- validation while files are already staged
- protected root file changes that require explicit approval

## Script

```text
automation/orchestration/guard/Invoke-AiOsGuard.ps1
```

## Parameters

- `-ExpectedPath`
- `-ExpectedBranch`
- `-ExpectedLaneId`
- `-CommandType`
- `-AllowMain`
- `-RequireApply`
- `-Apply`

`CommandType` values:

- `codex`
- `git_status`
- `git_save`
- `launch`
- `validate`
- `merge`
- `packet_update`

## Behavior

- Preview/check-only by default.
- Never mutates files.
- Never stages, commits, pushes, launches, or merges.
- Never runs the target command.
- Prints `COPY START` / `COPY END`.
- Prints current path, current branch, expected path, expected branch, expected lane, result, and `WHERE TO RUN NEXT`.
- Returns `PASS` only when all supplied expectations match and no blocking rule fails.

## Protected Root Files

Changes to these files are warned and require explicit approval before continuing:

- `README.md`
- `ERROR_LOG.md`
- `package.json`
- `package-lock.json`
- `.gitignore`

## Examples

Preview validate from the expected brainstem path:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\guard\Invoke-AiOsGuard.ps1 -ExpectedPath "C:\Users\mylab\OneDrive\GitHub\aios-worker-brainstem" -CommandType validate
```

Preview a git save guard that must match `main` and will also block saving on `main` unless `-AllowMain` is supplied:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\guard\Invoke-AiOsGuard.ps1 -ExpectedBranch main -CommandType git_save
```

## Next Safe Action

WHERE: visible tab/window for the intended lane

Path: expected repo root

Run:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\guard\Invoke-AiOsGuard.ps1 -ExpectedPath "<repo path>" -ExpectedBranch "<branch>" -ExpectedLaneId "<lane_id>" -CommandType validate
```
