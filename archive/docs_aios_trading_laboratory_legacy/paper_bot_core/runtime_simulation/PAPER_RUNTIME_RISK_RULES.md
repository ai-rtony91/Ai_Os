# Paper Runtime Risk Rules

The Paper Risk Gate blocks by default unless paper trade review conditions pass.

Required paper trade review checks:

- Paper Trade Signal source is paper-trade sample data
- live execution is BLOCKED
- latency is acceptable or under review
- Paper Regime Review is known or marked review
- confidence score is high enough
- Paper Scorecard has enough paper trade samples
- no broker/OANDA/API key/credential path exists

If any required check fails, the runtime result stays BLOCKED.
