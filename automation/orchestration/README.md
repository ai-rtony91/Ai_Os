# AI_OS Orchestration

This folder holds safe control files for AI_OS worker coordination.

The goal is simple: before a Codex worker starts, AI_OS should know which packet the worker is allowed to handle, which paths are allowed, which paths are blocked, and whether validation is required.

This folder is not for live trading, broker connections, OANDA access, API keys, secrets, startup tasks, scheduled tasks, or automatic commits.

## Phase 16.1 Backbone

Phase 16.1 adds three planning pieces:

- a packet queue example
- an assignment lock example
- a clean-state gate script

These files are scaffolds. They do not launch workers and do not claim packets.

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
