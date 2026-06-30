# FOREX Capital Rail Registry V1

## Purpose
Read-only redacted registry for rails and withdrawal routing review.

## Redaction Rules
- Only approved redacted fields are retained (last4 only, no full identifiers).
- Sensitive financial keys are rejected.
- Third-party rails are blocked unless explicitly allowed by policy.

## Allowed Types
- OANDA debit card/ACH/domestic wire/international wire.
- Personal bank ACH/wire.
- `unknown` placeholder.

## Outputs
- `rail_registry`: sanitized rail objects.
- `rails_by_type`: by allowed type.
- `eligible_rails`: active + withdrawal + same-name verified.
- `blocked_rails`: explicit blocker reasons.

## Rail Selection
- Lowest cost route among eligible rails.
- Fastest route among eligible rails.
- Preferred withdrawal rail: same-name verified, active, low fee, faster on tie, owner preferred.

## Safety
- No bank connectivity.
- No broker connectivity.
- No transfer or movement output.
- Owner decision required before execution.

