# AI_OS Orchestration Health Summary DRY_RUN

This folder contains a read-only operator health summary for AI_OS orchestration.

Purpose:

- Show one simple automation health result: `HEALTHY`, `REVIEW`, or `BLOCKED`.
- Check whether core orchestration tools exist.
- Show current repo status.
- List missing tools, risks, and the next safe action.

Safety rules:

- DRY_RUN only.
- No commits.
- No pushes.
- No dispatcher edits.
- No runtime integration.
- No dashboard edits.
- Do not touch `validator_chain_runner`.

Example:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\health_summary\Get-AiOsOrchestrationHealth.DRY_RUN.ps1
```

JSON output:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\health_summary\Get-AiOsOrchestrationHealth.DRY_RUN.ps1 -OutputJson
```

Next safe action: run this before APPLY, commit, push, or handoff work so the operator can see missing tools and repo risks.
