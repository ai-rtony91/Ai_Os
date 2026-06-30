# AIOS Forex Live Micro Evidence Review V1

## Purpose
Post-live-proof evidence review for one controlled micro-live order. This packet does not place a trade.

## Input
- owner_flag_present: True
- bw_session_present: True
- bitwarden_cli_available: True
- bitwarden_item_read_success: True
- live_credential_values_available_to_runtime: True
- endpoint_is_oanda_fxtrade: True
- environment_is_live: True
- allowed_mode_is_micro_live_only: True
- readonly_get_only_enforced: True
- summary_probe_called: True
- open_trades_probe_called: True
- open_positions_probe_called: True
- trades_probe_called: True
- transactions_probe_called: False
- order_endpoint_called: False
- post_request_called: False
- trade_close_called: False
- position_close_called: False
- live_order_execution: False
- demo_order_execution: False
- money_movement: False
- scheduler_started: False
- daemon_started: False
- webhook_started: False
- prior_live_order_created_evidence_present: True

## Result
- evidence_status: LIVE_MICRO_EVIDENCE_PROFIT_NEGATIVE
- current_stage: live_micro_evidence_review
- next_stage: owner_continue_repeatability
- safe_next_action: Capture post-live evidence persistence across sessions and continue repeatability testing.
## Blockers
- none

## Runtime summary
- summary_status_code: 200
- open_trades_status_code: 200
- open_positions_status_code: 200
- trades_status_code: 200
- transactions_status_code: None
- prior_order_status_code: 201
- prior_order_status: created
- instrument: EUR_USD
- units: 
- side: buy
- time_in_force: FOK
- open_trade_found: True
- open_position_found: False
- trade_count: 1
- position_count: 1
- trades_count: 1
- trade_fingerprints: ['sha256:98144d79af44']
- position_fingerprints: ['sha256:cfdf108c1549']
- unrealized_pl_available: True
- unrealized_pl_value: -0.0002
- pnl_classification: negative
- risk_controls_observed: True
- sl_tp_observed: True
- sl_observed: True
- tp_observed: True
- sltp_evidence_sources: ['open_trades']
- sl_source: open_trades
- tp_source: open_trades
- sl_fingerprint: sha256:fc5a72b2dcaa
- tp_fingerprint: sha256:717449c97979
- trailing_sl_observed: False
- trailing_sl_fingerprint: None
- sltp_evidence_complete: True
- redacted_account_id: REDACTED_ACCOUNT_ID
- safe_next_action: Capture post-live evidence persistence across sessions and continue repeatability testing.

## Allowed probes
- GET https://api-fxtrade.oanda.com/v3/accounts/{account_id}/summary
- GET https://api-fxtrade.oanda.com/v3/accounts/{account_id}/openTrades
- GET https://api-fxtrade.oanda.com/v3/accounts/{account_id}/openPositions
- GET https://api-fxtrade.oanda.com/v3/accounts/{account_id}/trades
- GET https://api-fxtrade.oanda.com/v3/accounts/{account_id}/transactions/sinceid?id=<safe transaction id>

## Forbidden actions
- Any order/mutation endpoint, non-GET method, /orders path, trade close, position close
- Any endpoint outside https://api-fxtrade.oanda.com
- Broker money movement, scheduler, daemon, webhook

## Status taxonomy
- LIVE_MICRO_EVIDENCE_OWNER_RUNTIME_REQUIRED
- LIVE_MICRO_EVIDENCE_CREDENTIAL_ACCESS_REQUIRED
- LIVE_MICRO_EVIDENCE_READONLY_REVIEW_READY
- LIVE_MICRO_EVIDENCE_ORDER_CREATED_NO_OPEN_TRADE_FOUND
- LIVE_MICRO_EVIDENCE_CLOSED_OR_NOT_VISIBLE
- LIVE_MICRO_EVIDENCE_OPEN_TRADE_FOUND
- LIVE_MICRO_EVIDENCE_OPEN_POSITION_FOUND
- LIVE_MICRO_EVIDENCE_PROFIT_POSITIVE
- LIVE_MICRO_EVIDENCE_PROFIT_FLAT
- LIVE_MICRO_EVIDENCE_PROFIT_NEGATIVE
- LIVE_MICRO_EVIDENCE_BROKER_UNAVAILABLE
- LIVE_MICRO_EVIDENCE_REPAIR_REQUIRED

## Safe next action
Capture post-live evidence persistence across sessions and continue repeatability testing.
## Validators
- python -m py_compile scripts/forex_delivery/run_forex_live_micro_evidence_review_v1.py
- python -m pytest tests/forex_engine/test_forex_live_micro_evidence_review_v1.py -q
- python scripts/forex_delivery/run_forex_live_micro_evidence_review_v1.py
