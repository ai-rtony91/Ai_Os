# AI_OS Supervisor Core

The AI_OS Supervisor Core is a read-only workflow watcher.

It tells the operator what is happening across:

- repo state
- GitHub state
- worker lanes
- queue files
- validator files
- stale state
- next safe action

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/supervisor/Start-AiOsSupervisor.ps1
```

The supervisor does not commit, push, merge, create branches, create issues, create PRs, launch Codex, launch workers, create startup tasks, create scheduled tasks, edit dashboard files, edit protected root files, or touch broker/OANDA/API/webhook/live trading work.

If GitHub CLI checks fail, the supervisor continues in local-only mode.
