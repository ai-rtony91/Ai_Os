# AIOS Forex Review-Ready Candidate Selector V1

## Purpose

Review-Ready Candidate Selector V1 chooses one best review-ready Forex candidate from a local list of candidate dictionaries after readiness and proof gates have produced review evidence.

The selector chooses a review-ready candidate only. It does not approve, prepare, route, place, close, or activate any trade.

## Scope

In scope:

- Pure local Python candidate selection.
- Deterministic scoring and ranking.
- Review-ready eligibility filtering.
- Rejection reasons for blocked, unsafe, below-threshold, or incomplete candidates.
- Hard false broker, credential, trade, and production permissions in every result.
- Standard-library CLI smoke path with optional local JSON input and optional explicit JSON output.

Out of scope:

- No broker/API/live/demo/paper trade action.
- No order placement.
- No order closure.
- No production activation.
- No scheduler, daemon, webhook, dashboard wiring, credential handling, account ID handling, or network access.

## Files Created

- `automation/forex_engine/forex_review_ready_candidate_selector_v1.py`
- `scripts/forex_delivery/run_forex_review_ready_candidate_selector_v1.py`
- `tests/forex_engine/test_forex_review_ready_candidate_selector_v1.py`
- `Reports/forex_delivery/AIOS_FOREX_REVIEW_READY_CANDIDATE_SELECTOR_V1.md`

## Selector Inputs

The public function is:

```python
select_review_ready_candidate(candidates: list[dict], *, min_score: float = 0.0) -> dict
```

Accepted candidate aliases include:

- `candidate_id` or `id`
- `strategy` or `strategy_id`
- `symbol` or `instrument`
- `direction`
- `review_ready` or `status`
- `gate_status` or `readiness_status`
- `evidence_depth_score`
- `statistical_profit_score`
- `profit_factor`
- `expectancy`
- `max_drawdown`
- `drawdown_score`
- `sample_size`
- `risk_score`
- `recency_score`
- `blocked_reasons` or `blockers`
- `proof_flags`
- `metadata`

Invalid or missing candidate lists return safe no-selection results instead of exceptions.

## Eligibility Rules

A candidate is eligible only when:

- `review_ready` is `True`, or `status` is `REVIEW_READY`, `READY_FOR_REVIEW`, or `REVIEW_READY_CANDIDATE`.
- It is not explicitly blocked.
- It has no non-empty blocker list.
- Its gate/readiness status does not contain `REJECT`, `BLOCKED`, `FAIL`, `FAILED`, or `NOT_READY`.
- `sample_size` exists and is greater than zero.
- `evidence_depth_score` exists and is greater than zero.
- It does not set protected proof flags such as broker, credential, trade, execution, or production permission flags to true.
- Its deterministic total score reaches `min_score`.

Rejected candidates are reported by candidate ID in `rejection_reasons`.

## Scoring Rules

Scoring prefers:

- Higher `statistical_profit_score`.
- Higher `evidence_depth_score`.
- Higher `profit_factor`.
- Higher `expectancy`.
- Higher `sample_size`.
- Higher `risk_score`.
- Higher `recency_score`.
- Higher optional `drawdown_score`.
- Lower `max_drawdown`.

The score is local arithmetic only and does not perform execution sizing or trade authorization.

## Tie-Breakers

Candidate ranking is deterministic:

1. Higher `total_score`.
2. Higher `evidence_depth_score`.
3. Higher `statistical_profit_score`.
4. Higher `profit_factor`.
5. Higher `expectancy`.
6. Lower `max_drawdown`.
7. Higher `sample_size`.
8. Lexicographically smallest `candidate_id`.

## Safety Boundaries

Every result includes:

- `execution_allowed: false`
- `broker_access_allowed: false`
- `credential_access_allowed: false`
- `account_access_allowed: false`
- `trade_action_allowed: false`
- `live_trade_allowed: false`
- `demo_trade_allowed: false`
- `paper_trade_allowed: false`
- `order_placement_allowed: false`
- `order_closure_allowed: false`
- `production_activation_allowed: false`

Safety `blocked_actions` include:

- `broker_access`
- `credential_access`
- `account_access`
- `live_trade`
- `demo_trade`
- `paper_trade`
- `order_placement`
- `order_closure`
- `production_activation`

Any future demo trade path remains separately gated by owner approval and higher AIOS policy.

## Validation

Validation status from this APPLY run:

- `python -m py_compile automation/forex_engine/forex_review_ready_candidate_selector_v1.py scripts/forex_delivery/run_forex_review_ready_candidate_selector_v1.py tests/forex_engine/test_forex_review_ready_candidate_selector_v1.py`: PASS
- `python -m pytest tests/forex_engine/test_forex_review_ready_candidate_selector_v1.py -q`: PASS, 18 passed
- `python scripts/forex_delivery/run_forex_review_ready_candidate_selector_v1.py`: BLOCKED by Windows sandbox runner error `CreateProcessAsUserW failed: 1312` before Python started
- CLI sample execution evidence: PASS through focused pytest subprocess coverage
- `git diff --check -- automation/forex_engine/forex_review_ready_candidate_selector_v1.py scripts/forex_delivery/run_forex_review_ready_candidate_selector_v1.py tests/forex_engine/test_forex_review_ready_candidate_selector_v1.py Reports/forex_delivery/AIOS_FOREX_REVIEW_READY_CANDIDATE_SELECTOR_V1.md`: PASS before validation report update
- `git status --short --branch`: branch `feature/forex-review-ready-candidate-selector-v1` with only the four allowed packet files untracked

## What This Does Not Do

- No broker/API/live/demo/paper trade action.
- No order placement.
- No order closure.
- No production activation.
- No credential access.
- No account access.
- No network access.
- No scheduler, daemon, webhook, dashboard, or production wiring.
- No execution permission.
- No claim that a future demo trade is approved.

## Next Safe Action

Run the local validator chain, then keep any future demo trade path behind separate owner approval and higher AIOS policy.
