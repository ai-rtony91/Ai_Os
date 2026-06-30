# AIOS Forex Supervised Demo Order Execution V1 Report

## Packet evaluation
- demo_order_status: SUPERVISED_DEMO_ORDER_READY
- current_stage: supervised_demo_order_execution
- next_stage: owner_execute_one_supervised_demo_order
- runtime_mode: owner_approved_supervised_demo_order
- safe_next_action: Execute owner-approved supervised demo order runtime path.
- blockers:
- (none)

## Runtime gate state
- runtime_enabled: true
- runtime_flag: --owner-approved-supervised-demo-order
- live_order_execution: false
- money_movement: false
- scheduler_started: false
- daemon_started: false
- webhook_started: false
- owner_approved_supervised_demo_order: true
- broker: OANDA
- endpoint: https://api-fxpractice.oanda.com
- broker_account_id: REDACTED_ACCOUNT_ID
- broker_api_token: REDACTED_TOKEN
- order_attempt_requested: true
- order_attempted: true
- order_attempt_count: 1
- order_attempt_success: true
- order_endpoint: https://api-fxpractice.oanda.com/v3/accounts/REDACTED_ACCOUNT_ID/orders

## Order intent
- order_intent_summary: instrument=EUR_USD, units=1, side=buy, order_type=market, time_in_force=FOK
- max_orders_per_run: 1
- side: buy
- order_type: market
- instrument: EUR_USD
