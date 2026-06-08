const assert = require("node:assert/strict");
const test = require("node:test");

const {
  getBridgeHealth,
  getLatestReports,
  getQueuePreview,
  getWorkersPreview,
  previewApproval,
  previewSos,
  validatePacketDraft
} = require("../../services/orchestrator/appServiceBridge");

test("bridge health advertises local preview-only safety boundary", () => {
  const health = getBridgeHealth();

  assert.equal(health.ok, true);
  assert.equal(health.mode, "LOCAL_DRY_RUN_PREVIEW_ONLY");
  assert.equal(health.providerCallsEnabled, false);
  assert.equal(health.approvalMutationEnabled, false);
  assert.equal(health.workerMutationEnabled, false);
  assert.equal(health.queuedCommandExecutionEnabled, false);
  assert.equal(health.cloudDeploymentEnabled, false);
  assert.equal(health.tunnelEnabled, false);
});

test("packet intake is preview-only and blocks risky text", () => {
  const result = validatePacketDraft({
    packet_id: "PKT-RISKY",
    packet_text: "CODEX-ONLY PROMPT\nAI_OS EXECUTION TOKEN\nMISSION\nOpenAI API call and create .env"
  });

  assert.equal(result.acceptedForExecution, false);
  assert.equal(result.providerCallPerformed, false);
  assert.equal(result.codexLaunched, false);
  assert.equal(result.queueMutated, false);
  assert.equal(result.approvalMutated, false);
  assert.equal(result.status, "BLOCKED");
  assert.ok(result.blockedReasons.includes("secret_request"));
  assert.ok(result.blockedReasons.includes("provider_call"));
});

test("queue, worker, approval, reports, and sos routes do not mutate state", () => {
  const queue = getQueuePreview();
  const workers = getWorkersPreview();
  const approval = previewApproval({ requested_action: "APPLY" });
  const reports = getLatestReports();
  const sos = previewSos({ severity: "SOS", message: "preview only" });

  assert.equal(queue.mode, "READ_ONLY");
  assert.equal(queue.mutationEnabled, false);
  assert.equal(queue.queuedCommandExecutionEnabled, false);
  assert.equal(workers.mode, "READ_ONLY");
  assert.equal(workers.mutationEnabled, false);
  assert.equal(workers.codexLaunchEnabled, false);
  assert.equal(approval.mode, "PREVIEW_ONLY");
  assert.equal(approval.approvalRecorded, false);
  assert.equal(approval.approvalInboxMutated, false);
  assert.equal(approval.applyGateMutated, false);
  assert.equal(reports.mode, "READ_ONLY");
  assert.equal(sos.mode, "PREVIEW_ONLY");
  assert.equal(sos.notificationSent, false);
  assert.equal(sos.telemetryWritten, false);
});
