# AI_OS Loop Closeout — Human-Owner-Only Final Steps

These two stages are reserved to Anthony Meza (Human Owner) by RISK_POLICY.md and
AI_OS_AUTONOMY_LEVELS.md (L5 hard gate). No automation, Claude, or Codex may perform
them. They are the last two arrows of vacation mode. Do them in order, only after the
relay/runtime processor and the soak proof are complete.

---

## STAGE 9 — Arm ONE real SOS channel (secret-bearing; human only)

Goal: when the unattended loop emits a BLOCKED SOS, it actually reaches you, instead of
writing `delivered: false` to a file.

Preconditions before arming:
- [ ] Relay/runtime processor packet complete (DRY_RUN preview proven).
- [ ] Soak proof complete: soak evidence status PASS or STOPPED, watchdog never BLOCKED.
- [ ] The governed packet `claude/sos-telegram-arming-v2` reviewed and approved.

Steps (you only):
1. [ ] Create the SOS channel credential OUTSIDE the repo (e.g. a bot token in your OS
       secret store or an env var). NEVER commit it. NEVER paste it into a packet, chat,
       or report. The repo stays secret-free.
2. [ ] Point the notifier (`services/python_supervisor/notifier.py`) at the channel via
       an environment variable the notifier already reads — not a file in the repo.
3. [ ] Send ONE test SOS and confirm it arrives on your phone.
4. [ ] Confirm a healthy heartbeat produces NO SOS (no false alarms), and a simulated
       stale heartbeat DOES produce exactly one SOS.
5. [ ] Record `delivered: true` evidence for the test in `Reports/endurance_soak/` —
       evidence only, no secret in the file.

Hard gate: this is the only place a real secret enters the picture, and it never enters
the repository. If any step would require writing the token into a tracked file, STOP.

---

## STAGE 10 — Register the scheduler (human only, final arrow)

Goal: the night cycle runs unattended on a schedule = vacation mode is live.

Preconditions before registering (ALL must be true):
- [ ] One clean unattended soak window in `-Watch` mode (Stage = soak proof) — done.
- [ ] SOS channel armed and reachable (Stage 9) — done.
- [ ] STOP kill-switch verified: creating `control/self_continuation/STOP` halts the loop
      cleanly, removing it allows resume — verified during the soak STOP drill.
- [ ] The approval `relay/approvals/register-night-scheduler.approval.md` reviewed and
      you have written your explicit approval.

Step (you only — run manually; no automation may do this):
```
schtasks /create /tn "AIOS_Night_Cycle" ^
  /tr "pwsh -NoProfile -ExecutionPolicy Bypass -File C:\Dev\Ai.Os\automation\orchestration\Invoke-AiOsNightCycle.ps1 -Apply" ^
  /sc DAILY /st 02:00 /ru "%USERNAME%" /rl LIMITED /f
```

After registration:
- [ ] Confirm the first scheduled run produces a heartbeat refresh and a morning brief.
- [ ] Confirm the dead-man watchdog would fire if the scheduled run failed to refresh.
- [ ] Keep the STOP kill-switch documented and one keystroke away.

---

## What stays permanently human, even in vacation mode

Per AI_OS authority, these are never delegated regardless of how green the dashboard is:
merge, secrets, broker, live trading, real orders/webhooks, governance edits, and
destructive repo actions. Vacation mode means the loop observes, drafts, prepares, and
escalates — and wakes you for exactly these gates. That is the finish line, by design.

_Observe-only checklist. It performs nothing. The Human Owner performs Stages 9 and 10._
