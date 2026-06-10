# AI_OS Observe Spine Runner

- observe_loop_status: `OBSERVE_LOOP_INVALID`
- p2_bridge_status: `INVALID`
- queue_gate_status: `BLOCKED`
- runtime_apply_status: `INVALID`
- sos_status: `INVALID`
- scheduler_status: `BLOCKED`

## Layer status
- p2_bridge: status=INVALID stale=False real=True governance=False code=False
- queue_mutation_gate: status=BLOCKED stale=False real=True governance=True code=False
- runtime_apply_lane: status=INVALID stale=False real=True governance=True code=True
- sos_arming: status=INVALID stale=False real=True governance=True code=False
- scheduler_registration: status=BLOCKED stale=False real=True governance=True code=False

## Mutation boundaries
- queue_mutation: false
- worker_inbox_mutation: false
- approval_inbox_mutation: false
- command_queue_mutation: false
- runtime_launch: false
- runtime_execution: false
- scheduler_registration: false
- sos_notification: false
- trading_execution: false
- safe_next_action: Resolve stale/invalid evidence and rerun observe-spine runner.
