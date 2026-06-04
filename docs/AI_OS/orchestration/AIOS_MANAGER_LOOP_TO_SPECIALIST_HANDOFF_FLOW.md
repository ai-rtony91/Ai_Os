# AI_OS Manager Loop to Specialist Handoff Flow

Purpose:
Define how AI_OS Manager uses specialists during a run.

## Default Flow

```text
manager_planner
-> route_decision
-> specialist_as_tool
-> manager_reviews_tool_output
-> validator_chain
-> approval_pause_if_needed
-> manager_final_report
```

## Tool Calls

Tool calls keep the same run alive. The specialist returns bounded output and the Manager continues the loop.

Use tools for:

- guardrail judge
- validator dispatcher
- packet generator
- clean-state verifier
- trace grader

## Handoffs

Handoff transfers branch ownership only when explicitly allowed.

Handoff requires:

- target specialist
- ownership reason
- branch
- worktree
- allowed paths
- forbidden paths
- approval rule
- validator chain
- stop point
- resume state

## Blocked Handoffs

No handoff may transfer live trading, broker/OANDA, Pi GPIO/motor, secret handling, uncontrolled autonomy, Night Supervisor runtime start, commit, push, merge, rebase, or force-push authority without a separate explicit human-approved packet.

