# Phase 18.13 Night Supervisor Preview Route

Expected route: `NIGHT_SUPERVISOR_PREVIEW`

Required status:

- `PREVIEW_ONLY`
- `RUNTIME_START_BLOCKED`
- `HUMAN_APPROVAL_REQUIRED`

The preview may classify work and produce a recommended plan. It must not start Night Supervisor, write telemetry, write control state, write locks, write approval inbox state, resume Paper SOS, call OpenAI, touch broker/OANDA/live trading, or touch Pi GPIO/motor.

