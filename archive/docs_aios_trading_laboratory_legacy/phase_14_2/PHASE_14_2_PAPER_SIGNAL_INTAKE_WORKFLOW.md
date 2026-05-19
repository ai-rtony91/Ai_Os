# Phase 14.2 Paper Signal Intake Workflow

Status: DRY_RUN validation scaffold
Mode: paper-only / simulation-only
Live execution: BLOCKED

## Purpose

Phase 14.2 connects the existing mock signal, latency ledger, regime checks, risk gates, paper result ledger, and profitability scorecard into one traceable workflow.

No broker, OANDA, API key, real webhook, real order, live market data dependency, or live trading action is allowed.

## Workflow

1. Mock signal intake
   - Source: `docs/AI_OS/trading_laboratory/mock_signals/MOCK_SIGNAL_SCORE_001.json`
   - Profitability intake: `docs/AI_OS/trading_laboratory/profitability/SIGNAL_INTAKE_LEDGER_001.json`
   - Required state: accepted for paper review only

2. Latency timestamp record
   - Source: `docs/AI_OS/trading_laboratory/latency/TRADING_LATENCY_LEDGER_001.json`
   - Required fields: alert created, alert received, validation start, validation end, route preview, simulated order time, total delay, latency status
   - `simulated_order_time` is not a real order.

3. Regime tag check
   - Mock regime ID: `MOCK_REGIME_001`
   - Profitability regime filter ID: `REGIME_FILTER_001`
   - Required state: blocked until trend, volatility, and chop review are complete

4. Risk gate check
   - Mock risk gate ID: `MOCK_RISK_GATE_001`
   - Profitability risk gate ID: `RISK_GATE_PROFITABILITY_001`
   - Required state: blocked until daily loss, position size, exposure, and drawdown review are complete

5. Paper trade simulation result
   - Paper trade ID: `PAPER_TRADE_SIM_001`
   - Required state: simulated-only result, no broker execution, no real order

6. Profitability scorecard update
   - Scorecard ID: `PAPER_PROFITABILITY_SCORECARD_001`
   - Required state: insufficient sample size until clean paper outcomes exist

## Blocked Actions

- broker execution
- OANDA execution
- API keys
- real webhooks
- real orders
- live market data dependency
- live trading
- automatic route execution

## Validation Rule

Phase 14.2 can validate field presence and traceability only. It cannot approve live execution.

Live execution remains BLOCKED until a future approved governance process says otherwise.

## Next Safe Action

Run the Phase 14.2 DRY_RUN validator and confirm the signal, latency, regime, risk, paper result, and scorecard trace is complete while execution remains blocked.
