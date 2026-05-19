# AI_OS Orchestration

This folder holds safe control files for AI_OS worker coordination.

The goal is simple: before a worker starts, AI_OS should know which packet the worker is allowed to handle, which paths are allowed, which paths are blocked, which approval gate applies, and which validation is required.

This folder is not for live trading, broker connections, OANDA access, API keys, secrets, startup tasks, scheduled tasks, or automatic commits.

## Current Boundary

Treat this folder as an active but unconsolidated orchestration workbench.

Active areas that should be preserved while consolidation is planned:

- clean-state checks and preflight gates
- work packet creation and state movement
- worker registry and worker inbox helpers
- approval inbox and approval gate helpers
- validator recommendation and validator chain helpers
- commit package recommendation helpers
- lock and path-conflict helpers

Areas that require consolidation before further scaling:

- duplicate worker registries
- duplicate packet and command queue concepts
- duplicate approval inbox examples and processors
- duplicate supervisor/runtime/control-loop concepts
- root-level `show-*` scripts that overlap with subfolder tools
- tracked example JSON state files that represent generated/runtime snapshots
- overlap between `scripts/` and `automation/orchestration/`

See `docs/audits/orchestration-consolidation-plan.md` for the cleanup plan.

## Safe Use

Run the clean-state gate before assigning work:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/clean_state_gate.ps1
```

If PowerShell 7 is installed, this command may also work:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/clean_state_gate.ps1
```

The gate reports whether the repo is clean enough for a launch decision. A blocked result means the operator should review the listed reasons before continuing.

## Cleanup Rule

Do not delete or move orchestration files blindly. Before archiving any file, verify references from:

- `aios.ps1`
- `automation/operator/`
- `automation/orchestration/`
- `scripts/`
- `docs/AI_OS/`
- `.github/`

When uncertain, write an audit note instead of changing files.
