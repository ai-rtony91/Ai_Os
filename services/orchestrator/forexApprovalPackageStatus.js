function getForexApprovalPackageStatus() {
  return {
    schema: "AIOS_FOREX_APPROVAL_PACKAGE_STATUS.v1",
    approval_package_status: "NOT_CURRENT",
    human_owner_required: true,
    absolute_timestamp_required: true,
    instrument_required: true,
    side_required: true,
    units_or_notional_required: true,
    max_loss_required: true,
    daily_loss_cap_required: true,
    stop_loss_required: true,
    approval_window_required: true,
    arming_step_required: true,
    stop_point_required: true,
    live_execution_allowed: false,
    next_safe_step: "BUILD_CURRENT_ONE_SHOT_APPROVAL_CARD_AFTER_SANDBOX_PROOF"
  };
}

module.exports = {
  getForexApprovalPackageStatus
};
