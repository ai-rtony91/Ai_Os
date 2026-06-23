# AIOS Capital Flow Future Connector Contract V11

## Future Broker/Bank/Payment Connector Requirements
- runtime-only connector proof
- no credential persistence
- no account identifier persistence
- explicit Human Owner approval
- transfer request ID before any external action
- sanitized audit log after any future approved action

## Account Alias Model
- `TRADING_FLOAT`
- `RESERVE_ACCOUNT`
- `PROFIT_VAULT`
- `TAX_BUCKET`
- `OPERATING_ACCOUNT`
- `WITHDRAWAL_TARGET`
- `RESUPPLY_SOURCE`
- `COMPOUND_BUCKET`

## Forbidden Credential Persistence
Credentials, tokens, keys, card data, and payment secrets must not be stored, printed, logged, or written to repo fixtures/reports.

## Forbidden Account ID Persistence
Bank account numbers, broker account IDs, payment account IDs, broker order IDs, and raw payloads must not be stored.

## Human Approval Model
Each future real capital movement requires separate Human Owner approval for source alias, destination alias, amount, reason, rail, window, and stop condition.

## Transfer Request ID Model
`AIOS-CAPITAL-<TYPE>-<DATE>-<SEQUENCE>` sanitized request IDs may be used. They must not include bank, broker, or payment account identifiers.

## Audit Log Model
Future audit logs must contain request ID, aliases, amount, policy gate result, approval marker, status, timestamp, and sanitized failure reason.

## Failure Handling
Fail closed on connector mismatch, approval mismatch, account alias mismatch, stale proof, settlement uncertainty, or risk freeze.

## Rollback/Reversal Note
Rollback or reversal depends on external rail support and must not be guaranteed by AIOS.

## Maintenance-Window Behavior
Treasury actions should be reviewed during maintenance windows unless a future emergency policy explicitly says otherwise.

## Daily/Weekly Capital Controls
Future packets must define per-event, daily, weekly, and drawdown-aware capital controls before activation.

## Regulatory/Compliance Review
Regulatory, tax, broker, bank, and payment compliance review is required before activation.

## Connector Activation Status
Connector is not active.
