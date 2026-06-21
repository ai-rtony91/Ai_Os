# AIOS Forex Long/Short Evidence Depth Matrix V1

## Directional counts
- LONG evidence rows: `2`
- SHORT evidence rows: `2`
- Directional readiness: `{'supports_long': True, 'supports_short': True, 'both_supported': True}`

## LONG candidates
| candidate | closed trades | blocked | blockers | promotion |
|---|---:|---|---|---|
| c1-eur-buy | 20 | False | none | PROFIT_OBJECTIVE_READY |
| c4-eur-buy | 20 | False | none | PROFIT_OBJECTIVE_READY |

## SHORT candidates
| candidate | closed trades | blocked | blockers | promotion |
|---|---:|---|---|---|
| c2-eur-sell | 20 | True | negative_expectancy, low_profit_factor | REJECT_NEGATIVE_EXPECTANCY |
| c3-usd-sell | 20 | True | negative_expectancy, low_profit_factor | REJECT_NEGATIVE_EXPECTANCY |

## Gate decision
- c1-eur-buy sample size gate cleared: `True`
- c1-eur-buy still blocked by other gates: `False`
