# Forex Governed Multi-Pair Burst Vacation Mode V1

## Purpose

This document describes the metadata-only AIOS Forex Vacation Mode upgrade for governed multi-pair burst execution.

The informal "machine-gun effect" is only the visible outcome of frequent, structured activity. The real system is governed burst execution: AIOS scans a declared pair universe, scores candidates, filters weak setups, builds a basket, applies individual and portfolio gates, prepares a governed burst intent, and requires owner/runtime gates before any external execution path.

This packet does not execute trades, call a broker, read credentials, move money, create a scheduler, create a daemon, create a webhook, or create dashboard runtime.

## Governed Burst Model

The governed burst model separates preparation from execution.

AIOS may prepare metadata for:

- `pair_universe`
- `candidate_trade`
- `candidate_batch`
- `multi_pair_basket`
- `portfolio_risk_gate`
- `currency_exposure_gate`
- `correlation_gate`
- `burst_permission`
- `receipt_required`
- `post_burst_review_required`

Actual execution remains outside this packet and requires a separate owner-approved runtime packet.

## Pair Universe

The pair universe is owner-declared. `all_pairs_scan_requested` means scan all declared allowed pairs only. It does not authorize open-ended discovery, broker queries, internet lookup, or runtime scanning.

AIOS blocks when:

- no allowed pairs are declared
- a candidate pair is outside `allowed_pairs`
- a candidate pair is listed in `excluded_pairs`
- `max_pairs_to_scan` is outside the declared universe size

## Opportunity Batch

The opportunity batch stage scores sanitized candidate trades and selects the highest-ranked candidates up to `max_candidates_per_burst`.

Each candidate must carry stop-loss, take-profit, session, news blackout, spread, slippage, score, setup, evidence, and risk metadata. Weak candidates are rejected or blocked before any basket is formed.

## Basket Risk And Exposure

The basket risk governor applies both individual trade gates and portfolio gates.

It blocks on:

- per-trade risk above policy
- total basket risk above policy
- max open-trade or burst-count limits
- currency exposure breach
- correlation breach
- kill switch
- daily loss stop

This is the layer that prevents visible rapid activity from becoming blind rapid-fire execution.

## Owner And Runtime Gates

The permission engine may prepare:

- demo burst runtime intent metadata
- live micro burst owner review metadata
- protected live micro burst runtime intent metadata

It must not execute by itself or call a broker by itself. Live micro burst runtime intent requires proof, owner approval metadata, and a clean runtime boundary with no credential or account values in payload.

## Receipts And Post-Burst Review

After any separately approved runtime path, AIOS requires sanitized receipts and a post-burst review before another burst can be considered.

Receipts must be redacted and count-matched to the governed burst intent. Post-burst review must record PnL, spread/slippage, risk review, owner review requirement, and the next-burst lock.

## No Profit Guarantee

This packet does not guarantee daily, weekly, monthly, or yearly profit. It does not fake PnL, fake receipts, or claim repeatability. Readiness is not profit.

## Banking Freeze

Banking, withdrawal, transfer, card, ACH, wire, sweep, deposit, and money movement work remain frozen. Any banking-focus payload is blocked unless the field is an explicitly false safety field.

## Next Safe Packets

- Demo burst ready: `AIOS_FOREX_OWNER_APPROVED_DEMO_MULTI_PAIR_BURST_RUNTIME_EXECUTION_V1`
- Live micro review ready: `AIOS_FOREX_LIVE_MICRO_MULTI_PAIR_BURST_OWNER_REVIEW_V1`
- Protected live burst runtime intent ready: `AIOS_FOREX_OWNER_APPROVED_PROTECTED_LIVE_MICRO_MULTI_PAIR_BURST_RUNTIME_EXECUTION_V1`
- Waiting receipts: `AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1`
