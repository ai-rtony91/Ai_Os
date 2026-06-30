# Forex Demo Capital Cadence Proof V1

## Purpose
This packet validates the deterministic behavior of `evaluate_capital_operating_program_v2` in demo-only mode across a curated scenario set before any live-capital action path is considered.

## Relationship to Capital Operating Program V2
The proof harness calls `run_demo_capital_cadence_proof_v1` which executes scenario payloads through `evaluate_capital_operating_program_v2`.
It does **not** execute broker calls or transfer funds. It only evaluates policy and safety logic.

## Demo-Only Proof Boundary
The harness is read-only:
- `read_only = True`
- `demo_only = True`
- `live_capital_action_authorized = False`
- no money transfer or bank/broker movement is requested or performed.

## No Banking Info / No Credentials
The scenario fixtures use only synthetic policy metadata:
- `broker_name = DEMO_POLICY_BROKER`
- `policy_source_reference = DEMO_POLICY_FIXTURE`
- no account numbers, routing numbers, cards, secrets, tokens, or API keys.

Boundary fields such as `bank_access_allowed` and `broker_api_allowed` are accepted as safety evidence but are not treated as secrets.

## Synthetic Policy Fixture
All proof runs use a sanitized fixture snapshot in baseline payloads:
- broker fixture values
- non-sensitive compounding/bucket history
- non-sensitive compliance and approval placeholders

## Scenario Matrix
- 21 built-in scenarios are executed by default.
- Required IDs include:
  - `COMPOUND_ELIGIBLE`
  - `PROFIT_SWEEP_ELIGIBLE`
  - `DEPOSIT_TOP_UP_OWNER_REVIEW`
  - `BUCKET_PURGE_ELIGIBLE`
  - `BELOW_THRESHOLD_NO_TRANSFER`
  - `WITHDRAWAL_CADENCE_EXHAUSTED`
  - `DEPOSIT_CADENCE_EXHAUSTED`
  - `WITHDRAWAL_COOLDOWN_BLOCKED`
  - `DEPOSIT_COOLDOWN_BLOCKED`
  - `OPEN_POSITION_BLOCKED`
  - `MARGIN_USED_BLOCKED`
  - `PENDING_SETTLEMENT_BLOCKED`
  - `DRAWDOWN_BLOCKED`
  - `DAILY_LOSS_STOP_BLOCKED`
  - `KILL_SWITCH_BLOCKED`
  - `BROKER_POLICY_MISSING_BLOCKED`
  - `TERMS_NOT_ACKNOWLEDGED_BLOCKED`
  - `APPROVAL_TOKEN_MISMATCH_BLOCKED`
  - `GENERIC_VOICE_YES_BLOCKED`
  - `EXACT_VOICE_TOKEN_ACCEPTED`
  - `LIVE_REVIEW_WITHOUT_DEMO_PROOF_BLOCKED`
  - `LIVE_REVIEW_WITH_DEMO_PROOF_READY_FOR_EXCEPTION`

## Expected Status / Action Matrix
Each required scenario maps to a deterministic expected recommendation:
- Compounding eligible -> `CAPITAL_ACTION_READY_FOR_OWNER_REVIEW` / `COMPOUND_IN_ACCOUNT`
- Profit sweep eligible -> `CAPITAL_ACTION_READY_FOR_OWNER_REVIEW` / `OWNER_REVIEW_PROFIT_SWEEP`
- Deposit/top-up owner review -> `CAPITAL_ACTION_READY_FOR_OWNER_REVIEW` / `OWNER_REVIEW_DEPOSIT_TOP_UP`
- Bucket purge eligible -> `CAPITAL_ACTION_READY_FOR_OWNER_REVIEW` / `OWNER_REVIEW_BUCKET_PURGE`
- Threshold below -> `BLOCKED_BY_PROFIT_THRESHOLD` / `NO_TRANSFER`
- Cadence/ cooldown blocks -> `BLOCKED_BY_TRANSFER_CADENCE` / owner review action
- Open risk blocks -> `BLOCKED_BY_OPEN_RISK` / owner review action
- Drawdown / daily loss blocks -> `BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS` / owner review action
- Broker/compliance blocks -> `BLOCKED_BY_MISSING_POLICY_SNAPSHOT` / `BLOCKED_BY_COMPLIANCE_EVIDENCE`
- Approval failures -> `BLOCKED_BY_APPROVAL_TOKEN`
- Live review without proof -> `BLOCKED_BY_DEMO_PROOF`
- Live review with proof and exception gates -> `READY_FOR_LIVE_CAPITAL_EXCEPTION_REVIEW`

## Compounding Proof
`COMPOUND_ELIGIBLE` confirms that positive realized profit below sweep threshold recommends compounding in account.

## Sweep Proof
`PROFIT_SWEEP_ELIGIBLE` confirms profit-bucket threshold behavior and owner review recommendation.

## Deposit/Top-Up Proof
`DEPOSIT_TOP_UP_OWNER_REVIEW` confirms top-up route remains owner-review gated.

## Bucket Purge Proof
`BUCKET_PURGE_ELIGIBLE` confirms stale bucket logic requests bucket purge review when purge age exceeds policy.

## Blocked Cadence Proof
Withdrawal and deposit cadence / cooldown scenarios are explicitly expected to fail with `BLOCKED_BY_TRANSFER_CADENCE`.

## Blocked Open-Risk Proof
Open-position, margin-used, and pending-settlement scenarios confirm `BLOCKED_BY_OPEN_RISK`.

## Blocked Drawdown / Daily-Loss Proof
Drawdown exceedance, daily-loss stop, and kill-switch scenarios confirm `BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS`.

## Approval Token Proof
`APPROVAL_TOKEN_MISMATCH_BLOCKED` and `GENERIC_VOICE_YES_BLOCKED` scenarios require strict token metadata checks.

## Voice Approval Proof
The harness expects exact token metadata:
- channel/type fields
- phrase/action/amount/ balance matches
- hash and timestamp presence
- no cancel phrase

`GENERIC_VOICE_YES_BLOCKED` remains rejected.
`EXACT_VOICE_TOKEN_ACCEPTED` remains owner-review eligible only.

## Live Exception Probe
Two scenarios validate:
- live review while demo proof missing is blocked
- live review with all exception gates satisfied can produce `READY_FOR_LIVE_CAPITAL_EXCEPTION_REVIEW`

`live_capital_action_authorized` is still false in both cases.

## Safety Hard-False Checks
The packet asserts and returns hard-false settings:
- `money_movement_allowed = False`
- `bank_access_allowed = False`
- `broker_api_allowed = False`
- `credential_storage_allowed = False`
- `credential_read_allowed = False`
- `live_capital_action_authorized = False`

Scenario safety snapshots include the same hard-false values.

## Next Packet
If all required scenario checks pass, next packet is:
- `AIOS_FOREX_OANDA_DEMO_BROKER_ADAPTER_RUNTIME_BINDING_V1`
If proof fails, next packet remains:
- `AIOS_FOREX_DEMO_CAPITAL_CADENCE_PROOF_V1`

## No Banking / Broker API / Credentials
This proof packet itself does not perform live movement, broker calls, or credential IO.

## No Legal Advice
This packet only emits operating status and evidence summaries and contains no legal or financial advice.
