# AIOS Forex Profitability Verdict V1

## 1) Does AIOS currently possess measurable edge?
**Yes, but only within current deterministic LONG-only closed-paper evidence.**

- Measurable paper edge exists on 3 closed trades (all LONG).
- No negative expectancy observed in closed paper outcomes.

## 2) Does AIOS currently possess positive expectancy?
**Yes, at candidate level for closed PAPER trades:**
- Best candidate expectancy: `200.00`
- Aggregate closed-trade expectancy across all candidates with outcomes: `53.3333`

## 3) Does AIOS currently possess a candidate suitable for governed progression?
**No.**
- All candidates fail governed progression readiness because sample and process gates are not yet satisfied.
- Governing blocker: insufficient sample size for promotion (sample gate, walk-forward gate, and portfolio stability gate requirements not yet met).

## 4) What is the largest remaining blocker?
**Largest blocker: evidence maturity for promotion readiness**
- Missing sustained candidate sample size (`< 20` closed trades per candidate path)
- Missing repeatable walk-forward validation (`insufficient_windows`, `insufficient_passing_windows`)
- Missing portfolio-level consistency evidence across batches

## Summary for Immediate Use
- Best strategy: `paper_long_run_supervisor_v2`
- Best candidate: `c1-eur-buy`
- Strongest direction: `LONG`
- Weakest direction: `SHORT`
- Actual expectancy: `200.00` (best candidate), `53.3333` (all closed trades)
- Actual profit factor: `999.00` (best candidate), `999.00` (aggregate for LONG closed trades)
- Actual drawdown: `0.00`
- Actual blocker: `evidence_depth_for_governed_progression`
