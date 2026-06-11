# AI_OS STOP Drill Evidence Template

## Status

- template_status: `REVIEW_ONLY_TEMPLATE`
- status: `HUMAN_GATE_REQUIRED`
- stop_drill_pass: `False`
- stop_drill_claimed_passed: `False`
- confirmation_phrase_used: `False`

## Evidence Fields

- performed_by: `Anthony / Human Owner`
- performed_at_local_time: manual entry required after a real human STOP drill.
- observed_stop_condition: manual entry required after a real human STOP drill.
- recovery_behavior_observed: manual entry required after a real human STOP drill.
- manual_evidence_recorded: `False`

## Safety Fields

- no_runtime_execution_by_codex: `True`
- no_queue_mutation: `True`
- no_worker_inbox_mutation: `True`
- no_command_queue_mutation: `True`
- no_scheduler_registration: `True`
- no_sos_send: `True`
- no_live_trading: `True`
- no_secret_written: `True`
- runtime_execution_allowed: `False`
- runtime_launch_allowed: `False`
- queue_write_allowed: `False`
- scheduler_registration_allowed: `False`
- sos_notification_allowed: `False`
- live_trading_allowed: `False`
- broker_action_allowed: `False`
- vacation_mode_complete: `False`

## Required Exact Phrase

`ANTHONY_CONFIRMS_STOP_DRILL_PASSED_FOR_DRY_RUN_RECOVERY_PROOF_ONLY`

This phrase only confirms STOP drill evidence after Anthony manually performs and records the drill. It does not authorize runtime execution, scheduler registration, SOS send, queue write, broker action, live trading, or vacation mode.

## Safe Next Action

Anthony reviews the checklist, then either declines the STOP drill and remains blocked, or performs the STOP drill manually and records evidence. After real human evidence exists, create a separate confirmation packet.

## Stop Condition

Stop before claiming STOP drill pass, executing STOP through Codex, killing processes, launching runtime, executing runtime, mutating queues, sending SOS, registering scheduler, touching credentials, writing secrets, enabling live trading, or setting `vacation_mode_complete = true`.
