# AI_OS Validator Chain Runner

This folder contains a DRY_RUN scaffold for running safe validation checks from one place.

The runner reports one of three outcomes:

- `PASS`: all validators passed.
- `REVIEW`: at least one validator needs operator review.
- `BLOCKED`: at least one validator found a hard stop.

The runner is read-only. It does not edit dispatcher runtime, dashboard files, approvals, locks, staged files, commits, pushes, pulls, rebases, or merges.

Validators included:

- `git diff --check`
- PowerShell parse for changed `.ps1` files
- JSON parse for changed `.json` files
- clean-state verifier if available
- approval runner if available
- post-push verifier only when on `main`

Example beginner command:

```powershell
powershell -ExecutionPolicy Bypass -File automation/orchestration/validator_chain_runner/Invoke-AiOsValidatorChain.DRY_RUN.ps1
```

JSON-only output:

```powershell
powershell -ExecutionPolicy Bypass -File automation/orchestration/validator_chain_runner/Invoke-AiOsValidatorChain.DRY_RUN.ps1 -Json
```

Optional context:

```powershell
powershell -ExecutionPolicy Bypass -File automation/orchestration/validator_chain_runner/Invoke-AiOsValidatorChain.DRY_RUN.ps1 -WorkerLanePath automation/orchestration -ValidationEvidencePath Reports/validation/example.json -WorkerReportPath Reports/operator/worker-reports/example.md -ApprovalReason "Review scaffold validation"
```

Next safe action: run this chain before any future APPLY, commit, or push approval.
