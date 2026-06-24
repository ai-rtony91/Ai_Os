# AIOS Forex Plumbing Diagnostic Campaign V1

## Packet Context

Packet ID: AIOS-MERGE-1049-THEN-FOREX-PLUMBING-DIAGNOSTIC-CAMPAIGN-V1

Branch: feature/forex-plumbing-diagnostic-campaign-v1

## Mission Outcome

Created AIOS Forex Plumbing Diagnostic Campaign V1. The campaign models the 10-point plumbing proof required before the first protected OANDA demo attempt review. It is deterministic, in-memory, side-effect free, and review-only.

## Ten Diagnostics

1. `end_to_end_dry_run_ticket`
2. `oanda_demo_read_only_connection_model`
3. `fake_buy_sell_ticket_replay`
4. `risk_failure_gate`
5. `evidence_capture`
6. `overnight_protection`
7. `compounding_bucket`
8. `final_owner_click_dry_run_rehearsal`
9. `demo_micro_trade_readiness_review_only`
10. `morning_proof_review_model`

## What Each Diagnostic Proves

- The dry-run ticket check proves the order ticket chain can produce a review-only, non-executable ticket.
- The OANDA demo read-only connection model proves demo readiness can be represented without a broker call, credential read, or account identifier read.
- The fake BUY/SELL replay proves both directional ticket paths can be rehearsed without execution.
- The risk failure gate proves stop loss, take profit, and risk failures block before any attempt.
- The evidence capture check proves sanitized pre-trade and post-trade evidence paths are ready.
- The overnight protection check proves kill switch, daily stop, max loss, and overnight risk notes are represented.
- The compounding bucket check proves the capital cycle supervisor supports the candidate without forced quota chasing.
- The final owner-click dry-run rehearsal proves the final confirmation path can be rehearsed without order placement.
- The demo micro-trade readiness gate proves the actual attempt remains review-only.
- The morning proof model proves the next-day proof review can be pending before an overnight outcome and complete after evidence exists.

## Why This Gets AIOS Ready For First Protected Overnight Demo Attempt

This campaign verifies the plumbing around the eventual attempt before a separate final owner-click bridge is considered. It checks the ticket chain, read-only runtime model, fake directional replay, risk failure behavior, evidence path, overnight protection, compounding dependency, owner-click rehearsal, review-only demo readiness, and morning proof model.

## What Remains Blocked

The campaign does not place a demo trade, call OANDA, read credentials, read account identifiers, authorize live trading, start a scheduler, start a daemon, or create a webhook. Actual demo order placement remains blocked until a separate owner-approved final-click packet exists.

## Execution Authority False

The campaign always returns false for:

- `execution_allowed`
- `demo_order_allowed`
- `live_order_allowed`
- `broker_write_allowed`
- `autonomous_order_allowed`
- `scheduler_allowed`
- `daemon_allowed`
- `webhook_allowed`

## Validation Results

Validation passed in this lane:

- `python -m py_compile automation/forex_engine/forex_plumbing_diagnostic_campaign_v1.py tests/forex_engine/test_forex_plumbing_diagnostic_campaign_v1.py`
- `python -m pytest tests/forex_engine/test_forex_plumbing_diagnostic_campaign_v1.py -q` - 10 passed
- `python -m compileall automation/forex_engine tests/forex_engine`
- `git diff --check`
- `git diff --name-only`
- `git status --short --branch`

## Git Status

Final status before staging showed branch `feature/forex-plumbing-diagnostic-campaign-v1` with only the three scoped diagnostic campaign files untracked plus `docs/legal/` still untracked and untouched.

## Next Safe Action

Validate, stage only the three approved diagnostic campaign files, commit, push, and open a PR. The next milestone remains `AIOS-FOREX-OANDA-DEMO-FINAL-OWNER-CLICK-ORDER-BRIDGE-V1`.
