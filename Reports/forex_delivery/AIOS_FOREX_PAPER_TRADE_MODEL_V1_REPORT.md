PACKET: FOREX-PAPER-TRADE-MODEL-V1
BRANCH: feature/forex-paper-trade-model-v1
FILES INSPECTED: automation/forex_engine/models.py, automation/forex_engine/paper_execution.py, apps/trading_lab/trading_lab/forex_portfolio_state.py, docs/orchestration/AIOS_FOREX_PORTFOLIO_STATE.md, tests/forex_engine/test_paper_execution.py, tests/forex_engine/test_schema_contracts.py, tests/forex_engine/test_paper_trade_lifecycle.py
FILES CHANGED: automation/forex_engine/paper_trade_lifecycle.py, tests/forex_engine/test_paper_trade_lifecycle.py, docs/orchestration/AIOS_FOREX_PAPER_TRADE_MODEL.md, Reports/forex_delivery/AIOS_FOREX_PAPER_TRADE_MODEL_V1_REPORT.md
MODEL ADDED: Canonical dataclass `PaperTradeLifecycle` in `automation/forex_engine/paper_trade_lifecycle.py` plus constants and helpers for deterministic status transitions.
STATUSES ADDED: candidate, previewed, rejected, queued, opened, active, closed, killed, expired, error.
VALIDATION RULES: Required non-empty `trade_id`, uppercase pair normalization, buy/sell direction, market/limit/stop entry type, positive entry/SL/TP/units, non-negative dollar/percent risk, required created timestamp, safety boundary enforcement, terminal status guardrails, close_reason whitelist.
TRANSITION RULES: `candidate->{previewed|rejected}`, `previewed->{queued|rejected}`, `queued->{opened|expired|killed}`, `opened->{active|closed|killed|error}`, `active->{closed|killed|expired|error}`, terminal statuses are final.
TESTS ADDED: tests/forex_engine/test_paper_trade_lifecycle.py
REPORT CREATED OR SKIPPED: REPORT CREATED
WHAT WAS NOT TOUCHED: automation/forex_engine/paper_execution.py, existing `automation/forex_engine/models.PaperTrade` and its constructors, dashboard and orchestrator trees, broker/demo/live modules, and all forbidden governance/doc files.
VALIDATORS RUN: NOT RUN BY CODEX
PROTECTED ACTIONS: none
BROKER/LIVE/SECRET RISK: Safety map is enforced in all returned trade dict payloads; no network, broker, scheduler, daemon, webhook, credentials, or file-write code added in lifecycle module.
NEXT HUMAN COMMANDS: Add targeted unit test execution in your local environment for this packet, then wire lifecycle into the paper-forward evidence pipeline when repository state allows.
STATUS: COMPLETE
