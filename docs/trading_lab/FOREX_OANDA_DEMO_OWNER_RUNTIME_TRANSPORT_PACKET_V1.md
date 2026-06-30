# AIOS OANDA Demo Owner Runtime Transport Packet V1

## Purpose
Create a deterministic evaluator that proves the owner-approved OANDA demo runtime handoff is ready for a one-order dry-run transport packet while preserving a strict offline boundary.

## Relationship to prior work
- This packet consumes the output of `AIOS_FOREX_OANDA_DEMO_BROKER_ADAPTER_RUNTIME_BINDING_V1`.
- It validates the binding is ready for owner runtime transport and converts the result to a sanitized packet for the next dry-run lane.
- It does not perform real broker calls and it does not mutate strategy logic.

## Relationship to next one-order dry-run packet
- If ready, the packet routes to `AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_ONE_ORDER_RUNTIME_DRY_RUN_V1`.
- The next packet handles the one-order-only runtime dry-run execution path under owner approval.

## Owner runtime transport packet boundary
- Read-only design with zero broker calls.
- Owner review is required for movement into the next packet.
- Approval evidence and one-order constraints must be present and valid.
- The output packet must contain only a sanitized transport request and metadata.

## No real OANDA call
- `owner_runtime_transport_packet` evaluation is metadata and summary validation only.
- No transport path performs network or exchange API calls in this packet.

## No direct broker API import
- The module does not import OANDA SDK packages, broker SDK packages, or direct HTTP transport modules.

## No credentials in repo
- Required credential fields must be false (`credential_values_provided`, `credential_values_persisted`, `credential_values_logged`, `credential_values_requested_by_aios`).
- Runtime-only credential entry and secret management are required.
- Credentials are never echoed and are explicitly excluded from the sanitized output packet.

## No account IDs in repo
- Account identifier values must not be provided and account identifiers must not be included in the sanitized output packet.
- Runtime policy must include `account_identifier_values_provided: false`.

## No bank access and no money movement
- `bank_access_allowed`, `live_account_allowed`, `real_money_allowed`, `money_movement_allowed`, and `live_trading_allowed` are required false.
- Packet is blocked when any live/money authority is present.

## Approval token metadata requirements
- `approval_token_required`, `approval_token_metadata_present`, `approval_token_id_present`, and all token match checks must be true.
- Approval phrase and voice fields must not be stored raw.

## Runtime credential boundary
- `owner_runtime_credential_entry_required`, `runtime_only_credentials_required`, `credential_redaction_required`, and `secret_scan_required` must be true.
- Repo secret storage, chat sharing, and environment variable credential reads are blocked by policy.

## Runtime transport policy
- Requires runtime transport handoff with injected transport design.
- Fake probe is allowed and may be requested.
- Fake probe can only execute with callable transport contract methods:
  - `validate_owner_runtime_transport_packet(packet: dict)` or
  - `submit_demo_order(packet: dict)`.
- Real network calls are forbidden, and background services are blocked.

## Demo account boundary
- Demo account mode required (`DEMO`, `PRACTICE`, or `OANDA_DEMO`), demo-only mode required.
- Live account and money movement flags must remain false.
- Demo account reference must be present.

## Sanitized order envelope requirements
- Must include required keys such as broker/mode/environment, side, order type, units, stop/take-profit flags, spread/slippage, risk limits, and candidate identifiers.
- Credential/account identifier flags in the envelope must be false.
- `transport_injected` must be present as boolean.

## One-order policy
- `one_order_only` must be true.
- No duplicate order or open-order/position conflict.
- Kill switch and daily loss stop must be inactive.
- Review is required and subsequent orders are blocked until review.
- `max_order_count_this_packet` must be exactly `1`.

## Audit telemetry
- Audit packet, sanitized packet, owner review, pre/post transport snapshots, exception capture, secret scan, and no raw secret/account-id logging are all required.

## Fake probe test path
- If `fake_transport_probe_requested` is false and input is valid, packet is `OWNER_RUNTIME_TRANSPORT_PACKET_READY`.
- If true and transport object is supplied, the packet calls one fake transport method once, sanitizes the result, and returns `OWNER_RUNTIME_TRANSPORT_PACKET_READY_WITH_FAKE_PROBE`.
- If fake probe contract is missing while requested, packet is blocked.

## Owner action queue
- Includes all review actions required before owner move:
  - `REVIEW_BROKER_ADAPTER_BINDING_RESULT`
  - `REVIEW_OWNER_RUNTIME_APPROVAL`
  - `REVIEW_APPROVAL_TOKEN_METADATA`
  - `REVIEW_RUNTIME_CREDENTIAL_BOUNDARY`
  - `REVIEW_RUNTIME_TRANSPORT_POLICY`
  - `REVIEW_DEMO_ACCOUNT_BOUNDARY`
  - `REVIEW_SANITIZED_ORDER_ENVELOPE`
  - `REVIEW_ONE_ORDER_POLICY`
  - `REVIEW_AUDIT_TELEMETRY`
  - `REVIEW_SANITIZED_RUNTIME_TRANSPORT_PACKET`
  - `REVIEW_FAKE_PROBE_RESULT`
  - `REVIEW_NEXT_PACKET`

## Blocker summary
- Blockers map to binding, owner approval, approval token evidence, credential boundary, transport policy, account boundary, envelope, one-order policy, telemetry, live/money authority, and sensitive data checks.

## Safety boundary
- Read-only transport generation only.
- Broker API access, live trading, live money movement, bank access, schedulers, daemons, webhooks, and dashboard runtime are forbidden.
- No secret or credential value persistence.
- Manual owner approval remains required at each packet transition.

## Next packet
- `AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_ONE_ORDER_RUNTIME_DRY_RUN_V1`
