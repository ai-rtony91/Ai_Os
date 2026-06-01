# Notification Bridge Operator Steps

These steps are operator-only. Codex must not create accounts, store credentials, or switch the live channel.

1. Create the Telegram bot through Telegram's official bot creation chat and keep the token private.
2. Store the token and destination chat value in Windows Credential Manager:

   ```powershell
   cmdkey /generic:AIOS_TELEGRAM_BOT_TOKEN /user:aios /pass:<bot_token>
   cmdkey /generic:AIOS_TELEGRAM_CHAT_ID /user:aios /pass:<chat_destination>
   ```

3. Copy `automation/orchestration/notifications/notification-config.example.json` to `automation/orchestration/notifications/notification-config.local.json`, set `"channel": "telegram"`, then run:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/notifications/Test-AiOsNotification.ps1 -Apply
   ```

Do not approve scheduler registration until one full `-Apply -Watch` night session has delivered the expected notification and remained clean.
