# AI_OS Orchestration Control Summary DRY_RUN

This folder contains one read-only operator control summary command.

Purpose:

- Summarize repo state.
- Summarize known backlog without turning known local backlog into a new alarm.
- Summarize PR lane readiness.
- Summarize commit/push gate readiness.
- Summarize worker lane status.
- Summarize compliance status.
- Summarize validator status.
- Summarize approval readiness.
- Summarize commit package readiness.
- Summarize clean-state result.
- Summarize post-push result.
- Print one clear next command.

Daily workflow role:

This command is the existing owner for the AI_OS daily workflow summary. It serves as Bridge #1 for the semi-automated daily workflow by connecting existing DRY_RUN helper scouts into one compact console report.

Integrated helper scouts when present:

- `automation/orchestration/pr_gates/Invoke-AiOsPrLaneRunner.DRY_RUN.ps1`
- `automation/orchestration/commit_packages/Test-AiOsCommitPushGate.DRY_RUN.ps1`
- `automation/orchestration/control_summary/Get-AiOsKnownStateFilter.DRY_RUN.ps1`
- `automation/orchestration/Export-AIOSPrHandoff.ps1`
- `automation/orchestration/approval_runner/Get-AiOsApprovalDecision.DRY_RUN.ps1`

If a helper scout is missing or returns a review condition, the control summary reports that condition and continues with the evidence it can collect safely. Missing optional helpers do not authorize mutation.

Safety rules:

- DRY_RUN only.
- No commits.
- No pushes.
- No dispatcher edits.
- No runtime integration.
- No dashboard edits.
- No side folders.
- No staging, commits, pushes, branch switching, resets, cleans, PR creation, PR merge, or backlog cleanup.
- Console output only.

Example:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\control_summary\Get-AiOsControlSummary.DRY_RUN.ps1
```

JSON output:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\control_summary\Get-AiOsControlSummary.DRY_RUN.ps1 -OutputJson
```

Next safe action: run this first when the operator needs a one-screen summary before deciding the next command.
