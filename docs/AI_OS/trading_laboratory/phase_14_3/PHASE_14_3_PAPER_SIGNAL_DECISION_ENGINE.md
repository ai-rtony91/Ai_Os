# Phase 14.3 Paper Signal Decision Engine

Status: DRY_RUN validation scaffold
Mode: paper-only / simulation-only
Live execution: BLOCKED

## Purpose

Phase 14.3 creates the first paper-only decision result for AI_OS Trading Lab. It reads the Phase 14.2 trace and supporting paper-only ledgers, then assigns one decision state.

No broker, OANDA, API key, real webhook, real order, live market data dependency, or live trading action is allowed.

## Decision Outputs

### BLOCKED

Use `BLOCKED` when any safety or readiness blocker exists:

- live execution is not `BLOCKED`
- `execution_allowed` is `true`
- risk gate is incomplete
- regime is not approved
- signal confidence is `very_low`
- scorecard blocks live execution
- required traceability is missing

### PAPER_REVIEW_READY

Use `PAPER_REVIEW_READY` only when:

- traceability is complete
- latency status is `acceptable` or `delayed`
- regime evidence is complete for paper review
- risk evidence is complete for paper review
- live execution remains `BLOCKED`
- execution is not allowed

This state still does not allow live trading.

### INSUFFICIENT_DATA

Use `INSUFFICIENT_DATA` when the workflow is not unsafe but lacks enough paper evidence:

- paper outcomes are missing
- trade count is below threshold
- confidence score is too low
- latency, regime, or risk fields are incomplete but do not indicate unsafe execution

## Current Phase 14.3 Result

The current mock chain remains `BLOCKED` because:

- mock signal confidence is `very_low`
- mock regime is not approved
- mock risk gate is incomplete
- profitability scorecard blocks live execution
- paper trade result is not executed

## Blocked Actions

- broker execution
- OANDA execution
- API keys
- real webhooks
- real orders
- live market data dependency
- live trading
- automatic route execution

## Next Safe Action

Run the Phase 14.3 DRY_RUN validator. Keep collecting clean paper-only evidence before considering any paper review readiness state.
