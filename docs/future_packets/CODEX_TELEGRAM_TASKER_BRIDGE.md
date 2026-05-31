# EXEC WORK ORDER — Telegram ↔ Tasker Two-Way SOS Bridge

```
EXEC-TOKEN: AIOS-TG-TASKER-BRIDGE-20260531
WORKER: codex
LANE: one worktree, one branch  ->  codex/telegram-tasker-bridge
MODE: DRY_RUN first, then APPLY after self-review checklist passes
AUTHORITY: Codex never commits/pushes/merges. Anthony commits. No secret written.
DEPENDS ON: CODEX_CLOSE_AUTONOMY_LOOP (notifier.py + approval-resume consumer + night cycle)
SOURCE AUDIT: relay/reports/AUDIT_AUTONOMY_GAPS_20260531.md + inbound audit (this session)
```

## GOAL
Give the night supervisor a TWO-WAY channel: it sends a report/SOS to Telegram; Anthony's
phone (Tasker) escalates a real blocker into a wake-up alarm; Anthony taps Approve/Reject;
the reply flows back into `relay/approvals/approved|rejected/` and the loop resumes.

Channel = Telegram bot. Polling only (`getUpdates` long-poll) — pure OUTBOUND, NO inbound
server, so the no-internet-facing-server doctrine holds. Mobile wake-up = Tasker
(https://tasker.joaoapps.com/) + AutoNotification on Anthony's phone (configured by Anthony,
documented here — NOT built by Codex).

---

## ISSUE 1 — Outbound: notifier has no Telegram channel
notifier.py (from prior packet) has only a `file` channel.

### SOLUTION 1 — Add `telegram` channel to notifier.py
- Extend `services/python_supervisor/notifier.py` with a `telegram` channel:
  - Reads `AIOS_TG_BOT_TOKEN` and `AIOS_TG_CHAT_ID` from env ONLY (never hardcode/commit).
  - On BLOCKED / NEEDS_APPROVAL transition, call Telegram `sendMessage`:
    - Text = approval id, risk, reason, proposed action (from the approval record).
    - `reply_markup` = inline keyboard with two callback buttons:
      `✅ Approve` -> callback_data `apv:<id>:approve`
      `❌ Reject`  -> callback_data `apv:<id>:reject`
    - Prefix SOS-class messages with a fixed token `#AIOS_SOS` so Tasker can pattern-match
      and fire the wake-up alarm.
  - Keep `file` channel as fallback (always also write `relay/reports/SOS_OUTBOX/`).
  - Idempotent via existing `telemetry/night_supervisor/last_notified.json`.

## ISSUE 2 — Inbound: no consumer for Anthony's reply
No code captures the button tap / reply and writes an approval decision.

### SOLUTION 2 — Telegram poller -> approval write-back
- New file `services/python_supervisor/telegram_relay.py`:
  - Long-poll `getUpdates` (offset-tracked in `telemetry/night_supervisor/tg_offset.json`;
    stdlib `urllib` only, no new deps if avoidable).
  - IDENTITY GATE (hard): accept updates ONLY when `from.id` / `chat.id` == `AIOS_TG_CHAT_ID`.
    Drop everything else silently and log it. This is the auth that replaces the hardcoded name.
  - Parse decision from either a callback_query (`apv:<id>:approve|reject`) or a text reply
    matching `^(approve|reject)\s+<id>`.
  - Resolve `<id>` to the waiting approval file in `relay/approvals/`. If found:
    - approve -> move/write to `relay/approvals/approved/<id>.approval.md` with
      `status: APPROVED`, `decided_by: Anthony`, `decided_via: telegram`, `decided_utc: <ISO>`.
    - reject  -> same into `relay/approvals/rejected/`.
    - Preserve the `origin_id`/`origin` field so the existing resume consumer can re-queue it.
  - Answer the callback (`answerCallbackQuery`) so the button shows "recorded".
  - Idempotent: never act on an update offset already processed; never double-write a decision.
  - Log every action to `relay/logs/telegram_relay.log` (UTC).

## ISSUE 3 — Wake-up escalation
A blocker at 02:00 must physically wake Anthony.

### SOLUTION 3 — Escalation contract (Codex documents; Anthony configures phone)
- AIOS side: SOS-class messages carry the `#AIOS_SOS` token + risk=RED/HIGH marker.
- Write `relay/reports/TASKER_SETUP.md` describing the phone-side profile Anthony builds:
  - AutoNotification "Intercept" on the Telegram app, content filter `#AIOS_SOS`.
  - Task: set alarm-stream volume to max + play alarm tone + TTS the reason, bypassing
    silent/DND (Tasker "Alarm" category). Optional: repeat until acknowledged.
  - Non-SOS (routine nightly report) -> normal notification, no alarm.
- Codex does NOT touch the phone; it only emits the contract + the `#AIOS_SOS` token.

## ISSUE 4 — Wire into the night cycle
### SOLUTION 4
- Add `telegram_relay.py` poll as a step in `Invoke-AiOsNightCycle.ps1` (after approval-resume,
  before bridge refresh), `-Apply`-gated, logged. One short poll per cycle is enough; the
  resume consumer picks up whatever the poll wrote.

---

## GATED ITEM — write approval, DO NOT execute
`relay/approvals/enable-telegram-bridge.approval.md` (already drafted by Claude) — needs
`AIOS_TG_BOT_TOKEN` + `AIOS_TG_CHAT_ID`. Anthony creates the bot via @BotFather, gets his
chat_id, and sets the env vars himself. Codex must not hold or commit the token.

## OUT OF SCOPE
- HMAC message signing (future hardening; chat_id lock is sufficient for v1).
- Approval store unification. ChatGPT Custom-GPT path (rejected: needs internet-facing server).

---

## SELF-REVIEW CHECKLIST (must pass before APPLY)
- [ ] notifier `telegram` channel: with fake token in DRY_RUN, builds correct sendMessage
      payload + inline keyboard, does NOT make a live call in DRY_RUN.
- [ ] telegram_relay drops any update whose chat_id != AIOS_TG_CHAT_ID (identity gate proven).
- [ ] Seeded callback `apv:<id>:approve` writes `relay/approvals/approved/<id>...` with origin
      preserved; resume consumer then re-queues it to `relay/inbox/`. Full O closes.
- [ ] Reject path writes to rejected/ and does NOT re-queue.
- [ ] Idempotent: replaying the same update offset writes nothing new.
- [ ] No token/secret value in the diff. No git/schtasks. urllib/stdlib only (or justify a dep).
- [ ] Writes confined to relay\, services/python_supervisor\, automation/orchestration\,
      telemetry/night_supervisor\. No protected root file touched.
- [ ] `relay/reports/TASKER_SETUP.md` and `enable-telegram-bridge.approval.md` present.

## DELIVERABLE
Branch `codex/telegram-tasker-bridge`, staged-not-committed, plus
`relay/reports/TELEGRAM_BRIDGE_RESULT.md` summarizing wiring + the pending bot-token approval.
Anthony reviews and commits.
```
