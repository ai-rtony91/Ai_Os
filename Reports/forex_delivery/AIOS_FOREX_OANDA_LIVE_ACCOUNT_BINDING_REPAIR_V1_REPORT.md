# Forex OANDA Live Account Binding Repair V1

- module: run_forex_oanda_live_account_binding_repair_v1
- packet_id: AIOS-FOREX-OANDA-LIVE-ACCOUNT-BINDING-REPAIR-V1

## Result
- account_binding_repair_status: ACCOUNT_BINDING_REPAIR_OWNER_RUNTIME_REQUIRED
- account_binding_update_status: 
- safe_next_action: Run with --owner-approved-readonly-account-binding-inspect for read-only inspection or --owner-approved-update-bitwarden-account-binding plus --select-visible-account-index for live account binding repair.
- blockers:
- owner runtime flag is required

## Input booleans
- owner_flag_present: False
- bw_session_present: False
- bitwarden_cli_available: False
- bitwarden_item_read_success: False
- broker_api_called: False
- accounts_probe_called: False
- bitwarden_update_requested: False
- bitwarden_update_attempted: False
- bitwarden_update_success: False
- order_endpoint_called: False
- post_request_called: False
- live_order_execution: False
- money_movement: False
- scheduler_started: False
- daemon_started: False
- webhook_started: False

## Runtime summary
- accounts_status_code: None
- account_list_count: 0
- configured_account_visible: False
- configured_account_fingerprint: None
- visible_account_fingerprints: []
- selected_visible_account_index: None
- selected_account_fingerprint: None
- safe_next_action: Run with owner runtime flag.

## Allowed actions
- default dry-run mode
- GET https://api-fxtrade.oanda.com/v3/accounts
- optional Bitwarden item update of broker_account_id only

## Forbidden actions
- POST requests
- /orders endpoint
- live order execution
- money movement
- scheduler, daemon, or webhook startup

## Validators
- python -m py_compile scripts/forex_delivery/run_forex_oanda_live_account_binding_repair_v1.py
- python -m pytest tests/forex_engine/test_forex_oanda_live_account_binding_repair_v1.py -q
- python scripts/forex_delivery/run_forex_oanda_live_account_binding_repair_v1.py
