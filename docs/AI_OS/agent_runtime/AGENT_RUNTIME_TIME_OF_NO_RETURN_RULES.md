# Agent Runtime Time-of-No-Return Rules

## Easy To Change

These are easy to change before commit:

- Docs
- Fixtures
- Local queues
- Local validators
- Local paper-only runners before commit

## Harder After Commit

These get harder after commit because other work may start depending on them:

- Public repo history
- Schema names used by dashboard
- File paths used by validators
- Backend fields used by data

## Harder After App Release

These get harder after an app release:

- Package names
- Privacy policy
- Financial declarations
- Public app description
- Business identity

## Never Rush

Never rush:

- Live trading
- Broker connection
- API keys
- User login
- Payments
- Play Store financial app release

