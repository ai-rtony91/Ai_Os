# AIOS Forex Demo Trade Readiness Bridge V1

## Purpose

The Demo Trade Readiness Bridge V1 connects the sanitized broker snapshot intake stack to the supervised demo trade execution review stack. It produces a local-only readiness result for Anthony to review before any supervised demo trade can be considered.

No broker call was made. No trade placed.

## How The Bridge Links The Stacks

The bridge uses the landed broker snapshot intake epic to confirm sanitized snapshot intake, broker snapshot review, and account readiness status. It then evaluates the selected local candidate context, risk gate, position sizing, demo order plan, operator ticket, post-trade evidence capture plan, and feedback routing plan.

The bridge is build-only. It does not approve execution and does not perform broker action.

## Ready Sample Status

- Status: `DEMO_TRADE_READINESS_BRIDGE_READY_FOR_OWNER_REVIEW`
- Selected strategy: `Supertrend`
- Candidate id: `supertrend-review-ready-sample`
- Instrument: `EUR_USD`
- Direction: `LONG`
- Proposed units: `20000`
- Entry price: `1.1000`
- Stop loss: `1.0950`
- Take profit: `1.1100`
- Max loss: `100.00`
- Expected reward: `200.00`
- Reward-to-risk: `2`

## Blocked Sample Status

- Status: `DEMO_TRADE_READINESS_BRIDGE_BLOCKED_SNAPSHOT`
- Cause: blocked sanitized broker snapshot intake sample
- Next safe action: resolve the bridge blocker before preparing an owner review bundle

## Blocked Actions

- Demo execution
- Broker action
- Real money
- Compounding
- Bank movement
- Live trading
- Credential access
- Account ID persistence

## Permission Status

All protected permissions remain false:

- `demo_execution_allowed`: false
- `broker_action_allowed`: false
- `real_money_allowed`: false
- `compounding_allowed`: false
- `bank_movement_allowed`: false
- `live_trading_allowed`: false
- `credential_access_allowed`: false
- `account_id_persistence_allowed`: false

## Next Safe Action

Anthony may review the local bundle manually. Codex must not execute, approve broker action, request credentials, request account identifiers, or place any trade.
