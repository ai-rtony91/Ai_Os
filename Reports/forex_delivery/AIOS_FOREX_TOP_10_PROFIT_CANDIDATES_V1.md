# AIOS Forex Top 10 Profit Candidates V1

## Selection Rule
- Candidate candidates are ranked by: expectancy (desc), profit factor (desc), max drawdown (asc), sample size.
- Promotion readiness uses paper-governed threshold checks (minimum sample >= 20, max drawdown gate, profit-factor gate, expectancy gate) and returns `REJECT_INSUFFICIENT_SAMPLE` for this evidence depth.

| rank | strategy | candidate | direction | expectancy | profit factor | drawdown | readiness |
|---:|---|---|---|---:|---:|---:|---|
| 1 | paper_long_run_supervisor_v2 | c1-eur-buy | LONG | 200.00 | 999.00 | 0.00 | REJECT_INSUFFICIENT_SAMPLE |
| 2 | paper_long_run_supervisor_v2 | c3-nzd-buy | LONG | 200.00 | 999.00 | 0.00 | REJECT_INSUFFICIENT_SAMPLE |
| 3 | paper_long_run_supervisor_v2 | c2-usd-buy | LONG | 80.00 | 999.00 | 0.00 | REJECT_INSUFFICIENT_SAMPLE |
| 4 | paper_long_run_supervisor_v2 | c1-gbp-sell | SHORT | 0.00 | 0.00 | 0.00 | REJECT_INSUFFICIENT_SAMPLE |
| 5 | paper_long_run_supervisor_v2 | c1-aud-buy | LONG | 0.00 | 0.00 | 0.00 | REJECT_INSUFFICIENT_SAMPLE |
| 6 | paper_long_run_supervisor_v2 | c2-eur-sell | SHORT | 0.00 | 0.00 | 0.00 | REJECT_INSUFFICIENT_SAMPLE |
| 7 | paper_long_run_supervisor_v2 | c2-cad-buy | LONG | 0.00 | 0.00 | 0.00 | REJECT_INSUFFICIENT_SAMPLE |
| 8 | paper_long_run_supervisor_v2 | c3-chf-sell | SHORT | 0.00 | 0.00 | 0.00 | REJECT_INSUFFICIENT_SAMPLE |
| 9 | paper_long_run_supervisor_v2 | c3-eur-dup | LONG | 0.00 | 0.00 | 0.00 | REJECT_INSUFFICIENT_SAMPLE |
| 10 | none | no-candidate | - | 0.00 | 0.00 | 0.00 | DATA_INSUFFICIENT |
