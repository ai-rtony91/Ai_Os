# AI_OS Operations Note — Android ADB Wake Rail and Raspberry Pi 5 Boundary

Date: 2026-06-06
Status: Documentation note only
Runtime effect: None
Secrets: None
Trading impact: None

## Android ADB Wake Rail

Validated working path:

AI_OS Windows host
→ ADB shell notification
→ Android notification tray
→ AutoNotification intercept
→ Tasker profile fires
→ AIOS SOS Wake rings/vibrates/speaks on Samsung Galaxy Z Fold 6.

Telegram wake trigger is on HOLD because Telegram bot messages did not reliably appear as real Android notifications for AutoNotification to intercept.

Validated Windows ADB path:

C:\Android\platform-tools\adb.exe

Validated AI_OS repo path:

C:\Dev\Ai.Os

Validated phone wireless ADB target:

192.168.1.251:5555

Validated packages under Android user 0:

- Telegram: org.telegram.messenger
- Tasker: net.dinglisch.android.taskerm
- AutoNotification: com.joaomgcd.autonotification
- AutoNotification Unlock: com.joaomgcd.autonotification.unlock

Observed Android users:

- User 0: main user
- User 10: Island
- User 150: Secure Folder

Validated wireless command:

powershell -ExecutionPolicy Bypass -File "C:\Dev\Ai.Os\tools\android\Send-AiosAdbSosWake.ps1"

Validated script:

C:\Dev\Ai.Os\tools\android\Send-AiosAdbSosWake.ps1

Validated log:

C:\Dev\Ai.Os\logs\android\adb_sos_wake.log

Validated result:

- USB ADB SOS Wake: PASS
- Wireless ADB SOS Wake: PASS
- Hardened PowerShell script: PASS
- Logging: PASS
- Telegram trigger: HOLD

Security boundary:

- Same trusted LAN only.
- Do not expose ADB port 5555 through router port forwarding, Cloudflare Tunnel, ngrok, public VPS, or any public internet route.
- No bot token used.
- No Telegram polling enabled.
- No approval mutation.
- No scheduler.
- No worker launch.
- No trading execution.

## Raspberry Pi 5 Boundary

The Raspberry Pi 5 should be hardened as a limited AI_OS support device only.

Allowed role:

AI_OS progress runner / reporter.

Allowed responsibilities:

- Report AI_OS progress/status.
- Run read-only health checks.
- Display or forward status summaries.
- Assist with uptime/status visibility.
- Preserve logs/evidence for review.

Not allowed:

- Approval mutation.
- GitHub write without explicit user-approved APPLY.
- Worker launch authority.
- Scheduler authority.
- Trading execution.
- Broker/OANDA/live order actions.
- Telegram bot token storage.
- Telegram live sending.
- Secrets on dashboard.
- Public remote-control exposure.

Pi 5 hardening should focus on:

- Stable power.
- Safe shutdown/reboot behavior.
- Network identity and static/reserved IP.
- SSH hardening.
- Minimal services.
- Read-only/report-only AI_OS commands.
- Log rotation.
- Health/status reporting.
- Recovery path after power loss.
- No live trading authority.
- No approval authority.

Next work item:

Harden Raspberry Pi 5 as limited AI_OS progress runner/reporter.
