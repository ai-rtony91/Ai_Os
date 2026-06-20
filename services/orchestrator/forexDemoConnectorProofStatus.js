function getForexDemoConnectorProofStatus() {
  return {
    schema: "AIOS_FOREX_DEMO_CONNECTOR_PROOF_STATUS.v1",
    bullet: "B_PROTECTED_BROKER_DEMO_RUNTIME_CONNECTOR_PROOF",
    status: "PARTIAL",
    proof_mode: "STATUS_ONLY_NO_CONNECTOR_CALL",
    connector_handle_present: false,
    connector_handle_required: true,
    practice_demo_only_required: true,
    sanitized_terminal_result_required: true,
    credentials_allowed: false,
    account_ids_allowed: false,
    endpoint_values_allowed: false,
    raw_broker_payloads_allowed: false,
    market_data_allowed: false,
    order_route_enabled: false,
    close_route_enabled: false,
    retry_loop_enabled: false,
    scheduler_enabled: false,
    daemon_enabled: false,
    live_execution_allowed: false,
    next_safe_step: "SUPPLY_VALUE_FREE_CALLABLE_HANDLE_THEN_RUN_PROTECTED_DEMO_PROOF",
    blocked_reasons: [
      "value_free_callable_handle_missing",
      "sanitized_terminal_demo_result_missing",
      "broker_demo_connector_proof_not_complete"
    ]
  };
}

module.exports = {
  getForexDemoConnectorProofStatus
};
