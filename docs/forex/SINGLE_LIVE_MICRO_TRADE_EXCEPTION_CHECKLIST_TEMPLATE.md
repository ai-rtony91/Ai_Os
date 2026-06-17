# Single Live Micro-Trade Exception Checklist Template

Status: template only. This file does not approve live trading.

Live arming remains blocked unless every field below is completed by the Human Owner under `RISK_POLICY.md`. Validator output, dashboard output, generated reports, or Codex output cannot approve this exception.

## Required Fields

| Field | Required state before arming review |
|---|---|
| broker path | Human Owner controlled external broker path reference present. |
| instrument | Exact instrument named. |
| side | Exact side named. |
| units or notional limit | Smallest allowed size or explicit limit named. |
| maximum loss | Exact maximum loss named. |
| daily loss cap | Exact daily loss cap named. |
| stop loss | Exact stop loss named and attached. |
| order type | Exact order type named. |
| approval window | Start and expiry named. |
| evidence bundle path | Sanitized evidence bundle path named. |
| arming step | Manual Human Owner arming step named. |
| stop point | Hard stop after fill, rejection, error, timeout, expiry, or manual kill named. |
| Human Owner approval field | Anthony Meza named as Human Owner approval authority. |
| timestamp | Approval timestamp present. |
| account mode | Explicit account mode confirmation present. |
| paper/live mode confirmation | Explicit paper/live mode confirmation present. |

## Live Arming Hard Blocks

- No broker path reference.
- No active approval window.
- No stop loss.
- No daily loss cap.
- No maximum loss.
- No evidence bundle.
- Any credential, token, password, private key, account identifier, broker order identifier, raw live payload, or private account data appears.
- Any approval source other than Human Owner approval is treated as sufficient.
- Any retry, autonomous re-entry, or more-than-one-order behavior is enabled.

## Required Final Human Check

The Human Owner must confirm that the exception is one order only, non-transferable, expires after use, sanitized, and disarms after the terminal result. Until that confirmation exists, live execution remains blocked.
