# AIOS Forex OANDA Demo Micro Trade Profitability Bridge V1

## Packet ID

AIOS-DASHBOARD-SAVE-AND-FOREX-PROFITABILITY-MILESTONE-BRIDGE-V1

## Branch

feature/dashboard-login-cloudflare-bot-connect-finish-v1

## Mission Outcome

Created an execution-grade OANDA demo micro-trade profitability bridge for owner review. The bridge evaluates whether a proposed demo micro-trade has a complete profit-seeking structure, hard risk controls, broker readiness evidence, read-only money visibility, outcome evidence requirements, and owner review gates.

This packet also preserves the owner-expected four-icon AIOS operator home as the active dashboard entry surface.

## Why This Encapsulates Profitability

The bridge does not promise profit. It requires a proposed trade to prove the structure needed to generate useful profit/loss evidence:

- candidate and strategy identity
- instrument and direction
- entry rationale
- planned entry, stop loss, and take profit
- bounded position size
- bounded risk amount
- expected reward amount
- reward/risk threshold
- spread limit
- order type and time-in-force
- hard stop controls for overnight review
- evidence capture before and after the trade outcome

Profitability remains an evidence gate. A trade can become ready for owner review only when it is structured to produce auditable P/L evidence under hard controls.

## Code Created

- `automation/forex_engine/oanda_demo_micro_trade_profitability_bridge_v1.py`

The module is deterministic, pure Python, side-effect free, and accepts only sanitized in-memory dictionaries.

## Tests Created

- `tests/forex_engine/test_oanda_demo_micro_trade_profitability_bridge_v1.py`

The tests cover missing plan, broker readiness, risk state, money state, BUY/SELL geometry, reward/risk threshold, oversized position, missing stop loss, missing take profit, overnight controls, margin use, open/pending order counts, evidence capture, owner approval, valid BUY/SELL owner-review paths, execution authority locks, and JSON serialization.

## Exact Gates Implemented

- Trade plan completeness gate
- Profitability structure gate
- BUY/SELL stop-loss and take-profit geometry gate
- Reward/risk threshold gate
- Micro/demo position-size cap gate
- Overnight risk gate
- Broker readiness gate
- Risk state gate
- Money state gate
- Evidence capture gate
- Owner approval gate
- Execution authority hard-lock gate

## Overnight Trade Handling

Overnight holding is blocked unless the plan includes an overnight risk note and the risk state proves daily stop, max loss gate, kill switch, stop loss, take profit, and bounded trade risk.

## Why This Does Not Place A Trade

The bridge has no broker import, no network path, no file read, no environment read, no persistence, no scheduler, no daemon, no webhook, and no order-placement logic. It returns a JSON-serializable readiness dictionary only.

## Why This Does Not Authorize Live Trading

All execution authority fields remain false in every result:

- `execution_allowed`
- `demo_order_allowed`
- `live_order_allowed`
- `broker_write_allowed`
- `autonomous_order_allowed`
- `scheduler_allowed`
- `daemon_allowed`
- `webhook_allowed`

The highest bridge result is `MICRO_TRADE_READY_FOR_OWNER_REVIEW`, not permission to place an order.

## How This Advances The First Governed OANDA Demo Micro-Trade

The next demo micro-trade can now be reviewed through a deterministic checklist before any separate human-approved execution packet exists. The owner can inspect whether the candidate has an entry plan, hard stop, hard take profit, position cap, spread cap, risk budget, money state, broker readiness, and evidence capture path.

## How This Supports Later 22-Hour / Six-Day Supervised Campaign Evidence

This bridge establishes the per-trade proof unit needed before any longer supervised campaign can be reviewed. A 22-hour / six-day campaign needs repeatable evidence units with consistent risk controls, money snapshots, broker readiness proof, outcome capture, and owner review boundaries.

## Validation Results

- `python -m py_compile automation/forex_engine/oanda_demo_micro_trade_profitability_bridge_v1.py tests/forex_engine/test_oanda_demo_micro_trade_profitability_bridge_v1.py`: PASS
- `python -m pytest tests/forex_engine/test_oanda_demo_micro_trade_profitability_bridge_v1.py -q`: PASS, 20 passed
- `python -m compileall automation/forex_engine tests/forex_engine`: PASS
- `npm --prefix apps/dashboard run build`: PASS
- `npm --prefix apps/dashboard run test --if-present`: PASS
- `git diff --check`: PASS with line-ending conversion warnings only
- `git diff --name-only`: dashboard active files only because new Forex/report files are untracked before staging
- `git status --short --branch`: expected dashboard and Forex bridge dirty files plus untouched `docs/legal/`

## Git Status

Expected local APPLY state before exact-file staging. `docs/legal/` remains outside lane and untouched.

## Next Safe Action

Run the full validator chain, stage only the exact approved files, commit, push the current feature branch, and open the PR into `main`. Do not merge.
