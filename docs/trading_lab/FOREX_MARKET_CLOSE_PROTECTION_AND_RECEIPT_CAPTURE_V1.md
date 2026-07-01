# Forex Market Close Protection And Receipt Capture V1

## Purpose

`AIOS_FOREX_MARKET_CLOSE_PROTECTION_AND_RECEIPT_CAPTURE_V1` is a metadata-only close-boundary evaluator for Trading Lab / Forex. It decides whether AIOS should stop new-risk seeking near market close, keep receipts under review, require owner attention, or route clean metadata to post-close maintenance.

This layer protects the system from carrying unresolved receipt evidence, incomplete post-trade review, or late-window new-risk behavior into market close.

## Close Protection Posture

When the runtime calendar reports `CLOSE_PROTECTION`, AIOS shifts out of active new-risk seeking. The close-protection posture keeps these actions blocked:

- opening a new trade by this module.
- executing demo or live trades by this module.
- closing demo or live trades by this module.
- calling a broker by this module.
- reading credentials by this module.
- moving money, withdrawing, routing bank details, or building transfer work.
- creating schedulers, daemons, webhooks, or dashboard runtime.
- mutating strategy logic.
- promising profit or fixed returns.

Calendar metadata never authorizes execution. It only routes work. Any order still requires a separate owner-approved runtime packet.

## Active Supervision Deferral

Active supervision may remain valid upstream, but close protection overrides new trade seeking. This evaluator records active supervision as deferred and routes attention toward:

- no-new-risk review.
- no-new-trade-seeking review.
- open-intent receipt checks.
- receipt capture watch.
- receipt sanitization checks.
- post-trade review checks.
- close-boundary owner summary.
- post-close maintenance preparation.

## Receipt Capture Watch

Receipts are required after execution. The evaluator checks only sanitized metadata:

- outstanding receipts.
- receipts sanitized.
- post-trade review complete.
- receipt capture ready.
- receipt values sanitized.
- no raw broker receipts.
- next trade blocked until receipt review.

If receipts are outstanding, the result routes to receipt review and keeps owner attention required. If receipts are unsanitized or raw broker receipt metadata is present, the result blocks by receipt state.

## Post-Trade Review

Post-trade review must complete before the clean post-close maintenance route is ready. Incomplete post-trade review routes to the burst receipt and post-burst review lane and keeps next trade seeking blocked.

## Owner Attention

Owner attention is required when receipts are unreviewed, post-trade review is incomplete, risk is blocked, or policy metadata is unsafe. Alerts remain metadata-only; this packet creates no alert runtime.

## Risk Gates

Close-boundary risk review requires:

- kill switch inactive.
- daily loss stop inactive.
- drawdown within limit.
- max risk per trade at or below `0.01`.
- max total burst risk at or below `0.03`.
- close-boundary risk review required.

Risk breaches route to risk scale-down review. This packet does not scale capital, execute orders, or close positions.

## Broker And Banking Boundary

Broker calls stay in separate owner-approved runtime packets because close protection is a product-facing metadata layer, not a transport layer. It does not import broker adapters, call OANDA, read credentials, or create execution payloads.

Withdrawal, banking, ACH, wire, card, deposit, transfer, and money-movement work remain deferred. Active banking or withdrawal focus blocks this evaluator with `BLOCKED_BY_BANKING_FOCUS`.

## False-Positive Guard

The banking scan is token-aware. Close-boundary terms such as `close_approaching`, `reopen_approaching`, and `close_boundary` do not match ACH or banking focus merely because of embedded letters.

## Next Safe Packets

- `AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1` for clean post-close maintenance.
- `AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1` for receipt capture, outstanding receipts, or incomplete post-trade review.
- `AIOS_FOREX_RUNTIME_CALENDAR_STATUS_AND_MAINTENANCE_MODE_V1` for calendar repair.
- `AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1` for active-supervision metadata repair.
- `AIOS_FOREX_RISK_SCALE_DOWN_REVIEW_V1` for close-boundary risk blocks.
