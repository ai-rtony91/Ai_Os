# Tasker Setup For AI_OS SOS

## Purpose

Use Tasker and AutoNotification on the phone to wake Anthony when a Telegram
notification contains the exact SOS tag:

```text
#AIOS_SOS
```

Tasker is a phone-side wake tool only. It is not AI_OS authority and must not
execute repo actions, mutate approvals, launch workers, register schedulers, or
touch trading paths.

## Telegram Notification Route

If Telegram is used, AI_OS sends SOS-worthy messages through the PowerShell
notification bridge:

```text
automation/orchestration/notifications/Send-AiOsNotification.ps1
```

The bridge reads Telegram credentials from Windows Credential Manager using
these canonical target names:

```text
AIOS_TELEGRAM_BOT_TOKEN
AIOS_TELEGRAM_CHAT_ID
```

No token or chat value belongs in Tasker, Git, docs, screenshots, logs, or
reports.

## Credential Setup

Install CredentialManager:

```powershell
Install-Module -Name CredentialManager -Force -Scope CurrentUser
```

Store token:

```powershell
New-StoredCredential -Target "AIOS_TELEGRAM_BOT_TOKEN" -UserName "aios" -Password "<your_bot_token>" -Type Generic -Persist LocalMachine
```

Store chat id:

```powershell
New-StoredCredential -Target "AIOS_TELEGRAM_CHAT_ID" -UserName "aios" -Password "<your_numeric_chat_id>" -Type Generic -Persist LocalMachine
```

## Tasker / AutoNotification Profile

Create a Tasker profile using AutoNotification Intercept.

Recommended profile idea:

- App/source: Telegram.
- Text/content filter: `#AIOS_SOS`.
- Action: raise alarm stream volume.
- Action: play alarm tone, vibrate, or speak a short alert.
- Optional action: open Telegram.
- Non-matching Telegram messages: no alarm.

## DND Bypass / Alarm Stream Guidance

Use the alarm stream or a Tasker action that is allowed through Do Not Disturb.
Keep the SOS profile narrow so normal Telegram messages do not wake the phone.

Recommended behavior:

- `#AIOS_SOS`: alarm/vibration/TTS.
- No `#AIOS_SOS`: no alarm.
- Non-critical AI_OS status: no alarm.

## Approve / Reject Flow Concept

Phase 1 is wake-only. Anthony still approves or rejects inside the normal AI_OS
approval workflow.

Future approve/reject buttons may be designed later, but they must pass through
an AI_OS identity gate, exact approval-card match, replay protection, and
Protected Action Readiness. Tasker must not directly approve, reject, commit,
push, merge, launch workers, or run repo commands.

## DRY_RUN Test Command

This command should not send Telegram unless `-Apply` is also used. It confirms
the bridge can classify a Telegram notification path safely:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/notifications/Send-AiOsNotification.ps1 -Message "TEST SOS" -Severity "CRITICAL" -Subject "AI_OS SOS" -DryNotify -ChannelOverride telegram
```

The packet-requested live-test shape is:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/notifications/Send-AiOsNotification.ps1 -Message "TEST SOS" -Severity "CRITICAL" -Subject "AI_OS SOS"
```

Run a live send only after explicit approval for that test.

## Expected Result

For DRY_NOTIFY:

- terminal prints `STATUS=DRY_NOTIFY`.
- terminal prints `CHANNEL=telegram`.
- no Telegram message is sent.
- no Tasker alarm fires.

For a separately approved live SOS test:

- Telegram receives the message.
- the message includes `#AIOS_SOS` when the test is wake-worthy.
- Tasker profile fires only on `#AIOS_SOS`.
- phone wakes by the configured alarm/vibration/TTS action.

## Troubleshooting

- If output falls back to file, check that both Credential Manager targets exist:
  `AIOS_TELEGRAM_BOT_TOKEN` and `AIOS_TELEGRAM_CHAT_ID`.
- If Tasker does not fire, confirm AutoNotification can see Telegram
  notifications.
- If every Telegram message wakes the phone, narrow the filter to `#AIOS_SOS`.
- If DND blocks the alert, move the action to the alarm stream or configure a
  DND-allowed Tasker action.
- If local output appears under `relay/reports/SOS_OUTBOX/`, Telegram credentials
  are missing or live send was not approved.
- Do not paste credential values into debugging output. Report only whether the
  canonical target names are present or missing.
