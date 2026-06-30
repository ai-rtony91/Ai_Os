# Forex Capital Operating Program V2

## Purpose

Deterministic read-only governance for Forex capital actions:

- no live money movement
- no broker/bank API access
- no credential use
- owner-approved review packets only

The module is `automation/forex_engine/capital_operating_program_v2.py` and evaluates whether capital actions should be blocked, reviewed, or ready for later exception review.

## Input sources

- `account_state`
- `bucket_state`
- `compounding_policy`
- `broker_policy_snapshot`
- `rail_registry`
- `transfer_history`
- `open_risk`
- `compliance_evidence`
- `approval_token_evidence`
- `demo_proof`
- `live_exception`
- `owner_approval`
- optional `as_of_date`, `owner_name`

## No banking information required

The program rejects payloads containing sensitive fields such as:

- routing numbers
- account numbers
- card numbers
- cvv
- passwords
- api keys
- tokens/secrets

No payload values are echoed when sensitive keys are detected.

## Sanitized rail metadata only

Rail evidence is treated as metadata only and must be sanitized:

- `rail_label`
- `rail_type`
- `verification_status`
- `rail_allowed_by_policy`
- `rail_owner_verified`
- `no_sensitive_identifiers_present`

## Compounding logic

When requested action is `AUTO`:

- `realized_profit_month <= 0` -> `NO_TRANSFER`, status `NO_CAPITAL_ACTION_RECOMMENDED`
- `realized_profit_month < min_profit_to_compound` -> `NO_TRANSFER`, status `BLOCKED_BY_PROFIT_THRESHOLD`
- `profit_bucket >= min_profit_to_sweep` -> `OWNER_REVIEW_PROFIT_SWEEP`
- otherwise -> `COMPOUND_IN_ACCOUNT`

## Profit bucket logic

Profit bucket gates determine whether to recommend:

- `COMPOUND_IN_ACCOUNT` (auto growth path)
- `OWNER_REVIEW_PROFIT_SWEEP` (take to manual review)

Sweep/review style actions remain read-only and are never auto-executed.

## Bucket purge / rollover / sweep

When:

- `stale_bucket_age_days >= bucket_purge_after_days`

the recommendation can become `OWNER_REVIEW_BUCKET_PURGE` or `OWNER_REVIEW_RESERVE_REALLOCATION` and still requires all normal gates.

## Broker policy snapshot requirements

For transfer-like actions:

- `broker_policy_snapshot` must exist
- `terms_acknowledged_by_owner == true`
- policy source reference present
- jurisdiction present
- if `kyc_required` and `kyc_status != COMPLETE`, block
- if `tax_review_required` and tax review missing, block
- if legal review required and incomplete, block

## Terms / user-agreement evidence requirements

Uses both:

- `broker_policy_snapshot.terms_acknowledged_by_owner`
- `compliance_evidence` booleans for `terms_acknowledged_by_owner`, `jurisdiction_present`, `kyc_status`, `tax_review_complete`, `legal_review_*`

## Transfer cadence logic

Blocks include:

- monthly withdrawal/deposit cap exceeded
- cooldown not satisfied
- transfer period too soon (`last_withdrawal_days_ago`, `last_deposit_days_ago`)

## Rail registry logic

`rail_registry` is reviewed for policy-safe routing:

- allowed/blocked rails
- verification status
- owner verification
- no sensitive identifiers

## Open risk blockers

Blocks all transfer/deposit/withdraw actions if:

- kill switch active
- daily-loss stop active
- drawdown/daily loss thresholds breached
- required no-open-position rule fails
- margin used when disallowed
- pending settlement / unsettled PnL / duplicate order detected

## Drawdown and daily-loss blockers

- `kill_switch_active` -> block
- `daily_loss_stop_active` -> block
- `drawdown_pct > max_drawdown_pct_for_capital_action` -> block
- `daily_loss_pct > max_daily_loss_pct_for_capital_action` -> block

All such blocks return `BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS`.

## Owner approval token gate

For any action other than `NO_TRANSFER`, required:

- owner metadata acceptance fields
- exact approval phrase accepted
- exact amount/balance match
- exact action/mode match
- token unexpired and unused
- owner cancel not detected
- challenge hash and timestamp present

For any action, owner must provide:

- `owner_approval_required == true`
- exact token phrase and metadata match

Generic non-specific approvals (for example “yes”) do not satisfy metadata checks.

## Voice approval rule

`approval_channel == VOICE` is accepted only when all token checks pass. It is not a free-form approval.

## Exact phrase/token/amount/mode/action requirement

`approval_token_evidence` must indicate exact match for:

- phrase
- action
- amount
- mode
- token/channel metadata integrity

## Generic yes rejection

`approval_phrase_present` true and `approval_phrase_matches` false is rejected.

## Owner cancel phrase

`owner_cancel_phrase_detected == true` forces `BLOCKED_BY_APPROVAL_TOKEN`.

## Demo proof before live

`DEMO_PROOF` mode returns:

- `CAPITAL_PROGRAM_READY_FOR_DEMO_PROOF` when all non-live gates and token gates pass
- `BLOCKED_BY_*` otherwise

No live action is authorized.

## Live capital exception review

`LIVE_REVIEW` mode additionally requires:

- `demo_proof.demo_proof_ready == true`
- `live_exception.broker_policy_snapshot_current == true`
- `live_exception.compliance_evidence_complete == true`
- `live_exception.no_open_risk == true`
- `live_exception.owner_live_exception_approval == true`
- approval token gate pass

If satisfied -> `READY_FOR_LIVE_CAPITAL_EXCEPTION_REVIEW`.

## Default failure prompt

Every result includes `default_failure_prompt`.

- Blocked status: includes attempted action, status, failed gates, missing evidence, policy reference, token status, and fixed no-money-movement statement.
- Ready statuses use dedicated owner review / live review prompt wording.

## Legal/compliance boundary

- `legal_advice_provided = false`
- `financial_advice_provided = false`
- legal claim statements are not generated

## No autonomous money movement

Hard-false fields:

- `money_movement_allowed`
- `deposit_allowed`
- `withdrawal_allowed`
- `ach_allowed`
- `wire_allowed`
- `card_transfer_allowed`
- `live_capital_action_authorized`

## No bank/broker API access

Hard-false fields:

- `bank_access_allowed`
- `broker_api_allowed`

## No credentials

Hard-false fields:

- `credential_storage_allowed`
- `credential_read_allowed`

## Owner action queue

`owner_action_queue` always includes:

- `REVIEW_ACCOUNT_STATE`
- `REVIEW_BUCKET_STATE`
- `REVIEW_COMPOUNDING_POLICY`
- `REVIEW_BROKER_POLICY_SNAPSHOT`
- `REVIEW_RAIL_REGISTRY`
- `REVIEW_TRANSFER_CADENCE`
- `REVIEW_OPEN_RISK`
- `REVIEW_COMPLIANCE_EVIDENCE`
- `REVIEW_APPROVAL_TOKEN`
- `REVIEW_DEMO_PROOF`
- `REVIEW_LIVE_EXCEPTION`
- `REVIEW_DEFAULT_FAILURE_PROMPT`
- `REVIEW_NEXT_PACKET`

## Blocker summary

Examples of blockers:

- `sensitive_data_provided`
- `terms_acknowledged_by_owner_false`
- `policy_source_reference_missing`
- `withdrawal_cadence_exhausted`
- `open_positions_block_transfer`
- `pending_settlement`
- `daily_loss_stop_active`
- `drawdown_pct_exceeded`
- owner/token mismatches

## Safety boundary

Output `safety` block always mirrors hard-false/true policy and includes:

- `read_only`
- `legal_advice_provided`
- `financial_advice_provided`
- all money movement/channel flags
- `owner_gate_required`
- `approval_token_required`
- `demo_proof_required_before_live`
- `broker_policy_snapshot_required`
- `fixed_return_target_promised`
- `profit_claim_authorized`

## Next packet

- ready demo proof -> `AIOS_FOREX_DEMO_CAPITAL_CADENCE_PROOF_V1`
- ready owner review -> `AIOS_FOREX_OWNER_REVIEW_CAPITAL_ACTION_PACKET_V1`
- ready live exception -> `AIOS_FOREX_LIVE_CAPITAL_RAIL_EXCEPTION_GATE_V1`
- otherwise -> `AIOS_FOREX_CAPITAL_OPERATING_PROGRAM_V2`
