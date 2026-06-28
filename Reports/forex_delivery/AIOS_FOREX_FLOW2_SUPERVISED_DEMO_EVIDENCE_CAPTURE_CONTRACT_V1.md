{
  "contract_status": "PREPARED",
  "external_authority_required": true,
  "flow_id": "FLOW_2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE",
  "objective": "capture supervised demo evidence and update countdown",
  "order_execution_authorized_by_this_contract": false,
  "outputs": [
    "evidence_bundle",
    "countdown_update",
    "duplicate_order_status",
    "runaway_exposure_status",
    "next_flow_handoff"
  ],
  "required_inputs": [
    "Flow 1 output",
    "owner-supervised demo authorization",
    "broker/demo snapshot",
    "trade state evidence",
    "TP/SL state",
    "realized P/L"
  ]
}