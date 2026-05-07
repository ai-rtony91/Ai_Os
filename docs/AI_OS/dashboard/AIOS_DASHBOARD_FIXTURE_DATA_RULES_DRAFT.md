# AI_OS Dashboard Fixture Data Rules Draft

## Purpose

This draft defines safe fixture data rules for a future dashboard preview.

No protected root files are edited by this draft. Human approval is required before fixture APPLY. This draft creates no live automation, no production dashboard, and no trading automation.

## Allowed Fixture Data

- Static fixture data.
- Fake sample health states.
- Non-secret validator statuses.
- Non-live progress percentages.
- Sample operator notes.
- Sample checkpoint links.

## Blocked Fixture Data

- Credentials.
- Tokens.
- API keys.
- Broker data.
- Private user data.
- Browser profiles.
- Live market data.
- Live order path.
- Trade execution decisions.

## Fixture Rule

Fixtures must be deterministic and safe to commit. Fixtures must not include private paths, secrets, broker data, live execution data, or live trading decisions.

## Boundary

This draft does not activate dashboard writers, does not create production dashboard output, and does not approve live automation.
