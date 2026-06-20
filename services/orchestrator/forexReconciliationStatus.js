function getForexReconciliationStatus() {
  return {
    schema: "AIOS_FOREX_RECONCILIATION_STATUS.v1",
    reconciliation_status: "PARTIAL",
    broker_read_only_evidence_required: true,
    account_reachability_required: true,
    open_position_reconciliation_required: true,
    daily_pl_required: true,
    realized_pl_required: true,
    unrealized_pl_required: true,
    margin_risk_required: true,
    closed_history_writeback_required: true,
    final_disarm_required: true,
    live_execution_allowed: false,
    next_safe_step: "COLLECT_SANITIZED_READ_ONLY_BROKER_EVIDENCE"
  };
}

module.exports = {
  getForexReconciliationStatus
};
