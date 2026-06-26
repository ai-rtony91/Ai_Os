# AIOS Forex OANDA Supervised Live Microtrade Owner Runbook V1

## Purpose

Generate owner-runbook template with placeholders only.

## Required Statements

- Anthony performs any real broker action manually outside Codex.
- Codex does not execute.
- AIOS does not execute autonomously.
- Runtime values are not persisted.
- Account identifiers are not stored.
- One tiny trade only.
- No compounding.
- No bank movement.
- No unattended loop.
- No vacation mode approval.
- No profit guarantee.

## Runtime Placeholders

- `OWNER_RUNTIME_PROVIDER_LABEL`
- `OWNER_RUNTIME_ACCOUNT_BOUNDARY_CONFIRMATION`
- `OWNER_RUNTIME_INSTRUMENT_CONFIRMATION`
- `OWNER_RUNTIME_UNITS_CONFIRMATION`
- `OWNER_RUNTIME_STOP_DISTANCE_CONFIRMATION`
- `OWNER_RUNTIME_TAKE_PROFIT_DISTANCE_CONFIRMATION`
- `OWNER_RUNTIME_FINAL_CONFIRMATION_PHRASE`

## Forbidden Values

- real endpoint URL
- credential value
- account identifier
- raw broker payload
- broker order identifier
- saved runtime value

## Next Packet After Owner Run

`AIOS-FOREX-OANDA-OWNER-RUN-LIVE-MICROTRADE-RESULT-CAPTURE-V1`

## Boundary

No trade placed by this packet.
No broker call was made by this packet.
No live approval was granted.
No real money approval was granted.
No compounding approval was granted.
No bank movement approval was granted.
No autonomous execution was granted.
Unattended vacation mode remains blocked.
Vacation profit trial remains blocked unless Anthony separately approves.
Profit is not guaranteed.
All protected flags remain false.
Owner-run only.
One-shot only.

