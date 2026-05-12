# Trading Bot Mock Handoff Contract

Workflow:
Strategy -> Signal -> Regime -> Risk -> Mock Ledger -> Journal -> Metrics -> Supervisor

Rules:
- Mock-only.
- No broker.
- No OANDA.
- No API keys.
- No real orders.
- No live market data.

Required handoff fields:
- input
- output
- status
- blocker
- next_safe_action

Agent handoff order:
- Strategy Agent outputs a versioned mock strategy record.
- Signal Agent scores one mock signal against the strategy.
- Regime Agent labels mock trend, chop, volatility, or UNKNOWN.
- Risk Agent blocks unsafe mock execution.
- Mock Ledger records simulated decisions only after risk approval.
- Journal Agent records reason, outcome, and lesson.
- Metrics Agent calculates mock performance fields only.
- Supervisor Agent selects the next safe action.

