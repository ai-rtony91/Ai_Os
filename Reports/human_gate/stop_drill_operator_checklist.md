# AI_OS STOP Drill Operator Checklist

## Status

- checklist_status: `HUMAN_CHECKLIST_DRY_RUN`
- stop_drill_pass: `False`
- stop_drill_claimed_passed: `False`
- runtime_execution_allowed: `False`
- runtime_launch_allowed: `False`
- queue_write_allowed: `False`
- scheduler_registration_allowed: `False`
- sos_notification_allowed: `False`
- live_trading_allowed: `False`
- vacation_mode_complete: `False`

## Preconditions

- Main must be clean before any separate human STOP drill confirmation packet is prepared.
- No runtime execution may be active unless Anthony knowingly starts a separate manual test outside this packet.
- No broker or live trading connection may be active.
- No secrets may be written to the repo.
- No scheduler action is authorized.
- No SOS action is authorized.
- Codex must not execute STOP, kill processes, launch runtime, mutate queues, send SOS, or register scheduler tasks.

## Manual STOP Drill Decision

- Anthony must decide whether to run the STOP drill manually.
- If Anthony does not run the STOP drill, leave `stop_drill_pass = false`.
- If Anthony runs the STOP drill, evidence must be recorded manually outside automation.
- This checklist does not prove the STOP drill passed.
- This checklist does not authorize runtime execution, scheduler registration, SOS send, queue write, broker action, live trading, or vacation mode.

## Required Evidence Fields

- `performed_by = Anthony / Human Owner`
- `performed_at_local_time`
- `observed_stop_condition`
- `recovery_behavior_observed`
- `no_runtime_execution_by_codex = true`
- `no_queue_mutation = true`
- `no_worker_inbox_mutation = true`
- `no_scheduler_registration = true`
- `no_sos_send = true`
- `no_live_trading = true`
- `no_secret_written = true`
- `stop_drill_pass = false` by default

## Required Exact Phrase

`ANTHONY_CONFIRMS_STOP_DRILL_PASSED_FOR_DRY_RUN_RECOVERY_PROOF_ONLY`

This phrase only confirms STOP drill evidence after Anthony manually performs and records the drill. It does not authorize runtime execution, scheduler registration, SOS send, queue write, broker action, live trading, or vacation mode.

## Safe Next Action

1. Anthony reviews this checklist.
2. Anthony either declines the STOP drill and AI_OS remains blocked, or performs the STOP drill manually and records evidence.
3. After real human evidence exists, create a separate confirmation packet.

## Stop Condition

Stop before claiming STOP drill pass, executing STOP through Codex, killing processes, launching runtime, executing runtime, mutating queues, sending SOS, registering scheduler, touching credentials, writing secrets, enabling live trading, or setting `vacation_mode_complete = true`.
