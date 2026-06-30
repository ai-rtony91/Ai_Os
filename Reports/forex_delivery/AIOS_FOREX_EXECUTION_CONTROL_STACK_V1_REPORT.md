# Forex Execution Control Stack V1 Report

## Packet evaluation
- control_status: SUPERVISED_DEMO_APPROVAL_REQUIRED
- current_stage: execution_control_stack
- next_stage: owner_supervised_demo_approval
- safe_next_action: Request owner supervised demo approval before order execution.
- blockers:
- owner_demo_approval is False

## Control output
- control_stage: execution_control_stack
- next_stage_after_success: owner_supervised_demo_approval
- packet_id: AIOS-FOREX-EXECUTION-CONTROL-STACK-V1
- default_mode: dry_run

## Boundaries
- broker_api_called: False
- bitwarden_cli_called: False
- credentials_read: False
- env_file_read: False
- order_execution: False
- demo_authorized: False
- live_authorized: False
- kill_switch_state: enabled
- risk_state: within_limits
- duplicate_guard_state: guard_enabled
- audit_state: audit_log_ok

## Scope settings
- order_intent_id: DRY_RUN_ORDER_INTENT_001
- instrument: EUR_USD
- units: 1
- side: buy
- order_type: market
- stop_loss_defined: True
- take_profit_defined: True
- session_window_hours: 22
- session_window_days_per_week: 6
