# Phase 18.13 Dispatch to Night Supervisor Preview

Dispatcher output for the runway must be:

- route: `NIGHT_SUPERVISOR_PREVIEW`
- stage status: `PREVIEW_ONLY`
- runtime start: `BLOCKED`
- human approval: `REQUIRED`
- telemetry/control/lock/approval writes: `BLOCKED`

The dispatcher may attach validators and preview risk. It must not start runtime.

