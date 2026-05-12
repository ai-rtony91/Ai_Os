# Trading Bot Agent Workflow Mock Only

Start point: mock Trading Lab only.

## Agents

1. Strategy Agent
2. Signal Agent
3. Regime Agent
4. Risk Agent
5. Journal Agent
6. Metrics Agent
7. Supervisor Agent

## Flow

Strategy -> Signal -> Regime -> Risk -> Mock Ledger -> Journal -> Metrics -> Supervisor

## Blocked

- No broker.
- No OANDA.
- No API keys.
- No real orders.

## First Build Target

Create one mock strategy record, then score one mock signal.

