# AIOS Forex OANDA Demo Post-Trade Evidence Capture V1

## Packet Context

Packet ID: AIOS-FOREX-OANDA-DEMO-POST-TRADE-EVIDENCE-CAPTURE-V1

Branch: feature/forex-oanda-demo-post-trade-evidence-capture-v1

Mission outcome: created the governed post-trade evidence capture evaluator, JSON-only capture script, and tests for the protected OANDA demo one-order attempt path.

## Why This Is The Post-Trade Evidence Layer

This packet sits after `AIOS_FOREX_OANDA_DEMO_OWNER_RUN_ACTUAL_ONE_ORDER_COMMAND_V1`. It validates the owner command result, validates a broker-call result or dry-run rehearsal result, validates sanitized post-trade evidence, classifies the outcome, and packages the evidence without broker access.

The layer exists to capture the outcome of the one protected demo attempt after Anthony performs any manual owner-run action outside Codex.

## Why This PR Does Not Call OANDA Or Place Trades

This PR does not call OANDA, does not call a broker, does not place an order, does not read `.env`, does not read credentials, does not read account identifiers, and does not persist runtime material.

The script uses example dry-run evidence only. It prints JSON evidence package output, a sanitized template, or a confirmation-blocked response.

## Owner Command Dependency

The owner command result must have status `OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND` and all execution authority fields false.

## Broker Call Result Dependency

The broker call result must have status `BROKER_CALL_ATTEMPTED_DEMO_ORDER_ONCE` or `BROKER_CALL_DRY_RUN_READY`. It must keep order attempt count at one or less, live order allowed false, autonomous order allowed false, all execution authority fields false, and no sensitive broker keys beyond approved runtime-only placeholders.

## Evidence Requirements

Post-trade evidence must include:

- evidence mode `DRY_RUN_REHEARSAL`, `ORDER_REJECTED`, `ORDER_SUBMITTED`, `ORDER_FILLED`, or `ORDER_CLOSED`
- broker `OANDA_DEMO`
- environment `DEMO`
- boolean order-attempted state
- sanitized order reference for submitted, filled, or closed evidence
- filled or rejected status
- fill price or rejection reason
- stop loss attachment boolean
- take profit attachment boolean
- realized P/L when closed as number or null
- unrealized P/L snapshot as number or null
- close reason when closed
- post balance as number or null
- post NAV as number or null
- timestamp
- one-order-only true
- max order attempts 1
- no second order true
- credential persistence false
- account ID persistence false
- no token, account ID, credential, secret, password, or authorization keys in the supplied evidence

## Owner Evidence Confirmation Requirements

Anthony must confirm:

- post-trade evidence reviewed
- no second order
- no credentials in evidence
- no account IDs in evidence
- stop loss checked
- take profit checked
- P/L recorded

## Classification Rules

The evaluator classifies:

- `DRY_RUN_REHEARSAL` as `DRY_RUN_ONLY`
- `ORDER_REJECTED` as `NO_FILL_REJECTED`
- submitted or pending orders as `OPEN_OR_PENDING`
- filled but not closed orders as `OPEN_POSITION`
- closed positive realized P/L as `PROFIT`
- closed negative realized P/L as `LOSS`
- closed zero realized P/L as `BREAKEVEN`

## Overnight And Morning Proof Rules

If the evidence classifies as an open or pending position and `hold_allowed_overnight` is true, the evaluator requires overnight follow-up and morning proof. Closed trades do not require overnight proof.

## No Credential Or Account Persistence

The evaluator and script read no credentials, read no account IDs, read no `.env`, and persist no credential or account identifier material. Normalized evidence uses sanitized references only.

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

This is an evidence-capture layer only.

## Validation Results

Targeted validation before report creation:

- `python -m py_compile automation/forex_engine/oanda_demo_post_trade_evidence_capture_v1.py tests/forex_engine/test_oanda_demo_post_trade_evidence_capture_v1.py scripts/forex_delivery/run_oanda_demo_post_trade_evidence_capture_v1.py`: pending final lane validation
- `python -m pytest tests/forex_engine/test_oanda_demo_post_trade_evidence_capture_v1.py -q`: pending final lane validation
- `python -m compileall automation/forex_engine tests/forex_engine scripts/forex_delivery`: pending final lane validation
- `git diff --check`: pending final lane validation

## Git Status

Branch `feature/forex-oanda-demo-post-trade-evidence-capture-v1` with four scoped post-trade evidence files pending final validation and staging. `docs/legal/` remains untouched and untracked.

## Exact Next Safe Action After PR Lands

Prepare:

`AIOS-FOREX-OANDA-DEMO-RESULT-TO-BUCKET-AND-NEXT-ALLOCATION-V1`

Use only sanitized evidence output from this packet. Do not call OANDA from Codex. Do not place a trade from Codex.
