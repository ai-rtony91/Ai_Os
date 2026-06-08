# Runbook: Arming the AI_OS SOS Last Mile (Tier 0.1)

- Status: operator runbook (evidence-and-planning; not an APPLY or live-send authorization)
- Date: 2026-06-08
- Branch: claude/repo-overview-D1GBF
- Audience: Human Owner / operator (Anthony)
- Roadmap item: Tier 0, T0.1 ("Wire one live SOS channel end to end") in `docs/roadmap/AIOS_ENDURANCE_HARDENING_ROADMAP.md`

## Why this exists (the finding)

Today the SOS path dead-ends at a local file. When the night cycle hits a BLOCKED state, the notifier writes a markdown file to `relay/reports/SOS_OUTBOX/` and stops. Nothing leaves the machine. A 02:00 CRITICAL would never reach your phone — you would only see it the next time you opened the outbox folder yourself.

Evidence:

- `services/python_supervisor/notifier.py` only ever runs the **file** channel in the cycle. The night cycle invokes it as `--channel file` (`Invoke-AiOsNightCycle.ps1:305`, phase `sos-file-notifier`).
- The notifier **hard-blocks** live Telegram: with `--channel telegram --apply` it prints `LIVE_SEND=BLOCKED` and exits 2 (`notifier.py:223-231`). With `--channel email` or `--channel push` it exits 2 as "disabled" (`notifier.py:208-210`).
- The dispatcher `automation/orchestration/notifications/Send-AiOsNotification.ps1` *does* contain working webhook and Telegram senders (lines 212-246), but they require stored credentials and **fall back to the file channel** when the credential is missing (lines 216-220, 235-239). No credentials are provisioned, so it always falls back to file.
- `automation/orchestration/notifications/AIOS_ALERT_ROUTING_RULES.example.json` has `telegram_live_send_enabled: false` and `webhook_live_send_enabled: false` (lines 9-10), and `no_real_senders: true` (line 4).
- `tools/android/Send-AiosAdbSosWake.ps1` is a **working** Android push, but it is **unwired** — no phase or notifier path calls it.

This runbook documents the exact operator steps to arm **exactly one** live channel and prove it reaches you. You do not need all three. Pick one.

## The quiet-by-default guarantee (read before arming)

Arming a channel does **not** make AI_OS chatty. The severity model is quiet by design and stays quiet:

- **Only BLOCKED wakes you.** In `notifier.py`, `SOS_WAKE_STATUSES = {"BLOCKED"}` and `FILE_NOTIFY_STATUSES = {"BLOCKED"}` (lines 20-21). A BLOCKED state is the only thing that produces an SOS wake (`wake_class()` returns `SOS`).
- **NEEDS_APPROVAL does not wake you.** It is `REVIEW_ONLY` (`display_alert` true, `sos_wake_required` false, lines 52-65). It shows on a dashboard; it does not page you.
- **Everything else is `NO_WAKE`.**

So even with a live channel armed, the only thing that can reach your phone at 2 AM is a genuine BLOCKED.

## De-dupe, rate-limit, and quiet-hours behavior

These guards are already in the code and apply to whatever channel you arm:

- **De-dupe (suppression).** `notifier.py` computes a `notification_key` from `status|generated_at|plain_summary` (lines 68-72) and records the last-notified key in `telemetry/night_supervisor/last_notified.json`. If the next cycle produces the same key, it prints `STATUS=SUPPRESSED` and sends nothing (lines 244-248). You get one page per distinct BLOCKED state, not one per cycle.
- **Rate limit.** `Send-AiOsNotification.ps1` enforces `max_per_hour` from the config (12 in the example, `notification-config.example.json`) using a rolling one-hour window in `state/rate_window.json` (`Test-AiOsRateLimit`, lines 116-148). Over the cap, it logs `RATE_LIMITED` and exits without sending (lines 193-197).
- **Quiet hours with CRITICAL bypass.** `Send-AiOsNotification.ps1` reads `control/mode/AIOS_MODE_POLICY.json`; inside the quiet window it **redirects non-CRITICAL alerts to the file channel** (lines 170-179). CRITICAL (which is what an SOS BLOCKER is sent as — see `notifier.py:176`, `-Severity CRITICAL`) **bypasses quiet hours** and still goes out live. The routing rules mirror this: `quiet_hours.suppress_below_severity: "CRITICAL"`, `sos_can_bypass: true` (`AIOS_ALERT_ROUTING_RULES.example.json:13-19`).
- **Severity floor.** Alerts below the configured `severity_floor` (WARN in the example) are dropped with `BELOW_FLOOR` (lines 187-191). SOS is CRITICAL, so it clears the floor.
- **Trading-term payload block.** The dispatcher refuses any message containing trade/order/buy/sell/live/broker terms (`PAYLOAD_BLOCKED_TRADING_TERMS`, lines 160-164). Keep SOS text operational, not financial.

Net effect: arming one channel gives you "one page per distinct overnight blocker, CRITICAL only, never more than `max_per_hour`," and nothing else.

---

## Channel options and tradeoffs

Pick ONE. You do not need more than one armed channel to satisfy Tier 0.1.

| Channel | Reaches phone when away from LAN? | Setup cost | External dependency | Notes |
|---|---|---|---|---|
| Telegram | Yes (push over internet) | Low: create a bot, get token + chat id | Telegram Bot API | Best "wakes me anywhere" option. Requires the notifier live-send block to be lifted for this channel. |
| Webhook | Yes, if the webhook endpoint pages you | Low on AI_OS side, but you must own a relay (e.g. a paging service / IFTTT / your own endpoint) | Your webhook endpoint | AI_OS just POSTs JSON; the *paging* is your endpoint's job. |
| Android / ADB | Only on the same LAN as the phone | Medium: USB/wireless ADB, fix hardcoded paths and IP, wire it in | adb + a reachable device | Posts a real Android notification. LAN-bound, so weak for "I'm not home." Already works standalone. |

### A note on env-var / credential names (verify before you start)

There is a naming mismatch in the current code you should be aware of so you provision the right names:

- The **config** (`notification-config.example.json`) and this runbook use `AIOS_TELEGRAM_BOT_TOKEN`, `AIOS_TELEGRAM_CHAT_ID`, and `AIOS_WEBHOOK_URL` as the **stored-credential target names** the dispatcher looks up via `Get-StoredCredential` (`Send-AiOsNotification.ps1:213, 229-230`).
- The **notifier's** Telegram preview presence-check reads **different** env-var names: `AIOS_TG_BOT_TOKEN` and `AIOS_TG_CHAT_ID` (`notifier.py:22`). These are only used for the DRY_RUN scaffold report; they are not the live-send path.

The live send goes through the dispatcher's stored-credential lookup, so provision `AIOS_TELEGRAM_BOT_TOKEN` / `AIOS_TELEGRAM_CHAT_ID` / `AIOS_WEBHOOK_URL` as **stored credentials** (Windows Credential Manager `Get-StoredCredential` targets), not plain environment variables. If you change the wiring to read env vars directly, reconcile these two name sets first.

---

## Option 1 — Telegram (recommended for off-LAN wake)

What you are doing: creating a Telegram bot, giving AI_OS its token and your chat id as stored credentials, flipping the live-send flag on, and lifting the one hard block in `notifier.py` for the Telegram channel.

1. **Create the bot.** In Telegram, message `@BotFather`, send `/newbot`, follow prompts, and copy the **bot token** it returns. Treat it as a secret.
2. **Get your chat id.** Send any message to your new bot, then visit `https://api.telegram.org/bot<TOKEN>/getUpdates` and read `message.chat.id`. That number is your `AIOS_TELEGRAM_CHAT_ID`.
3. **Store the credentials locally (never commit them).** Store them as `Get-StoredCredential` targets named `AIOS_TELEGRAM_BOT_TOKEN` and `AIOS_TELEGRAM_CHAT_ID` (the names the dispatcher looks up at `Send-AiOsNotification.ps1:229-230`). Use your local Credential Manager / secret store. Do not put them in any tracked file.
4. **Point the dispatcher config at the Telegram channel.** Copy `notification-config.example.json` to `notification-config.local.json` (the dispatcher prefers `.local` if present, `Send-AiOsNotification.ps1:166`) and set `"channel": "telegram"`. Keep `.local.json` untracked.
5. **Flip the routing flag.** In your local copy of the routing rules, set `telegram_live_send_enabled: true`. Note: the validator `Test-AiOsAlertRouting.DRY_RUN.ps1` (lines 57-59) currently *fails* if this flag is true or if `no_real_senders` is true. Arming a channel intentionally changes that posture for your live config; either run with an operator-owned live rules file the validator is not pointed at, or update the validator's expectation under Human Owner approval. Do not silently weaken the validator for the example file that ships in the repo.
6. **Lift the notifier hard-block for Telegram.** In `services/python_supervisor/notifier.py`, the block at lines 223-231 makes `--channel telegram --apply` return `LIVE_SEND=BLOCKED`. Remove/guard *that block for the Telegram channel only* so an apply run is allowed to hand off to the dispatcher's Telegram sender. (This is a code change; do it under packet/APPLY governance, not ad hoc.)
7. **Test with a synthetic BLOCKED** (see the test section below). Confirm the message lands on your phone.

Tradeoff: best reach (push over the internet), but you depend on Telegram and you are lifting a deliberate safety block — so test carefully and keep the token secret.

---

## Option 2 — Webhook

What you are doing: giving AI_OS a webhook URL that fronts a paging service you control, and flipping the webhook live flag on. No `notifier.py` block needs lifting for the dispatcher webhook path, but the cycle currently calls the notifier with `--channel file`; to deliver via webhook end to end you either invoke the dispatcher directly with `-ChannelOverride webhook` or change the cycle's notifier call to route through the webhook channel.

1. **Stand up an endpoint that pages you.** This is the part AI_OS does not own. Use a service (e.g. a pager/IFTTT/your own server) that turns an HTTP POST into a phone alert. Get its URL.
2. **Store the URL as a credential (never commit it).** Store it as the `Get-StoredCredential` target named `AIOS_WEBHOOK_URL` (the name at `Send-AiOsNotification.ps1:213`). The dispatcher reads the URL as the credential secret and POSTs JSON (`{subject, severity, message, sent_at_utc}`) to it (lines 221-223).
3. **Config + flag.** In `notification-config.local.json` set `"channel": "webhook"`, and in your local routing rules set `webhook_live_send_enabled: true`. Same validator caveat as Telegram step 5 applies.
4. **Wire delivery.** Either call `Send-AiOsNotification.ps1 -ChannelOverride webhook -Apply ...` directly, or adjust the cycle's notifier invocation so a BLOCKED routes through the webhook channel rather than `--channel file`. If the credential is ever missing, the dispatcher silently falls back to the file channel (lines 216-220) — so a missing `AIOS_WEBHOOK_URL` will look "green" but page nobody. Verify the credential is present.
5. **Test with a synthetic BLOCKED** (below) and confirm your endpoint pages you.

Tradeoff: flexible and off-LAN capable, but the actual "wake me" behavior lives in *your* endpoint. If that endpoint is down or misconfigured, AI_OS thinks it sent and you are not woken. Test the whole chain, not just the POST.

---

## Option 3 — Android / ADB

What you are doing: wiring the already-working `tools/android/Send-AiosAdbSosWake.ps1` into the BLOCKED path so a BLOCKED state triggers a real Android notification on your device.

`tools/android/Send-AiosAdbSosWake.ps1` already works standalone: it connects to a device (wireless or USB), posts a notification via `cmd notification post`, and verifies it appeared in `dumpsys notification` (lines 66-83). What it lacks is any caller.

**Hardcoded values you must set first** (this script was written for one specific machine and phone):

- `$AdbPath = "C:\Android\platform-tools\adb.exe"` (line 2) — set to your real adb path.
- `$WirelessTarget = "192.168.1.251:5555"` (line 3) — set to your phone's actual LAN IP:port. This is the device-specific value that must change.
- `$RepoRoot = "C:\Dev\Ai.Os"` (line 11) — used for its log dir; set to your repo root or it logs to the wrong place / fails to create the dir.

**Wiring steps:**

1. Fix the three hardcoded values above for your environment.
2. Confirm it works standalone: with your phone reachable over ADB, run the script directly and confirm `PASS notification visible in Android notification service` in its log (`logs/android/adb_sos_wake.log`).
3. Wire it into the BLOCKED path. The clean insertion point is where the notifier resolves an SOS wake (`notifier.py` `sos_wake_required(status)` true, lines 56-57) or as an additional step in the `sos-file-notifier` phase of `Invoke-AiOsNightCycle.ps1`. On a BLOCKED, invoke `Send-AiosAdbSosWake.ps1` after (or instead of) the file write, so a real BLOCKED produces a real phone notification. Do this under packet/APPLY governance.
4. **Test with a synthetic BLOCKED** (below).

Tradeoff: it already works and needs no third-party account, but it is **LAN-bound** — your phone must be on the same network as the AI_OS host and reachable over ADB. If you are away from home, an ADB push will not reach you. Weakest option for "wake me when I'm out," strongest for "no external dependency."

---

## How to test with a synthetic BLOCKED

You must prove the channel reaches you *before* you trust it. Do not wait for a real 2 AM blocker to find out it is broken.

1. **Make a synthetic BLOCKED state.** The notifier reads `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json` by default (`notifier.py:201`). Create a throwaway copy of that state file with `"night_supervisor_status": "BLOCKED"` (and a `plain_summary` like "SYNTHETIC SOS TEST"), and point the notifier at it with `--state <path-to-your-test-file>`. Do not overwrite the real bridge state.
2. **Dry-run first.** Run the notifier without `--apply` for your channel. For Telegram you will see the `DRY_RUN_TELEGRAM_SCAFFOLD` preview (`notifier.py:137-160`); for file you will see `STATUS=DRY_RUN_WOULD_NOTIFY` with `WAKE_CLASS=SOS` (lines 250-257). Confirm `WAKE_CLASS=SOS` before going live.
3. **Clear the de-dupe key.** If you test twice with the same state, the second run is `SUPPRESSED` (lines 244-248). Delete or change `telemetry/night_supervisor/last_notified.json` between tests, or vary the synthetic `plain_summary` so the `notification_key` differs.
4. **Live send.** Run with `--apply` (Telegram/webhook via the dispatcher; ADB via the wired call). Confirm the alert actually arrives **on your phone**, not just that the command returned `STATUS=NOTIFIED`.
5. **Test the quiet-hours bypass.** Set `AIOS_MOCK_LOCAL_TIME` (the dispatcher honors it, `Send-AiOsNotification.ps1:173`) to a time inside the quiet window and confirm a CRITICAL still goes out live (it should bypass; a non-CRITICAL should redirect to file).
6. **Clean up.** Remove the synthetic state file and reset `last_notified.json` so test state does not leak into a real run.

A channel is "armed" only after step 4 succeeds end to end and you have held the phone and seen the alert.

## HARD GATE

> **Do not register the unattended scheduler until one live channel is armed AND the dead-man watchdog is running.** Arming SOS (T0.1) closes the "I'm never woken when it dies *on purpose*" gap; the dead-man watchdog (T0.2, roadmap A2) closes the "I'm never woken when it dies *silently*" gap. Both are required before any scheduler/autostart. **Credentials and secrets are operator-provided and must never be committed** — store them in your local secret store, keep `notification-config.local.json` and any live routing-rules file untracked, and never put a token, chat id, or webhook URL into a tracked file or log.

This mirrors the roadmap's Operator safety rule: "Do not register the unattended scheduler until Tier 0 is complete."

## References

- `docs/roadmap/AIOS_ENDURANCE_HARDENING_ROADMAP.md` — finding A1, A2; Tier 0 items T0.1, T0.2; "What is already good" (quiet-by-default severity model); Operator safety rule.
- `services/python_supervisor/notifier.py` — wake classes, de-dupe, file channel, Telegram hard-block.
- `automation/orchestration/notifications/Send-AiOsNotification.ps1` — dispatcher: webhook/Telegram senders, rate limit, quiet hours, severity floor, payload block, file fallback.
- `automation/orchestration/notifications/AIOS_ALERT_ROUTING_RULES.example.json` and `Test-AiOsAlertRouting.DRY_RUN.ps1` — the `*_live_send_enabled` flags and the validator that enforces them false.
- `automation/orchestration/notifications/notification-config.example.json` — channel config and stored-credential names.
- `tools/android/Send-AiosAdbSosWake.ps1` — the working-but-unwired Android push and its hardcoded device IP/path.
- `docs/architecture/AIOS_CANONICAL_LOOP_DECISION.md` — the canonical loop this SOS path protects.

## Authority

This document is evidence and planning material only. It does not approve APPLY, scheduler registration, live-send, ADB execution, lifting the notifier live-send block, or live trading. Following it requires Human-Owner-provided credentials and governed APPLY for any code change (the `notifier.py` block, the routing-rules flag, the ADB wiring). It does not weaken AI_OS validators, approvals, locks, stop points, or any protected safety boundary defined by `AGENTS.md` and `RISK_POLICY.md`. Human Owner approval gates remain final.
