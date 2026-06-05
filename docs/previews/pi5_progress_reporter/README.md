# Pi5 Progress Reporter Preview

This folder contains a static local preview for the AI_OS Pi5 Progress Reporter display.

## How to open

Open `PI5_PROGRESS_REPORTER_PREVIEW.html` in a browser from the repo checkout.

The page tries to read:

```text
../../../telemetry/morning_digest/PI5_PROGRESS_REPORT_LATEST.json
```

Some browsers block local `file://` JSON fetches. When that happens, the preview uses a clearly marked fallback sample copied from the current `AIOS_PI5_PROGRESS_REPORT.v1` shape.

## Boundary

This preview is display-only.

It does not:

- deploy to the Raspberry Pi 5
- create a service
- create a scheduler or background task
- touch GPIO or motor controls
- launch workers
- mutate approvals
- stage, commit, push, or merge
- touch secrets, broker/API, OANDA, live trading, real orders, real webhooks, or production

## Data contract

The preview renders the existing Pi5 progress report contract:

```text
AIOS_PI5_PROGRESS_REPORT.v1
```

Visible fields include AI_OS progress, Forex paper-build progress, Night Supervisor health, validation health, worker readiness, approval clearance, human-needed state, current phase, next safe action, blocker count, active approval count, last updated time, stale warnings, and display cards.

## Safety labels

The preview keeps these labels visible:

- `DISPLAY ONLY`
- `NOT APPROVAL AUTHORITY`
- `NO MOTOR / GPIO / TRADING CONTROL`

Forex is shown as `REPORT_ONLY_PROFILE / paper simulation planning only`; the UI must not imply a live bot, broker connection, real market data, or real orders.
