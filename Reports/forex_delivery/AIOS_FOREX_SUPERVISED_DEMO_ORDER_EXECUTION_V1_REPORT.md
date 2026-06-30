# AIOS Forex Supervised Demo Order Execution V1 Report

## Packet evaluation
- demo_order_status: OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED
- current_stage: supervised_demo_order_execution
- next_stage: owner_supervised_demo_approval
- runtime_mode: dry_run
- safe_next_action: Collect owner supervised demo approval and rerun with approval context.
- blockers:
- owner_supervised_demo_approval is False

## Runtime gate state
- runtime_enabled: False
- runtime_flag: --owner-approved-supervised-demo-order
- live_order_execution: false
- money_movement: false
- scheduler_started: false
- daemon_started: false
- webhook_started: false
- broker: OANDA
- endpoint: https://api-fxpractice.oanda.com
- order_attempt_requested: False
- order_attempted: False
- order_attempt_count: 0
- order_attempt_success: False
## Order intent
- order_intent_summary: instrument=EUR_USD, units=1, side=buy, order_type=market, time_in_force=FOK
- max_orders_per_run: 1
- side: buy
- order_type: market
- instrument: EUR_USD
