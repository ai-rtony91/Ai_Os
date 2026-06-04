# AI_OS Dispatch Route Scoring

## Scores

- `route_confidence`: 0.0 to 1.0 confidence that the route is correct.
- `risk_score`: 0.0 to 1.0 risk of unsafe execution.
- `readiness_score`: 0.0 to 1.0 evidence that all preconditions and validators exist.
- `safety_score`: 0.0 to 1.0 evidence that blocked actions stay blocked.

## Thresholds

- Minimum route confidence for non-blocked routes: `0.75`.
- Maximum risk score for non-blocked routes: `0.40`.
- Minimum readiness score for non-blocked routes: `0.80`.
- Minimum safety score for non-blocked routes: `0.90`.

## Fail-Closed Scoring Rules

- Any `UNKNOWN_RISK` lowers route confidence.
- Any `SECRET_RISK`, `API_KEY_RISK`, `ENV_FILE_RISK`, or `SERVICE_ACCOUNT_FILE_RISK` blocks execution.
- Any `LIVE_TRADING_RISK`, `BROKER_RISK`, `OANDA_RISK`, or `PI_MOTOR_RISK` blocks execution.
- Any profitability-priority violation blocks execution.
- Missing validators route to `BLOCKED`.
- Confidence below threshold routes to `BLOCKED`.
- When uncertain, fail closed.

