# AI_OS Operator Control Loop

This folder contains the DRY_RUN operator control loop.

Run it through the AI_OS shortcut:

```powershell
.\aios.ps1 -Mode control
```

The control loop is read-only. It gathers git state, tool availability,
runtime health, worker inbox status, lock status, approval status, commit
package guidance, clean-state status, GitHub status, and next safe action.

Safety rules:

- No git add.
- No commit.
- No push.
- No file staging.
- No broker, OANDA, API key, webhook, or live trading action.
- No dashboard edits.

