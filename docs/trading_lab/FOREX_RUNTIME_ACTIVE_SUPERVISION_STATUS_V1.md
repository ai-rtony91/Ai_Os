# Forex Runtime Active Supervision Status V1

## Purpose

This packet defines a metadata-only active supervision status layer for Trading Lab / Forex.

It answers what AIOS should watch when the Forex market is open, Vacation Mode is ON or RESUME, runtime calendar posture is active supervision, risk is clean, receipts are clean, balance and equity memory is ready, and execution remains gated behind a later owner-approved runtime packet.

It does not execute trades.
It does not call a broker.
It does not read credentials.
It does not move money.
It does not create a scheduler, daemon, webhook, dashboard runtime, banking lane, or withdrawal lane.

## Market-Open Posture

Active supervision requires runtime calendar metadata showing:

- `current_runtime_posture` is `ACTIVE_SUPERVISION`
- `trade_window_open` is `true`
- `primary_job_lane` is `supervise_runtime`
- `runtime_job_router_enabled` is `true`
- `execution_authorized_by_calendar` is `false`

The calendar can confirm a market window and route workload, but it cannot authorize trade execution.

## Vacation Mode Requirement

Vacation Mode must be ON or RESUME.

Allowed active supervision operation states are:

- `VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE`
- `VACATION_MODE_ON_EVALUATING_GATES`

Vacation Mode OFF or PAUSE routes to maintenance fallback. It does not create a trade lane.

## Kill Switch And Risk Gates

The evaluator watches:

- kill switch state
- daily loss stop state
- drawdown state
- current and maximum drawdown
- current and maximum daily loss
- maximum risk per trade
- maximum total burst risk
- owner-reviewed risk policy state

Kill switch active, daily loss stop active, drawdown breach, or risk policy values above packet thresholds block active supervision readiness.

## Receipt Watch

The evaluator watches whether receipts are required, outstanding, sanitized, and reviewed.

Outstanding receipts route to receipt review. Unsanitized receipts or incomplete post-trade review block active supervision readiness.

## Balance And Equity Watch

The evaluator watches balance memory, equity memory, current balance presence, current equity presence, and compounding observer readiness.

Missing balance memory or observer readiness routes to balance review. Money movement remains blocked.

## Compounding Watch

The evaluator watches the governed compounding state, scale decision, scale direction, proposed next risk budget, and owner decision requirement.

Compounding readiness gaps route to the governed compounding review packet. Withdrawal and bank routing remain false.

## Profit Protection Watch

The evaluator watches profit protection readiness, realized-profit-only policy, future withdrawal-review metadata, and hard blocks against withdrawal execution, bank routing, and money movement.

Profit protection gaps route to the profit protection review packet. Future withdrawal review remains metadata only.

## Candidate Metadata Refresh

Candidate metadata refresh may be prepared only when candidate policy allows metadata refresh and blocks:

- strategy mutation
- broker calls
- live market data calls

Candidate policy must require stop loss, take profit, spread policy, slippage policy, news blackout policy, and a later owner runtime packet before execution.

## Proof Continuity

The evaluator watches proof readiness, proof continuity, fake proof blocking, repeatability review readiness, and owner review requirements for live review.

Proof required but not ready, or proof continuity missing, routes to proof pause and continue.

## Owner Alert Readiness

The output includes an owner alert summary and owner review queue.

The review queue always includes `runtime_execution_packet_required_for_any_order` because this layer cannot create an order or approve execution.

## Blocked Actions

The blocked action queue always includes:

- demo execution by this module
- live execution by this module
- broker call by this module
- credential read by this module
- money movement by this module
- withdrawal by this module
- bank routing by this module
- scheduler creation by this module
- daemon creation by this module
- strategy mutation by this module
- profit promise by this module

## Why Active Supervision Does Not Execute Trades

Active supervision is a product-facing status layer. It watches readiness, blockers, and next packet routing.

Trade execution requires a separate owner-approved runtime packet with its own permission, risk, receipt, and broker boundary checks.

## Why Calendar Does Not Authorize Execution

The runtime calendar can say whether the market window is open and what work lane is appropriate.

It must keep `execution_authorized_by_calendar` false. Calendar state alone never authorizes orders.

## Why Broker Calls Stay Separate

Broker calls belong in a later owner-approved runtime packet.

This layer does not import broker SDKs, does not call transport, does not read credentials, and does not create execution payloads.

## Why Withdrawal And Banking Remain Deferred

Profit protection may identify future review metadata, but withdrawal, banking, routing, ACH, wire, card, deposit, transfer, and money movement stay frozen.

Explicit false banking fields are accepted. Active banking or withdrawal focus blocks.

## Next Safe Packets

- ready active supervision: `AIOS_FOREX_OWNER_APPROVED_DEMO_MULTI_PAIR_BURST_RUNTIME_EXECUTION_V1`
- metadata scan only: `AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1`
- owner review: `AIOS_FOREX_LIVE_MICRO_MULTI_PAIR_BURST_OWNER_REVIEW_V1`
- maintenance fallback: `AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1`
- proof waiting: `AIOS_FOREX_PROOF_PIPELINE_PAUSE_AND_CONTINUE_V1`
- receipt waiting: `AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1`
- balance review: `AIOS_FOREX_BALANCE_EQUITY_MEMORY_AND_COMPOUNDING_OBSERVER_V1`
- compounding review: `AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1`
- profit protection review: `AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1`
