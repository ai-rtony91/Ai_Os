# Forex Vacation Mode Owner Toggle And Operation State V1

This packet defines the product-facing Vacation Mode control layer as metadata only.
It does not execute trades, call a broker, read credentials, create a scheduler or daemon, create dashboard runtime, move money, or build banking, withdrawal, transfer, or bank routing work.

## Vacation Mode ON/OFF

Vacation Mode ON means the owner is asking AIOS to evaluate governed operation. It does not authorize execution by itself.

Vacation Mode OFF stops new trade seeking. Maintenance, proof review, receipt review, and balance/equity review may still be represented as safe metadata when appropriate.

PAUSE holds new trade seeking. RESUME rechecks calendar, proof, receipt, risk, balance/equity, runtime, credential, and owner gates before any operation state can become eligible again.

## Kill Switch

The kill switch is separate from Vacation Mode. Vacation Mode ON/OFF is an operating posture request. Kill switch is an emergency hard stop.

When kill switch stop is active, new trade seeking is blocked and owner attention is required. Kill switch reset is a review state, not an execution permission.

## Runtime Calendar

Runtime calendar state controls trade-window eligibility. Active supervision, close protection, closed maintenance, reopen preparation, weekend maintenance, and degraded maintenance are routed into the Vacation Mode operation state machine.

Calendar state never authorizes live or demo execution by itself.

## Maintenance Work

When market execution is closed, degraded, close to close, or in weekend posture, AIOS can route safe non-broker work such as proof review, receipt review, balance/equity review, report cleanup, and next-session preparation. This is productive maintenance, not autonomous trading.

## Balance And Proof Dependencies

The balance/equity observer supports profit stacking and learning metadata, but it does not compound or withdraw by itself. Proof and receipts gate repeated operation. Outstanding receipts block the next trade-seeking cycle until reviewed.

## Permission Snapshot

The permission snapshot converts operation state into explicit flags:

- metadata scanning may be allowed only when Vacation Mode is ON and gates are clean
- maintenance work may be allowed during maintenance states
- owner review metadata may be prepared when proof, receipts, or balance memory require attention
- live execution, demo execution, broker calls, credential reads, money movement, withdrawal, and bank routing remain false

## Owner Attention

Owner attention state provides INFO, REVIEW, BLOCKED, or STOP_NOW metadata for display. It does not create alert runtime and does not echo sensitive values.

## Deferred Work

Withdrawal, bank routing, transfers, and money movement remain deferred to a future owner-approved packet. Runtime execution remains a separate owner-approved runtime packet:

- `AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1`
- `AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1`
- `AIOS_FOREX_MARKET_CLOSE_PROTECTION_AND_RECEIPT_CAPTURE_V1`
- `AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1`
- `AIOS_FOREX_WEEKEND_HEAVY_MAINTENANCE_AND_AUDIT_V1`
- `AIOS_FOREX_PROOF_PIPELINE_PAUSE_AND_CONTINUE_V1`
- `AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1`
- `AIOS_FOREX_BALANCE_EQUITY_MEMORY_AND_COMPOUNDING_OBSERVER_V1`
- `AIOS_FOREX_OWNER_APPROVED_PROTECTED_LIVE_MICRO_MULTI_PAIR_BURST_RUNTIME_EXECUTION_V1`
- `AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1`
