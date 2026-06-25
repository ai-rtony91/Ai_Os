# AIOS Forex OANDA Read-Only Closed Result TP/SL Classifier Adapter V1 Report

## Root Cause

The landed read-only filled-trade P/L capture and the landed closed-trade TP/SL classifier used different evidence shapes. AIOS needed a bounded adapter so sanitized capture output could be accepted and reshaped for the classifier without requiring the owner to manually rebuild evidence.

## Implementation Summary

- Added a pure-Python in-memory adapter that accepts sanitized read-only capture output plus an optional trade anchor.
- Extracted classifier-safe open trade, closed trade, trade evidence, transaction, transaction-match, account-summary presence, and P/L evidence from known capture shapes.
- Called `evaluate_oanda_closed_trade_tpsl_result_capture_v1` after adapter-level unsafe-field and unsafe-authority rejection.
- Added adapter status pass-through for still-open, TP close, SL close, other profit, other loss, breakeven, trade-not-found, unsafe, and invalid classifier outcomes.
- Added a JSON-only CLI runner with `--print-template` and dry-run samples for still-open, TP, SL, other profit, other loss, trade not found, and unsafe evidence.
- Added focused tests for adapter status mapping, profit-claim control, unsafe rejection, sensitive-value rejection, open unrealized profit handling, and CLI sanitized output.

## Tests

- `python -m pytest tests/forex_engine/test_oanda_readonly_closed_result_tpsl_classifier_adapter_v1.py -q`
- `python -m py_compile automation/forex_engine/oanda_readonly_closed_result_tpsl_classifier_adapter_v1.py scripts/forex_delivery/run_oanda_readonly_closed_result_tpsl_classifier_adapter_v1.py`

## Safety

This is adapter-only. It is not a broker caller, OANDA caller, order placer, order closer, order mutator, trade mutator, position mutator, bucket updater, scheduler, daemon, webhook, next-trade authorizer, or live funding step.

The adapter does not import or call `urllib`, `requests`, `socket`, `ctypes`, Windows Vault APIs, `.env`, environment variables, or broker endpoints. It rejects unsafe allowed/performed flags and sensitive runtime values before calling the classifier.

## Next Safe Action

Review the adapter diff and validation output. No commit, push, PR, merge, broker call, OANDA call, vault read, env read, bucket update, or next-order authorization was performed.
