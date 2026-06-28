{
  "contract_status": "PREPARED",
  "external_authority_required": true,
  "flow_id": "FLOW_3_PROFIT_LOOP_LIVE_WEEK_VACATION_GATE",
  "live_trading_authorized_by_this_contract": false,
  "objective": "classify result, update candidate quality, and prepare promotion gates",
  "outputs": [
    "result_classification",
    "candidate_update",
    "next_candidate",
    "live_week_readiness_status",
    "runtime_readiness_status",
    "vacation_mode_readiness_status"
  ],
  "required_inputs": [
    "Flow 2 evidence bundle",
    "closed trade result",
    "countdown update",
    "candidate score inputs"
  ]
}