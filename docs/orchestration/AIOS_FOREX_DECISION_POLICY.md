# AIOS Forex Decision Policy

This generated component is the seventh `forex-paper-bot` build step. It turns
a local paper scorecard from `forex_report` into a deterministic next-action
decision for AIOS continuation.

Allowed decisions are `continue_build`, `improve_strategy`, `improve_data`,
`improve_risk_controls`, and `stop_for_human_review`.

The policy stops for human review when risk flags are present, improves data
when no trades were produced, improves strategy when win rate is low, improves
risk controls when total paper PnL is negative, and continues building only
when the report is acceptable.

The component is paper/research-only. It blocks live execution, broker orders,
credentials, API keys, real orders, webhooks, and network fields. It performs no
file writes and no network access.
