# AIOS P/L Truth Layer Requirements V1

## Status

Status: REQUIRED_FOR_LIVE_TRADE_EVIDENCE

Zone: FOREX_DELIVERY

Human Owner: Anthony Meza

## Purpose

Define mandatory profit/loss truth requirements for future live-trade evidence.

This document is a canonical evidence contract for the FOREX_DELIVERY lane. It does not authorize live trading, broker API calls, secret access, dashboard mutation, validator changes, runtime implementation, or any larger live-trading workflow.

## Problem Statement

The first recorded live micro-trade established execution evidence and reconciliation evidence, but it did not establish a durable P/L truth standard.

Future live-trade evidence must establish trade outcome truth in addition to execution and reconciliation status. AIOS must never again treat live-trade evidence as complete without a standardized profit/loss truth layer.

## Core Principle

No future live-trade evidence packet is complete without P/L truth.

Execution evidence alone is insufficient.

Reconciliation evidence alone is insufficient.

Trade outcome, P/L, balance impact when available, and sanitized post-close state must be captured before any future live-trade evidence can claim completion.

## Required Evidence Fields

Future evidence packets must include these fields:

```text
TRADE_OPENED:
TRADE_CLOSED:
INSTRUMENT:
SIDE:
UNITS:
ENTRY_STATUS:
CLOSE_STATUS:
TRADE_OUTCOME:
REALIZED_PL_RECORDED:
REALIZED_PL_VALUE_SANITIZED:
UNREALIZED_PL_RECORDED:
UNREALIZED_PL_VALUE_SANITIZED:
BALANCE_DELTA_RECORDED:
BALANCE_DELTA_SANITIZED:
BROKER_ROUNDED_RESULT_RECORDED:
POST_CLOSE_RECONCILIATION_STATUS:
OPEN_TRADES_AFTER_CLOSE:
```

Field values may be rounded, bucketed, or otherwise sanitized when needed to avoid private data exposure. Sanitization must not remove the fact of whether P/L was recorded.

## Required Security Fields

Future evidence packets must explicitly prove that private data and secrets were not recorded:

```text
PRIVATE_DATA_RECORDED: false
SECRET_VALUES_RECORDED: false
ACCOUNT_ID_RECORDED: false
RAW_BROKER_PAYLOAD_RECORDED: false
ORDER_ID_RECORDED: false
TRANSACTION_ID_RECORDED: false
```

Any `true`, missing, unknown, or ambiguous value in these security fields is a stop condition for evidence completion unless a future Human Owner-approved packet creates a narrower safe exception.

## Truth Rules

- execution evidence alone is insufficient
- reconciliation evidence alone is insufficient
- trade outcome must be recorded
- P/L must be recorded
- realized P/L must be recorded after close
- unrealized P/L must be recorded when a trade remains open
- balance impact must be recorded when available
- broker-rounded result must be recorded when balance delta is unavailable but broker result is safely reportable
- evidence must remain sanitized
- secrets must never appear
- account IDs must never appear
- raw broker payloads must never appear
- order IDs and transaction IDs must not appear unless explicitly approved and safe

## Failure Conditions

Evidence is incomplete if:

- realized P/L is missing after close
- unrealized P/L is missing while a trade is still open
- trade outcome is missing
- entry status is missing
- close status is missing when a close was attempted
- post-close reconciliation is missing
- open-trades-after-close state is missing
- balance delta or broker-rounded result is missing when safely available
- private broker data is exposed
- secret values are exposed
- account IDs are exposed
- raw broker payloads are exposed
- order IDs or transaction IDs are recorded without explicit approval

If any failure condition appears, the evidence packet must report incomplete status and identify the missing or unsafe field.

## Relationship To Other Authority Files

This document works with:

- `docs/forex_delivery/AIOS_MASTER_OPERATOR_DASHBOARD_FOREX_AUTONOMY_BACKLOG_V1.md`
- `docs/forex_delivery/AIOS_AUTO_EXIT_INTELLIGENCE_GATE_V1.md`
- `AGENTS.md`
- `README.md`
- `RISK_POLICY.md`

The master backlog defines the next AIOS FOREX_DELIVERY phase direction. The auto-exit gate blocks entry when exit controls are missing. This P/L truth layer blocks evidence completion when outcome, P/L, reconciliation, or privacy-safe proof is missing.

Root governance, safety, and risk authority still win if any conflict appears.

## Dashboard Boundary

The dashboard may display sanitized P/L truth status, trade outcome, current position state, and evidence completeness. The dashboard must not create truth.

Dashboard display must never include API keys, tokens, account IDs, raw broker payloads, endpoint secrets, private order identifiers, or transaction identifiers unless a future explicit approval defines a safe exception.

## Broker And Runtime Boundary

This document does not authorize broker calls, live orders, credential access, secret persistence, runtime connector changes, API tests, or OANDA integration.

Future implementation must remain fail-closed. If safe P/L truth cannot be captured, the live-trade evidence packet is incomplete.

## Success Criteria

Future live-trade evidence packets cannot claim completion unless P/L truth requirements are satisfied.

Minimum success means:

- the trade outcome is recorded
- realized P/L is recorded after close
- unrealized P/L is recorded if still open
- balance delta or broker-rounded result is recorded when safely available
- reconciliation status is recorded
- open-trades-after-close state is recorded
- all required security fields prove no private or secret data was recorded

## Stop Conditions

Stop if:

- P/L values cannot be safely captured
- outcome cannot be determined
- reconciliation cannot determine open or closed state
- balance impact cannot be safely represented and no broker-rounded result is available
- secret exposure risk appears
- broker payload would be recorded
- account IDs would be recorded
- order IDs or transaction IDs would be recorded without explicit approval
- live trading, broker API use, or secret access is requested without separate Human Owner approval

