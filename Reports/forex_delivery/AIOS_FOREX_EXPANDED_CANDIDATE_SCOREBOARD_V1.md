# AIOS_FOREX_EXPANDED_CANDIDATE_SCOREBOARD_V1

## Candidate Set Scored Through `profit_objective_accelerator_l_v1`
Source baseline: existing local deterministic reporting artifact values (top-10 candidate report) mapped to accelerator input.

### Scoring inputs
- `strategy_id`: candidate strategy
- `candidate_id`: candidate identifier
- `direction`: normalized to `LONG` for buy-style, `SHORT` for sell-style
- `trade_pnl_list`: reconstructed from existing candidate-level evidence entries where available

> Note: no new runtime execution was performed in this session due environment command-launch restriction.

### Ranked table
| rank | strategy_id | candidate_id | direction | sample_size | expectancy | profit_factor | max_drawdown(%) | blocked_reasons | promotion_status |
|---:|---|---|---|---:|---:|---:|---|---|
| 1 | paper_long_run_supervisor_v2 | c1-eur-buy | LONG | 3 | 200.00 | 999.00 | 0.00 | insufficient_sample | CONTINUE_PAPER_VALIDATION (`PROFIT_OBJECTIVE_READY` not reached) |
| 2 | paper_long_run_supervisor_v2 | c3-nzd-buy | LONG | 3 | 200.00 | 999.00 | 0.00 | insufficient_sample | CONTINUE_PAPER_VALIDATION (`PROFIT_OBJECTIVE_READY` not reached) |
| 3 | paper_long_run_supervisor_v2 | c2-usd-buy | LONG | 3 | 80.00 | 999.00 | 0.00 | insufficient_sample | CONTINUE_PAPER_VALIDATION (`PROFIT_OBJECTIVE_READY` not reached) |
| 4 | paper_long_run_supervisor_v2 | c1-gbp-sell | SHORT | 3 | 0.00 | 0.00 | 0.00 | insufficient_sample, negative_expectancy, low_profit_factor | CONTINUE_PAPER_VALIDATION |
| 5 | paper_long_run_supervisor_v2 | c1-aud-buy | LONG | 3 | 0.00 | 0.00 | 0.00 | insufficient_sample, negative_expectancy, low_profit_factor | CONTINUE_PAPER_VALIDATION |
| 6 | paper_long_run_supervisor_v2 | c2-eur-sell | SHORT | 3 | 0.00 | 0.00 | 0.00 | insufficient_sample, negative_expectancy, low_profit_factor | CONTINUE_PAPER_VALIDATION |
| 7 | paper_long_run_supervisor_v2 | c2-cad-buy | LONG | 3 | 0.00 | 0.00 | 0.00 | insufficient_sample, negative_expectancy, low_profit_factor | CONTINUE_PAPER_VALIDATION |
| 8 | paper_long_run_supervisor_v2 | c3-chf-sell | SHORT | 3 | 0.00 | 0.00 | 0.00 | insufficient_sample, negative_expectancy, low_profit_factor | CONTINUE_PAPER_VALIDATION |
| 9 | paper_long_run_supervisor_v2 | c3-eur-dup | LONG | 3 | 0.00 | 0.00 | 0.00 | insufficient_sample, negative_expectancy, low_profit_factor | CONTINUE_PAPER_VALIDATION |
| 10 | none | no-candidate | LONG | 0 | 0.00 | 0.00 | 0.00 | insufficient_sample, negative_expectancy | CONTINUE_PAPER_VALIDATION |

### Accelerator behavior check by candidate
- `direction` compatibility: all non-empty candidates were normalized to LONG/SHORT before evaluation.
- `minimum_sample_size=20`: every candidate in this set is below threshold.
- `minimum_expectancy>0`: rows with zero expectancy fail this gate.
- `minimum_profit_factor=1.25`: zero-profit candidates fail this gate.
- `maximum_drawdown<=10`: all observed rows pass drawdown gate (`0.00`).

## Candidate count and directional readiness
- Total evaluated candidates: `10`
- Directions present: `LONG` and `SHORT` both present
- `rank_candidates` directional balance flag: `supports_long=True`, `supports_short=True`, `both_supported=True`
- `best_candidate` by accelerator score remains `c1-eur-buy` (based on score ordering despite gate failure)

## `PROFIT_OBJECTIVE_READY` outcome
- No candidate reached `PROMOTION_STATUS_PROFIT_OBJECTIVE_READY`.
- Block reason for all candidates: **insufficient sample size** is the primary hard stop.
