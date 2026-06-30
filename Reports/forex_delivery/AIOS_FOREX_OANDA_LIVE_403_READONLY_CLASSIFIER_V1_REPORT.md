# Forex OANDA Live 403 Read-Only Classifier V1 Report

- module: run_forex_oanda_live_403_readonly_classifier_v1
- packet_id: AIOS-FOREX-OANDA-LIVE-403-READONLY-CLASSIFIER-V1
- classifier_status: OANDA_LIVE_403_CLASSIFIER_ACCOUNT_VISIBLE_SUMMARY_OK_ORDER_FORBIDDEN
- current_stage: oanda_live_403_readonly_classifier_v1
- next_stage: owner_review_403_classification
- safe_next_action: Order placement is likely blocked; do not retry order. Review token scopes.
- blockers:
- (none)

## Input booleans
- owner_flag_present: True
- bw_session_present: True
- bitwarden_cli_available: True
- bitwarden_item_read_success: True
- live_credential_values_available_to_runtime: True
- endpoint_is_oanda_fxtrade: True
- environment_is_live: True
- allowed_mode_is_micro_live_only: True
- readonly_get_only_enforced: True
- orders_endpoint_blocked: True
- broker_api_called: True
- accounts_probe_called: True
- summary_probe_called: True
- order_endpoint_called: False
- post_request_called: False
- live_order_execution: False
- money_movement: False
- scheduler_started: False
- daemon_started: False
- webhook_started: False

## Allowed probes
- GET https://api-fxtrade.oanda.com/v3/accounts
- GET https://api-fxtrade.oanda.com/v3/accounts/{account_id}/summary

## Forbidden actions
- POST requests
- endpoints outside api-fxtrade
- PUT/PATCH/DELETE
- /orders endpoint
- any live order or money movement
- scheduler / daemon / webhook startup

## Status taxonomy
- OANDA_LIVE_403_CLASSIFIER_OWNER_RUNTIME_REQUIRED
- OANDA_LIVE_403_CLASSIFIER_CREDENTIAL_ACCESS_REQUIRED
- OANDA_LIVE_403_CLASSIFIER_READONLY_PROBE_READY
- OANDA_LIVE_403_CLASSIFIER_ACCOUNT_LIST_FORBIDDEN
- OANDA_LIVE_403_CLASSIFIER_ACCOUNT_SUMMARY_FORBIDDEN
- OANDA_LIVE_403_CLASSIFIER_ACCOUNT_NOT_VISIBLE_TO_TOKEN
- OANDA_LIVE_403_CLASSIFIER_ACCOUNT_VISIBLE_SUMMARY_OK_ORDER_FORBIDDEN
- OANDA_LIVE_403_CLASSIFIER_BROKER_UNAVAILABLE
- OANDA_LIVE_403_CLASSIFIER_REPAIR_REQUIRED

## Runtime summary
- accounts_status_code: 200
- summary_status_code: 200
- configured_account_visible: True
- account_list_count: 2
- read_only_probe_count: 0
- forbidden_reason_guess: 
- redacted_account_id: REDACTED_ACCOUNT_ID
- redacted_endpoint: https://api-fxtrade.oanda.com

## Validators
- python -m py_compile scripts/forex_delivery/run_forex_oanda_live_403_readonly_classifier_v1.py
- python -m pytest tests/forex_engine/test_forex_oanda_live_403_readonly_classifier_v1.py -q
- python scripts/forex_delivery/run_forex_oanda_live_403_readonly_classifier_v1.py
