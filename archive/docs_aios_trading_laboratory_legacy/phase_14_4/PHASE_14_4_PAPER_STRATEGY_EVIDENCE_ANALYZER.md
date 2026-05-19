# Phase 14.4 Paper Strategy Evidence Analyzer

Status: APPLY scaffold
Mode: paper-only / simulation-only
Live execution: BLOCKED

## Purpose

Phase 14.4 designs a paper-only evidence analyzer for the Trading Lab.

It reviews the evidence already collected from paper signal intake, latency, regime checks, risk gates, paper outcomes, scorecards, mock contracts, and dashboard mock data.

It does not approve live trading.

## Safety Boundary

Blocked:

- broker execution
- OANDA execution
- API keys
- secrets
- real webhook activation
- real orders
- live market execution
- account login systems
- scheduled trading
- background trading

Allowed:

- paper-only evidence review
- mock signal review
- simulated outcome review
- strategy comparison from paper data
- strategy ranking for paper review only
- replay and human review notes
- dashboard fixture visibility

Live execution remains BLOCKED.

## Current Paper Signal Flow

Current paper flow:

1. Mock or manual signal intake.
2. Latency timestamp record.
3. Regime tag check.
4. Risk gate check.
5. Paper trade simulation result.
6. Profitability scorecard update.
7. Paper decision result.
8. Dashboard fixture summary.

The current chain is useful, but it needs stronger evidence review before strategy ranking can be trusted.

## Weakest Area

The weakest area is evidence tracking tied to decision enforcement.

Some documents require regime, risk, and paper evidence before a paper result can be trusted. The backend paper path can still create a paper fill after a simple paper risk check if candle data exists. This remains paper-only, but Phase 14.4 should make the stricter evidence chain visible and reviewable.

This is a MISMATCH to review before future implementation work.

## Strongest Area

The strongest area is the safety boundary.

The project consistently blocks broker execution, OANDA, API keys, real orders, real webhooks, credentials, and live trading.

## Needed Before Any Live Consideration

Before any live consideration, the system needs:

- clean paper sample history
- strategy-by-strategy trade outcomes
- regime evidence for each signal
- risk gate evidence for each signal
- latency samples with separate timestamps
- expectancy analysis by strategy
- strategy comparison logic
- strategy ranking logic
- replay and review reports
- validator confirmation that live execution remains BLOCKED

Phase 14.4 does not provide live approval.

## Proposed Phase 14.4 Structure

Phase 14.4 should contain these paper-only parts:

- Evidence Intake: gathers signal, latency, regime, risk, paper result, scorecard, journal, and safety data.
- Evidence Completeness Check: marks missing facts as UNKNOWN and unverifiable claims as INVALID DATA.
- Evidence Scorecard: scores how complete and usable the paper evidence is.
- Expectancy Analyzer: reviews sample size, win rate, average win/loss in R, expectancy in R, profit factor, drawdown, and consecutive losses.
- Strategy Comparator: compares strategies only after minimum paper sample requirements are met.
- Strategy Ranker: ranks paper strategies without approving live execution.
- Replay Reviewer: shows the full chain for one signal so a human can review each step.
- Dashboard Summary Fixture: gives the dashboard a read-only mock-data view.

## Proposed Evidence Scoring

Total: 100 points.

- Signal trace complete: 15
- Regime evidence complete: 15
- Risk gate evidence complete: 20
- Paper outcome recorded: 15
- Latency evidence usable: 10
- Journal or review note complete: 10
- Expectancy metrics available: 10
- Safety locks confirmed: 5

Status levels:

- 0-49: BLOCKED
- 50-69: INSUFFICIENT_DATA
- 70-84: PAPER_REVIEW_READY
- 85-100: STRONG_PAPER_EVIDENCE

No score can approve live trading.

## Proposed Strategy Ranking Logic

Ranking should use:

- evidence score
- trade count
- expectancy R
- profit factor
- max drawdown
- consecutive losses
- regime consistency
- latency reliability
- review or journal completeness

Hard blockers:

- missing risk gate
- missing regime tag
- trade count below threshold
- live execution not blocked
- broker, API, credential, real webhook, or order field enabled

## Proposed Replay Review Loop

Beginner-readable review loop:

1. Pick one paper signal.
2. Replay the chain from signal to scorecard.
3. Mark missing facts as UNKNOWN.
4. Mark conflicting evidence as MISMATCH.
5. Mark unverifiable claims as INVALID DATA.
6. Record what blocked the signal.
7. Update the evidence score.
8. Re-rank the strategy only after review is complete.

## Proposed Dashboard Visibility

The dashboard fixture should show:

- Live Execution: BLOCKED
- Strategy rank: paper-only
- Evidence score
- Missing evidence count
- Current blocker
- Trade count
- Expectancy R
- Profit factor
- Max drawdown
- Replay review status
- Next safe action

No dashboard control may enable routing, broker login, real webhooks, or orders.

## Next Safe Action

Review the Phase 14.4 JSON fixtures, confirm all JSON parses, and confirm live execution remains BLOCKED.
