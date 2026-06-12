# AI_OS Trading Lab Latency Measurement Contract

## Status and Authority Boundary

Status: canonical spec after approved APPLY.

This document defines the Trading Lab latency measurement contract for paper-only validation, fixture review, generated-evidence review, and future read-only display surfaces. It does not authorize live trading, broker execution, real orders, real webhooks, credentials or API keys, runtime mutation, APPLY, commit, push, merge, deployment, approval, dashboard control actions, or archive promotion.

Root safety authority remains `AGENTS.md`, `README.md`, and `RISK_POLICY.md`. If this spec conflicts with root safety authority, root safety authority wins.

## Purpose

The purpose of this spec is to define how AI_OS measures and validates Trading Lab latency across a paper-only workflow:

```text
paper signal -> validation -> route preview -> paper simulation -> journal -> scorecard -> review
```

Latency measurement is a readiness and review signal only. It must never become execution authority, approval authority, live-trading readiness, broker-routing readiness, webhook readiness, or profit assurance.

## Paper-Only Scope

Trading Lab latency measurement is limited to local paper simulation, deterministic fixtures, generated paper-run evidence, and validator review.

Allowed scope:

- local paper signal fixtures.
- local dashboard mock latency fixtures.
- local generated paper-run latency evidence.
- paper-only route previews.
- paper-only replay, scorecard, journal, and review records.
- read-only validator checks.

Blocked scope:

- live market execution.
- broker or OANDA execution.
- real order placement.
- real webhook execution.
- credential, API key, token, account, or secret handling.
- dashboard-triggered APPLY or execution.
- runtime, telemetry, report, approval, or archive mutation.

## Prohibited Behavior

This spec does not authorize and must not be interpreted to authorize:

- live trading.
- broker execution.
- OANDA integration or live order execution.
- real orders.
- real webhooks.
- broker credentials, API keys, tokens, account identifiers, passwords, private keys, or secrets.
- production deployment.
- runtime mutation.
- telemetry mutation.
- report mutation.
- approval mutation.
- APPLY, commit, push, merge, or protected Git actions.
- archive promotion.
- dashboard execution controls.
- autonomous execution.

Any appearance of these behaviors in a latency record, fixture, validator, report, dashboard surface, or generated result is a stop condition unless a separate approved production policy explicitly changes the boundary.

## Latency Measurement Record

A Trading Lab latency measurement record should identify a paper-only signal and the local paper workflow timestamps used to review timing quality.

Recommended core fields:

- `schema_version`
- `record_id` or `latency_report_id`
- `mode`: must be `paper_only`
- `signal_id`
- `alert_created_time` or `alert_created_at`
- `alert_received_time` or `alert_received_at`
- `validation_start_time` or `validation_started_at`
- `validation_end_time` or `validation_completed_at`
- `route_preview_time` or `route_preview_at`
- `paper_execution_time`, `paper_trade_simulated_at`, or equivalent paper simulation timestamp
- `journal_write_time` or `journal_recorded_at`
- `scorecard_update_time` or `scorecard_updated_at`
- `total_delay_seconds`
- `latency_status` or `stale_status`
- `delayed_reason` or `delay_reason`
- `clock_skew_status`
- `blocked_reason`
- `step_delays` or named derived delay fields
- `live_execution` or `live_execution_status`: must be `BLOCKED`
- `broker` or `broker_status`: must be `BLOCKED` or `PAPER_ONLY` as appropriate for the record type
- `oanda_status`: must be `BLOCKED` when present
- `real_webhook_status`: must be `BLOCKED` when present
- `real_order` or `real_order_status`: must be `BLOCKED`
- `api_key_required`: must be `false` when present
- `secrets_status`: must be `BLOCKED` when present
- `next_safe_action`

Recommended step-delay fields:

- `alert_to_receive_seconds`
- `receive_to_validation_start_seconds`
- `validation_duration_seconds`
- `validation_to_route_preview_seconds`
- `route_preview_to_paper_execution_seconds` or `route_preview_to_paper_simulation_seconds`
- `paper_execution_to_journal_seconds` or `paper_simulation_to_journal_seconds`
- `journal_to_scorecard_seconds`

## Timestamp Order and Clock Skew

Validators should compare available timestamps in workflow order. When all required timestamps are present, each derived delay should equal the difference between its start and end timestamp.

If any measured step produces a negative delay, the validator must not report PASS. Negative delay means the record has a future timestamp, reversed timestamp order, system clock mismatch, fixture error, or clock-skew condition.

Required clock-skew behavior:

- mark `clock_skew_status` as `CLOCK_SKEW_DETECTED` or an equivalent blocked clock-skew status.
- mark the review state as `REVIEW`, `BLOCKED`, `BLOCKED_FOR_REVIEW`, or equivalent.
- include a `blocked_reason` or review reason.
- keep live execution, broker execution, real webhook, real order, and credential fields blocked.
- require a next safe action that reviews or repairs fixture timestamps before trusting timing quality.

## Stale, Delayed, Fresh, Pending, and Future Signal Handling

Latency validators must distinguish missing data, valid data, delayed data, stale data, and future/clock-skew data.

Recommended status meanings:

- `PENDING_VALIDATION` or `Pending validation`: timestamps or measured values are incomplete.
- `UNKNOWN`: evidence is absent or cannot be verified.
- `FRESH`: measured paper workflow delay is within the approved review threshold.
- `DELAYED_REVIEW`: measured paper workflow delay requires review but is not stale.
- `STALE_BLOCKED` or `Stale`: measured delay exceeds the stale threshold and must block readiness.
- `CLOCK_SKEW_DETECTED` or `CLOCK_SKEW_BLOCKED`: timestamp order is negative or future-dated and must block readiness.
- `BLOCKED_FOR_REVIEW`: evidence exists but must not be trusted until review.

Missing timestamps must not be treated as PASS. Future timestamps, negative delays, and clock skew must not be treated as PASS. Stale signals must not unlock routing, execution, webhook, broker, order, or dashboard control paths.

## Evidence File Roles

Generated Trading Lab latency results are evidence only. They may prove what a local paper run reported, but they do not define contract authority by themselves.

Known active evidence examples include:

- `apps/trading_lab/trading_lab/results/paper_runner/PAPER_LATENCY_REPORT_001.json`
- `apps/trading_lab/trading_lab/results/paper_runner/PAPER_REPLAY_RESULT_001.json`
- `apps/trading_lab/trading_lab/results/paper_runner/PAPER_REPLAY_LEDGER_001.json`
- `apps/trading_lab/trading_lab/results/paper_runner/PAPER_VALIDATION_REPORT_001.json`

Generated evidence may be used by validators to confirm:

- JSON parses.
- mode remains `paper_only`.
- live execution remains blocked.
- broker, OANDA, real webhook, real order, API key, and secret fields remain blocked.
- clock skew is detected when timestamps are inconsistent.
- stale or blocked review states are represented accurately.

Generated evidence must never be treated as approval authority, execution authority, source-of-truth authority, archive-promotion authority, commit authority, or push authority.

## Dashboard Fixture Role

Dashboard mock latency files are fixture-only unless a future approved spec or implementation packet assigns a more specific role.

Known fixture examples include:

- `apps/dashboard/mock-data/phase-25-latency-measurement-core.example.json`
- `apps/dashboard/mock-data/latency-ledger-v1.example.json`
- `apps/dashboard/mock-data/trading-lab-latency-replay.example.json`

Dashboard fixtures may be used to test deterministic display shape, local fixture parsing, blocked status labels, and read-only panel behavior. They must not be treated as live state, runtime truth, trading readiness, broker readiness, webhook readiness, or active execution input.

## Archive Historical Reference Role

Archive files are historical reference only unless separately promoted by approved canonical governance.

Known historical reference examples include:

- `archive/docs_aios_trading_laboratory_legacy/phase_25/LATENCY_MEASUREMENT_CORE_CONTRACT.json`
- `archive/docs_aios_trading_laboratory_legacy/phase_25/PHASE_25_LATENCY_MEASUREMENT_CORE.md`
- related old latency contracts under `archive/docs_aios_trading_laboratory_legacy/latency/`

Archive material may explain why older validators expected certain fields or thresholds. Archive material must not be treated as current operating authority, current validator authority, live readiness, broker readiness, or dashboard runtime source unless an approved APPLY packet promotes a specific rule into an active canonical file.

## Validator Expectations

Future Trading Lab latency validators should check:

- canonical spec path exists.
- referenced fixture and evidence paths exist when required by that validator.
- JSON fixture and generated evidence files parse.
- mode remains `paper_only`.
- required latency fields exist for the record type being checked.
- timestamp order is valid when timestamps are present.
- derived delay fields match timestamp differences.
- `total_delay_seconds` matches the sum or declared measurement rule for available delays.
- missing timestamps produce pending, unknown, or review states, not PASS.
- negative delay or future timestamp conditions produce clock-skew or blocked review states, not PASS.
- stale and delayed thresholds produce stale or delayed review states.
- blocked live execution fields remain blocked.
- prohibited fields are absent.
- archive references are labeled historical if used for context.
- generated evidence is labeled evidence-only.
- dashboard fixtures are labeled fixture-only.
- validator output does not approve APPLY, live trading, broker execution, commit, push, merge, deployment, or archive promotion.

Validators must not repair files during validation. Repair requires a separate approved APPLY packet with exact allowed paths, forbidden paths, validation, and stop point.

## Failure Severity Labels

Latency validators should use AI_OS severity language and fail closed when safety or authority is unclear.

Recommended severity handling:

- `PASS`: all required evidence is present, parsed, paper-only, internally consistent, and safety-blocked.
- `REVIEW`: evidence exists but needs human review, including delayed status or incomplete noncritical evidence.
- `WARNING`: nonblocking concern that should be reviewed before downstream use.
- `BLOCKED`: safety, authority, missing contract, invalid JSON, clock skew, stale signal, forbidden field, live path, broker path, webhook path, order path, credential path, or archive-promotion risk is present.
- `UNKNOWN`: evidence is absent or cannot be verified.

Any invalid severity value must be treated as blocked until corrected by a separate approved task.

## No-Live-Trading Safety Requirements

Every latency fixture, generated evidence file, validator, and dashboard display must preserve paper-only safety.

Required blocked states:

- live trading: blocked.
- live execution: blocked.
- broker execution: blocked.
- OANDA execution: blocked.
- real webhook execution: blocked.
- real order placement: blocked.
- credentials and API keys: blocked or absent.
- secrets: blocked or absent.
- account identifiers: blocked or absent.
- autonomous execution: blocked.

Prohibited fields include:

- `api_key`
- `secret`
- `token`
- `broker_account`
- `account_id`
- `webhook_url`
- `order_id`
- `live_order`
- `real_order`
- any field that carries a credential, broker account, live endpoint, live route, or real order identifier.

The presence of any prohibited live, broker, webhook, order, or credential field must not be treated as PASS.

## Relationship to Latency Schema

`schemas/aios/latency/LATENCY_DECISION.schema.json` is a related AI_OS latency decision and safety-policy schema. It supports broader latency doctrine such as deterministic-first processing, local-fixture-only decisions, blocked live trading, blocked broker execution, and blocked secrets.

That schema does not replace this Trading Lab latency measurement contract. This spec owns the paper-only Trading Lab measurement record expectations, dashboard fixture role, generated evidence role, historical archive role, and validator expectations for paper latency records.

## Relationship to Active App and Tests

Active app and test paths provide paper-only behavior proof. They do not replace this spec as contract authority.

Relevant behavior-proof paths include:

- `apps/trading_lab/README.md`
- `apps/trading_lab/trading_lab/execution/live_broker_stub.py`
- `apps/trading_lab/trading_lab/execution/paper_broker.py`
- `aios/modules/trader/config.py`
- `tests/trader/test_mock_alert_payload_v01.py`
- `tests/trader/test_paper_route_preview_v01.py`

Future readiness claims should require both contract validation and paper-only behavior proof. A validator must not claim live readiness from app/test evidence, generated latency evidence, dashboard fixtures, or archive material.

## Future UI / Game-Like Display Boundary

Future dashboard, rich UI, WebGPU/WebGL, UE-style, or game-like command-center surfaces may display latency status only as read-only evidence.

Allowed UI behavior:

- display latency badge or panel.
- display source path or source label.
- display freshness, stale, invalid, blocked, pending, or review status.
- display next safe action.
- display paper-only and no-live-trading status.

Blocked UI behavior:

- direct repo file mutation.
- direct telemetry mutation.
- direct Trading Lab runtime mutation.
- dashboard-triggered APPLY.
- broker, webhook, order, or credential entry.
- live trading controls.
- hidden background automation.
- treating fixtures as live runtime truth.

Future UI clients must use approved read-only API or fixture boundaries. They must not read runtime ledgers, approval inboxes, secrets, broker data, local filesystem state, or generated evidence directly unless a separate approved architecture and API boundary allows it.

## Stop Conditions

Stop and report `BLOCKED` or `REVIEW` when any of these occur:

- canonical spec is missing when required.
- referenced fixture or evidence file is missing.
- JSON parse fails.
- required latency fields are missing.
- timestamp order is negative without clock-skew handling.
- future timestamps are present without blocked review status.
- stale status is treated as PASS.
- missing timestamps are treated as PASS.
- live trading, broker, OANDA, real webhook, real order, credential, API key, token, account, or secret fields are present.
- archive material is treated as current authority.
- generated evidence is treated as current authority.
- dashboard fixture data is treated as runtime truth.
- validator output is treated as approval.
- APPLY, commit, push, merge, deployment, runtime mutation, telemetry mutation, report mutation, approval mutation, or archive promotion appears without separate explicit approval.

## Future Repair Sequence

Recommended future sequence:

1. Map all active Trading Lab latency validators to this canonical spec, dashboard fixtures, generated evidence files, and historical archive references.
2. Repair stale validator references in a separate approved APPLY packet.
3. Label dashboard latency mock files as fixture-only if needed in a separate approved APPLY packet.
4. Add validator guards for evidence-only and archive-historical boundaries.
5. Re-run paper-only safety validators.
6. Keep all commits, pushes, merges, dashboard runtime changes, trading runtime changes, telemetry mutation, archive mutation, and live/broker work blocked unless separately approved.
