# AIOS Dashboard OANDA Read-Only Balance Finish V1

## Packet

- packet_id: AIOS-OANDA-READONLY-BALANCE-DASHBOARD-FINISH-V1
- lane: OANDA_READONLY_BALANCE_DASHBOARD_FINISH
- branch: feature/oanda-readonly-balance-dashboard-finish-v1
- priority: profit path first, then read-only money visibility, then minimal dashboard display

## Endpoint Status

- endpoint: `GET /api/forex/oanda/money-strip`
- backend owner: `services/orchestrator/index.js`
- source model: `src/forex_delivery/read_only_live_data_bridge.py`
- sanitizer owner: `automation/forex_engine/read_only_live_data_sanitizer.py`
- default behavior: blocked/sanitized when runtime controls are missing
- browser-to-OANDA calls: not added

## Dashboard Status

- active surface: `apps/dashboard/src/MinimalOperatorDashboard.jsx`
- new component: `apps/dashboard/src/BrokerMoneyStrip.jsx`
- fixture: `apps/dashboard/mock-data/aios-oanda-money-strip-v1.example.json`
- display mode: read-only, blocked by default
- execution state shown: `EXEC OFF`

## Fields Shown

- BAL
- NAV
- P/L
- MARGIN
- OPEN
- PAIR
- SPREAD
- TARGET
- EXEC OFF

## Safety Guarantees

- No broker writes.
- No POST, PUT, PATCH, or DELETE broker calls.
- No order placement, order modification, order cancellation, trade close, or position close.
- No demo order and no live trade.
- No credentials persisted or displayed.
- No account identifiers persisted or displayed.
- No raw broker payloads persisted or displayed.
- No browser-side OANDA calls.
- No scheduler, daemon, webhook, or background execution created.
- No Azure deployment.
- No merge.

## Validation

- Pending final command chain:
  - `python -m compileall src/forex_delivery automation/forex_engine scripts/forex_delivery tests/forex_engine`
  - `python -m pytest tests/forex_engine -q`
  - `npm --prefix apps/dashboard run build`
  - `npm --prefix apps/dashboard run test --if-present`
  - `git diff --check`
  - `git diff --name-only`
  - `git status --short --branch`

## Remaining Blockers

- Real OANDA money numbers still require separately configured runtime-only read-only environment controls.
- This dashboard strip does not authorize demo orders, live orders, broker writes, Azure deploy, or live trading.
- Profit target remains evidence-gated and not guaranteed.

## Next Safe Action

Run the validator chain, then stage only exact lane files if validation passes.
