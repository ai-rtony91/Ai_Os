# Pi5 Progress Reporter Preview

This folder contains a static local screen-mode preview for the AI_OS Pi5 Progress Reporter display.

## How to open

Best local preview path:

```powershell
python -m http.server 8765
```

Then open:

```text
http://localhost:8765/docs/previews/pi5_progress_reporter/PI5_PROGRESS_REPORTER_PREVIEW.html
```

Opening `PI5_PROGRESS_REPORTER_PREVIEW.html` directly from the repo checkout can still work as a static fallback preview.

The preview uses large touch-friendly tabs:

- Status
- Approval
- Forex
- Workers
- Brief
- Safety

The page tries to read:

```text
../../../telemetry/morning_digest/PI5_PROGRESS_REPORT_LATEST.json
```

Some browsers block local `file://` JSON fetches. When that happens, the preview uses a clearly marked fallback sample copied from the current `AIOS_PI5_PROGRESS_REPORT.v1` shape.

The preview refreshes from the JSON report every 8 seconds when loaded through a local server. It shows the last refresh time, the data source (`JSON`, `FALLBACK`, or `ERROR`), and a stale-data warning when the report timestamp is missing, invalid, older than 15 minutes, or the JSON fetch fails.

## Boundary

This preview is display-only. Tabs switch visible sections only; they are not action controls.

It does not:

- deploy to the Raspberry Pi 5
- create a service
- create a scheduler or background task
- touch GPIO or motor controls
- expose motor, GPIO, broker, trading, worker-launch, or approval buttons
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

The actual Pi screen size or resolution is not required yet. This preview can be tuned later for the final Raspberry Pi display dimensions without changing authority or adding controls.

## Safety labels

The preview keeps these labels visible:

- `DISPLAY ONLY`
- `NOT APPROVAL AUTHORITY`
- `NO MOTOR / GPIO / TRADING CONTROL`

Forex is shown as `REPORT_ONLY_PROFILE / paper simulation planning only`; the UI must not imply a live bot, broker connection, real market data, or real orders.
