# AIOS Codex Handoff Example

Mode: DRY_RUN_READ_ONLY

## Current Branch

phase-74-codex-handoff

## Current Dirty Files

- aios.ps1
- automation/orchestration/handoff/New-AiOsCodexHandoff.DRY_RUN.ps1
- automation/orchestration/handoff/AIOS_CODEX_HANDOFF.example.md

## Active Packet

packet-001 [active]

## Next Recommended Command

```powershell
powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1
```

## Validator Recommendation

PowerShell parser check for changed `.ps1` files, then `git diff --check`.

## Commit Package Recommendation

Approved source files:

- aios.ps1
- automation/orchestration/handoff/New-AiOsCodexHandoff.DRY_RUN.ps1
- automation/orchestration/handoff/AIOS_CODEX_HANDOFF.example.md

Ignored runtime files:

- automation/orchestration/work_packets/active/example.json

Risky files:

- none

## Ready-To-Paste Codex Prompt

```text
PHASE NEXT - APPLY OR DRY_RUN PER OPERATOR APPROVAL
AIOS Operator Handoff

Continue from the current branch using read-only validation first. Do not stage, commit, push, delete, touch dashboard files, touch broker/trading execution, touch scheduled/startup tasks, or touch secrets unless explicitly approved.
```

## Ready-To-Paste PowerShell Command Block

```powershell
git status --short --branch
powershell -ExecutionPolicy Bypass -File automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1
powershell -ExecutionPolicy Bypass -File automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1
powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1
```

## Safety Reminders

- Read-only handoff generation only.
- No git add, commit, or push is performed.
- No delete, dashboard, broker/trading execution, scheduled task, startup task, or secret action is performed.
