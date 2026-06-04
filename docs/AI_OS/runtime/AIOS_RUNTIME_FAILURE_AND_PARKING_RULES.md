# AI_OS Runtime Failure and Parking Rules

Purpose:
Define explicit failure and parking states for interrupted AI_OS runs.

## Failure States

- `runtime_error`
- `validation_error`
- `guardrail_blocked`
- `dirty_tree_blocked`
- `wrong_worktree_blocked`
- `night_supervisor_lock_blocked`
- `approval_rejected`
- `human_parked`
- `timeout`

## Parking

A run may be parked when:

- the human pauses the lane
- approval is not available
- validation evidence is stale
- worktree or branch state changed
- runtime context is uncertain
- stream or run was canceled

Parked runs must record:

- parked reason
- state strategy
- last safe state
- next safe action
- unsafe actions blocked
- resume requirements

## Fail Closed

If state cannot be trusted, the run must fail closed. The next response must report the blocked condition and avoid file edits, commits, pushes, merges, API calls, live trading, Pi motor control, Night Supervisor runtime starts, or secret handling.

