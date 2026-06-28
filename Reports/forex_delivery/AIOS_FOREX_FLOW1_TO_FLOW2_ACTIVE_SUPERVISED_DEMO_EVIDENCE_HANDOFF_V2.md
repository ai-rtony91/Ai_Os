# AIOS Forex Flow 1 to Flow 2 Active Supervised Demo Evidence Handoff V2

## Flow 1 Status
FLOW1_BLOCKED_OWNER_INPUT_REQUIRED

## Next Required Flow
FLOW_1_ACTIVE_EXECUTION_AUTHORITY_RUNTIME_SOS_PROFIT_COUNTDOWN

## Owner Live-Capital Intent
1000

## Baseline Equity Rule
baseline_equity_source: OWNER_INPUT_OR_BROKER_DEMO_OR_LIVE_SNAPSHOT
baseline_equity: 0.0
hardcoded_10000_baseline_forbidden: true

## Requested Max Open Positions
4

## Final Position Capacity
0

## 4X Target Scale Status
4.0

## Target Return Countdown Status
BASELINE_EQUITY_REQUIRED

## SOS Alert Requirement
REQUIRED_GATE_PENDING

## Runtime Objective Status
GATED_PENDING_SUPERVISED_EVIDENCE

## Evidence Capture Requirements for Flow 2
- broker snapshot capture
- TP/SL capture
- realized P/L capture
- no duplicate order requirement
- no runaway exposure requirement
- post-trade countdown update

## Broker Snapshot Requirement
Capture broker/demo-only snapshot before entry.

## TP/SL Capture Requirement
Capture TP/SL data for each managed position.

## Realized P/L Capture Requirement
Capture realized P/L for close events.

## No Duplicate Order Requirement
Maintain no-duplicate-order control while Flow 2 captures evidence.

## No Runaway Exposure Requirement
Maintain capped aggregate open risk and notional exposure while evidence is collected.

## Post-Trade Countdown Update Requirement
Update return countdown after each close-trade input.

## Blocked Actions
- order_submission_authorized
- broker_connection_authorized
- money_movement_authorized
- autonomous_trading_authorized
- runtime_22h6d_activated
- vacation_mode_activated

## Final Owner Sentence
AIOS Forex Flow 1 active execution authority runtime SOS profit countdown gate is prepared locally: the owner live-capital intent remains $1,000, requested max open positions is 4 with 4X target scaling bounded by risk and margin capacity, the target return band remains 100–120% tracked from dynamic baseline equity, Flow 2 supervised demo evidence capture is the next governed flow when validated owner input passes, and live trading, broker/API access, credentials, order submission, execution command, 22h6d runtime, vacation mode, autonomy, and money movement remain blocked until separately proven and approved.
