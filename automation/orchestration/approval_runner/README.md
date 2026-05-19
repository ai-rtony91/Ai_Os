# AI_OS Approval Inbox Runner

This folder contains a DRY_RUN scaffold for deciding whether the next operator action is safe to consider.

The runner reports one of three outcomes:

- `SAFE TO APPLY`: no blocking or review risks were found.
- `NEEDS REVIEW`: warnings exist and the operator should review them before approval.
- `BLOCKED`: a hard stop exists. Do not apply until corrected.

The runner is read-only. It does not edit dispatcher runtime, dashboard files, approval inboxes, locks, commits, pushes, or staged files.

Checks included:

- git status cleanliness
- staged files
- untracked files
- protected path risk
- broker, live trading, API key, secret, webhook, or real order risk
- missing validation evidence
- missing worker report
- missing approval reason
- dirty worker lane warning

Example beginner command:

```powershell
powershell -ExecutionPolicy Bypass -File automation/orchestration/approval_runner/Get-AiOsApprovalDecision.DRY_RUN.ps1 -ValidationEvidencePath Reports/validation/example.json -WorkerReportPath Reports/operator/worker-reports/example.md -ApprovalReason "Approve docs-only APPLY after validation" -WorkerLanePath automation/orchestration
```

JSON-only output:

```powershell
powershell -ExecutionPolicy Bypass -File automation/orchestration/approval_runner/Get-AiOsApprovalDecision.DRY_RUN.ps1 -Json
```

Next safe action: run this against one packet's validation evidence and worker report before using it in any larger approval flow.
