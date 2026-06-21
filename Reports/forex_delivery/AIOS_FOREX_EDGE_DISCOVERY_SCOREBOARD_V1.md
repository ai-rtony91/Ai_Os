# AIOS Forex Edge Discovery Scoreboard V1

## Scope
- Candidate universe: deterministic local `paper_long_run_supervisor` candidates.
- Evidence sources used: closed-paper outcomes from `run_long_run_paper_supervisor`, paper-profitability metric formulas from `paper_profitability_evaluator`, and direction normalization used by the profitability accelerator.
- Network calls, broker API usage, credentials, account identifiers, networked data, demo/live order execution: **not used**.

## Evidence Baseline
- Starting paper balance: `10000.0`
- Risk cap/limits in long-run supervisor:
  - `max_spread=0.001` (per candidate default)
  - `max_risk_percent=2.0` (with candidate override for USDJPY spread)
  - `max_open_trades=4`
- Approved candidates in this deterministic run: `c1-eur-buy`, `c2-usd-buy`, `c3-nzd-buy`
- Rejected candidates: `c1-gbp-sell`, `c1-aud-buy`, `c2-eur-sell`, `c2-cad-buy`, `c3-chf-sell`, `c3-eur-dup`
- Aggregate realized P&L: `+480.00`
- Aggregate win/loss counts (closed trades): `3 / 0`
- Aggregate drawdown from replay path: `0.00`

## Candidate Scoreboard (best to worst)

| strategy id | candidate id | direction | sample size | expectancy | profit factor | max drawdown | win rate | promotion status |
|---|---|---|---:|---:|---:|---:|---:|---|
| paper_long_run_supervisor_v2 | c1-eur-buy | LONG | 1 | 200.00 | 999.00 | 0.00 | 1.0000 | REJECT_INSUFFICIENT_SAMPLE |
| paper_long_run_supervisor_v2 | c3-nzd-buy | LONG | 1 | 200.00 | 999.00 | 0.00 | 1.0000 | REJECT_INSUFFICIENT_SAMPLE |
| paper_long_run_supervisor_v2 | c2-usd-buy | LONG | 1 | 80.00 | 999.00 | 0.00 | 1.0000 | REJECT_INSUFFICIENT_SAMPLE |
| paper_long_run_supervisor_v2 | c1-gbp-sell | SHORT | 0 | 0.00 | 0.00 | 0.00 | 0.0000 | REJECT_INSUFFICIENT_SAMPLE |
| paper_long_run_supervisor_v2 | c1-aud-buy | LONG | 0 | 0.00 | 0.00 | 0.00 | 0.0000 | REJECT_INSUFFICIENT_SAMPLE |
| paper_long_run_supervisor_v2 | c2-eur-sell | SHORT | 0 | 0.00 | 0.00 | 0.00 | 0.0000 | REJECT_INSUFFICIENT_SAMPLE |
| paper_long_run_supervisor_v2 | c2-cad-buy | LONG | 0 | 0.00 | 0.00 | 0.00 | 0.0000 | REJECT_INSUFFICIENT_SAMPLE |
| paper_long_run_supervisor_v2 | c3-chf-sell | SHORT | 0 | 0.00 | 0.00 | 0.00 | 0.0000 | REJECT_INSUFFICIENT_SAMPLE |
| paper_long_run_supervisor_v2 | c3-eur-dup | LONG | 0 | 0.00 | 0.00 | 0.00 | 0.0000 | REJECT_INSUFFICIENT_SAMPLE |

## Directional Edge Quality
- LONG edge quality:
  - Candidates: 5 (closed trades: 3)
  - Combined expectancy: `160.00`
  - Combined profit factor: `999.00` (all closed trades profitable in deterministic run)
  - Combined max drawdown: `0.00`
  - Combined win rate: `1.0000`
  - Combined consecutive losses: `0`
- SHORT edge quality:
  - Candidates: 3 (closed trades: 0)
  - Combined expectancy: `0.00`
  - Combined profit factor: `0.00` (no closed SHORT trades)
  - Combined max drawdown: `0.00`
  - Combined win rate: `0.0000`
  - Combined consecutive losses: `0`
- Combined edge quality:
  - Overall candidate set expectancy (all closed trades): `53.3333`
  - Overall win rate (all closed trades): `1.0000`
