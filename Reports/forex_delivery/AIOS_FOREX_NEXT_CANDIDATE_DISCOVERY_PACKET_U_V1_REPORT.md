# AIOS Forex Next Candidate Discovery Packet U V1

## Paper-only scope
- paper_only: True
- no broker connectivity
- no credentials
- no account IDs
- no network
- no order execution
- no demo trading
- no live trading

## Discovery summary
- generated candidates: 5
- anchor candidate included: `c1-eur-buy`
- champion candidate: `c1-eur-buy`
- runner-up candidate: `c5-gbp-buy`
- any candidate exceeds anchor: `False`
- replacement needed: `False`

## Ranking context
- replacement analysis: deterministic, score-based with static candidate profiles
- failure context consumed: latest Packet S verdict and confidence included for history only

## Key metrics
- c1-eur-buy: expectancy=200.0, profit_factor=999.0, win_rate=1.0, max_drawdown=0.0, trades=20, consecutive_losses=0
- c5-gbp-buy: expectancy=70.0, profit_factor=2.56, win_rate=0.8667, max_drawdown=1.5385, trades=15, consecutive_losses=1

## Outcome
- replacement analysis generated and persisted in `AIOS_FOREX_CANDIDATE_REPLACEMENT_ANALYSIS_V1.md`
