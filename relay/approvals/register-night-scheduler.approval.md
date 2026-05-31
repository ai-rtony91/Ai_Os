# APPROVAL REQUIRED — Register Nightly Scheduled Task

```
APPROVAL-ID: AIOS-APV-NIGHT-SCHEDULER-20260531
STATUS: WAITING
RISK: RED (scheduled/background execution — ultimate blocker)
REQUESTED-BY: Claude (overwatch)
RELATED: relay/handoffs/CODEX_CLOSE_AUTONOMY_LOOP.md (GATED ITEM 2)
```

## What this unblocks
The closed loop (`Invoke-AiOsNightCycle.ps1 -Apply`) runs unattended overnight instead of
being hand-started. This is the final step that removes Anthony from the start trigger.

## What is being requested
Register ONE Windows scheduled task. Codex must NOT run this — Anthony runs it manually
after approving, because registering a scheduled/background task is an ultimate blocker.

```powershell
# REGISTER (Anthony runs this himself, once, after approval):
# schtasks /create /tn "AIOS_Night_Cycle" `
#   /tr "pwsh -NoProfile -ExecutionPolicy Bypass -File C:\Dev\Ai.Os\automation\orchestration\Invoke-AiOsNightCycle.ps1 -Apply" `
#   /sc DAILY /st 02:00 /ru "%USERNAME%" /rl LIMITED /f

# ROLLBACK (remove it):
# schtasks /delete /tn "AIOS_Night_Cycle" /f
```

## Why it is gated
Scheduled/background execution gives the loop standing authority to act without a human
present. It must not be created automatically. Anthony reviews the loop's behavior in
`-Watch` mode first, THEN registers the task.

## Pre-conditions before approving
- [ ] Night cycle has run clean in `-Apply -Watch` mode at least one full session.
- [ ] SOS notifier is reachable (file channel at minimum) so a 02:00 blocker reaches Anthony.
- [ ] Self-continuation STOP kill-switch verified working.

## Decision
- [ ] APPROVE — Anthony runs the schtasks /create line above.
- [ ] REJECT / DEFER — keep starting the night cycle manually.

## On approval
Move this file to `relay/approvals/approved/` and run the register command.
