# Forex Big-Winner Watchtower 22H6D V1

## Purpose

Forex Big-Winner Watchtower 22H6D V1 is a governed read-only review tool for ranking supplied Forex paper/simulation candidates by asymmetric big-winner potential. It accepts only provided candidate payloads, scores them deterministically, rejects unsafe or weak setups, and surfaces owner-reviewed alerts for paper/simulation review.

The watchtower does not fetch market data, contact a broker, read credentials, place orders, create schedulers, run daemons, or trigger webhooks.

## High Reward With Capped Downside

AIOS interprets high reward as high upside potential with bounded downside, not reckless risk. A candidate must show:

- clear reward-to-risk advantage or expected R multiple.
- positive expectancy evidence.
- strong upside capture and volatility expansion.
- sufficient sample size.
- strong evidence quality.
- defined stop loss, take profit, and invalidation.
- risk percent at or below the policy cap.
- no hard blockers.

This classification does not approve a trade. It only marks the candidate for owner-reviewed paper/simulation analysis.

## 22h/6d Review-Only Scan Behavior

The watchtower always returns:

- `watch_schedule.status = REVIEW_ONLY_22H_6D`.
- `watch_schedule.hours_per_day = 22`.
- `watch_schedule.days_per_week = 6`.
- `watch_schedule.alert_only = true`.
- `watch_schedule.execution_allowed = false`.
- `watch_schedule.scheduler_created = false`.
- `watch_schedule.daemon_created = false`.
- `watch_schedule.webhook_created = false`.

The 22h/6d schedule is a review window only. It is not a scheduler, daemon, webhook runner, auto-entry loop, or trade executor.

## Big-Winner Qualification Rules

A candidate is marked `big_winner_candidate = true` only when all conditions are met:

- `reward_risk_ratio >= min_reward_risk_ratio` or `expected_r_multiple >= min_expected_r_multiple`.
- `expectancy_score >= min_expectancy_score`.
- `upside_capture_score >= min_upside_capture_score`.
- `volatility_expansion_score >= min_volatility_expansion_score`.
- `evidence_quality_score >= min_evidence_quality_score`.
- `liquidity_score >= min_liquidity_score`.
- `spread_score >= min_spread_score`.
- `slippage_score >= min_slippage_score`.
- `drawdown_risk_score >= min_drawdown_risk_score`.
- `invalidation_quality_score >= min_invalidation_quality_score`.
- `sample_size >= min_sample_size`.
- `risk_percent <= max_risk_percent`.
- `stop_loss_defined`, `take_profit_defined`, and `invalidation_defined` are true.
- no hard blockers exist.

Default policy:

- `max_risk_percent = 1.0`.
- `min_reward_risk_ratio = 3.0`.
- `min_expected_r_multiple = 2.5`.
- `min_expectancy_score = 60`.
- `min_upside_capture_score = 65`.
- `min_volatility_expansion_score = 55`.
- `min_evidence_quality_score = 60`.
- `min_liquidity_score = 50`.
- `min_spread_score = 50`.
- `min_slippage_score = 50`.
- `min_drawdown_risk_score = 40`.
- `min_invalidation_quality_score = 60`.
- `min_sample_size = 20`.

## Scoring Fields

The deterministic `opportunity_score` is built from:

- `asymmetric_payoff_score`.
- `reward_to_risk_score`.
- `upside_capture_score`.
- `expectancy_score`.
- `volatility_expansion_score`.
- `trend_alignment_score`.
- `liquidity_score`.
- `spread_score`.
- `slippage_score`.
- `drawdown_risk_score`.
- `evidence_quality_score`.
- `invalidation_quality_score`.
- `sample_size_score`.

Ranked opportunities are sorted by `opportunity_score` descending, then `evidence_quality_score` descending, then `reward_risk_ratio` descending, then `pair` ascending.

## Alert Levels

- `BLOCKED_UNSAFE_REQUEST`: live execution, broker API, auto-entry, leverage escalation, credential/secret, martingale, or revenge trading input was detected.
- `BIG_WINNER_REVIEW`: top qualifying opportunity is ready for owner-reviewed paper/simulation review.
- `WATCHLIST_ONLY`: supplied candidates exist but none currently qualifies as a big-winner candidate.
- `NO_VALID_CANDIDATES`: no candidates were supplied or all supplied candidates were rejected.

Qualified candidates append an `ASYMMETRIC_BIG_WINNER_CANDIDATE` alert with `review_only = true`, `paper_only = true`, `owner_decision_required = true`, and `execution_allowed = false`.

## Hard Blockers

A candidate is rejected when any of these blockers are present:

- `missing_pair`.
- `missing_direction`.
- `missing_stop_loss`.
- `missing_take_profit`.
- `missing_invalidation`.
- `insufficient_sample_size`.
- `reward_risk_too_low`.
- `expectancy_too_low`.
- `upside_capture_too_low`.
- `volatility_expansion_too_low`.
- `evidence_quality_too_low`.
- `liquidity_too_low`.
- `spread_too_wide`.
- `slippage_risk_too_high`.
- `drawdown_risk_too_high`.
- `invalidation_quality_too_low`.
- `risk_percent_above_cap`.
- `martingale_detected`.
- `revenge_trade_detected`.
- `live_execution_requested`.
- `broker_api_requested`.
- `auto_entry_requested`.
- `leverage_escalation_requested`.
- `credential_or_secret_supplied`.

Credential or secret keys are blocked at the payload and candidate level, and their values are not echoed.

## Safety Boundary

No live execution, no broker API, no auto-entry, no leverage escalation, no martingale, no revenge trading.

The watchtower is always:

- read-only.
- paper-only.
- owner-gated.
- alert-only.
- not a broker connector.
- not a scheduler.
- not a daemon.
- not a webhook.
- not a credential handler.
- not financial advice.

Only Anthony, the Human Owner, can approve escalation from watch-only output to a paper run, demo run, or future governed live gate.
