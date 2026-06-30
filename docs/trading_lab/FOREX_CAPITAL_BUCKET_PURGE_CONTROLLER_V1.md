# FOREX Capital Bucket Purge Controller V1

## Purpose
Read-only controller for purge, rollover, and sweep planning of capital buckets.

## Design
The controller evaluates sanitized payload fields and returns only review records:

- proposed purge actions
- rollover carries
- sweep allocation proposals
- bucket and reserve health

It never transfers funds.

## Purge Logic
- Purge stale metadata only.
- Purge stale review states and audit artifacts.
- Preserve audit history.
- No deletion of historical evidence.

## Rollover Logic
- Close review windows when configured rollover frequency is met.
- Carry forward realized profit/loss and reserve carry data.
- Add an audit placeholder in output only.

## Sweep Logic
- Conceptual `proposed_bucket_allocation` from `profit_bucket`.
- Targets: tax reserve, operating reserve, withdrawal bucket, compounding bucket.
- No live transfer or balance mutation.

## Safety
- `read_only = True`
- `money_movement_allowed = False`
- `broker_api_allowed = False`
- `bank_access_allowed = False`
- owner review remains required.

