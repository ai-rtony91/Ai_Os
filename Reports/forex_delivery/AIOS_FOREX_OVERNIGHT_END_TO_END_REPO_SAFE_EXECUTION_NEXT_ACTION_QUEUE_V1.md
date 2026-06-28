# AIOS Forex Overnight End-to-End Next Action Queue V1

Repo-safe execution continues by dependency order.

- step 1: collect_owner_input -> AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1
- step 2: prepare_flow3_packet -> AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1
- step 3: prepare_live_exception_bridge -> AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1

overnight_contract_status: OVERNIGHT_CONTRACT_BLOCKED_OWNER_INPUT_REQUIRED
overnight_contract_mode: PAUSE_READY
next_required_flow: FLOW_2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE
Flow 2 must complete evidence bridge inputs before Flow 3 candidate checks.
Live exception bridge remains a separate packet with external gates.
