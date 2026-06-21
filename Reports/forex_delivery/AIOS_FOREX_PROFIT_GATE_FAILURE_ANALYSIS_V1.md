# AIOS_FOREX_PROFIT_GATE_FAILURE_ANALYSIS_V1

## Why candidates fail

### Primary blocker
`minimum_sample_size >= 20` is not met.
- All candidates in the currently available scored local set are derived from short evidence windows with effectively low closed-trade volume.
- Accelerator output therefore defaults to `REJECT_INSUFFICIENT_SAMPLE` for all entries.

### Secondary blockers
- Candidates with non-positive expectancy trigger `REJECT_NEGATIVE_EXPECTANCY`.
- Candidates with non-productive PF geometry trigger `REJECT_LOW_PROFIT_FACTOR`.
- Direction compatibility is now normalized (`LONG`/`SHORT`) for this pass; no failures were due to unsupported direction after normalization.

## Failure-by-candidate summary
- `c1-eur-buy`: strong expectancy/PF but insufficient sample.
- `c3-nzd-buy`: strong expectancy/PF but insufficient sample.
- `c2-usd-buy`: positive expectancy but insufficient sample.
- `c1-gbp-sell`, `c2-eur-sell`, `c3-chf-sell`: additional `negative_expectancy` and `low_profit_factor` blockers.
- `c1-aud-buy`, `c2-cad-buy`, `c3-eur-dup`: `negative_expectancy` and `low_profit_factor` plus sample deficit.
- `no-candidate`: malformed/empty payload and sample deficit.

## Operational risk checks (still clean)
- No broker, no live execution, no credentials, no network usage in candidate source path.
- Deterministic local fixture catalog and simulator modules remain local-only.

## Readiness against `PROFIT_OBJECTIVE_READY`
- `PROFIT_OBJECTIVE_READY`: **No**
- `directionally_balanced`: `True` (both LONG and SHORT present), but readiness requires candidate-safe + gates satisfied.
