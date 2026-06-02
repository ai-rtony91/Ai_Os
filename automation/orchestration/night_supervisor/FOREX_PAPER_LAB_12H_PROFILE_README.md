# Forex Paper Lab 12H Report-Only Profile

Status: REPORT_ONLY_PROFILE

This profile defines a future 12-hour Night Supervisor planning session for AIOS Lab Forex Paper Trading Simulation. It does not start Night Supervisor and does not enable any scheduler.

Source plan:

- `docs/AI_OS/trading_laboratory/reference/FOREX_PAPER_LAB_12H_SUPERVISOR_PLAN_DRY_RUN_001.md`

Principle:

- Base44 gives us the map. AIOS Lab paints the map later.

Safety boundary:

- Educational Use Only.
- Paper Trading Simulation only.
- Report-only by default.
- No live trading.
- No broker APIs.
- No OANDA.
- No webhooks.
- No real market data.
- No real orders.
- No API keys or secrets.
- No automatic commit, push, or merge.
- No dashboard theme, CSS, layout, color, or visual identity changes.
- No Base44 code or style import.

Allowed report-only work:

- Inspect Trading Lab paper simulation state.
- Generate hourly gap reports.
- Generate next-action packets.
- Generate validator checklist proposals.
- Update report-only outputs only if a later packet approves those paths.

Blocked work:

- Live trading, broker APIs, OANDA, webhooks, real market data, real orders, secrets, or API keys.
- Dashboard theme, CSS, or layout changes.
- Base44 visual or code import.
- Commits, pushes, merges, or branch deletion.
- Scheduler enable, disable, registration, or task mutation.

Hourly plan:

1. repo/status/safety baseline
2. forex paper workflow map
3. signal intake gap report
4. risk gate gap report
5. practice ledger gap report
6. latency tracker gap report
7. scorecard/report gap report
8. strategy journal gap report
9. wording/safety-label gap report
10. packet queue generation
11. validator/checklist generation
12. final digest and next-action queue

Activation rule:

- This profile is configuration/reference only. A separate approved APPLY packet is required before any Night Supervisor run, runtime output write, scheduler change, commit, push, or merge.
