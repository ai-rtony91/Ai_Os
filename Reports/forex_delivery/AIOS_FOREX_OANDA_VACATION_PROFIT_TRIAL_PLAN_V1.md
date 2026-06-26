# AIOS Forex OANDA Vacation Profit Trial Plan V1

## Purpose

Create a non-executing vacation profit trial plan preview for owner review.

## Plan Preview

- Trial capital placeholder: `OWNER_RUNTIME_TRIAL_CAPITAL_VALUE`
- Trial duration placeholder: `OWNER_RUNTIME_TRIAL_DURATION_VALUE`
- Maximum allowed drawdown: `5.00`
- Daily stop: `2.00`
- Max trade risk: `0.50`
- No compounding.
- No withdrawals.
- No deposits.
- No unattended approval yet.
- Owner review required.

## Abort Rules

- Abort if drawdown limit is reached.
- Abort if daily stop is reached.
- Abort if trade risk exceeds contract.
- Abort if account boundary is unclear.
- Abort if credential boundary is unclear.
- Abort if monitoring or alerting is not confirmed.
- Abort if owner SOS escalation is not confirmed.

## Post-Trial Review Requirements

- Capture realized P/L summary.
- Capture drawdown summary.
- Capture trade count summary.
- Capture reconciliation summary.
- Capture journal summary.
- Route result back to evidence ledger.

## Boundary

No trade placed by this packet.
No broker call was made by this packet.
No live approval was granted.
No real money approval was granted.
No compounding approval was granted.
No bank movement approval was granted.
No autonomous execution was granted.
Unattended vacation mode remains blocked.
Profit is not guaranteed.
All protected flags remain false.

