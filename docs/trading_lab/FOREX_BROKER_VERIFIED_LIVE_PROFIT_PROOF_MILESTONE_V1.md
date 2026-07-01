# Forex Broker-Verified Live Profit Proof Milestone V1

## Final milestone definition

The final Forex milestone is broker-verified live profit proof under owner governance. It is reached only when local readiness gates pass, read-only live broker state is sanitized and consumable, the owner receives a final one-order decision packet, and post-live evidence can prove the result after the owner-governed live micro attempt.

This milestone is not demo completion, paper completion, dashboard truth, or an ATM alert by itself.

## Why this is stronger than ATM Milestone

The ATM Milestone proves a demo-only tipping-bucket and owner SOS contract. Broker-verified live profit proof is stronger because it requires:

- governance and risk gates.
- sanitized read-only broker verification.
- one-order owner decision boundary.
- receipt intake for entry, exit, costs, and realized PnL.
- post-trade review before any repeat attempt.

The ATM Milestone remains useful evidence, but it is not final proof of live profit.

## What local code can prove

Local code can prove that the control plane is bounded, metadata-only, and review-only. It can validate required gate fields, reject sensitive or raw broker data, produce a final owner packet, define the receipt evidence contract, and stop before protected actions.

## What local code cannot prove

Local code cannot prove that a real broker account is reachable, that a live order was filled, that profit was realized, or that the owner collected valid broker receipts. Those facts require external sanitized evidence supplied after owner action.

## Why broker-verified live evidence is required

Demo, paper, and local state can be internally consistent without proving live broker outcome. Broker-verified live evidence is required to prove that the entry, exit, realized PnL, costs, slippage, and post-trade review came from the actual governed live micro attempt.

## Why Codex must not execute trades

Codex is a repo worker. It must not call broker APIs, read credentials, place orders, close orders, route webhooks, create schedulers, or move money. Owner approval and broker action remain outside this packet.

## Read-only broker verification requirements

Read-only broker verification must be sanitized and must include no account IDs, credentials, raw payloads, or private identifiers. Required state includes account reachability, redacted live-account label, reconciled open positions, margin-risk availability, realized and unrealized PnL availability, daily PnL availability, trading history availability, read-only mode true, and execution permission false.

## Single live micro-trade owner action boundary

The final owner packet is one-order-only. It requires stop loss, take profit or exit plan, max risk per trade at or below 0.5 percent, max daily loss at or below 2 percent, no repeat without review, and owner acknowledgement that loss is possible and profit is not guaranteed.

## Receipt intake contract

The receipt contract requires sanitized entry and exit receipts, instrument, side, redacted size, entry and exit prices, stop loss, take profit or exit plan, realized PnL, PnL currency, spread cost, fee cost, slippage, net PnL after costs, and private-data absence checks.

## Post-trade review requirements

Post-trade review must classify whether the rule was followed, whether a mistake occurred, whether costs were recorded, and whether the attempt can be reviewed without private data.

## Repeat attempt gate

Repeat attempts remain blocked until review. A winning result does not authorize another live attempt. A losing result also stops for review.

## Profit proof definition

Profit proof means sanitized broker receipt evidence shows realized net PnL after costs for the one governed live micro attempt, with no private identifiers and with post-trade review complete.

## Safety boundary

This milestone is metadata-only and review-only. It does not authorize broker calls, credential reads, account ID storage, live execution, money movement, banking, withdrawal, schedulers, daemons, webhooks, or profit promises.

## Remaining owner actions

The owner must supply sanitized read-only broker verification, review the final one-order packet, make any live action outside Codex if approved, collect sanitized post-live receipt evidence, and stop for review before any repeat.

## Final statuses

- `READY_FOR_OWNER_GOVERNED_LIVE_MICRO_TRADE_ACTION`
- `READY_FOR_READ_ONLY_LIVE_BROKER_VERIFICATION`
- `BLOCKED_BY_GOVERNANCE`
- `BLOCKED_BY_RISK`
- `BLOCKED_BY_MARKET_STATE`
- `BLOCKED_BY_BROKER_READ_ONLY_STATE`
- `BLOCKED_BY_PROOF_STATE`
- `BLOCKED_BY_ATM_MILESTONE_STATE`
- `BLOCKED_BY_OWNER_STATE`
- `BLOCKED_BY_SAFETY_POLICY`
- `BLOCKED_BY_LIVE_EXECUTION_BOUNDARY`
- `INCOMPLETE_INPUTS`
