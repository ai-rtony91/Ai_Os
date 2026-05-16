# AI_OS GitHub Save Automation

`Submit-AiOsWork.ps1` packages the current worker branch into GitHub with explicit approval gates.

Script:

```text
automation/orchestration/git/Submit-AiOsWork.ps1
```

## Safety Rules

- Preview is default.
- `-Apply` is required before staging, commit, push, PR creation, or merge.
- No PR is created unless `-Apply -CreatePR` is used.
- No merge is performed unless `-Apply -MergePR` is used.
- The script refuses `main` unless `-AllowMain` is explicitly passed.
- It stages only `-IncludePaths` when provided.
- If `-IncludePaths` is omitted, it stages currently changed paths from `git status --porcelain`.
- It commits only when staged changes exist.
- It pushes the current branch.
- If a PR already exists, it prints the PR URL instead of failing.

## Preview

WHERE: visible tab/window `SAVE · git`

Path: repo root

Run:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\git\Submit-AiOsWork.ps1 -Preview -Title "Save current worker branch" -CommitMessage "Save current worker branch"
```

## Apply With PR

WHERE: visible tab/window `SAVE · git`

Path: repo root

Run only after validation is clean:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\git\Submit-AiOsWork.ps1 -Apply -CreatePR -Title "Save current worker branch" -CommitMessage "Save current worker branch"
```

## Merge

Merge remains explicit:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\git\Submit-AiOsWork.ps1 -Apply -MergePR -Title "Save current worker branch" -CommitMessage "Save current worker branch"
```

## Operator Rule

Prefer repo-owned save/PR automation over repeated manual gh CLI commands. Manual gh commands should be fallback only.
