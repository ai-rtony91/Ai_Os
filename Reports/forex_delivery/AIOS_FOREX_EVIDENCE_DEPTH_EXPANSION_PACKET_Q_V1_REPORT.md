# AIOS Forex Evidence Depth Expansion Packet Q V1

## Mission
Expand deterministic paper-only evidence for current best candidate `c1-eur-buy` and force both LONG and SHORT directional scoring.

## Anchor and blocker status
- Strategy: `paper_long_run_supervisor_v2`
- Anchor: `c1-eur-buy`
- Closed evidence rows: `20`
- Sample-size gate: `cleared`
- Anchor blockers remaining: `none`
- Best candidate from this expansion pass: `c1-eur-buy` (LONG)

## Evidence constraints
- Paper-only execution: `True`
- Broker connectivity: `False`
- Credentials: `False`
- Account IDs: `False`
- Network: `False`
- Order execution: `False`
- Demo trading: `False`
- Live trading: `False`

## Scored candidate rows
| strategy | candidate | direction | closed trades | expectancy | profit factor | drawdown | win rate | consecutive wins | consecutive losses | promotion | blockers |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| paper_long_run_supervisor_v2 | c1-eur-buy | LONG | 20 | 200.00 | 999.00 | 0.00 | 1.00 | 20 | 0 | PROFIT_OBJECTIVE_READY | none |
| paper_long_run_supervisor_v2 | c4-eur-buy | LONG | 20 | 44.25 | 4.16 | 0.57 | 0.50 | 1 | 1 | PROFIT_OBJECTIVE_READY | none |
| paper_long_run_supervisor_v2 | c3-usd-sell | SHORT | 20 | -1.60 | 0.67 | 0.45 | 0.60 | 2 | 1 | REJECT_NEGATIVE_EXPECTANCY | negative_expectancy, low_profit_factor |
| paper_long_run_supervisor_v2 | c2-eur-sell | SHORT | 20 | -5.00 | 0.75 | 1.30 | 0.50 | 1 | 1 | REJECT_NEGATIVE_EXPECTANCY | negative_expectancy, low_profit_factor |