# AI_OS Night Supervisor Dispatch Preview Boundary

Purpose:
Define the preview-only boundary for routing future OpenAI-produced packet drafts toward Night Supervisor review.

## Preview Only

Night Supervisor can receive packet preview data only. It can classify risk, recommend a night-plan route, and identify missing validation evidence.

Night Supervisor cannot:

- start runtime automatically
- write telemetry yet
- touch locks
- touch control state
- touch approval inbox state
- execute a 12h Paper SOS run
- modify runtime scripts
- touch broker/OANDA/live trading
- touch Pi GPIO/motor

## Future Runtime Start

Any future Night Supervisor run requires:

- separate human-approved packet
- runtime context precheck
- active lock check
- clean tree check
- expected worktree check
- mode check
- explicit stop controls

If any runtime context check mismatches, the supervisor start must fail closed.
