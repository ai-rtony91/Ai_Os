# AIOS Forex OANDA Demo Result To Bucket And Next Allocation V1

## Packet Context

Packet ID: AIOS-FOREX-OANDA-DEMO-RESULT-TO-BUCKET-AND-NEXT-ALLOCATION-V1

Branch: feature/forex-oanda-demo-result-to-bucket-and-next-allocation-v1

Mission outcome: created the governed result-to-bucket evaluator, safe next-allocation script, and tests for the protected OANDA demo one-order evidence path.

## Why This Is The Result-To-Bucket Layer

This packet sits after `AIOS_FOREX_OANDA_DEMO_POST_TRADE_EVIDENCE_CAPTURE_V1`. It converts sanitized post-trade evidence into deterministic demo bucket math, cycle progress, and a next-allocation recommendation.

The layer is accounting and decision support only. It does not create a broker command, does not schedule a next trade, and does not grant execution authority.

## Why This PR Does Not Call OANDA Or Place Trades

This PR does not call OANDA, does not call a broker, does not place an order, does not read `.env`, does not read credentials, does not read account identifiers, and does not persist runtime material.

The script uses example dry-run evidence only. It prints JSON result-to-bucket package output, a sanitized template, or a confirmation-blocked response.

## Post-Trade Evidence Dependency

The post-trade capture result must have status `EVIDENCE_CAPTURE_READY`, a supported post-trade classification, a normalized evidence package, all execution authority fields false, and no token, account ID, credential, secret, password, or authorization keys outside approved safe status flags.

## Bucket State Requirements

The demo bucket state requires:

- bucket currency `USD`
- starting bucket balance numeric and non-negative
- current bucket balance numeric and non-negative
- total realized P/L numeric
- current cycle start balance numeric and positive
- current cycle realized P/L numeric
- cycle profit target minimum percentage positive
- cycle profit target maximum percentage greater than or equal to minimum
- max single trade risk percentage positive and no more than five
- one-order-only true
- demo-only true
- live trading false

## Allocation Policy Requirements

The allocation policy requires:

- allocation mode `PAUSE`, `CONTINUE_DEMO`, `REDUCE_RISK`, or `INCREASE_EVIDENCE`
- compounding enabled boolean
- collect profit at target boolean
- require more evidence after loss boolean
- require owner approval for next trade true
- max next trade risk percentage positive and no greater than the bucket limit
- no live allocation true

## Owner Confirmation Requirements

Anthony must confirm:

- result reviewed
- demo-only bucket update
- no live allocation
- next trade requires approval
- no autonomous compounding

## Classification Rules

The evaluator maps:

- `DRY_RUN_ONLY` to `DRY_RUN`
- `NO_FILL_REJECTED` to `REJECTED`
- `OPEN_OR_PENDING` or `OPEN_POSITION` to `OPEN`
- `PROFIT` to `PROFIT`
- `LOSS` to `LOSS`
- `BREAKEVEN` to `BREAKEVEN`

## Bucket Math Rules

Dry-run, rejected, open, and breakeven outcomes do not change the bucket balance. Profit adds realized P/L to current bucket balance and total realized P/L. Loss subtracts the realized loss from current bucket balance and total realized P/L.

All math is deterministic and uses supplied sanitized evidence only.

## Cycle Target Handling

Cycle return percentage is calculated as:

`current_cycle_realized_pl_after_update / current_cycle_start_balance * 100`

The evaluator reports whether the cycle minimum target and maximum target are hit after applying closed trade P/L.

## Next Allocation Decisions

The evaluator recommends:

- dry run: continue demo rehearsal
- rejected or no fill: repair order or context before retry
- open or pending: wait for close evidence
- profit below target: continue demo with same or lower risk
- profit hitting target: collect profit and pause for owner review
- loss: reduce risk and require more evidence
- breakeven: continue demo with no size increase

Every recommendation keeps next-trade owner approval required, live allocation false, and autonomous compounding false.

## No Credential Or Account Persistence

The evaluator and script read no credentials, read no account IDs, read no `.env`, and persist no credential or account identifier material.

## Execution Authority False

All execution authority fields remain false:

- execution_allowed
- demo_order_allowed
- live_order_allowed
- broker_write_allowed
- autonomous_order_allowed
- scheduler_allowed
- daemon_allowed
- webhook_allowed

This is result accounting only.

## Validation Results

Targeted validation before report creation:

- `python -m py_compile automation/forex_engine/oanda_demo_result_to_bucket_and_next_allocation_v1.py tests/forex_engine/test_oanda_demo_result_to_bucket_and_next_allocation_v1.py scripts/forex_delivery/run_oanda_demo_result_to_bucket_and_next_allocation_v1.py`: pending final lane validation
- `python -m pytest tests/forex_engine/test_oanda_demo_result_to_bucket_and_next_allocation_v1.py -q`: pending final lane validation
- `python -m compileall automation/forex_engine tests/forex_engine scripts/forex_delivery`: pending final lane validation
- `git diff --check`: pending final lane validation

## Git Status

Branch `feature/forex-oanda-demo-result-to-bucket-and-next-allocation-v1` with four scoped result-to-bucket files pending final validation and staging. `docs/legal/` remains untouched and untracked.

## Exact Next Safe Action After PR Lands

Prepare:

`AIOS-FOREX-OANDA-DEMO-FIRST-TRADE-RUNBOOK-AND-OWNER-GO-NOGO-V1`

Use only sanitized evidence and bucket-output results. Do not call OANDA from Codex. Do not place a trade from Codex.
