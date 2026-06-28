# FLOW-FOREX-001 Active Execution Authority Runtime SOS Profit Countdown V2

## Flow Identity
FLOW-FOREX-001 Active Execution Authority Runtime SOS Profit Countdown V2

## Purpose
Build a repo-local Flow 1 active authority control surface that converts bridge output into controlled Flow 2 readiness with dynamic baseline handling, capacity engine checks, countdown governance, and bridge handoff gates.

## Current Verified Anchor
continuous bridge controller packet is merged on main from PR #1193.

## Owner Live-Capital Intent
owner_live_capital_intent_usd is 1000.

## Baseline Equity Rule
baseline equity must be operator input or broker/demo snapshot derived. hardcoded_10000_baseline_forbidden is true.

## Target Return Band
target_return_band is 100_TO_120_PERCENT.

## Position Capacity Engine
Position capacity is computed from requested max positions, dynamic risk budget, margin budget, and open-slot availability.

## Requested Max Open Positions
requested max open positions default to 4.

## Requested 4X Quantity Scale
requested quantity scale default is 4.0.

## Profit-Return Countdown
Countdown uses dynamic baseline equity with target equity at 100 percent and 120 percent.

## Runtime Objective
Target runtime objective is 22_HOURS_PER_DAY_6_DAYS_PER_WEEK.

## Vacation Mode Target
Vacation target status is required until Flow 2 evidence capture receives evidence.

## SOS Alert Contract
SOS escalation gate must pass with acknowledged milestone and warning rules before continue.

## Risk Control Gate
Risk controls and drawdown thresholds must be acknowledged and within defined limits.

## Idempotency And No-Duplicate-Order Gate
Idempotency and no duplicate order controls must be acknowledged before continue.

## Stale-Price Guard
Stale-price guard must be acknowledged before continue.

## Kill-Switch Gate
Kill-switch state must be false.

## Flow 2 Handoff
Flow 2 handoff requires readiness status, evidence requirements, and blocked external gates.

## Blocked External Actions
- broker API access
- credentials
- demo order placement
- live trading
- execution command
- autonomous trading
- money movement

## What This Completes
Flow 1 active authority now controls dynamic capacity, return countdown, SOS alerts, and evidence handoff readiness.

## What This Does Not Approve
Live trading, broker API access, credentials, order submission, autonomous operation, and money movement remain blocked.

## Final Owner Sentence
AIOS Forex Flow 1 active execution authority runtime SOS profit countdown gate is prepared locally: the owner live-capital intent remains $1,000, requested max open positions is 4 with 4X target scaling bounded by risk and margin capacity, the target return band remains 100–120% tracked from dynamic baseline equity, Flow 2 supervised demo evidence capture is the next governed flow when validated owner input passes, and live trading, broker/API access, credentials, order submission, execution command, 22h6d runtime, vacation mode, autonomy, and money movement remain blocked until separately proven and approved.
