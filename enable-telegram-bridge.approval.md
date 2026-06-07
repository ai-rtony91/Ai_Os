# Enable Telegram Bridge Approval Notes

Status: approval notes only. This file does not enable Telegram live send.

## Scope

Telegram is an opt-in notification channel for SOS-worthy AI_OS messages. It is
not approval authority, command authority, scheduler authority, worker authority,
or trading authority.

## Canonical Credential Names

The PowerShell notification bridge uses Windows Credential Manager. Store values
under these canonical target names:

```text
AIOS_TELEGRAM_BOT_TOKEN
AIOS_TELEGRAM_CHAT_ID
```

Legacy local Python-only environment names, when referenced by older tooling, are
not canonical:

```text
AIOS_TG_BOT_TOKEN
AIOS_TG_CHAT_ID
```

Do not paste token or chat values into chat, docs, Git, screenshots, logs, or
reports.

## Required Manual Setup

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

## Safe Test

DRY_NOTIFY does not send Telegram:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/notifications/Send-AiOsNotification.ps1 -Message "TEST SOS" -Severity "CRITICAL" -Subject "AI_OS SOS" -DryNotify -ChannelOverride telegram
```

Live Telegram send requires a separate explicit approval. Validator PASS,
presence of credentials, this approval note, or a config file is not approval to
send.

## Boundaries

- No live trading.
- No broker/API/order execution.
- No secrets in repo files.
- No scheduler registration.
- No Tasker-generated repo control.
- No inbound Telegram commands.
- No approval mutation from Telegram.
- No commit, push, merge, or protected action from Telegram.
