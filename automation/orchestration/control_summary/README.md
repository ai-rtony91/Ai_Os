# AI_OS Orchestration Control Summary DRY_RUN

This folder contains one read-only operator control summary command.

Purpose:

- Summarize repo state.
- Summarize worker lane status.
- Summarize compliance status.
- Summarize validator status.
- Summarize approval readiness.
- Summarize commit package readiness.
- Summarize clean-state result.
- Summarize post-push result.
- Print one clear next command.

Safety rules:

- DRY_RUN only.
- No commits.
- No pushes.
- No dispatcher edits.
- No runtime integration.
- No dashboard edits.
- No side folders.

Example:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\control_summary\Get-AiOsControlSummary.DRY_RUN.ps1
```

JSON output:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\control_summary\Get-AiOsControlSummary.DRY_RUN.ps1 -OutputJson
```

Next safe action: run this first when the operator needs a one-screen summary before deciding the next command.
