# Forex Broker Runtime Read-Only Auth Probe V1 Report

## Packet evaluation
- probe_status: OWNER_RUNTIME_READ_ONLY_PROBE_READY
- current_stage: broker_runtime_read_only_auth_probe
- next_stage: owner_run_read_only_auth_probe
- broker_runtime_item_ref: AIOS / OANDA / Practice Demo / Broker Runtime
- redaction_status: redaction_required_boundaries_honored
- safe_next_action: Run with --owner-approved-read-only-probe when owner is ready.
- blockers:
- (none)

## Boundaries
- bitwarden_cli_called: False
- bitwarden_vault_read: False
- credentials_read: False
- env_file_read: False
- broker_api_called: False
- order_execution: False
- demo_authorized: False
- live_authorized: False

## Contract values
- default_mode: dry_run
- owner_runtime_flag: --owner-approved-read-only-probe
- runtime_mode: disabled
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
- bitwarden_cli_available: False
- bw_session_present: False
- bitwarden_item_read_success: False
- oanda_account_summary_read_success: False
