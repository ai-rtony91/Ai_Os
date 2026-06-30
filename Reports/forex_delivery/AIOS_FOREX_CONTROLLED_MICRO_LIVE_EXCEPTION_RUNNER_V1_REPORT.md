# AIOS Forex Controlled Micro-Live Exception Runner V1 Report

## Packet evaluation
- micro_live_status: OWNER_RUNTIME_LIVE_FLAG_REQUIRED
- current_stage: controlled_micro_live_exception_runner
- next_stage: owner_run_controlled_micro_live_exception
- runtime_mode: dry_run
- safe_next_action: Run this packet with --owner-approved-controlled-micro-live-exception.
- blockers:
- live_runtime_owner_flag is False

## Repo-safe gate state
- live_order_execution: false
- demo_order_execution: false
- money_movement: false
- broker_api_called: false
- bitwarden_cli_called: false
- credentials_read: false
- env_file_read: false
- scheduler_started: false
- daemon_started: false
- webhook_started: false
- runtime_item_ref: AIOS / OANDA / Live / Broker Runtime
- order_intent_summary: instrument=EUR_USD, units=1, side=buy, order_type=market, time_in_force=FOK
- order_attempt_requested: false
- order_attempted: false
- order_attempt_count: 0
- order_status: not_attempted
- order_status_code: 0
