# Notification Bridge Operator Steps

These steps are operator-only. Codex must not create accounts, store credentials, or switch the live channel.

## SOS-only wake policy

AI_OS may wake the Human Owner only for true SOS/blocker conditions. Routine pass reports,
normal approval backlog, warnings, stale/reference evidence, and morning digest updates must
not trigger the phone alarm.

AI_OS should handle normal evidence and recommendation workflow without interrupting Anthony.
Notify Anthony only for SOS-level events where safe continuation is blocked or a protected
action needs explicit approval or intervention.

SOS includes:

- attempted protected actions without explicit approval.
- forbidden write attempts.
- secrets, `.env`, or API-key access attempts.
- broker, OANDA, or live trading attempts.
- real order or real webhook attempts.
- production promotion attempts.
- scheduler or worker launch attempts without approval.
- GPIO or motor control attempts.
- Night Supervisor crash or missing required report.
- validation failure that blocks safe continuation.

SOS does not include:

- `NEEDS_APPROVAL` alone.
- one active approval card.
- stale warnings.
- historical relay noise.
- recommendation-only defer.
- Pi5 human-needed display.
- Bridge `NEEDS_APPROVAL` with zero blockers.
- Protected Action Readiness `NEEDS_EXPLICIT_APPROVAL` when no execution was attempted
  and production flow is not blocked.

Display surfaces must separate `display_alert` from `sos_wake_required`. Pi5 may show
human-needed status without waking Anthony unless `sos_wake_required` is true.

Wake-worthy Telegram messages must include the exact tag:

```text
#AIOS_SOS
```

Non-SOS Telegram messages must not include that tag.

## Owner setup

1. Create the Telegram bot through Telegram's official bot creation chat and keep the token private.
2. Store the token and destination chat value locally. Do not paste values into chat, docs, Git,
   screenshots, logs, or reports. The notifier may check whether these variable names exist, but
   must not print their values:

   ```text
   AIOS_TG_BOT_TOKEN
   AIOS_TG_CHAT_ID
   ```

   Windows Credential Manager can hold the values:

   ```powershell
   cmdkey /generic:AIOS_TELEGRAM_BOT_TOKEN /user:aios /pass:<bot_token>
   cmdkey /generic:AIOS_TELEGRAM_CHAT_ID /user:aios /pass:<chat_destination>
   ```

3. Configure Tasker + AutoNotification on the phone:
   - app/source: Telegram.
   - content filter: `#AIOS_SOS`.
   - action: raise alarm stream volume, play alarm tone or vibration, and optionally repeat
     until acknowledged.
   - non-matching messages: no alarm.

4. Before any live send, run the notifier Telegram DRY_RUN scaffold. It must report only
   whether the required variable names are present or missing, and it must not send a message:

   ```powershell
   python services\python_supervisor\notifier.py --channel telegram
   ```

5. A later approval packet may run a single live Telegram SOS test. That live test must use
   `#AIOS_SOS TEST ONLY`, verify the phone wakes, and verify a non-SOS message does not wake.

6. Copy `automation/orchestration/notifications/notification-config.example.json` to `automation/orchestration/notifications/notification-config.local.json`, set `"channel": "telegram"`, then run only after a separate live-send approval:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/notifications/Test-AiOsNotification.ps1 -Apply
   ```

Do not approve scheduler registration until one bounded `-Apply -Watch` session has remained
clean and one separately approved live SOS wake test has delivered the expected phone alarm.
