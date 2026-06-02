# Forex Paper Lab 12H Loop Runner README 001

Status: REPORT_ONLY_LOOP_RUNNER_REFERENCE

## What This Runner Does

`automation/orchestration/night_supervisor/Invoke-AiOsForexPaperLab12HReportOnlyLoop.DRY_RUN.ps1` is a dedicated Forex Paper Lab report-only loop runner. It reads `FOREX_PAPER_LAB_12H_PROFILE.json`, validates the report-only profile boundary, and can later run up to 12 bounded report-only cycles.

## Why It Exists

The existing wrapper previews the 12-hour plan. It does not execute repeated hourly cycles. This runner closes that missing capability without using the old Night Cycle path.

## Wrapper Preview vs Loop Runner

- Wrapper preview: prints the 12-hour plan and safety closeout only.
- Loop runner: validates the same profile, checks STOP markers before start and before every cycle, checks repo status, and plans per-cycle report/status output.

## Report-Only Boundary

The runner is Educational Use Only and Paper Trading Simulation only. It blocks live trading, broker APIs, OANDA, webhooks, real market data, real orders, API keys, secrets, dashboard theme/CSS/layout changes, Base44 code/style import, automatic commits, automatic pushes, and automatic merges.

## STOP Marker Behavior

The runner checks these markers before starting and before every cycle:

- `control/self_continuation/STOP`
- `relay/STOP.flag`

If a marker exists, the runner stops before continuing.

## OutputRoot Behavior

Default `OutputRoot`:

```text
telemetry/night_supervisor/forex_paper_lab_12h
```

Preview mode writes no telemetry/runtime output. A later approved non-preview report-only launch may write report/status files only under `OutputRoot`.

## Why Old Night Cycle Is Not Used

`Invoke-AiOsNightCycle.ps1` is not profile-specific to Forex Paper Lab report-only work. This runner avoids that path so the session does not inherit unrelated automation, scheduler, PR watch, hygiene, or APPLY behavior.

## Future Human Owner Launch

A later Human Owner approved launch packet can run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/night_supervisor/Invoke-AiOsForexPaperLab12HReportOnlyLoop.DRY_RUN.ps1 -MaxCycles 12 -IntervalSeconds 3600
```

For validation only, use no-wait preview:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/night_supervisor/Invoke-AiOsForexPaperLab12HReportOnlyLoop.DRY_RUN.ps1 -MaxCycles 1 -IntervalSeconds 0 -PreviewOnly
```

## Blocked

- Old Night Cycle usage.
- Scheduler enable, disable, registration, or mutation.
- Git add, commit, push, merge, force push, reset, clean, or branch deletion.
- Dashboard or Trading Lab runtime edits.
- Broker, webhook, API, secret, OANDA, real-market-data, real-order, or live-trading work.

## Tonight Status

This file and runner do not start tonight by themselves. A separate explicit Human Owner launch packet is required.
