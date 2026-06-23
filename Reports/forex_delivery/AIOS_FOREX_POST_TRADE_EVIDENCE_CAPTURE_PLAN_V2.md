# AIOS Forex Post-Trade Evidence Capture Plan V2

## Objective

Define the sanitized evidence that must be captured after any future Human Owner-executed live micro-trade. This plan does not authorize Codex, the dashboard, a scheduler, a daemon, a webhook, or an LLM to place an order.

## Trade Reference

| Field | Value |
|---|---|
| Trade number | AIOS-TRADE-PENDING-BLOCKED-V2 |
| Session ID | SESSION-EVIDENCE-MISSING |
| Candidate ID | c1-eur-buy directional evidence, not approved |
| Evidence bundle | LIVE-MICRO-TRADE-EVIDENCE-001 referenced in fixture evidence |
| Status | PLAN_CREATED_FOR_FUTURE_HUMAN_EXECUTION_ONLY |

## Capture Requirements

| Evidence item | Capture rule | Sanitization rule |
|---|---|---|
| Timestamp capture | Record pre-trade, fill, exit, and reconciliation timestamps. | No account IDs, broker order IDs, transaction IDs, tokens, or raw payloads. |
| Screenshot or proof capture | Capture broker-side visible confirmation if Anthony executes manually in the future. | Crop or redact account identifiers and private balances if needed. |
| Broker-side confirmation reference | Record a sanitized human-readable reference that proves order state. | Do not persist account ID, credential material, broker order ID, transaction ID, endpoint payload, or raw broker response. |
| Entry record | Capture instrument, side, entry price, order type, and units. | Store only sanitized trade metadata. |
| Stop-loss record | Capture stop-loss value and whether it was attached before execution. | Do not store broker payloads. |
| Take-profit record | Capture take-profit value or explicit Human Owner-approved none. | Current V2 live ticket is blocked because this packet requires take-profit evidence. |
| Fill/slippage record | Capture expected entry, actual fill, slippage, and whether cap passed. | Store numeric trade evidence only, not account identifiers. |
| Spread record | Capture spread at pre-trade and fill if available. | Store spread value only. |
| Exit record | Capture exit method, exit price, and exit timestamp. | No raw broker payloads. |
| P/L record | Capture realized P/L and result pips. | Do not expose private account identifiers. |
| Realized R | Capture realized R against planned risk. | Use sanitized calculation inputs. |
| Reconciliation status | Record OPEN, CLOSED, RECONCILED, or INCIDENT_REVIEW_REQUIRED. | Store status without private broker identifiers. |
| Incident flag | Mark true if fill, stop, take-profit, spread, slippage, close, or reconciliation fails. | No credential or account details. |
| Journal note | Record short operator note and whether the trade matched the approved ticket. | Keep notes free of secrets and account identifiers. |

## Sanitized Storage Path

Future evidence should be written only to an explicitly approved `Reports/forex_delivery/` evidence artifact or other Human Owner-approved sanitized evidence path. This packet does not create a live trade evidence artifact because no trade was executed.

## Stop Conditions

- Stop if a credential, token, account ID, broker order ID, transaction ID, or raw broker payload would need to be written.
- Stop if the live trade was not executed by Anthony as a human operator.
- Stop if the dashboard, Codex, an LLM, a scheduler, a daemon, or a webhook is asked to submit or close an order.
- Stop if take-profit evidence or an explicit future approved no-take-profit exception is missing.
- Stop if reconciliation cannot be completed with sanitized evidence.

## Next Review Packet

Create a separate future post-trade reconciliation packet only after Anthony performs a separately approved human-only live micro-trade and provides sanitized evidence. That packet must preserve the no-credentials, no-account-ID, no-broker-order-ID, and no-raw-payload boundary.
