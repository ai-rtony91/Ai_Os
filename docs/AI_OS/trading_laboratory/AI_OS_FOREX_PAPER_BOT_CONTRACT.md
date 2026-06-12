# AI_OS Classification Header

Classification: PAPER_ONLY_CONTRACT_REFERENCE.

This `docs/AI_OS` file is a subordinate paper-only Trading Lab reference. Root `AGENTS.md`, `README.md`, `RISK_POLICY.md`, `docs/governance/**`, `docs/workflows/**`, `docs/specs/**`, `docs/security/**`, `docs/architecture/**`, and `docs/audits/**` remain canonical above `docs/AI_OS` unless explicitly delegated.

This file does not authorize live trading, broker execution, real orders, real webhooks, credentials, secrets, runtime mutation, APPLY, commit, push, merge, deployment, or archive promotion.

# AI_OS Forex Paper Bot Contract

Status: docs-only contract.

This contract defines the first safe Forex Paper Bot build lane for AI_OS. It is paper-only, simulation-only, and educational-use-only. It does not create runner code, telemetry writers, market API calls, broker/OANDA integration, real orders, webhooks, scheduler behavior, worker launch, or approval mutation.

Source alignment:

- `automation/orchestration/night_supervisor/FOREX_PAPER_LAB_12H_PROFILE.json`
- `automation/orchestration/night_supervisor/FOREX_PAPER_LAB_12H_PROFILE_README.md`
- `docs/AI_OS/trading_laboratory/reference/FOREX_PAPER_LAB_12H_SUPERVISOR_PLAN_DRY_RUN_001.md`

## Paper-Only Purpose

The Forex Paper Bot exists to test signal quality, risk rules, ledger behavior, report wording, and operator visibility using deterministic fixture data. It may model paper decisions for review, but it must not express or route a live order, real order, broker instruction, webhook payload, or market API request.

Allowed early build work:

- Define fixture input contracts.
- Define paper signal intake fields.
- Define signal validation and rejection rules.
- Define paper risk gate behavior.
- Define paper ledger and report records.
- Define validators that prove paper-only boundaries.
- Define Pi5 display/progress fields.
- Draft future APPLY phases.

## Fixture Price Input

All price input must be local fixture data until a separate approval changes the boundary.

Required fixture fields:

- `fixture_id`
- `generated_at`
- `instrument`
- `timeframe`
- `source_type`: must be `LOCAL_FIXTURE`, `STATIC_REPLAY`, or `MANUAL_SAMPLE`
- `candles`: array of timestamped OHLCV-like records
- `spread_points`: optional simulated spread value
- `data_quality_status`: `PASS`, `NEEDS_REVIEW`, `INVALID_DATA`, or `UNKNOWN`
- `known_gaps`
- `paper_only`: true
- `live_market_data`: false

Blocked fixture fields:

- broker account identifiers
- OANDA account identifiers
- api key references
- real-time subscription handles
- webhook destinations
- execution endpoints

## Paper Signal Intake Schema

Paper signals are analysis inputs, not order requests.

Required fields:

- `signal_id`
- `strategy_id`
- `instrument`
- `timeframe`
- `observed_at`
- `input_source`
- `input_type`
- `direction`: `LONG`, `SHORT`, or `NEUTRAL`
- `entry_reference`
- `stop_reference`
- `target_reference`
- `confidence_hint`
- `evidence_paths`
- `fixture_price_input_id`
- `paper_only`: true
- `execution_allowed`: false

Blocked signal fields:

- live order identifiers
- real order identifiers
- broker routing instructions
- OANDA routing instructions
- webhook URLs
- credential or api key references

## Signal Validation Rules

A paper signal may move forward only when validation says it is safe for paper review.

Minimum validation checks:

- `strategy_id` exists in the paper strategy registry.
- `instrument`, `timeframe`, and `observed_at` are present.
- Fixture price input exists and is marked paper-only.
- Evidence paths are present and local/repo-approved.
- Direction is one of the allowed enum values.
- Risk references are present or marked `UNKNOWN`.
- `execution_allowed` is false.
- No broker, OANDA, api key, webhook, live order, or real order fields are present.

Validation statuses:

- `PASS`
- `FAIL`
- `NEEDS_EVIDENCE`
- `MISMATCH`
- `INVALID_DATA`
- `UNKNOWN`

Validation `PASS` allows paper review only. It never grants live trading or execution authority.

## Strategy And Risk Rule Boundary

Strategy and risk rules are review gates, not execution gates.

Required strategy fields:

- `strategy_id`
- `strategy_name`
- `market_scope`
- `timeframe_scope`
- `allowed_signal_inputs`
- `blocked_signal_inputs`
- `risk_model_reference`
- `validation_rules_reference`
- `paper_trading_status`
- `approval_status`
- `known_gaps`

Required risk gate fields:

- `risk_gate_id`
- `signal_id`
- `max_risk_units`
- `stop_distance_status`
- `position_size_model`: simulated only
- `risk_reward_estimate`
- `stale_signal_status`
- `blocked_reason`
- `paper_decision`: `ACCEPT_FOR_REVIEW`, `REJECT`, `PAUSE`, or `UNKNOWN`
- `execution_allowed`: false

Risk rules must be deterministic, inspectable, and fixture-backed before any runner work is proposed.

## Paper Ledger Schema

The paper ledger records simulated outcomes for review. It is not a broker ledger and must not be used for settlement, accounting, tax, or live position tracking.

Required ledger fields:

- `ledger_entry_id`
- `signal_id`
- `strategy_id`
- `fixture_price_input_id`
- `paper_opened_at`
- `paper_closed_at`
- `paper_status`: `OPEN_SIMULATED`, `CLOSED_SIMULATED`, `CANCELLED`, `INVALID`, or `UNKNOWN`
- `entry_reference`
- `exit_reference`
- `result_r_multiple`
- `max_favorable_excursion_r`
- `max_adverse_excursion_r`
- `rule_followed`: true/false/unknown
- `notes`
- `paper_only`: true
- `execution_allowed`: false

Blocked ledger fields:

- broker fill identifiers
- real order identifiers
- live account balances
- live P/L claims
- payout or withdrawal fields
- webhook receipts

## Paper Report Output

Paper reports summarize fixture-backed evidence only.

Required report fields:

- `report_id`
- `generated_at`
- `source_ledger_entries`
- `source_signal_ids`
- `strategy_summary`
- `risk_gate_summary`
- `paper_result_summary`
- `validation_summary`
- `blocked_live_path_summary`
- `next_safe_action`
- `human_review_required`
- `paper_only`: true
- `approval_authority`: false
- `execution_authority`: false

Report wording must use Paper Trading Simulation, paper decision, simulated result, fixture input, and review. It must avoid implying a live bot, live order, broker connection, OANDA connection, real market feed, webhook execution, or profitability guarantee.

## Validator Requirements

Before any future APPLY phase creates code, the lane needs validators that prove:

- JSON fixture records parse.
- Required schema fields are present.
- `paper_only` is true where required.
- `execution_allowed` is false where required.
- No broker, OANDA, api key, webhook, live order, real order, scheduler, worker launch, or live market endpoint fields are present.
- Paper report output carries no approval authority.
- Paper report output carries no execution authority.
- Pi5 display fields remain display-only.

## Pi5 Display And Progress Fields

Pi5 display is allowed to show status only. It must not expose action controls.

Recommended fields:

- `forex_paper_bot_progress_percent`
- `forex_paper_bot_status`
- `paper_only`
- `report_only`
- `fixture_input_ready`
- `signal_schema_ready`
- `risk_gate_ready`
- `paper_ledger_ready`
- `validator_ready`
- `blocked_live_paths_count`
- `next_safe_action`
- `display_alert`
- `sos_wake_required`
- `wake_class`

Display boundary:

- no approve/reject/defer controls
- no broker/OANDA controls
- no live order controls
- no webhook controls
- no scheduler controls
- no worker launch controls

## Blocked Live Execution Paths

The Forex Paper Bot lane must block:

- broker integration
- OANDA integration
- live market API calls
- api key use
- `.env` access
- live order creation
- real order creation
- webhook creation or execution
- scheduler creation or mutation
- worker launch
- approval mutation
- production promotion

Any appearance of these paths in a paper lane should stop the work and require a separate Human Owner approval review.

## Future APPLY Phases

Recommended order:

1. `FOREX_FIXTURE_SCHEMA_APPLY`: add local fixture schemas and examples only.
2. `FOREX_SIGNAL_VALIDATOR_DRYRUN`: inspect fixture and signal records without writing telemetry.
3. `FOREX_RISK_GATE_CONTRACT_APPLY`: define deterministic paper risk gate fixtures and validators.
4. `FOREX_PAPER_LEDGER_CONTRACT_APPLY`: define paper ledger schema and report contract.
5. `FOREX_PAPER_RUNNER_DRYRUN`: inspect existing app runner design under a separately approved allowed path; no execution.
6. `FOREX_PI5_DISPLAY_DRYRUN`: map display-only progress fields to existing Pi5 preview; no controls.

Do not create runner/runtime work until the fixture, signal, risk, ledger, report, and validator contracts are reviewed.
