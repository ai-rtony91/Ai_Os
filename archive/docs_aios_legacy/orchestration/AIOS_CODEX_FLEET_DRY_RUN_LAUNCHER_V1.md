# AI_OS Codex Fleet DRY_RUN Launcher V1

## Purpose

The AI_OS parallel worker launcher opens a labeled PowerShell window for each registered worker in `automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json`.

Each worker is assigned a lane, allowed paths, blocked paths, report target, and DRY_RUN-only prompt seed. The launcher is for inspection and planning only. It does not authorize APPLY, commits, pushes, live trading, broker actions, API keys, or secrets work.

## Registry-Controlled Codex Launch

Codex launch behavior is controlled by the registry `codex_launch` block:

```json
{
  "enabled": true,
  "command": "codex",
  "arguments": ["--cd", "C:\\Users\\mylab\\OneDrive\\GitHub\\ai-rtony91_Ai_Os_CLEAN"],
  "fallback_to_instruction_window": true,
  "prompt_argument_name": "UNKNOWN"
}
```

When enabled, the launcher checks for the configured `codex` command. If the command is available, each worker window launches Codex with the configured registry arguments.

Because `prompt_argument_name` is `UNKNOWN`, the launcher does not guess a CLI prompt flag. Instead, it places the worker prompt in:

```powershell
$env:AIOS_CODEX_WORKER_PROMPT
```

The worker window still prints the worker assignment and safety rules in plain English.

## Fallback Behavior

If `codex` is not found, the worker window remains open as an instruction window. The operator can read the lane, allowed paths, blocked paths, report target, and DRY_RUN-only prompt.

The registry keeps `fallback_to_instruction_window` set to `true` so missing Codex does not cause unsafe behavior or silent failure.

## Why APPLY Is Still Blocked

Every registered worker remains `DRY_RUN_ONLY` or `DRY_RUN_ONLY_REVIEW_ONLY`.

The launcher prompt tells every worker:

- inspect only the assigned lane
- produce DRY_RUN findings only
- list planned files and validation commands
- do not APPLY
- do not commit
- do not push
- do not touch protected root files

The launcher does not contain any apply command and does not grant workers permission to edit files.

## Commit and Push Control

Commits and pushes still require operator approval.

The registry keeps these safety controls:

- `git_add_dot_allowed`: `false`
- `commit_allowed_without_operator_approval`: `false`
- `push_allowed_without_operator_approval`: `false`
- `commit_after_whole_batch_clean_only`: `true`
- `push_once_only`: `true`

The launcher does not run `git add`, `git commit`, or `git push`.

## How To Run

From the active repo root:

```powershell
cd C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN
powershell -ExecutionPolicy Bypass -File automation/operator/Start-AiOsParallelDryRunCrew.ps1
```

Expected result:

- one labeled PowerShell worker window per registry worker
- worker number, role, lane, allowed paths, and blocked paths printed
- Codex launched when available
- instruction-window fallback when Codex is unavailable
- all workers remain DRY_RUN only

Stop condition:

- workers produce DRY_RUN reports only
- no APPLY
- no commit
- no push

## Verify Git Status After Use

After running the launcher, verify the working tree before any next step:

```powershell
git status --short --branch
```

If any unexpected changed file appears, stop and review it before continuing.

Suggested registry validation:

```powershell
powershell -Command "Get-Content automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json -Raw | ConvertFrom-Json | Out-Null; Write-Host 'REGISTRY JSON OK'"
```

