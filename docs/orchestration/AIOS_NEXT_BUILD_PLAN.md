# AIOS Next Build Plan

`aios_next_build_plan.py` is the read-only router that converts a completed
AIOS goal decision into the next deterministic build plan.

The current Forex chain is:

```text
build -> test -> score/report -> decision -> next build plan
```

The router accepts an `AIOS_FOREX_GOAL_DECISION.v1` style dictionary and emits
`AIOS_NEXT_BUILD_PLAN.v1` with the goal, input decision, route, next component,
next packet ID, reason code, plan reasons, next safe action, approval
requirements, and safety flags.

Routing is deterministic:

- `continue_build` routes to `forex_risk_controls`.
- `improve_strategy` routes to a strategy rules review.
- `improve_data` routes to a data quality review.
- `improve_risk_controls` routes to `forex_risk_controls`.
- `stop_for_human_review` and invalid decisions route to `stop`.

This router does not write files, use network access, mutate queues or
approvals, dispatch workers, launch runtime, start schedulers or daemons, touch
credentials, connect to brokers, place orders, call webhooks, stage, commit,
push, or merge. It is planning evidence only; protected actions still require
Anthony approval.
