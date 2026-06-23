# AIOS Forex Broker Proof Runtime-Only Human Intake Template V1

## Sanitized Proof Fields To Provide
- broker alias, not account ID: `BROKER_ALIAS_ONLY`
- environment: `DEMO` or `LIVE_PROOF_ONLY`
- proof timestamp: `ISO-8601`
- instrument availability: `AVAILABLE_OR_BLOCKED`
- spread snapshot, if visible: `SPREAD_ALIAS_OR_WITHIN_CAP`
- connection proof status: `CURRENT_OR_BLOCKED`
- order placement disabled confirmation: `true`
- account ID redacted confirmation: `true`
- credential not pasted confirmation: `true`
- credential not persisted confirmation: `true`
- screenshot/evidence filename alias if applicable: `SANITIZED_ALIAS`
- broker UI balance redacted confirmation: `true`
- risk disclaimer acknowledgement: `true`
- human operator confirmation: `true`
- next safe action: `STOP_OR_REVIEW_PACKET`

## Explicitly Forbidden
- API keys
- passwords
- account IDs
- card/bank data
- account balances tied to account IDs
- raw broker secrets
- copied .env content
- live order commands
- auto-trading commands

## Safety Statement
This template is intake-only. It does not authorize broker calls, order placement, money movement, automation, scheduler, daemon, webhook, or dashboard execution authority.
