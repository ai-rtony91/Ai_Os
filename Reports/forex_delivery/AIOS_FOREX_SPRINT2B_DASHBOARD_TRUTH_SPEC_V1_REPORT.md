# AIOS Forex Sprint2B Dashboard Truth Spec V1 Report

## Packet Readback

- Packet ID: `AIOS-FOREX-SPRINT2B-DASHBOARD-TRUTH-SPEC-V1`
- Target future implementation: `AIOS-FOREX-DASHBOARD-TRUTH-SUMMARY-IMPLEMENTATION-V1`
- Mode: reports-only APPLY
- Created file: `Reports/forex_delivery/AIOS_FOREX_SPRINT2B_DASHBOARD_TRUTH_SPEC_V1_REPORT.md`
- Current branch preflight observed: `main`
- Worktree preflight observed: clean before report creation
- Scope boundary: planning/spec report only

## Context Readback

The existing Forex dashboard truth surface is display-only. The current wiring report and source describe a read-only projection chain:

`evidence_ledger -> session_replay -> orchestrator read model -> dashboard display`

The current `services/orchestrator/forexDashboardTruthStatus.js` builds a paper-only truth status with no broker, no live trading, no credentials, no real orders, and no network access safety flags. It includes fields for freshness, replay status, evidence ledger status, candidates, previews, risk, trades, P/L, balance, drawdown, missing evidence warnings, blocked reasons, and next safe action.

`automation/forex_engine/candidate_scoring_v1.py` exists and provides deterministic candidate ranking with statuses such as `REVIEW_READY`, `REQUIRE_MORE_EVIDENCE`, `REJECT`, `BLOCKED_BY_RISK`, `BLOCKED_BY_EVIDENCE`, and `BLOCKED_BY_DEMO_READINESS`. It performs no file reads, network calls, broker calls, credential access, account lookup, order placement, scheduling, or runtime mutation.

Exact files named `automation/forex_engine/risk_budget_v1.py`, `automation/forex_engine/broker_health_readonly_v1.py`, and `automation/forex_engine/profitability_evidence_v1.py` were not present during this report pass. Closest current modules observed were:

- `automation/forex_engine/paper_risk_governor.py`
- `automation/forex_engine/broker_read_only_snapshot_contract_v1.py`
- `automation/forex_engine/long_only_profitability_evidence_depth_gate_v1.py`
- `automation/forex_engine/oanda_demo_to_live_profit_readiness_truth_v1.py`

## 1. Purpose

Define a collision-free implementation specification for a deterministic Forex dashboard truth summary generator.

The future generator must convert already-sanitized Forex engine outputs into a compact dashboard-safe card model. It must not create trade truth, order truth, broker truth, account truth, readiness authority, or live execution authority. It is a pure summary layer over existing evidence and status outputs.

The intended result is a stable Python read-model generator that can be tested independently and later consumed by orchestrator/dashboard wiring under a separate approved packet.

## 2. Scope

The future implementation may create a new read-only generator that:

- accepts in-memory dictionaries or typed dataclasses from approved Forex engine outputs.
- builds a normalized dashboard truth summary envelope.
- emits deterministic cards for readiness, risk, candidates, broker health, profit evidence, blockers, and next action.
- redacts or blocks on sensitive field names and sensitive-looking values.
- preserves paper-only safety flags.
- ranks blockers and next actions deterministically.
- includes focused tests proving safety, ordering, dominance, and output shape.

The future implementation must remain display-only and review-only. It may summarize whether something is review-ready, but it must not make anything execution-ready.

## 3. Non-goals

The future generator must not:

- place trades.
- call broker APIs.
- read environment variables.
- read credentials, account identifiers, bearer values, authorization headers, or local vaults.
- open network connections.
- start schedulers, daemons, background loops, or webhooks.
- write dashboard UI code.
- mutate existing orchestrator routes.
- modify `candidate_scoring_v1.py`, risk engines, broker engines, or profit evidence engines.
- create a new governance authority document.
- override `RISK_POLICY.md`, `AGENTS.md`, or protected-action gates.
- claim live readiness, live approval, funding approval, compounding approval, or real-money authority.

## 4. Allowed Future Implementation Paths

The recommended future implementation packet should allow only these paths:

- `automation/forex_engine/dashboard_truth_summary_v1.py`
- `tests/forex_engine/test_dashboard_truth_summary_v1.py`
- `scripts/forex_delivery/run_dashboard_truth_summary_v1.py`
- `Reports/forex_delivery/AIOS_FOREX_DASHBOARD_TRUTH_SUMMARY_IMPLEMENTATION_V1_REPORT.md`

The runner is optional. If included, it must only transform explicitly supplied sanitized JSON or in-memory sample payloads and must not inspect secret stores, environment variables, broker endpoints, or account files.

## 5. Forbidden Future Implementation Paths

The future implementation packet should forbid:

- `apps/**`
- `services/orchestrator/**`
- `schemas/**`, unless a later schema-specific packet is approved
- `docs/**`, unless a later documentation packet is approved
- `.github/**`
- `.env`
- `**/.env`
- `**/*secret*`
- `**/*credential*`
- `**/*token*`
- broker transport modules
- live order modules
- account persistence modules
- credential vault helpers
- existing source modules named in the collision notes, unless the packet is a read-only inspection pass

The future generator must not edit `candidate_scoring_v1.py`, any future `risk_budget_v1.py`, any future `broker_health_readonly_v1.py`, or any future `profitability_evidence_v1.py`.

## 6. Input Contract

The core function should be pure and accept an input mapping:

```text
build_forex_dashboard_truth_summary(input_payload: Mapping[str, Any] | None) -> dict[str, Any]
```

Required top-level input shape:

```text
{
  "as_of": string or null,
  "source": string,
  "candidate_scoring": mapping or null,
  "risk_budget": mapping or null,
  "broker_health": mapping or null,
  "profit_evidence": mapping or null,
  "runtime_truth": mapping or null,
  "operator_context": mapping or null
}
```

Input rules:

- `as_of` must be a supplied timestamp string or `null`; the generator must not call the wall clock for deterministic tests.
- `source` must describe the sanitized source bundle, for example `sanitized_forex_engine_outputs`.
- `candidate_scoring` should accept the JSON-safe envelope from `candidate_scores_to_jsonable_dict`.
- `risk_budget` should accept a future `risk_budget_v1.py` result if present, or a compatible paper risk result containing `risk_passed`, `risk_used`, `rejection_reasons`, `blockers`, and `paper_only`.
- `broker_health` should accept a future `broker_health_readonly_v1.py` result if present, or a compatible read-only broker snapshot validation result containing `classification`, `valid_for_review`, `blockers`, `next_safe_action`, and permission flags.
- `profit_evidence` should accept a future `profitability_evidence_v1.py` result if present, or a compatible evidence-depth result containing `status`, `ready`, `metrics`, `blockers`, and `next_safe_action`.
- `runtime_truth` may accept the existing dashboard truth status shape for optional context.
- `operator_context` may contain display-safe values such as lane, packet id, mode, and paper-only label.

Input must be treated as untrusted. Sensitive keys or sensitive-looking values must be redacted and must create a blocking status.

## 7. Output Contract

The generator must return a JSON-safe dictionary:

```text
{
  "schema_version": "dashboard_truth_summary_v1",
  "engine_version": "dashboard_truth_summary_v1",
  "mode": "DISPLAY_ONLY",
  "paper_only": true,
  "as_of": string or null,
  "source": string,
  "overall_status": string,
  "overall_severity": string,
  "cards": list[card],
  "blockers": list[blocker],
  "warnings": list[string],
  "next_action": next_action,
  "redaction": redaction_summary,
  "permissions": permission_flags,
  "safety": safety_flags
}
```

Required permission and safety flags must always remain false for protected actions:

```text
{
  "broker_action_allowed": false,
  "real_orders_allowed": false,
  "live_trading_allowed": false,
  "demo_order_allowed": false,
  "credential_access_allowed": false,
  "account_id_persistence_allowed": false,
  "network_access_allowed": false,
  "scheduler_allowed": false,
  "daemon_allowed": false,
  "webhook_allowed": false
}
```

The output must never contain raw secrets, raw account identifiers, raw tokens, authorization headers, private URLs, or raw broker credential material.

## 8. Dashboard-safe Truth Card Model

Each dashboard card must use this stable shape:

```text
{
  "card_id": string,
  "title": string,
  "status": string,
  "severity": "critical" | "warning" | "info" | "ok",
  "summary": string,
  "facts": list[fact],
  "blockers": list[blocker],
  "warnings": list[string],
  "next_action": string,
  "source_refs": list[string],
  "redaction": redaction_summary,
  "permissions": permission_flags
}
```

Facts must use this stable shape:

```text
{
  "label": string,
  "value": string | number | boolean | null,
  "unit": string | null
}
```

Blockers must use this stable shape:

```text
{
  "code": string,
  "severity": "critical" | "warning",
  "source_card": string,
  "summary": string,
  "next_action": string
}
```

Card IDs must be stable:

- `readiness`
- `risk`
- `candidate`
- `broker_health`
- `profit_evidence`
- `blockers`
- `next_action`

## 9. Status Hierarchy

Overall status must be derived from the highest-priority active status:

1. `BLOCKED_SENSITIVE_INPUT`
2. `BLOCKED_LIVE_OR_BROKER_AUTHORITY`
3. `BLOCKED_UNSANITIZED_BROKER_HEALTH`
4. `BLOCKED_RISK`
5. `BLOCKED_PROFIT_EVIDENCE`
6. `BLOCKED_CANDIDATE`
7. `BLOCKED_DEMO_READINESS`
8. `NEEDS_EVIDENCE`
9. `REVIEW_READY_NOT_EXECUTION_READY`
10. `DISPLAY_ONLY_NO_RUNTIME_EVIDENCE`
11. `DISPLAY_ONLY_READY`

No status may imply execution authority. `DISPLAY_ONLY_READY` means the summary is well-formed for review, not that a trade is allowed.

## 10. Readiness Card Specification

Card ID: `readiness`

Purpose: summarize the whole Forex truth bundle in one operator-readable result.

Inputs:

- all normalized child cards.
- global blocker list.
- redaction summary.
- permission flags.

Required facts:

- `mode`: always `DISPLAY_ONLY`.
- `paper_only`: always `true`.
- `overall_status`.
- `dominant_blocker_code` or `none`.
- `cards_ready_count`.
- `cards_blocked_count`.
- `live_trading_allowed`: always `false`.

Status rules:

- If redaction blockers exist, status is `BLOCKED_SENSITIVE_INPUT`.
- Else if live, broker, network, order, scheduler, daemon, webhook, or credential authority appears true anywhere, status is `BLOCKED_LIVE_OR_BROKER_AUTHORITY`.
- Else inherit the highest-priority child blocker.
- Else status is `REVIEW_READY_NOT_EXECUTION_READY` when all required inputs are present and child cards are not blocked.
- Else status is `DISPLAY_ONLY_NO_RUNTIME_EVIDENCE` when optional runtime data is missing but no unsafe condition is present.

Next action must be the next action from the dominant blocker or `Continue review-only dashboard truth summary validation`.

## 11. Risk Card Specification

Card ID: `risk`

Purpose: summarize risk-budget or paper-risk evidence without granting execution.

Accepted input fields:

- `risk_passed`
- `status`
- `classification`
- `risk_used`
- `risk_budget_used`
- `risk_budget_remaining`
- `limits`
- `rejection_reasons`
- `blockers`
- `paper_only`
- `next_safe_action`

Status rules:

- If any live or broker permission is true, status is `BLOCKED_LIVE_OR_BROKER_AUTHORITY`.
- If `risk_passed` is false or blockers/rejection reasons exist, status is `BLOCKED_RISK`.
- If risk input is missing, status is `NEEDS_EVIDENCE`.
- If risk input passes, status is `REVIEW_READY_NOT_EXECUTION_READY`.

Facts:

- risk passed.
- risk used.
- risk budget remaining when present.
- rejection reason count.
- paper-only flag.

## 12. Candidate Card Specification

Card ID: `candidate`

Purpose: summarize review-ready candidate ranking without selecting a trade for execution.

Accepted input fields:

- `engine_version`
- `candidate_count`
- `results`
- per-result `candidate_id`
- per-result `rank`
- per-result `decision`
- per-result `normalized_score`
- per-result `decision_reasons`
- per-result `blockers`
- per-result `recommended_next_action`
- per-result `safety`

Status rules:

- If no candidates are present, status is `NEEDS_EVIDENCE`.
- If the top candidate decision is `REJECT`, status is `BLOCKED_CANDIDATE`.
- If the top candidate decision is `BLOCKED_BY_RISK`, status is `BLOCKED_RISK`.
- If the top candidate decision is `BLOCKED_BY_EVIDENCE`, status is `BLOCKED_PROFIT_EVIDENCE`.
- If the top candidate decision is `BLOCKED_BY_DEMO_READINESS`, status is `BLOCKED_DEMO_READINESS`.
- If all candidates require more evidence, status is `NEEDS_EVIDENCE`.
- If top candidate is `REVIEW_READY`, status is `REVIEW_READY_NOT_EXECUTION_READY`.

Candidate card must display at most the top five candidate facts. More candidates may be counted but not expanded unless a later dashboard packet approves a drilldown.

## 13. Broker Health Card Specification

Card ID: `broker_health`

Purpose: summarize sanitized read-only broker health without exposing account data or enabling broker action.

Accepted input fields:

- `engine_version`
- `classification`
- `valid_for_review`
- `account_reference_allowed`
- `blockers`
- `next_safe_action`
- `demo_execution_allowed`
- `broker_action_allowed`
- `real_money_allowed`
- `live_trading_allowed`
- `credential_access_allowed`
- `account_id_persistence_allowed`

Status rules:

- If input is missing, status is `NEEDS_EVIDENCE`.
- If sanitized/account-reference checks fail, status is `BLOCKED_UNSANITIZED_BROKER_HEALTH`.
- If broker/live/credential/account persistence permission is true, status is `BLOCKED_LIVE_OR_BROKER_AUTHORITY`.
- If blockers exist or `valid_for_review` is false, status is `BLOCKED_UNSANITIZED_BROKER_HEALTH`.
- If valid for review, status is `REVIEW_READY_NOT_EXECUTION_READY`.

Facts must never include a raw account identifier. A placeholder such as `DEMO_ACCOUNT_REFERENCE_PRESENT` is display-safe.

## 14. Profit Evidence Card Specification

Card ID: `profit_evidence`

Purpose: summarize whether sanitized profitability evidence is deep enough for review.

Accepted input fields:

- `status`
- `ready`
- `candidate_id`
- `strategy_id`
- `instrument`
- `direction`
- `blockers`
- `warnings`
- `metrics`
- `thresholds`
- `next_safe_action`
- `execution_allowed`
- `ready_to_execute`
- `demo_order_allowed`
- `live_autonomy_allowed`

Status rules:

- If input is missing, status is `NEEDS_EVIDENCE`.
- If any execution permission flag is true, status is `BLOCKED_LIVE_OR_BROKER_AUTHORITY`.
- If blockers exist or `ready` is false, status is `BLOCKED_PROFIT_EVIDENCE`.
- If evidence is ready, status is `REVIEW_READY_NOT_EXECUTION_READY`.

Required facts:

- candidate id, after redaction scan.
- strategy id, after redaction scan.
- instrument.
- direction.
- sample size.
- closed trades.
- expectancy.
- profit factor.
- max drawdown.
- evidence-ready flag.

## 15. Blocker Card Specification

Card ID: `blockers`

Purpose: show the consolidated blocker list in deterministic order.

The blocker card must include:

- blocker count.
- critical blocker count.
- warning blocker count.
- dominant blocker code.
- up to ten blocker summaries.
- next repair action from the dominant blocker.

If there are no blockers, the blocker card must still render with:

- status `DISPLAY_ONLY_READY`.
- severity `ok`.
- summary `No dashboard truth blockers detected; execution remains blocked by policy unless separately approved.`

The blocker card must not hide the no-execution boundary.

## 16. Next Action Card Specification

Card ID: `next_action`

Purpose: provide one safe next action for the operator or next packet author.

Selection rules:

- Redaction repair comes first.
- Live/broker authority removal comes second.
- Broker health repair comes before candidate review when broker input is present and blocked.
- Risk repair comes before candidate advancement when risk is blocked.
- Profit evidence repair comes before candidate advancement when profit evidence is blocked.
- Candidate evidence repair comes before dashboard wiring.
- If no blockers exist, recommend the next review-only validation or UI wiring packet, not execution.

The next action must be a sentence, not a shell command that executes broker, order, credential, or live behavior.

## 17. Secret/account/token Redaction Doctrine

The generator must perform recursive redaction before card construction.

Sensitive key fragments:

- `secret`
- `token`
- `credential`
- `password`
- `authorization`
- `bearer`
- `api_key`
- `apikey`
- `account_id`
- `accountid`
- `private_key`
- `refresh`
- `session_token`

Sensitive value patterns:

- long opaque strings that look like API values.
- bearer-style values.
- account identifier-looking values under account-related keys.
- URLs containing embedded credentials.
- private key delimiters.

Redaction behavior:

- Replace sensitive values with `REDACTED_SENSITIVE_VALUE`.
- Preserve safe booleans such as `credential_access_allowed: false`.
- Preserve safe placeholders such as `DEMO_ACCOUNT_REFERENCE_PRESENT`.
- Add blocker `sensitive_input_detected`.
- Set overall status to `BLOCKED_SENSITIVE_INPUT`.
- Include redaction counts, not raw sensitive values.

The redaction scanner must fail closed. If a value is ambiguous and risk is material, redact it and block.

## 18. Deterministic Ordering Rules

Card order must always be:

1. `readiness`
2. `risk`
3. `candidate`
4. `broker_health`
5. `profit_evidence`
6. `blockers`
7. `next_action`

Candidate ordering:

1. numeric `rank` ascending when present.
2. status priority from candidate scoring.
3. normalized score descending.
4. candidate id ascending.

Blocker ordering:

1. severity priority: `critical`, then `warning`.
2. status hierarchy priority.
3. card order priority.
4. blocker code ascending.
5. blocker summary ascending.

Warnings ordering:

1. card order priority.
2. warning text ascending.

The generator must not use insertion-order accidents from untrusted input to decide operator-facing priority.

## 19. Dominance Rules for Blockers

Dominance rules must be enforced across the full summary:

- Any sensitive input blocker dominates all other statuses.
- Any live, broker action, real order, credential access, account persistence, network access, scheduler, daemon, or webhook permission set to true dominates normal readiness.
- A card with blockers cannot report `ok` severity.
- Overall readiness cannot be more permissive than the most severe child card.
- Candidate review-ready cannot override risk blockers.
- Candidate review-ready cannot override broker health blockers.
- Candidate review-ready cannot override missing or blocked profit evidence.
- Missing required input creates `NEEDS_EVIDENCE`, not a pass.
- `REVIEW_READY_NOT_EXECUTION_READY` is the highest permissible positive status.
- `DISPLAY_ONLY_READY` means the display model is valid, not that the trading system is ready.

Dominant next action must come from the highest-priority blocker.

## 20. Test Plan

Future implementation should include at least these tests:

1. `test_empty_input_returns_display_only_no_runtime_evidence`
2. `test_none_input_returns_json_safe_summary`
3. `test_sensitive_key_redacts_and_blocks`
4. `test_sensitive_value_redacts_and_blocks`
5. `test_false_permission_flags_do_not_trigger_redaction`
6. `test_true_live_trading_permission_dominates_status`
7. `test_true_broker_action_permission_dominates_status`
8. `test_candidate_review_ready_is_not_execution_ready`
9. `test_candidate_blocked_by_risk_maps_to_blocked_risk`
10. `test_candidate_blocked_by_evidence_maps_to_profit_or_evidence_block`
11. `test_candidate_reject_maps_to_blocked_candidate`
12. `test_risk_rejection_reasons_create_blocked_risk`
13. `test_missing_risk_input_creates_needs_evidence`
14. `test_broker_unsanitized_result_blocks_broker_health`
15. `test_broker_valid_result_remains_review_only`
16. `test_profit_evidence_ready_remains_review_only`
17. `test_profit_evidence_blockers_create_blocked_profit_evidence`
18. `test_missing_profit_input_creates_needs_evidence`
19. `test_card_order_is_stable`
20. `test_blocker_order_is_stable`
21. `test_candidate_order_uses_rank_then_score_then_id`
22. `test_next_action_uses_dominant_blocker`
23. `test_output_permissions_are_always_false`
24. `test_output_contains_no_raw_sensitive_values`
25. `test_runtime_truth_no_evidence_maps_to_display_only_no_runtime_evidence`
26. `test_existing_candidate_scoring_fixture_can_feed_summary`
27. `test_existing_broker_read_only_snapshot_fixture_can_feed_summary`
28. `test_existing_profitability_evidence_fixture_can_feed_summary`

## 21. Validator Chain

Future implementation validator chain:

```text
git status --short --branch
python -m pytest tests/forex_engine/test_dashboard_truth_summary_v1.py
python -m pytest tests/forex_engine/test_candidate_scoring_v1.py
python -m pytest tests/orchestrator/test_forex_dashboard_truth_status.py
git diff --check
git status --short --branch
```

If future implementation does not touch orchestrator/dashboard code, the orchestrator truth status test is still useful as a regression check because the new summary generator must not weaken the existing display-only contract.

## 22. Expected Future Implementation Paths

Expected file names:

- `automation/forex_engine/dashboard_truth_summary_v1.py`
- `tests/forex_engine/test_dashboard_truth_summary_v1.py`
- `scripts/forex_delivery/run_dashboard_truth_summary_v1.py`
- `Reports/forex_delivery/AIOS_FOREX_DASHBOARD_TRUTH_SUMMARY_IMPLEMENTATION_V1_REPORT.md`

Expected public Python names:

- `DASHBOARD_TRUTH_SUMMARY_VERSION`
- `DISPLAY_ONLY_READY`
- `REVIEW_READY_NOT_EXECUTION_READY`
- `NEEDS_EVIDENCE`
- `BLOCKED_SENSITIVE_INPUT`
- `BLOCKED_LIVE_OR_BROKER_AUTHORITY`
- `build_forex_dashboard_truth_summary`
- `dashboard_truth_summary_to_jsonable_dict`
- `redact_dashboard_truth_input`

The generator should use only the standard library unless the repository already has a directly relevant local helper.

## 23. Exact Future Implementation Packet Prompt Summary

This is not a paste-ready Codex packet. It is the exact summary that a future packet should convert into a complete governed AI_OS executable packet.

Future packet summary:

- Packet ID: `AIOS-FOREX-DASHBOARD-TRUTH-SUMMARY-IMPLEMENTATION-V1`
- Mode: `APPLY`
- Zone: Forex Engine
- Lane: Dashboard Truth Summary Generator
- Worktree: `C:\Dev\Ai.Os`
- Branch: resolve after preflight, expected `main` if clean
- Purpose: create a pure Python display-only Forex dashboard truth summary generator, focused tests, optional sanitized JSON runner, and implementation report.
- Allowed paths:
  - `automation/forex_engine/dashboard_truth_summary_v1.py`
  - `tests/forex_engine/test_dashboard_truth_summary_v1.py`
  - `scripts/forex_delivery/run_dashboard_truth_summary_v1.py`
  - `Reports/forex_delivery/AIOS_FOREX_DASHBOARD_TRUTH_SUMMARY_IMPLEMENTATION_V1_REPORT.md`
- Forbidden paths:
  - `apps/**`
  - `services/orchestrator/**`
  - `schemas/**`
  - `.github/**`
  - `.env`
  - `**/.env`
  - `**/*secret*`
  - `**/*credential*`
  - `**/*token*`
- Required preflight:
  - `pwd`
  - `git status --short --branch`
  - `git branch --show-current`
  - `git remote -v`
- Required readback before writing:
  - inspect `candidate_scoring_v1.py`
  - inspect closest risk, broker health, and profit evidence modules that exist at that time
  - inspect existing dashboard truth status tests
- Required implementation:
  - pure summary function
  - recursive redaction
  - fixed card model
  - status hierarchy
  - blocker dominance
  - deterministic ordering
  - no broker, live, account, credential, network, scheduler, daemon, webhook, or order behavior
- Required validators:
  - `python -m pytest tests/forex_engine/test_dashboard_truth_summary_v1.py`
  - `python -m pytest tests/forex_engine/test_candidate_scoring_v1.py`
  - `python -m pytest tests/orchestrator/test_forex_dashboard_truth_status.py`
  - `git diff --check`
- Stop point: create local files only, no commit, no push, no PR.

## 24. Collision Notes

### `candidate_scoring_v1.py`

Observed file: `automation/forex_engine/candidate_scoring_v1.py`

Collision risk:

- It already owns candidate scoring, ranking, decision labels, score dimensions, and candidate safety flags.

Future generator rule:

- Do not duplicate scoring logic.
- Do not reweight score dimensions.
- Do not reinterpret candidate score internals beyond the published JSON-safe result fields.
- Treat candidate scoring as an input producer.
- Map candidate decisions into dashboard card statuses without changing candidate decisions.

### `risk_budget_v1.py`

Observed exact file: not present during this report pass.

Closest observed file: `automation/forex_engine/paper_risk_governor.py`

Collision risk:

- A future `risk_budget_v1.py` may own risk budget calculations, limits, usage, rejection reasons, and budget readiness.

Future generator rule:

- Do not create or modify `risk_budget_v1.py` inside the dashboard summary implementation packet.
- If the file exists during future implementation, import or accept only its public JSON-safe result shape.
- If it does not exist, accept a compatible risk mapping and classify missing risk evidence as `NEEDS_EVIDENCE`.
- Do not invent risk budget pass results from candidate score alone.

### `broker_health_readonly_v1.py`

Observed exact file: not present during this report pass.

Closest observed file: `automation/forex_engine/broker_read_only_snapshot_contract_v1.py`

Collision risk:

- A future `broker_health_readonly_v1.py` may own sanitized broker health, read-only snapshot validation, account placeholder discipline, market status, exposure reconciliation, and broker-specific blockers.

Future generator rule:

- Do not create or modify `broker_health_readonly_v1.py` inside the dashboard summary implementation packet.
- Accept broker health as input only.
- Do not call brokers.
- Do not read account identifiers.
- Do not normalize raw account values into display.
- Redact and block if raw account or credential material appears.

### `profitability_evidence_v1.py`

Observed exact file: not present during this report pass.

Closest observed file: `automation/forex_engine/long_only_profitability_evidence_depth_gate_v1.py`

Collision risk:

- A future `profitability_evidence_v1.py` may own profitability evidence thresholds, sample sufficiency, expectancy, profit factor, drawdown, walk-forward coverage, and evidence depth decisions.

Future generator rule:

- Do not create or modify `profitability_evidence_v1.py` inside the dashboard summary implementation packet.
- Accept profitability evidence as input only.
- Do not recalculate expectancy, profit factor, drawdown, or sample sufficiency.
- Display metrics and blockers after redaction.
- Keep positive output at `REVIEW_READY_NOT_EXECUTION_READY`.

## Recommended Next Packet

Run a governed implementation packet for `AIOS-FOREX-DASHBOARD-TRUTH-SUMMARY-IMPLEMENTATION-V1` using the future packet summary above, with the exact allowed paths limited to the new generator, focused tests, optional sanitized runner, and implementation report.
