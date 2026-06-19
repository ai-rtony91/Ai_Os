function getForexPaperSandboxStatus() {
  return {
    schema: "AIOS_FOREX_PAPER_SANDBOX_STATUS.v1",
    mode: "PAPER_SANDBOX_STATUS_ONLY",
    paper_preview_ready: true,
    sandbox_demo_connected: false,
    live_execution_allowed: false,
    broker_connected: false,
    order_route_enabled: false,
    close_route_enabled: false,
    auto_trade_enabled: false,
    selected_pair: "EUR_USD placeholder",
    candidate_filter_status: "LOCAL_PREVIEW_ONLY",
    risk_gate_status: "BLOCKED_PENDING_APPROVAL",
    next_safe_step: "WIRE_PAPER_EXECUTION_PREVIEW_NOT_LIVE",
    blocked_reasons: [
      "broker_not_connected",
      "sandbox_demo_not_connected",
      "order_route_disabled",
      "close_route_disabled",
      "live_execution_blocked",
      "human_approval_required_for_live"
    ]
  };
}

module.exports = {
  getForexPaperSandboxStatus
};
