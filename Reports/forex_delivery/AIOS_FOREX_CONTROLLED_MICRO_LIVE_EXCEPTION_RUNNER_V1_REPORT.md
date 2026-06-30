# AIOS Forex Controlled Micro-Live Exception Runner V1 Report

## Packet evaluation
- micro_live_status: LIVE_RUNTIME_CREDENTIAL_ACCESS_REQUIRED
- current_stage: controlled_micro_live_exception_runner
- next_stage: owner_unlock_bitwarden_live_runtime
- runtime_mode: owner_approved_controlled_micro_live_exception
- safe_next_action: Resolve BW_SESSION, Bitwarden CLI availability, and live runtime credentials.
- blockers:
- bitwarden_item_read_success is False
- live_credential_values_available_to_runtime is False

## Repo-safe gate state
- live_order_execution: false
- demo_order_execution: false
- money_movement: false
- broker_api_called: false
- bitwarden_cli_called: true
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
