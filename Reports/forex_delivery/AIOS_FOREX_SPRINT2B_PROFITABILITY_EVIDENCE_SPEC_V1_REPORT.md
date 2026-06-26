# AIOS Forex Sprint 2B Profitability Evidence Spec V1

Packet ID: `AIOS-FOREX-SPRINT2B-PROFITABILITY-EVIDENCE-SPEC-V1`

Target future implementation: `AIOS-FOREX-PROFITABILITY-EVIDENCE-IMPLEMENTATION-V1`

Mode of this report: planning/specification only. This report creates no code, tests, schemas, docs, branches, commits, pushes, broker calls, credential reads, account reads, order routes, or live-trading authority.

## 1. Purpose

Define the collision-free implementation specification for the next Forex profitability evidence evaluator.

The future evaluator must convert sanitized paper or replay evidence into a deterministic profitability verdict. It must answer whether the evidence shows positive expectancy, acceptable profit factor, acceptable drawdown, adequate sample depth, fresh evidence, and clean safety boundaries.

The evaluator must remain an evidence gate only. It must not authorize broker access, live execution, compounding, bank movement, scheduler creation, daemon creation, webhook creation, or unattended trading.

## 2. Scope

The future implementation should add a new local, deterministic evaluator and tests:

- `automation/forex_engine/profitability_evidence_v1.py`
- `tests/forex_engine/test_profitability_evidence_v1.py`
- `Reports/forex_delivery/AIOS_FOREX_PROFITABILITY_EVIDENCE_IMPLEMENTATION_V1_REPORT.md`

The evaluator should accept in-memory sanitized input objects supplied by callers. It should not read files, inspect environment variables, call subprocesses, call networks, call brokers, or persist output.

The evaluator should cover:

- closed-trade evidence intake.
- ledger/replay consistency checks.
- expectancy calculation.
- profit factor calculation.
- win/loss/breakeven counts.
- max drawdown calculation.
- sample-size and diversity checks.
- evidence freshness checks.
- weak-evidence classification.
- blocker and rejection reason codes.
- JSON-safe output for future dashboard or scoring consumers.

## 3. Non-Goals

This specification does not approve:

- editing existing runtime code in this packet.
- modifying `candidate_scoring_v1.py`.
- modifying `paper_profitability_evaluator.py`.
- creating or modifying `risk_budget_v1.py`.
- modifying dashboard truth surfaces.
- creating schemas.
- creating broker adapters.
- reading `.env` or secrets.
- reading account identifiers.
- calling OANDA, brokers, or external APIs.
- placing paper, demo, or live orders.
- approving compounding or money movement.
- staging, committing, pushing, opening PRs, merging, resetting, cleaning, or stashing.

## 4. Allowed Future Implementation Paths

The future implementation packet may use these paths only if explicitly named in that packet:

- `automation/forex_engine/profitability_evidence_v1.py`
- `tests/forex_engine/test_profitability_evidence_v1.py`
- `Reports/forex_delivery/AIOS_FOREX_PROFITABILITY_EVIDENCE_IMPLEMENTATION_V1_REPORT.md`

The future implementation may read, but not modify, these context files:

- `automation/forex_engine/candidate_scoring_v1.py`
- `automation/forex_engine/paper_profitability_evaluator.py`
- `automation/forex_engine/forex_evidence_depth_quality_gate_v1.py`
- `automation/forex_engine/forex_statistical_profit_proof_gate_v1.py`
- `automation/forex_engine/paper_account_state.py`
- `apps/trading_lab/trading_lab/forex_risk_controls.py`
- `services/orchestrator/forexDashboardTruthStatus.js`
- related tests under `tests/forex_engine/`
- prior reports under `Reports/forex_delivery/`

## 5. Forbidden Future Implementation Paths

The future implementation packet must not modify:

- `automation/forex_engine/candidate_scoring_v1.py`
- `automation/forex_engine/paper_profitability_evaluator.py`
- any `risk_budget_v1.py` path unless a separate packet explicitly creates that file.
- `apps/**`
- `services/**`
- `schemas/**`
- `.github/**`
- `docs/**`
- `.env`
- `**/.env`
- `**/*secret*`
- `**/*credential*`
- `**/*token*`

It must not add new governance authority, duplicate evaluator authority, or create dashboard truth wiring.

## 6. Input Contract

Recommended public entry point:

`evaluate_profitability_evidence(evidence_input: Mapping[str, Any] | ProfitabilityEvidenceInput | None = None) -> ProfitabilityEvidenceResult`

Recommended input fields:

- `candidate_id`: required non-empty string.
- `as_of_utc`: required ISO-8601 UTC timestamp used for deterministic freshness checks.
- `paper_trade_ledger`: optional sanitized ledger object.
- `replay_evidence`: optional sanitized replay object.
- `session_metrics`: optional sanitized metrics object.
- `balance_history`: optional sequence of balances, equity points, or mappings with `equity`, `current_balance`, or `balance`.
- `evidence_metadata`: optional mapping with `generated_at_utc`, `session_ids`, `market_condition_buckets`, `instrument_ids`, `source_report_paths`, and `source_event_ids`.
- `limits`: optional mapping of thresholds.
- `protected_flags`: optional mapping of protected action booleans, all expected false.
- `owner_notes_sanitized`: optional string that must be scanned for unsafe fragments.

Closed trade records should be accepted from ledger events, replay closed trades, or session metrics. The preferred closed-trade fields are:

- `trade_id`
- `closed_at_utc`
- `pair`
- `side`
- `realized_pl`, `realized_pnl`, `pnl_usd`, or `pnl`
- `costs`, `commission`, `spread_cost`, or explicit `net_pnl_after_costs`
- `risk_dollars`, `dollar_risk`, `risk`, or `initial_risk`
- `session_id`
- `market_condition_bucket`

All input is sanitized evidence. Raw broker payloads, tokens, account identifiers, credential fields, authorization headers, network URLs, and raw order IDs are invalid.

## 7. Output Contract

Recommended result fields:

- `version`: `profitability_evidence_v1`.
- `packet_id`: `AIOS-FOREX-PROFITABILITY-EVIDENCE-IMPLEMENTATION-V1`.
- `candidate_id`.
- `verdict`.
- `decision`: human-readable review decision.
- `progression_allowed`: boolean. True only means eligible for a future review packet, never trading.
- `profitability_ready`: boolean.
- `weak_evidence`: boolean.
- `blocked_reasons`: ordered unique list.
- `rejection_reasons`: ordered unique list.
- `warnings`: ordered unique list.
- `metrics`: JSON-safe mapping.
- `thresholds`: JSON-safe mapping of active limits.
- `freshness`: mapping with `generated_at_utc`, `as_of_utc`, `age_days`, and `status`.
- `evidence`: mapping with source counts and consistency flags.
- `protected_flags`: all false in safe results.
- `blocked_actions`: fixed list of forbidden actions.
- `safety`: fixed mapping proving no broker, network, credential, account, order, live, compounding, scheduler, daemon, webhook, commit, push, PR, or merge action occurred.
- `next_safe_action`.

Recommended `metrics` fields:

- `closed_trade_count`
- `winner_count`
- `loser_count`
- `breakeven_count`
- `gross_profit`
- `gross_loss`
- `net_pnl_after_costs`
- `win_rate`
- `loss_rate`
- `breakeven_rate`
- `average_win`
- `average_loss`
- `average_trade`
- `expectancy_per_trade`
- `expectancy_r`
- `profit_factor`
- `profit_factor_status`
- `max_drawdown`
- `max_drawdown_pct`
- `max_consecutive_losses`
- `session_count`
- `market_condition_bucket_count`
- `instrument_count`

## 8. Profitability Verdict Enum

Use this exact enum unless the implementation packet has a better approved name:

- `PROFITABILITY_EVIDENCE_READY`
- `PROFITABILITY_EVIDENCE_WEAK_POSITIVE`
- `PROFITABILITY_EVIDENCE_REQUIRE_MORE_EVIDENCE`
- `PROFITABILITY_EVIDENCE_REJECTED`
- `PROFITABILITY_EVIDENCE_BLOCKED_RISK`
- `PROFITABILITY_EVIDENCE_BLOCKED_EVIDENCE`
- `PROFITABILITY_EVIDENCE_BLOCKED_SCHEMA_INVALID`
- `PROFITABILITY_EVIDENCE_BLOCKED_UNSAFE`

Verdict precedence must be deterministic:

1. schema invalid.
2. unsafe payload or protected flag true.
3. evidence missing, malformed, stale, or inconsistent.
4. hard risk block.
5. rejection after adequate sample.
6. weak positive evidence.
7. require more evidence.
8. ready.

## 9. Expectancy Calculation Doctrine

Closed trades only count after valid close evidence is present.

Use net PnL after costs:

- If `net_pnl_after_costs` is present and finite, use it.
- Otherwise use realized PnL minus known costs.
- If realized PnL is missing, non-finite, or not numeric, reject the trade record as invalid evidence.

Currency expectancy:

`expectancy_per_trade = sum(net_pnl_after_costs) / closed_trade_count`

Equivalent audit formula:

`expectancy_per_trade = (win_rate * average_win) - (loss_rate * average_loss)`

Breakeven trades remain in the denominator through the win/loss/breakeven rates. They do not add profit or loss.

R expectancy:

`expectancy_r = average(net_pnl_after_costs / risk_dollars)`

Only calculate `expectancy_r` when every included closed trade has finite positive `risk_dollars`. Missing or zero risk must block R-adjusted readiness because it can create false positive risk evidence.

Ready evidence requires:

- `expectancy_per_trade > minimum_expectancy_per_trade`.
- `expectancy_r > minimum_expectancy_r`.
- no invalid trade records.
- no evidence consistency blockers.

Default limits:

- `minimum_expectancy_per_trade`: `0.0`
- `minimum_expectancy_r`: `0.0`

## 10. Profit Factor Calculation Doctrine

Use closed trades only.

Definitions:

- `gross_profit = sum(net_pnl_after_costs for trades where net_pnl_after_costs > epsilon)`
- `gross_loss = abs(sum(net_pnl_after_costs for trades where net_pnl_after_costs < -epsilon))`
- `profit_factor = gross_profit / gross_loss` when `gross_loss > 0`

Default `epsilon`: `0.00000001`

JSON must not emit infinity. When `gross_loss == 0`:

- if `gross_profit > 0`, set `profit_factor` to `999.0` and `profit_factor_status` to `NO_LOSSES_CAPPED`.
- if `gross_profit == 0`, set `profit_factor` to `0.0` and `profit_factor_status` to `NO_PROFIT_NO_LOSS`.
- if gross loss cannot be computed because evidence is invalid, block with `invalid_profit_factor_evidence`.

Ready evidence requires:

- `profit_factor >= minimum_profit_factor`.
- `profit_factor_status` in `NORMAL` or `NO_LOSSES_CAPPED`.

Default limit:

- `minimum_profit_factor`: `1.2`

## 11. Win/Loss/Breakeven Handling

Classify each closed trade by net PnL after costs:

- win: `net_pnl_after_costs > epsilon`
- loss: `net_pnl_after_costs < -epsilon`
- breakeven: `abs(net_pnl_after_costs) <= epsilon`

Breakeven trades:

- count toward sample size.
- count toward breakeven rate.
- do not increase gross profit or gross loss.
- reduce win rate because they remain in the denominator.
- do not reset evidence validity.

Ready evidence should normally include at least one win and one loss so profit factor and risk behavior are meaningful. A no-loss positive sample may be `WEAK_POSITIVE` unless sample size, session diversity, market bucket diversity, drawdown evidence, and balance history are strong enough to make the capped no-loss profit factor acceptable for review.

## 12. Max Drawdown Handling

Calculate max drawdown from equity or balance history when valid history is supplied.

If no valid history is supplied, derive a deterministic balance curve:

1. start with `starting_balance` from replay evidence or default `10000.0`.
2. apply closed-trade net PnL in close order.
3. track peak equity and trough after each point.

Absolute drawdown:

`max_drawdown = max(peak - current_equity)`

Percent drawdown:

`max_drawdown_pct = max_drawdown / peak_at_drawdown`

Invalid balance history must not be silently ignored. It should add `invalid_balance_history` and block risk readiness.

Default limits:

- `maximum_drawdown`: `500.0`
- `maximum_drawdown_pct`: `0.15`
- `maximum_consecutive_losses`: `5`

Any exceeded hard risk limit returns `PROFITABILITY_EVIDENCE_BLOCKED_RISK`.

## 13. Minimum Sample-Size Doctrine

Use two sample thresholds:

- `minimum_observable_closed_trades`: default `5`.
- `minimum_ready_closed_trades`: default `30`.

Evidence with fewer than 5 valid closed trades cannot produce a profitability verdict beyond `REQUIRE_MORE_EVIDENCE` or a blocker.

Evidence with 5 to 29 valid closed trades can produce `WEAK_POSITIVE` when metrics are positive and no blocker exists, but it cannot produce `READY`.

Evidence with at least 30 valid closed trades may produce `READY`, `REJECTED`, or a blocker depending on metrics and evidence quality.

Readiness also requires:

- `minimum_independent_sessions`: default `10`.
- `minimum_market_condition_buckets`: default `3`.
- at least one instrument unless a single-instrument candidate is explicitly marked and approved by the caller.

This aligns with existing evidence-depth quality expectations without editing those gates.

## 14. Evidence Freshness Doctrine

Freshness must be deterministic and based on input timestamps, not ambient current time.

Required fields:

- `as_of_utc`
- `evidence_metadata.generated_at_utc` or newest valid closed-trade `closed_at_utc`

Default freshness limits:

- `fresh_evidence_days`: `7`
- `stale_evidence_days`: `30`

Freshness statuses:

- `FRESH`: age is 0 to 7 days.
- `AGING`: age is greater than 7 and less than 30 days.
- `STALE`: age is 30 days or greater.
- `MISSING`: timestamp cannot be found.
- `INVALID`: timestamp cannot be parsed.

`STALE`, `MISSING`, and `INVALID` freshness must block readiness. `AGING` may permit `WEAK_POSITIVE` or `REQUIRE_MORE_EVIDENCE`, but should not produce `READY` unless the future packet explicitly approves an aging-evidence exception.

## 15. Weak-Evidence Handling

Weak evidence is not a failure, but it is not readiness.

Return `PROFITABILITY_EVIDENCE_WEAK_POSITIVE` when all are true:

- no schema blocker.
- no unsafe blocker.
- no evidence integrity blocker.
- no risk blocker.
- closed trade count is at least `minimum_observable_closed_trades`.
- expectancy is positive.
- profit factor meets threshold.
- drawdown is within limits.
- sample depth, session depth, market bucket depth, no-loss distribution, or freshness is not strong enough for `READY`.

Weak positive output must set:

- `progression_allowed`: `False`
- `profitability_ready`: `False`
- `weak_evidence`: `True`
- `next_safe_action`: `collect_more_profitability_evidence`

Weak evidence must not be translated into demo, live, compounding, or autonomous approval.

## 16. Blocker Logic

Blockers are fail-closed conditions that prevent a profitability conclusion.

Schema blockers:

- missing `candidate_id`.
- missing `as_of_utc`.
- invalid limits.
- non-mapping input when mapping is required.
- malformed source containers.

Unsafe blockers:

- credential, token, authorization, account ID, raw order ID, broker URL, live execution, autonomous execution, compounding, scheduler, daemon, webhook, or bank movement fragments.
- any protected flag set true.

Evidence blockers:

- no closed trades.
- missing ledger evidence when dual-source evidence is required.
- missing replay evidence when dual-source evidence is required.
- inconsistent ledger and replay closed trades.
- invalid trade PnL.
- missing or zero risk for R-adjusted readiness.
- inconsistent replay balance.
- stale, missing, or invalid freshness.

Risk blockers:

- drawdown above absolute or percent cap.
- consecutive losses above cap.
- invalid balance history.
- risk evidence contradicts `paper_only` safety expectations.

## 17. Rejection Logic

Rejection is different from a blocker.

Use `PROFITABILITY_EVIDENCE_REJECTED` only when evidence is valid, safe, fresh enough, and at or above `minimum_ready_closed_trades`, but profitability metrics fail.

Recommended rejection reasons:

- `negative_expectancy`
- `negative_expectancy_r`
- `profit_factor_below_threshold`
- `net_pnl_not_positive`
- `loss_rate_excessive`
- `average_loss_exceeds_average_win_without_offset`
- `drawdown_reward_profile_unfavorable`

If sample size is below `minimum_ready_closed_trades`, prefer `REQUIRE_MORE_EVIDENCE` or `WEAK_POSITIVE` instead of final rejection unless a hard risk blocker exists.

## 18. Test Plan

The future test file should include at least these 24 test cases:

1. ready evidence returns `PROFITABILITY_EVIDENCE_READY` with all safety flags false.
2. missing input returns schema-invalid or evidence-blocked deterministically.
3. missing `candidate_id` returns `PROFITABILITY_EVIDENCE_BLOCKED_SCHEMA_INVALID`.
4. missing `as_of_utc` returns `PROFITABILITY_EVIDENCE_BLOCKED_SCHEMA_INVALID`.
5. positive sample below 5 closed trades returns `PROFITABILITY_EVIDENCE_REQUIRE_MORE_EVIDENCE`.
6. positive sample from 5 to 29 closed trades returns `PROFITABILITY_EVIDENCE_WEAK_POSITIVE`.
7. positive sample at 30 closed trades with sessions and buckets ready returns `PROFITABILITY_EVIDENCE_READY`.
8. negative expectancy with ready sample returns `PROFITABILITY_EVIDENCE_REJECTED`.
9. zero expectancy with ready sample returns rejected or require-more-evidence according to the implemented threshold doctrine.
10. profit factor below threshold returns `profit_factor_below_threshold`.
11. no-loss positive sample emits `profit_factor` `999.0` with `NO_LOSSES_CAPPED`.
12. all-breakeven sample emits zero profit factor and does not create false positive readiness.
13. breakeven trades count in total sample and reduce win rate denominator.
14. missing or zero `risk_dollars` blocks R-adjusted readiness.
15. excessive absolute drawdown returns `PROFITABILITY_EVIDENCE_BLOCKED_RISK`.
16. excessive drawdown percent returns `PROFITABILITY_EVIDENCE_BLOCKED_RISK`.
17. excessive consecutive losses returns `PROFITABILITY_EVIDENCE_BLOCKED_RISK`.
18. invalid balance history blocks risk readiness.
19. stale evidence at 30 days or more returns `PROFITABILITY_EVIDENCE_BLOCKED_EVIDENCE`.
20. aging evidence older than 7 days but less than 30 days cannot return ready.
21. ledger/replay mismatch returns `inconsistent_ledger_replay_evidence`.
22. malformed numeric PnL returns invalid evidence instead of zero coercion.
23. unsafe owner notes or raw broker fragments return `PROFITABILITY_EVIDENCE_BLOCKED_UNSAFE`.
24. source inspection confirms no forbidden runtime APIs, including `requests`, `urllib`, `socket`, `subprocess`, `os.environ`, `getenv`, `open(`, broker SDK strings, and OANDA endpoint strings.

## 19. Validator Chain

Future implementation validator chain:

- `python -m pytest tests/forex_engine/test_profitability_evidence_v1.py -q`
- `python -m py_compile automation/forex_engine/profitability_evidence_v1.py tests/forex_engine/test_profitability_evidence_v1.py`
- `git diff --check`
- `git status --short --branch`

Future implementation tests should also include a source-inspection test that rejects forbidden imports, file I/O, environment reads, broker identifiers, and network primitives.

This spec packet validator chain:

- `git status --short --branch`
- `git diff --check`

## 20. Expected Report Path For Future Implementation Packet

`Reports/forex_delivery/AIOS_FOREX_PROFITABILITY_EVIDENCE_IMPLEMENTATION_V1_REPORT.md`

The future implementation report should include:

- files changed.
- verdict enum implemented.
- formulas implemented.
- test results.
- forbidden action confirmation.
- remaining blockers.
- next safe packet.
- commit status.
- push status.

## 21. Exact Future Implementation Packet Prompt Summary

This is a non-executable packet-authoring summary, not a complete Codex packet.

Future packet name:

`AIOS-FOREX-PROFITABILITY-EVIDENCE-IMPLEMENTATION-V1`

Future packet mode:

`APPLY`

Future packet lane:

`Forex Profitability Evidence Evaluator Implementation`

Future packet mission:

Implement `automation/forex_engine/profitability_evidence_v1.py`, add focused tests at `tests/forex_engine/test_profitability_evidence_v1.py`, and create `Reports/forex_delivery/AIOS_FOREX_PROFITABILITY_EVIDENCE_IMPLEMENTATION_V1_REPORT.md`.

Future allowed write paths:

- `automation/forex_engine/profitability_evidence_v1.py`
- `tests/forex_engine/test_profitability_evidence_v1.py`
- `Reports/forex_delivery/AIOS_FOREX_PROFITABILITY_EVIDENCE_IMPLEMENTATION_V1_REPORT.md`

Future forbidden write paths:

- `automation/forex_engine/candidate_scoring_v1.py`
- `automation/forex_engine/paper_profitability_evaluator.py`
- `apps/**`
- `services/**`
- `schemas/**`
- `.github/**`
- `docs/**`
- `.env`
- `**/.env`
- `**/*secret*`
- `**/*credential*`
- `**/*token*`

Future stop point:

Stop after implementation, tests, `git diff --check`, and `git status --short --branch`. Do not stage, commit, push, open PR, merge, reset, clean, or stash.

## 22. Collision Notes

### `candidate_scoring_v1.py`

Observed role: deterministic local scorer for review-ready candidates. It consumes candidate metrics such as expectancy, profit factor, max drawdown, sample size, evidence age, evidence quality, risk quality, and demo readiness. It ranks candidates and returns decisions such as `REVIEW_READY`, `REQUIRE_MORE_EVIDENCE`, `REJECT`, `BLOCKED_BY_RISK`, `BLOCKED_BY_EVIDENCE`, and `BLOCKED_BY_DEMO_READINESS`.

Collision rule: the future profitability evidence evaluator must not replace or modify candidate scoring. It should compute a profitability-evidence verdict and metrics that a later bridge may pass into candidate scoring. Integration should happen through explicit JSON-safe fields, not imports that create circular ownership.

### `paper_profitability_evaluator.py`

Observed role: existing paper-only evaluator that calculates win rate, average win/loss, expectancy, expectancy in R, profit factor, drawdown, consecutive losses, gross profit, and gross loss. It blocks missing or inconsistent ledger/replay evidence and currently has focused test coverage.

Collision rule: the future evaluator should be a stricter evidence-verdict layer, not a rewrite of the existing paper evaluator. It should add explicit freshness, weak-evidence, verdict enum, sample-depth, session-depth, market-bucket, and JSON contract doctrine while preserving the same safety boundary.

### `risk_budget_v1.py`

Observed repo state: no exact `risk_budget_v1.py` file was found during this packet's context scan. Existing nearby risk concepts appear in `paper_account_state.py`, `forex_risk_controls.py`, compounding capital bucket supervision, and governance/report references to future risk-budget evidence.

Collision rule: the future profitability evaluator must not create `risk_budget_v1.py` as a side effect. If risk-budget evidence is needed, the future evaluator should accept optional sanitized `risk_budget_status` input and treat absent risk-budget authority as `risk_budget_not_evaluated`, not as a new authority file. A separate owner-approved packet should create any risk-budget ledger.

### Dashboard Truth Future Work

Observed role: `services/orchestrator/forexDashboardTruthStatus.js` normalizes replay evidence for display-only dashboard truth. It exposes paper-only PnL, profit factor, drawdown, risk usage, freshness labels, and safety fields, but it is not the source evaluator for profitability evidence.

Collision rule: the future implementation must not edit dashboard truth surfaces. It should produce a stable output contract that later dashboard work can consume. A separate dashboard packet can map `verdict`, `metrics`, `freshness`, and `safety` into the dashboard after the evaluator is implemented and tested.

## Final Safety Position

The future evaluator should strengthen AIOS profitability evidence without expanding execution authority. A ready profitability verdict may justify only a later governed review packet. It must never mean trade approval, broker approval, live readiness, compounding readiness, unattended operation, or production authorization.
