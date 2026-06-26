# AI_OS Agent Run Loop Doctrine

Purpose:
Define one AI_OS application-level run from goal intake through final report.

## Core Rules

- One AI_OS run is one application-level turn.
- The manager loop continues until a real stopping point.
- Tool calls are executed and the same run continues.
- Handoffs transfer branch ownership only when explicitly allowed.
- Human approval pauses a run; it does not start a new run.
- Interrupted runs must resume from saved state.
- Canceled streams or runs must be marked parked or resumable.
- State strategy must be explicit.
- Do not mix local replay with server-managed continuation unless intentionally reconciling.
- Final answer or result must include paste-back summary and clean-state result.

## Lifecycle

```text
goal_input
-> manager_planner
-> route_decision
-> specialist/tool call
-> validator_chain
-> approval_pause if needed
-> resume_from_state
-> execution_result
-> clean_state_verifier
-> trace_grade
-> improvement_loop_candidate
-> final_report
```

## Manager Ownership

The AI_OS Manager owns the run by default. Specialists are tools unless an explicit handoff transfers bounded branch ownership.

The Manager owns:

- route decision
- tool call selection
- validator chain
- approval pause
- resume state
- final report
- paste-back summary
- clean-state result

## Safety

Every run state must preserve:

- trusted/proven profitability priority
- default paper/simulation trading until gates pass
- no broker/OANDA/live trading
- no secrets
- no uncontrolled autonomy
- no Pi GPIO/motor action
- no Night Supervisor runtime modification
