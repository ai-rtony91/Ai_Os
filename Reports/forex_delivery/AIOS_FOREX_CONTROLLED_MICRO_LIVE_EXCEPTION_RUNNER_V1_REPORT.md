# AIOS Forex Controlled Micro-Live Exception Runner V1 Report

## Packet evaluation
- micro_live_status: CONTROLLED_MICRO_LIVE_EXCEPTION_READY
- current_stage: controlled_micro_live_exception_runner
- next_stage: owner_execute_one_controlled_micro_live_order
- runtime_mode: owner_approved_controlled_micro_live_exception
- safe_next_action: Execute at most one owner-run controlled micro-live OANDA order.
- blockers:
- (none)

## Repo-safe gate state
- live_order_execution: false
- demo_order_execution: false
- money_movement: false
- broker_api_called: true
- bitwarden_cli_called: true
- credentials_read: false
- env_file_read: false
- scheduler_started: false
- daemon_started: false
- webhook_started: false
- runtime_item_ref: AIOS / OANDA / Live / Broker Runtime
- order_intent_summary: instrument=EUR_USD, units=1, side=buy, order_type=market, time_in_force=FOK
- order_attempt_requested: true
- order_attempted: true
- order_attempt_count: 1
- order_status: not_created
- order_status_code: 403
