# AIOS Forex Goal Decision

`aios_forex_goal_decision.py` is the read-only bridge between the completed
paper Forex build chain and the next AIOS build recommendation.

The bridge verifies that the required Forex paper components exist, creates a
deterministic local paper report fixture, passes that report into
`forex_decision_policy.decide_next_action`, and emits a machine-readable goal
decision.

Output uses schema `AIOS_FOREX_GOAL_DECISION.v1` and includes the goal,
component presence, report summary, decision, reason code, decision reasons,
next build recommendation, next safe action, and safety flags.

This bridge does not write files, use network access, dispatch workers, mutate
queues or approvals, launch runtime, connect to brokers, use credentials, place
orders, or call webhooks. Commit, push, merge, and any production action remain
human-approved actions only.
