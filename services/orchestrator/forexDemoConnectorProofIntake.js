const REQUIRED_DEMO_CONNECTOR_PROOF_FIELDS = {
  proof_scope: "PRACTICE_DEMO_ONLY",
  connector_handle_type: "VALUE_FREE_CALLABLE",
  sanitized_terminal_result_present: true,
  credentials_present: false,
  account_ids_present: false,
  endpoint_values_present: false,
  raw_broker_payload_present: false,
  market_data_present: false,
  order_route_present: false,
  close_route_present: false,
  retry_loop_present: false,
  scheduler_present: false,
  daemon_present: false,
  live_execution_present: false
};

function isPlainObject(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function requirementText(value) {
  return String(value).toLowerCase();
}

function evaluateForexDemoConnectorProofEvidence(evidence) {
  const evidenceObject = isPlainObject(evidence) ? evidence : {};
  const blockedReasons = [];
  const missingFields = [];

  if (!isPlainObject(evidence)) {
    blockedReasons.push("evidence_must_be_plain_object");
  }

  const supportedFields = new Set(Object.keys(REQUIRED_DEMO_CONNECTOR_PROOF_FIELDS));
  const unsupportedFieldsPresent = Object.keys(evidenceObject).some((field) => !supportedFields.has(field));
  if (unsupportedFieldsPresent) {
    blockedReasons.push("unsupported_fields_present");
  }

  for (const [field, requiredValue] of Object.entries(REQUIRED_DEMO_CONNECTOR_PROOF_FIELDS)) {
    if (!Object.prototype.hasOwnProperty.call(evidenceObject, field)) {
      missingFields.push(field);
      blockedReasons.push(`${field}_missing`);
      continue;
    }

    if (evidenceObject[field] !== requiredValue) {
      blockedReasons.push(`${field}_must_be_${requirementText(requiredValue)}`);
    }
  }

  const canCloseBulletB = missingFields.length === 0 && blockedReasons.length === 0;

  return {
    schema: "AIOS_FOREX_DEMO_CONNECTOR_PROOF_INTAKE.v1",
    bullet: "B_PROTECTED_BROKER_DEMO_RUNTIME_CONNECTOR_PROOF",
    intake_status: canCloseBulletB ? "APPROVED" : "BLOCKED",
    can_close_bullet_b: canCloseBulletB,
    live_execution_allowed: false,
    broker_call_sent: false,
    order_sent: false,
    trade_placed: false,
    blocked_reasons: blockedReasons,
    missing_fields: missingFields,
    next_safe_step: canCloseBulletB
      ? "HUMAN_REVIEW_SANITIZED_DEMO_CONNECTOR_PROOF"
      : "PROVIDE_SANITIZED_TERMINAL_DEMO_PROOF"
  };
}

function getForexDemoConnectorProofIntakeSample() {
  return {
    ...evaluateForexDemoConnectorProofEvidence({}),
    sample_only: true
  };
}

module.exports = {
  evaluateForexDemoConnectorProofEvidence,
  getForexDemoConnectorProofIntakeSample
};
