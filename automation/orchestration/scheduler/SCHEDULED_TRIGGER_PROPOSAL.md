# AI_OS Scheduled Trigger Proposal

## Status

PROPOSAL ONLY. Do not run automatically. Anthony registers manually only after separate explicit approval.

## Proposed Task

- Task name: `AIOS_Relay_Nightly`
- Purpose: start one gated AI_OS relay cycle without manual launch.
- Trigger: daily at `02:00` local time.
- Run-as context: current Windows user `mylab`.
- Working directory: `C:\Dev\Ai.Os`
- Wake/idle behavior: do not wake the machine; do not require idle; do not start a missed run automatically.

The existing night reports were generated during afternoon manual work on `2026-05-30`. A `02:00` nightly trigger keeps the loop away from normal operator work windows and leaves reports ready before the morning review.

## Exact Command That Would Be Scheduled

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "C:\Dev\Ai.Os\automation\orchestration\Invoke-AiOsNightCycle.ps1" -Apply
```

Task Scheduler start-in directory:

```text
C:\Dev\Ai.Os
```

## Safety Restatement

The scheduled trigger would only launch the existing full night cycle. The cycle remains gated:

- No git stage, commit, push, merge, reset, clean, or branch operation.
- No scheduled task creation from inside the runner.
- No secret, credential, broker, OANDA, webhook, or live-trading action.
- Protected terms route to `relay/approvals/`.
- Out-of-scope, destructive, or protected work stops to approval.
- Human approval remains required for protected actions.

## Rollback Command

Verified syntax for removing the proposed task if Anthony later registers it:

```powershell
schtasks /delete /tn "AIOS_Relay_Nightly" /f
```

## Register Command Reference

```powershell
# ===== PROPOSAL ONLY - DO NOT RUN. Anthony registers manually. =====
# schtasks /create /tn "AIOS_Relay_Nightly" /tr "pwsh -NoProfile -ExecutionPolicy Bypass -File \"C:\Dev\Ai.Os\automation\orchestration\Invoke-AiOsNightCycle.ps1\" -Apply" /sc DAILY /st 02:00 /ru "%USERNAME%" /rl LIMITED /f
# ==================================================================
```

## Non-Goals

- This proposal does not register, create, enable, or start any scheduled task.
- This proposal does not modify the relay runner.
- This proposal does not add a service, registry autostart entry, or startup-folder item.
- This proposal does not commit or push.
