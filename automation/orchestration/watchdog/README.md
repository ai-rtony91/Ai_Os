# AI_OS Tier 0 — Dead-Man Watchdog

`aios_deadman_watchdog.py` is a cross-platform (pure Python 3 stdlib) dead-man
watchdog. It closes the scariest audit finding: **if the unattended loop dies,
nothing fires and the operator is never woken.**

## What it does

- Reads the runtime heartbeat (`telemetry/runtime/runtime_heartbeat.json`) and
  parses its timestamp (`heartbeatAt` / `last_beat` / etc.).
- Computes staleness against a threshold (default **600s / 10 min**).
- If the heartbeat is **missing, unreadable, or older than the threshold**, it
  classifies the situation as `BLOCKED` — the loop is presumed **dead** — and
  produces an SOS alert record (`detected_at`, `last_heartbeat`,
  `staleness_seconds`, `threshold_seconds`, `severity=BLOCKED`,
  `recommended_action`).
- **Fail-closed:** any failure to read the heartbeat is treated as `BLOCKED`
  (presumed dead), never as OK. The watchdog itself never crashes — all file IO
  is wrapped, and an internal error fail-closes to `BLOCKED`.
- **Exit code:** `0` if healthy, `2` if `BLOCKED`, so an external scheduler
  could later act on it.

Severity model matches `services/python_supervisor/notifier.py`: **`BLOCKED`
is the only SOS-worthy / wake-worthy state** (quiet-by-default).

## Safety posture — intentionally NOT armed (Tier 0 gate)

This module is **DISABLED-BY-DEFAULT and DRY_RUN by default**. It does **not**:

- send any live notification (`live_send`)
- register any scheduler / cron / systemd / Task Scheduler entry (`scheduler_registration`)
- start any background loop (`loop_start`)

These appear in the script's `BLOCKED_CAPABILITIES` list. In DRY_RUN it only
writes the alert to `telemetry/watchdog/DEADMAN_ALERT_LATEST.json` and prints a
clear summary — it delivers the alert nowhere.

The `--apply` flag is **reserved for future live delivery**. In this version,
even with `--apply`, it still only writes the alert file and prints
`LIVE_DELIVERY_NOT_ARMED: wire an SOS channel first`. **It does not send.**
Wiring an actual SOS channel + scheduler registration is a deliberate later tier.

## How to run (DRY_RUN)

```bash
# Default: read the real runtime heartbeat, 600s threshold.
python3 automation/orchestration/watchdog/aios_deadman_watchdog.py

# Custom threshold (e.g. 5 minutes).
python3 automation/orchestration/watchdog/aios_deadman_watchdog.py --threshold-seconds 300

# Point at a specific heartbeat file.
python3 automation/orchestration/watchdog/aios_deadman_watchdog.py \
  --heartbeat-path /path/to/runtime_heartbeat.json

# Reserved flag: still DRY_RUN-only, prints LIVE_DELIVERY_NOT_ARMED.
python3 automation/orchestration/watchdog/aios_deadman_watchdog.py --apply
```

Arguments:

| Flag | Default | Meaning |
| --- | --- | --- |
| `--threshold-seconds` | `600` | Max heartbeat age before `BLOCKED`. |
| `--heartbeat-path` | `telemetry/runtime/runtime_heartbeat.json` | Heartbeat file to check (relative paths resolve to repo root). |
| `--alert-path` | `telemetry/watchdog/DEADMAN_ALERT_LATEST.json` | Where the DRY_RUN alert JSON is written. |
| `--apply` | off | Reserved; live delivery is NOT armed in this version. |

## Output

The alert JSON (`AIOS_DEADMAN_ALERT.v1`) is written to
`telemetry/watchdog/DEADMAN_ALERT_LATEST.json`. It is local runtime evidence,
not source authority.
