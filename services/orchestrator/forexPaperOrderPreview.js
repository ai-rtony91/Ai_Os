function getForexPaperOrderPreview() {
  return {
    schema: "AIOS_FOREX_PAPER_ORDER_PREVIEW.v1",
    mode: "PAPER_PREVIEW_ONLY",
    preview_status: "READY",
    selected_pair: "EUR_USD",
    side: "BUY",
    units: 1,
    order_type: "MARKET_PREVIEW_ONLY",
    stop_loss_required: true,
    take_profit_required: false,
    max_loss_required: true,
    order_route_enabled: false,
    broker_connected: false,
    live_execution_allowed: false,
    order_sent: false,
    trade_placed: false,
    next_safe_step: "WIRE_PAPER_EXECUTION_SIMULATOR_NOT_BROKER",
    blocked_reasons: [
      "preview_only_no_order_sent",
      "broker_not_connected",
      "order_route_disabled",
      "live_execution_blocked"
    ]
  };
}

module.exports = {
  getForexPaperOrderPreview
};
