# AIOS Owner Shell Git PR Bridge V1 Report

## Purpose

This bridge exists because the Codex execution context for this repository is restricted and cannot safely run
GitHub network operations, repository writes, or PR publish actions directly.

The required publish sequence for promotion artifacts is therefore moved to a bounded owner-run PowerShell entrypoint.
This keeps Codex changes focused on local, deterministic file preparation while leaving networked promotion actions
to the operator.

## Codex execution constraints

- Codex must not perform GitHub authentication or networked PR operations.
- Codex must not run `git push`, branch creation, or PR merge in the restricted execution context.
- Owner-controlled shell execution performs the networked GitHub publish flow with explicit human-run confirmation.

## What this bridge does

The bridge validates that:

- repository root is exactly `C:\Dev\Ai.Os`
- known forex promotion pipeline artifacts exist
- working-tree dirty scope is limited to eight promotion pipeline artifacts plus bridge-owned artifacts:
  - `Reports/forex_delivery/AIOS_ENVIRONMENT_DOCTOR_V1_REPORT.md`
  - `Reports/forex_delivery/AIOS_ENVIRONMENT_DOCTOR_V2_WINPS51_ONLY_REPORT.md`
  - `Reports/forex_delivery/AIOS_OWNER_SHELL_GIT_PR_BRIDGE_V1_REPORT.md`
  - `scripts/forex_delivery/Invoke-OwnerShellGitPrBridge.V1.ps1`
- branch and `git add` flow are valid for staging this 12-file bridge artifact set
- commit, push, PR creation, checks watching, merge state checks, merge, and `main` sync are executed in sequence

## Safety boundary

This script does **not** authorize or invoke:

- broker/API interaction
- credential loading or rotation
- demo/live order placement
- live trading
- money movement

It only stages and publishes repository artifacts already produced for the promotion pipeline workflow.

## Exact owner run command

```powershell
powershell -ExecutionPolicy Bypass -File scripts/forex_delivery/Invoke-OwnerShellGitPrBridge.V1.ps1
```

## Optional parameters

- `-DryRun` runs validation only, without pushing, PR creation, merge, or main sync.
- `-NoMerge` performs all steps through PR creation and checks, then skips merge/sync.
- `-BranchPrefix` allows custom branch naming; default is `owner/forex-promotion-pipeline-v1`.
