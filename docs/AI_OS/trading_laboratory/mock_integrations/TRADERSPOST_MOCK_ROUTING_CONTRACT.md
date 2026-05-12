# TradersPost Mock Routing Contract

TradersPost is an optional mock routing layer only.

AI_OS Trading Lab remains the validation/orchestration brain.

Allowed mock fields:
- source
- route_id
- signal_id
- strategy_id
- symbol
- timeframe
- routing_mode
- validation_status
- blocked_reason
- next_safe_action

Blocked fields:
- broker
- OANDA
- API keys
- secrets
- live broker route
- real webhook execution
- real orders
- live market data
- account id

Validation step:
Confirm the route is mock-only and blocked before any ledger or journal review.

Next safe action:
Keep route blocked and send the mock signal through regime and risk gates.

