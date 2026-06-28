# AIOS Forex Overnight End-to-End Repo-Safe Execution Contract V1

Flow 1 PR #1194 is the current anchor.

overnight_contract_status: OVERNIGHT_CONTRACT_BLOCKED_OWNER_INPUT_REQUIRED
overnight_contract_mode: PAUSE_READY
anchor_status: FLOW1_PR_1194_MERGED
target_return_band: 100_TO_120_PERCENT
runtime_objective: 22_HOURS_PER_DAY_6_DAYS_PER_WEEK
runtime_objective is a target and not active state.
vacation_mode_status: TARGET_DEFINED_GATE_PENDING
sos_alert_contract_status: REQUIRED_GATE_PENDING

Dependency order:
- FLOW_2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE
- FLOW_3_PROFIT_LOOP_LIVE_WEEK_VACATION_GATE
- LIVE_EXCEPTION_AND_REAL_MONEY_GATE
- RUNTIME_SUPERVISOR_AND_SOS_GATE

flow2_contract_status: PREPARED
flow3_contract_status: PREPARED
live_exception_contract_status: PREPARED_NOT_AUTHORIZED

next_required_flow: FLOW_2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE
next_required_packet: AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1

This packet builds Flow 2 evidence capture scope, Flow 3 profit loop scope, and live-exception bridge scope in a repo-safe way.
Live action and live money movement remain gated by external bridges.
Flow 2 captures evidence. Flow 3 updates candidate gates. Live exception remains separate.
Real-money trading is not authorized by this packet.
100–120% is target band, not verified proof.
22h/6d is runtime objective, not active state.
vacation mode is target state, not active state.

overnight_contract_sentence: AIOS Forex overnight end-to-end repo-safe execution contract is established locally: Flow 1 PR #1194 is the anchor, Flow 2 supervised demo evidence capture, Flow 3 profit loop gating, live exception bridging, real-money readiness bridging, 100–120% target tracking, requested 4-position capacity, 22h/6d runtime objective, vacation-mode target, and SOS escalation are dependency-ordered for continuation while broker/API access, credentials, order submission, live trading, autonomous operation, and money movement remain separately gated.
