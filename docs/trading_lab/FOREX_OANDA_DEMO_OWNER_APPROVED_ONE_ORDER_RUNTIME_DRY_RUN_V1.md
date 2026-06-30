# AIOS OANDA Demo Owner-Approved One-Order Runtime Dry-Run V1

## Purpose
This packet validates the final owner-approved OANDA demo one-order dry-run path before any protected demo broker execution packet is drafted.

It answers whether AIOS can consume a sanitized owner runtime transport packet, validate final owner approval, validate approval-token metadata, prove one-order/risk/audit controls, and return a sanitized dry-run receipt without a real OANDA call.

## Relationship to Owner Runtime Transport Packet
This evaluator consumes `AIOS_FOREX_OANDA_DEMO_OWNER_RUNTIME_TRANSPORT_PACKET_V1` output.

Required upstream state:
- `packet_status` is `OWNER_RUNTIME_TRANSPORT_PACKET_READY` or `OWNER_RUNTIME_TRANSPORT_PACKET_READY_WITH_FAKE_PROBE`.
- `ready_for_owner_runtime_transport` is true.
- `next_best_packet` points to this dry-run packet.
- Broker, network, credential, account identifier, bank, money, and live-trading authority fields remain false.

## Relationship to Next Protected Runtime Execution Packet
When all gates pass, this packet routes to:

`AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_ONE_ORDER_PROTECTED_RUNTIME_EXECUTION_V1`

That next packet is still protected. This packet only proves the dry-run receipt path and does not grant broker execution authority.

## Dry-Run Boundary
- Read-only evaluation only.
- Dry-run only.
- Demo-only boundary.
- Owner decision remains required.
- No real order is submitted.
- No demo broker order is submitted.
- No scheduler, daemon, webhook, or dashboard runtime is created.

## No Real OANDA Call
The evaluator does not contact OANDA. It can call an injected fake dry-run transport in tests only. That fake call receives only the sanitized one-order dry-run packet.

## No Direct Broker API Import
The production module does not import broker SDK packages, OANDA SDK packages, direct HTTP packages, process launchers, or runtime launch helpers.

## No Credentials in Repo
Credential values must not be provided, persisted, logged, requested by AIOS, or read from environment variables in this packet.

Runtime credential entry remains owner-managed and runtime-only. Secret scan and redaction requirements must be true.

## No Account IDs in Repo
Account identifier values must not be provided, logged, persisted, or included in the sanitized packet.

The packet may validate `demo_account_reference_present` metadata, but it must not include raw account identifiers.

## No Master Password
`master_password_required` must be false. Master-password values are classified as sensitive input and block evaluation.

## No Vault Password
`vault_password_required` must be false. Vault-password values are classified as sensitive input and block evaluation.

## No Bank Access
`bank_access_allowed` must be false in all input boundaries and output safety objects.

## No Money Movement
`money_movement_allowed`, `real_money_allowed`, `live_trading_allowed`, and `live_execution_allowed` must be false.

## Final Owner Approval Requirements
Final owner approval must prove Anthony accepts:
- one-order dry-run only.
- demo-only boundary.
- no real broker call.
- no credential values in repo.
- no account identifiers in repo.
- no real money.
- no money movement.
- one order only.
- post-dry-run review.
- owner cancellation authority.

Generic yes approval is explicitly blocked.

## Approval Token Metadata Requirements
The approval-token evidence must prove:
- metadata is present.
- token ID metadata is present.
- phrase, action, mode, instrument, units, and risk all match.
- token is unexpired and unused.
- challenge hash and timestamp metadata are present.
- raw approval phrase and voice audio are not retained.

## Runtime Credential Boundary
Credential values must not be supplied, persisted, logged, requested, or read from environment variables in this packet.

Runtime-only credential entry, secret manager use, redaction, and secret scan requirements must be true.

## Demo Account Boundary
The boundary must remain OANDA demo/practice only:
- broker mode is `DEMO`, `PRACTICE`, or `OANDA_DEMO`.
- account environment is `DEMO`, `PRACTICE`, or `OANDA_DEMO`.
- demo account reference metadata is present.
- live account, real money, live execution, money movement, and bank access remain false.

## Sanitized Runtime Transport Packet
The consumed sanitized runtime packet must contain only safe metadata:
- broker/mode/environment.
- instrument, side, order type, units.
- strategy and candidate IDs.
- stop-loss and take-profit presence flags.
- spread, slippage, and risk limits.
- owner cancel, approval-token, runtime credential, demo-only, and one-order flags.

It must exclude credential values, account identifiers, raw approval phrases, voice audio, banking data, card data, passwords, token values, and bearer/private key material.

## One-Order Policy
The policy must prove:
- one order only.
- dry-run only.
- no duplicate order.
- no existing open order or position for the candidate.
- kill switch inactive.
- daily loss stop inactive.
- post-dry-run and post-execution review required.
- next order blocked until review.
- packet order count exactly one.

## Risk Envelope
The risk envelope must require:
- max risk per trade at or below 0.01.
- max daily loss at or below 0.03.
- stop-loss required.
- take-profit required.
- max spread and slippage present.
- one-order only.
- kill switch and daily loss stop inactive.
- duplicate order absent.

## Audit Telemetry
Audit telemetry must require:
- audit record.
- dry-run receipt.
- sanitized packet.
- owner review.
- pre/post dry-run snapshots.
- exception capture.
- secret scan.
- no raw secret, account identifier, approval phrase, or voice-audio logging.

## Fake Dry-Run Transport Path
If no fake transport is requested and all gates pass, the evaluator returns `ONE_ORDER_RUNTIME_DRY_RUN_READY`.

If fake transport is requested and a fake transport object is supplied, it must expose:
- `validate_one_order_runtime_dry_run(packet: dict)`, or
- `run_one_order_runtime_dry_run(packet: dict)`.

The fake transport is called once, receives only the sanitized dry-run packet, and its result is sanitized before output.

## Owner Action Queue
The output action queue includes:
- `REVIEW_OWNER_RUNTIME_TRANSPORT_PACKET`
- `REVIEW_FINAL_OWNER_APPROVAL`
- `REVIEW_APPROVAL_TOKEN_METADATA`
- `REVIEW_RUNTIME_CREDENTIAL_BOUNDARY`
- `REVIEW_DEMO_ACCOUNT_BOUNDARY`
- `REVIEW_SANITIZED_RUNTIME_TRANSPORT_PACKET`
- `REVIEW_ONE_ORDER_POLICY`
- `REVIEW_RISK_ENVELOPE`
- `REVIEW_AUDIT_TELEMETRY`
- `REVIEW_DRY_RUN_TRANSPORT_POLICY`
- `REVIEW_SANITIZED_DRY_RUN_PACKET`
- `REVIEW_FAKE_DRY_RUN_RESULT`
- `REVIEW_NEXT_PACKET`

Every action preserves owner decision required, no live execution, no money movement, no real broker call, and no order submission.

## Blocker Summary
Blockers map to:
- owner runtime transport packet.
- final owner approval.
- approval token.
- runtime credential boundary.
- demo account boundary.
- sanitized runtime packet.
- one-order policy.
- risk envelope.
- audit telemetry.
- dry-run transport contract.
- live/money authority.
- sensitive data.

## Safety Boundary
The safety object hard-codes read-only, dry-run-only, demo-only, owner gate, approval token, one-order, runtime credential, and post-dry-run review requirements.

Broker/API access, real broker calls, network calls, live trading, real money, money movement, bank access, credential/account identifier read or persistence, schedulers, daemons, webhooks, dashboard runtime, and order submission remain false.

## Next Packet
`AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_ONE_ORDER_PROTECTED_RUNTIME_EXECUTION_V1`
