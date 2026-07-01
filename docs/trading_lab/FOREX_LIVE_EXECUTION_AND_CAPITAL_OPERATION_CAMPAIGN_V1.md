# Forex Live Execution And Capital Operation Campaign V1

## Campaign Packet Boundary

`AIOS_FOREX_LIVE_EXECUTION_AND_CAPITAL_OPERATION_CAMPAIGN_V1` is a local metadata-evaluation packet for Trading Lab / Forex live-operation readiness. It creates no runtime, scheduler, daemon, webhook, dashboard, broker connector, strategy change, or capital operating runtime.

The evaluator is design and review only. It accepts a caller-provided metadata payload and returns a deterministic readiness envelope.

## Live Execution Campaign Boundary

The campaign checks whether metadata is ready for owner live exception review. It does not approve execution. It does not make broker calls. It does not execute demo or live orders. It does not move money.

The protected one-order gate requires:

- OANDA mode metadata with no account identifier provided.
- runtime credential/session metadata with no credential values.
- exact owner approval-token metadata.
- one-order-only policy metadata.
- risk-limit metadata for stop loss, take profit, spread, slippage, max trade risk, max daily loss, kill switch, and daily loss stop.
- sanitized post-execution review metadata.

## Owner Credential And Session Handling

Credentials remain outside the repo and outside chat. The campaign only evaluates boolean metadata showing that credentials are owner-entered, runtime-only, session-scoped, unexpired, redacted, and not stored or logged.

The packet does not request, read, write, store, or validate actual credentials.

## No API Key In Repo Or Chat

API keys, tokens, bearer strings, broker tokens, private keys, account identifiers, passwords, and bank/card details are blocked as sensitive data. Safe metadata fields such as `no_stored_api_key`, `approval_token_id_present`, and `secret_scan_required` are allowed only as metadata.

## No Master Password

Master-password and vault-password values are blocked. The campaign only accepts metadata proving that no master password and no vault password were provided, stored, read, or used.

## Safe Value Entry

The owner value-entry workflow accepts sanitized metadata only:

- account balance snapshot.
- equity snapshot.
- risk amount.
- max loss amount.
- instrument.
- units.
- pair allocation targets.
- compounding percent.
- sweep percent.
- reserve percent.
- bank or card rail label.

The workflow blocks raw routing numbers, account numbers, account IDs, card numbers, CVV values, passwords, tokens, and credentials.

## Capital Redistribution Planner

The planner produces only non-executing recommendations:

- compound into the same pair.
- redistribute into an allowed pair basket.
- hold profit reserve.
- owner review withdrawal.
- owner review debit-card or bank-transfer label.
- no capital action recommended.
- blocked by broker policy, open risk, cooldown, or drawdown/daily loss.

The planner never authorizes money movement, deposits, withdrawals, ACH, wire, or card transfer. Transfer-like recommendations require owner decision metadata and are blocked by open risk, missing broker policy, cooldown, drawdown, or daily loss.

## Bank And Debit-Card Label-Only Rails

Rail labels such as `OANDA_WITHDRAWAL_RAIL`, `BANK_REVIEW_RAIL`, or `DEBIT_CARD_REVIEW_RAIL` are allowed as labels. Actual bank, card, routing, account, CVV, token, or credential values are blocked.

## SOS Reminders

The SOS reminder packet emits sanitized reminders when:

- approval-token metadata is missing.
- credential session metadata is expired.
- post-execution review metadata is missing.
- daily loss stop is active.
- kill switch is active.
- open risk blocks transfer review.
- broker policy metadata is missing.
- capital redistribution is blocked.
- 22h/6d readiness is incomplete.

Reminders do not contain secret values, account IDs, raw token values, bank numbers, card numbers, or credential material.

## 22h/6d Readiness Index

The readiness index scores ten components at 0 or 10 points:

- broker session readiness.
- monitoring readiness.
- kill-switch readiness.
- post-trade review readiness.
- audit readiness.
- capital planner readiness.
- SOS readiness.
- owner approval readiness.
- credential boundary readiness.
- recovery readiness.

The index passes only at 100 total points with every component at 10.

## Post-Execution Review Loop

Final campaign readiness requires sanitized post-execution review metadata:

- post-trade review required.
- post-trade review completed.
- sanitized execution receipt present.
- PnL review recorded or explicitly not applicable for metadata-only review.
- next order blocked until review.
- owner review required.

## Live Exception Review

`CAMPAIGN_READY_FOR_OWNER_LIVE_EXCEPTION_REVIEW` means the metadata envelope is ready for owner review of the next governed packet. It does not authorize live trading, demo execution, credential entry, broker calls, or capital movement.

## Remaining Path To Protected Execution

The next safe packet is:

`AIOS_FOREX_OWNER_LIVE_EXCEPTION_AND_RUNTIME_SECRET_SESSION_BRIDGE_V1`

That packet must still preserve owner approval, runtime-only credentials, one-order limits, kill-switch checks, daily loss controls, sanitized evidence, and no credential persistence.

## No Broker Call / No Trade / No Money Movement / No Credential Storage Guarantee

This campaign module is pure metadata evaluation. It imports no broker SDK, imports no OANDA module, performs no network call, reads no environment variable, reads no file, stores no credential, creates no runtime, executes no trade, and moves no money.
