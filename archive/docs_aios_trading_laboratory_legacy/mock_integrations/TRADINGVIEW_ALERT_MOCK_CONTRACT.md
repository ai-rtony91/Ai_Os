# TradingView Alert Mock Contract

TradingView is an optional chart/alert source only.

AI_OS Trading Lab remains the validation/orchestration brain.

Allowed mock fields:
- source
- alert_id
- signal_id
- strategy_id
- symbol
- timeframe
- alert_condition
- alert_time_mock
- message
- next_safe_action

Blocked fields:
- broker
- OANDA
- API keys
- secrets
- real webhook execution
- live market data
- order size
- order side for execution
- account id

Validation step:
Confirm the alert payload maps to a mock signal and contains no executable broker route.

Next safe action:
Route the mock alert into Signal Agent scoring only.

