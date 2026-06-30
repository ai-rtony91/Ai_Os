# Forex Broker Runtime Read-Only Auth Probe V1 Report

## Packet evaluation
- probe_status: BROKER_RUNTIME_READ_ONLY_AUTH_PROVEN
- current_stage: broker_runtime_read_only_auth_probe
- next_stage: execution_control_stack
- broker_runtime_item_ref: AIOS / OANDA / Practice Demo / Broker Runtime
- redaction_status: redaction_required_boundaries_honored
- safe_next_action: Move to execution control stack and keep this packet read-only.
- blockers:
- (none)

## Boundaries
- bitwarden_cli_called: True
- bitwarden_vault_read: True
- credentials_read: True
- env_file_read: False
- broker_api_called: True
- order_execution: False
- demo_authorized: False
- live_authorized: False

## Contract values
- default_mode: dry_run
- owner_runtime_flag: --owner-approved-read-only-probe
- runtime_mode: enabled
- runtime_stage: broker_runtime_read_only_auth_probe
- bw_session_required: True
- bitwarden_cli_required: True
- expected_endpoint: https://api-fxpractice.oanda.com
- expected_environment: practice_demo
- expected_allowed_mode: read_only_until_owner_demo_approval
- session_window_hours: 22
- session_window_days_per_week: 6
- item_ref: AIOS / OANDA / Practice Demo / Broker Runtime
- next_stage_after_success: execution_control_stack

## Scope checks
- bitwarden_cli_available: True
- bw_session_present: True
- bitwarden_item_read_success: True
- oanda_account_summary_read_success: True
