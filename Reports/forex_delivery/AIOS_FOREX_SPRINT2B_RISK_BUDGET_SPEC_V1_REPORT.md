# AIOS Forex Sprint 2B Risk Budget Spec V1

## 1. Purpose

Define a collision-free implementation specification for `AIOS-FOREX-RISK-BUDGET-IMPLEMENTATION-V1`, the next paper-only Forex risk budget and position sizing decision engine.

The future engine must determine whether a proposed Forex trade can proceed, must be reduced, requires operator review, or must be blocked based on account risk budget, stop-loss validity, drawdown pressure, daily/session limits, open exposure, pair exposure, and candidate-level risk context.

This report is a planning artifact only. It does not approve code execution, broker access, live trading, credential access, order placement, commit, push, PR creation, or merge.

## 2. Scope

The future implementation packet should create a new deterministic local engine:

- `automation/forex_engine/risk_budget_engine_v1.py`
- `tests/forex_engine/test_risk_budget_engine_v1.py`
- `Reports/forex_delivery/AIOS_FOREX_RISK_BUDGET_IMPLEMENTATION_V1_REPORT.md`

The engine should be a pure in-memory evaluator. It should accept sanitized dictionaries or dataclasses, return JSON-safe output, and perform no file reads, file writes, network calls, broker calls, credential reads, account lookup, order placement, scheduling, or runtime mutation.

The engine may compose conceptually with existing paper-only behavior from:

- `automation/forex_engine/position_sizing.py`
- `automation/forex_engine/risk_governor.py`
- `automation/forex_engine/paper_risk_decision.py`
- `automation/forex_engine/candidate_scoring_v1.py`

The first implementation should not wire the engine into live routing, broker connectors, candidate scoring, dashboard services, or execution loops.

## 3. Non-goals

- No live trading.
- No demo or live broker order routing.
- No OANDA calls.
- No broker API calls.
- No credential, token, account ID, or environment variable access.
- No `.env` reads.
- No mutation of existing trading ledgers.
- No change to `candidate_scoring_v1.py`.
- No change to existing risk governor or position sizing modules in the first implementation packet.
- No dashboard, orchestrator, service, schema, GitHub workflow, or governance edits.
- No commit, push, PR creation, merge, reset, clean, branch switch, or branch creation.

## 4. Allowed Future Implementation Paths

For the first implementation packet, allow only:

- `automation/forex_engine/risk_budget_engine_v1.py`
- `tests/forex_engine/test_risk_budget_engine_v1.py`
- `Reports/forex_delivery/AIOS_FOREX_RISK_BUDGET_IMPLEMENTATION_V1_REPORT.md`

Allowed implementation style:

- Add a new module instead of editing existing engines.
- Use `dataclass(frozen=True)` result/config objects where useful.
- Use deterministic Python standard library behavior only.
- Use numeric coercion helpers that reject booleans as numeric values.
- Return JSON-safe dictionaries through a named serializer function.
- Expose a single primary function, recommended name: `evaluate_risk_budget`.
- Keep `paper_only=True` and all live/broker/credential/network safety flags false.
- Include `__all__` with public constants, dataclasses, and functions.

## 5. Forbidden Future Implementation Paths

The first implementation packet must not touch:

- `automation/forex_engine/candidate_scoring_v1.py`
- `automation/forex_engine/position_sizing.py`
- `automation/forex_engine/risk_governor.py`
- `automation/forex_engine/paper_risk_decision.py`
- `automation/forex_engine/demo_*`
- `automation/forex_engine/oanda_*`
- `automation/forex_engine/*live*`
- `scripts/**`
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

The first implementation must not import broker clients, HTTP clients, environment loaders, subprocess runners, schedulers, filesystem persistence, dashboard services, or execution loops.

## 6. Input Contract

Primary function signature:

```python
def evaluate_risk_budget(
    trade_preview: Mapping[str, Any],
    account_state: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
    *,
    candidate_context: Mapping[str, Any] | None = None,
    open_trades: Sequence[Mapping[str, Any]] | None = None,
    closed_trades: Sequence[Mapping[str, Any]] | None = None,
    now_utc: str | None = None,
) -> RiskBudgetDecision:
```

Required `trade_preview` fields:

- `pair`: normalized uppercase symbol such as `EURUSD`.
- `direction`: `buy` or `sell`.
- `entry_price`: positive numeric.
- `stop_loss`: positive numeric.
- `pip_value_per_unit`: positive numeric, or provided through pair policy.

Optional `trade_preview` fields:

- `take_profit`.
- `spread`.
- `market_data_age_seconds`.
- `requested_risk_percent`.
- `requested_risk_dollars`.
- `requested_units`.
- `setup_id`.
- `candidate_id`.
- `session_id`.

Required `account_state` fields:

- `mode`: must be `paper` or `PAPER_ONLY`.
- `configured_trade_bucket_balance`: positive numeric risk base.
- `current_balance` or `equity`: numeric account reference value for reporting.
- `peak_balance`: positive numeric for drawdown calculation.
- `daily_loss_used`: non-negative numeric.
- `session_loss_used`: non-negative numeric.
- `open_risk`: non-negative numeric.

Optional `account_state` fields:

- `broker_balance`.
- `nav`.
- `unrealized_pl`.
- `realized_pl`.
- `trade_count_today`.
- `session_trade_count`.
- `loss_streak`.
- `kill_switch_active`.
- `owner_review_required`.

Policy fields with recommended defaults:

- `default_risk_percent`: `1.0`.
- `max_single_trade_risk_percent`: `1.0`.
- `max_single_trade_risk_dollars`: `0.0` means disabled.
- `max_daily_loss_percent`: `3.0`.
- `max_daily_loss_dollars`: `0.0` means derive from percent.
- `max_session_loss_percent`: `1.5`.
- `max_session_loss_dollars`: `0.0` means derive from percent.
- `max_open_risk_percent`: `3.0`.
- `max_open_trades`: `1`.
- `max_pair_exposure_percent`: `2.0`.
- `max_correlated_currency_exposure_percent`: `4.0`.
- `max_drawdown_percent`: `10.0`.
- `drawdown_soft_threshold_fraction`: `0.50`.
- `drawdown_severe_threshold_fraction`: `0.75`.
- `min_units`: `1.0`.
- `max_units`: `0.0` means disabled.
- `rounding_increment`: `1.0`.
- `allow_fractional_units`: `False`.
- `min_stop_distance`: `0.0` means disabled.
- `max_stop_distance`: `0.0` means disabled.
- `max_spread`: `0.0` means disabled.
- `max_market_data_age_seconds`: `300.0`.
- `cooldown_after_loss_seconds`: `0.0` means disabled.
- `duplicate_setup_block`: `True`.
- `supported_pairs`: default `("EURUSD", "GBPUSD", "USDJPY")`.

Optional `candidate_context` fields:

- `candidate_id`.
- `risk_blocked`.
- `risk_controls_present`.
- `risk_quality_score`.
- `max_drawdown`.
- `expectancy`.
- `strategy_id`.
- `regime`.

## 7. Output Contract

The primary result should be a frozen dataclass named `RiskBudgetDecision` plus a serializer named `risk_budget_decision_to_jsonable_dict`.

Required output fields:

- `engine_version`: exact string `risk_budget_engine_v1`.
- `decision`: one value from the risk decision enum.
- `allowed`: boolean.
- `paper_only`: always `True`.
- `mode`: exact string `PAPER_ONLY`.
- `pair`.
- `direction`.
- `candidate_id`.
- `risk_base`.
- `requested_risk_dollars`.
- `approved_risk_dollars`.
- `risk_reduction_dollars`.
- `risk_reduction_percent`.
- `entry_price`.
- `stop_loss`.
- `stop_distance`.
- `pip_value_per_unit`.
- `raw_units`.
- `approved_units`.
- `estimated_loss_at_stop`.
- `single_trade_cap`.
- `daily_risk_remaining`.
- `session_risk_remaining`.
- `open_risk_remaining`.
- `pair_exposure_remaining`.
- `drawdown_percent`.
- `drawdown_multiplier`.
- `reduction_reasons`.
- `blocked_reasons`.
- `warnings`.
- `next_safe_action`.
- `candidate_scoring_bridge`.
- `safety`.

`candidate_scoring_bridge` must be an inert summary map only:

- `risk_blocked`: `True` only when the risk budget decision is `BLOCK`.
- `risk_controls_present`: `True` when the engine evaluated valid risk controls.
- `risk_quality_score`: optional numeric score from 0 to 100.
- `risk_blockers`: copied blocked reasons.

`safety` must include:

- `paper_only`: `True`.
- `broker`: `False`.
- `live_trading`: `False`.
- `credentials`: `False`.
- `real_orders`: `False`.
- `network_access`: `False`.
- `account_lookup`: `False`.
- `filesystem_write`: `False`.
- `scheduler_started`: `False`.

## 8. Risk Decision Enum

Use exact public constants:

```python
RISK_BUDGET_ALLOW = "RISK_BUDGET_ALLOW"
RISK_BUDGET_REDUCE = "RISK_BUDGET_REDUCE"
RISK_BUDGET_REVIEW_REQUIRED = "RISK_BUDGET_REVIEW_REQUIRED"
RISK_BUDGET_BLOCK = "RISK_BUDGET_BLOCK"
```

Decision semantics:

- `RISK_BUDGET_ALLOW`: all hard gates pass and requested risk equals approved risk after rounding.
- `RISK_BUDGET_REDUCE`: all hard gates pass, but requested risk or units must be reduced to fit budget.
- `RISK_BUDGET_REVIEW_REQUIRED`: deterministic checks pass but policy marks owner review required, drawdown pressure is severe but not hard-blocked, or warnings require supervised review.
- `RISK_BUDGET_BLOCK`: one or more hard blockers prevents the trade from proceeding.

Ranking severity for downstream consumers:

1. `RISK_BUDGET_BLOCK`
2. `RISK_BUDGET_REVIEW_REQUIRED`
3. `RISK_BUDGET_REDUCE`
4. `RISK_BUDGET_ALLOW`

## 9. Position Sizing Formula Assumptions

The future engine should preserve the existing position sizing formula shape from the prior position sizing report:

1. `stop_distance = abs(entry_price - stop_loss)`
2. `requested_risk_dollars = requested_risk_dollars if provided else risk_base * requested_risk_percent / 100`
3. `available_budget = min(single_trade_cap, daily_risk_remaining, session_risk_remaining, open_risk_remaining, pair_exposure_remaining, drawdown_adjusted_cap)`
4. `approved_risk_dollars = min(requested_risk_dollars, available_budget)`
5. `raw_units = approved_risk_dollars / (stop_distance * pip_value_per_unit)`
6. `approved_units = floor or nearest rounding policy applied to raw_units`
7. `estimated_loss_at_stop = approved_units * stop_distance * pip_value_per_unit`

Required invariants:

- `estimated_loss_at_stop <= approved_risk_dollars` after rounding.
- `approved_units >= min_units` or the decision must block.
- `approved_units <= max_units` when `max_units > 0` or reduce/block.
- `approved_risk_dollars <= requested_risk_dollars`.
- `requested_risk_dollars > 0` for allow/reduce/review.
- `risk_base` must come from `configured_trade_bucket_balance`, not full broker balance, unless policy explicitly permits equality with broker balance.

## 10. Drawdown Protection Rules

Drawdown calculation:

```text
drawdown = max(0, peak_balance - current_balance_or_equity)
drawdown_percent = (drawdown / peak_balance) * 100
```

Hard rules:

- Block when `peak_balance` is missing, non-positive, or invalid.
- Block when `drawdown_percent >= max_drawdown_percent`.
- Block when `kill_switch_active` is true.
- Block when candidate context has `risk_blocked=True`.

Reduction rules:

- If drawdown is below `max_drawdown_percent * drawdown_soft_threshold_fraction`, multiplier is `1.0`.
- If drawdown is at or above the soft threshold and below the severe threshold, multiplier is `0.50`.
- If drawdown is at or above the severe threshold and below the hard maximum, multiplier is `0.25` and decision is at least `RISK_BUDGET_REVIEW_REQUIRED`.
- If drawdown reaches the hard maximum, multiplier is `0.0` and decision is `RISK_BUDGET_BLOCK`.

The multiplier applies to the single-trade risk cap before position sizing.

## 11. Daily/session Risk Rules

Daily budget:

- `daily_loss_limit = max_daily_loss_dollars` when positive; otherwise `risk_base * max_daily_loss_percent / 100`.
- `daily_risk_remaining = daily_loss_limit - daily_loss_used`.
- Block when `daily_risk_remaining <= 0`.
- Reduce when requested risk exceeds daily remaining budget and reduced size still meets minimum units.

Session budget:

- `session_loss_limit = max_session_loss_dollars` when positive; otherwise `risk_base * max_session_loss_percent / 100`.
- `session_risk_remaining = session_loss_limit - session_loss_used`.
- Block when `session_risk_remaining <= 0`.
- Reduce when requested risk exceeds session remaining budget and reduced size still meets minimum units.

Reset assumptions:

- The engine does not own resets.
- The caller must provide already-reset daily/session counters.
- If reset freshness is required later, it belongs in a separate orchestration packet.

## 12. Exposure Rules

Open risk:

- `open_risk_remaining = risk_base * max_open_risk_percent / 100 - open_risk`.
- Block when open risk remaining is non-positive.
- Block when adding the new approved risk exceeds open risk remaining and cannot be reduced.

Open trade count:

- Count non-terminal open trades only.
- Block when `open_trade_count >= max_open_trades`.

Pair exposure:

- Pair exposure should use absolute notional exposure for the same pair.
- `pair_exposure_remaining = risk_base * max_pair_exposure_percent / 100 - pair_exposure`.
- Block or reduce when the new trade would exceed the pair exposure cap.

Correlated currency exposure:

- Aggregate exposure by currency token extracted from pair symbols.
- A `EURUSD` trade contributes to `EUR` and `USD` exposure.
- Block or review when correlated exposure exceeds `max_correlated_currency_exposure_percent`.
- If pair parsing is unsupported, block with `unsupported_pair`.

Duplicate setup:

- When `duplicate_setup_block=True`, block same pair, same direction, same setup ID if already open, queued, active, or previewed.

## 13. Stop-loss Validation Rules

Hard stop-loss blockers:

- Missing stop loss.
- Non-numeric stop loss.
- Non-positive stop loss.
- Stop distance equal to zero.
- Buy direction with stop loss greater than or equal to entry.
- Sell direction with stop loss less than or equal to entry.
- Stop distance below `min_stop_distance` when configured.
- Stop distance above `max_stop_distance` when configured.
- Missing or invalid `pip_value_per_unit`.
- Unsupported pair.
- Stale market data when `market_data_age_seconds > max_market_data_age_seconds`.

Review or warning conditions:

- Missing take profit when policy requires reward/risk validation.
- Reward/risk ratio below policy minimum when take profit exists.
- Spread above warning threshold but below hard max.

## 14. Reduction Logic

Reduction is allowed only when all hard blockers are absent.

Reduction sequence:

1. Compute requested risk.
2. Compute all active caps.
3. Apply drawdown multiplier to the single-trade cap.
4. Set approved risk to the minimum active remaining budget.
5. Compute units from approved risk.
6. Apply rounding.
7. Recompute estimated loss at stop.
8. If rounded units are below minimum units, block.
9. If estimated loss is zero or negative, block.
10. If approved risk is less than requested risk and size remains valid, return `RISK_BUDGET_REDUCE`.

Reduction reasons should be deterministic strings:

- `single_trade_cap_reduction`
- `daily_budget_reduction`
- `session_budget_reduction`
- `open_risk_reduction`
- `pair_exposure_reduction`
- `drawdown_multiplier_reduction`
- `max_units_reduction`
- `rounding_reduction`

## 15. Blocker Logic

Hard blocker strings should be deterministic and stable:

- `invalid_trade_preview`
- `invalid_account_state`
- `non_paper_mode`
- `live_trading_blocked`
- `candidate_risk_blocked`
- `missing_risk_base`
- `invalid_risk_base`
- `missing_entry_price`
- `invalid_entry_price`
- `missing_stop_loss`
- `invalid_stop_loss`
- `invalid_stop_distance`
- `invalid_pip_value`
- `unsupported_pair`
- `invalid_requested_risk`
- `risk_budget_exhausted`
- `daily_loss_limit_hit`
- `session_loss_limit_hit`
- `max_drawdown_hit`
- `kill_switch_active`
- `max_open_risk_hit`
- `max_open_trades_hit`
- `max_pair_exposure_hit`
- `max_correlated_exposure_hit`
- `duplicate_setup`
- `spread_too_high`
- `stale_market_data`
- `min_units_not_met`
- `max_units_exceeded`
- `owner_review_required`

When multiple blockers exist, return all blockers in deterministic validation order and use the first blocker as `primary_blocker`.

## 16. Test Plan

Minimum future tests for `tests/forex_engine/test_risk_budget_engine_v1.py`:

1. Imports module and exposes expected constants through `__all__`.
2. Allows a valid paper-only trade when all budgets have room.
3. Blocks non-paper mode.
4. Blocks explicit live trading flag.
5. Blocks missing configured trade bucket balance.
6. Blocks invalid or negative risk base.
7. Blocks missing entry price.
8. Blocks missing stop loss.
9. Blocks buy trade when stop loss is not below entry.
10. Blocks sell trade when stop loss is not above entry.
11. Blocks invalid pip value.
12. Blocks unsupported pair.
13. Reduces size when requested risk exceeds single-trade cap.
14. Reduces size when requested risk exceeds daily remaining budget.
15. Reduces size when requested risk exceeds session remaining budget.
16. Blocks when daily risk budget is exhausted.
17. Blocks when session risk budget is exhausted.
18. Applies soft drawdown multiplier.
19. Requires review at severe drawdown threshold.
20. Blocks at max drawdown threshold.
21. Blocks kill switch active.
22. Blocks candidate context `risk_blocked=True`.
23. Blocks open trade count cap.
24. Blocks duplicate setup.
25. Blocks pair exposure cap.
26. Blocks correlated currency exposure cap.
27. Blocks stale market data.
28. Blocks spread above hard max.
29. Blocks when rounded units fall below minimum units.
30. Ensures estimated loss at stop never exceeds approved risk after rounding.
31. Returns deterministic blocker order for multiple invalid inputs.
32. Returns JSON-safe dictionary with required safety flags.
33. Source safety scan confirms no forbidden imports or tokens for broker, network, credentials, filesystem writes, subprocess, scheduler, or environment access.
34. Existing `tests/forex_engine/test_candidate_scoring_v1.py` remains unchanged and passes, proving no scorer collision.
35. Existing `tests/forex_engine/test_position_sizing.py` and `tests/forex_engine/test_risk_governor.py` remain unchanged and pass when included in the validation chain.

## 17. Validator Chain

Future implementation packet validators:

```powershell
python -m py_compile automation/forex_engine/risk_budget_engine_v1.py
python -m pytest tests/forex_engine/test_risk_budget_engine_v1.py tests/forex_engine/test_candidate_scoring_v1.py tests/forex_engine/test_position_sizing.py tests/forex_engine/test_risk_governor.py -q
git diff --check
git status --short --branch
```

Current reports-only packet validators:

```powershell
git status --short --branch
git diff --check
```

## 18. Expected Report Path For Future Implementation Packet

The implementation packet must create:

```text
Reports/forex_delivery/AIOS_FOREX_RISK_BUDGET_IMPLEMENTATION_V1_REPORT.md
```

That report must include:

- files created.
- files updated.
- safety boundary.
- risk decision enum delivered.
- input/output contract implemented.
- test list and validator output.
- candidate scoring collision confirmation.
- commit status.
- push status.

## 19. Exact Future Implementation Packet Prompt Summary

This section is a non-executable summary. A full future Codex packet must still be generated and validated under `AGENTS.md` before execution.

Future packet summary:

- Packet ID: `AIOS-FOREX-RISK-BUDGET-IMPLEMENTATION-V1`
- Mode: `APPLY`
- Zone: `Forex Engine`
- Lane: `Risk Budget Engine V1`
- Worktree: `C:\Dev\Ai.Os`
- Branch: `main` only after clean preflight; do not switch branches.
- Approval authority: Human Owner-approved local APPLY packet.
- Preflight: run `git status --short --branch`; stop if not `main`; stop if dirty.
- Allowed paths:
  - `automation/forex_engine/risk_budget_engine_v1.py`
  - `tests/forex_engine/test_risk_budget_engine_v1.py`
  - `Reports/forex_delivery/AIOS_FOREX_RISK_BUDGET_IMPLEMENTATION_V1_REPORT.md`
- Forbidden paths:
  - `automation/forex_engine/candidate_scoring_v1.py`
  - `automation/forex_engine/position_sizing.py`
  - `automation/forex_engine/risk_governor.py`
  - `automation/forex_engine/paper_risk_decision.py`
  - `automation/forex_engine/demo_*`
  - `automation/forex_engine/oanda_*`
  - `automation/forex_engine/*live*`
  - `scripts/**`
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
- Task: implement `risk_budget_engine_v1.py` from this report, add targeted tests, run validator chain, and create the implementation report.
- Stop point: create only the allowed files, no protected actions, no broker/API/secret/live behavior, no commit, no push.

## 20. Collision Notes With candidate_scoring_v1.py

Observed `candidate_scoring_v1.py` boundaries:

- It is a deterministic local candidate ranking engine.
- It performs no file reads, network calls, broker calls, credential access, account lookup, order placement, scheduling, or runtime mutation.
- It exposes candidate-level decisions including `BLOCKED_BY_RISK`.
- It consumes `risk_blocked`, `risk_controls_present`, and `risk_quality_score`.
- It scores `risk_quality_score` as one dimension in a broader candidate ranking model.
- It blocks candidates when `risk_blocked` is true or candidate max drawdown exceeds its configured limit.

Collision-free rule:

- `risk_budget_engine_v1.py` must not import or modify `candidate_scoring_v1.py`.
- `candidate_scoring_v1.py` must not import the new risk budget engine in the first implementation packet.
- The new engine must make trade-level risk budget decisions, not candidate ranking decisions.
- Candidate scoring should remain upstream or parallel evidence ranking.
- Risk budget output may provide an inert `candidate_scoring_bridge` dictionary, but no automatic mutation of candidate dictionaries should happen in this packet.
- A later bridge packet may map `RISK_BUDGET_BLOCK` to candidate `risk_blocked=True`, but that bridge must be separately scoped and validated.
- Existing candidate scoring tests must remain unchanged and pass during future implementation validation.

Recommended collision boundary:

```text
candidate_scoring_v1.py:
  ranks candidate evidence and may say candidate is BLOCKED_BY_RISK.

risk_budget_engine_v1.py:
  evaluates one proposed paper trade against account, stop-loss, drawdown, daily/session, and exposure budgets.

future bridge packet:
  may copy risk budget summary fields into candidate context after both engines are independently validated.
```

## Final Recommendation

Proceed next with a narrow implementation packet for `AIOS-FOREX-RISK-BUDGET-IMPLEMENTATION-V1` that creates only the new engine, its focused tests, and its delivery report. Do not wire it into runtime execution, candidate scoring, broker connectors, or dashboard services until the standalone engine passes its validator chain.
