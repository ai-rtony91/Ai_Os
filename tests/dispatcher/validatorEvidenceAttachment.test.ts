import assert from "node:assert/strict";
import test from "node:test";
import type {
  AssignmentPreviewPersistenceRecord
} from "../../services/dispatcher/assignmentPreviewPersistence.ts";
import {
  buildValidatorEvidenceAttachmentRecord,
  serializeValidatorEvidenceAttachmentRecord,
  validateValidatorEvidenceAttachmentRecord,
  type ValidatorEvidenceAttachmentRecord,
  type ValidatorEvidenceResult
} from "../../services/dispatcher/validatorEvidenceAttachment.ts";

function assignmentPreviewRecord(): AssignmentPreviewPersistenceRecord {
  return {
    schema: "AIOS_ASSIGNMENT_PREVIEW_PERSISTENCE.v1",
    generated_at: "2026-05-29T00:00:00.000Z",
    source: {
      resolver_schema: "AIOS_WORKER_RESOLVER_PREVIEW.v1",
      resolver_generated_at: "2026-05-29T00:00:00.000Z",
      preview_only: true
    },
    persistence_mode: "preview_record_only",
    preview_only: true,
    assignments: [
      {
        packet_id: "PKT-PASS",
        recommended_worker_id: "dispatcher_worker",
        recommended_worker_name: "Dispatcher Worker",
        match_score: 29,
        risk_allowed: true,
        status_allowed: true,
        lane_match: true,
        matched_capabilities: ["dispatcher"],
        missing_capabilities: [],
        reason: "matched",
        preview_only: true,
        persistence_status: "recorded_preview"
      }
    ],
    unmatched_actions: [
      {
        packet_id: "PKT-UNMATCHED",
        required_capabilities: ["docs"],
        risk_level: "high",
        reason: "unmatched",
        preview_only: true
      }
    ],
    summary: {
      total_assignments: 1,
      total_unmatched: 1,
      total_preview_items: 2,
      dispatch_authorized: false,
      inbox_mutation_authorized: false,
      runtime_mutation_authorized: false,
      human_approval_required: true
    },
    warnings: [],
    human_required_next_step: "Human approval required."
  };
}

function validatorResult(
  packetId: string,
  overrides: Partial<ValidatorEvidenceResult> = {}
): ValidatorEvidenceResult {
  return {
    validator_id: `validator-${packetId}`,
    validator_name: "Dispatcher Validator",
    packet_id: packetId,
    status: "passed",
    severity: "low",
    evidence_ref: `tests/${packetId}.txt`,
    message: "passed",
    ran_at: "2026-05-29T00:00:00.000Z",
    blocking: false,
    ...overrides
  };
}

test("builds validator evidence attachment record from assignment preview record and validator results", () => {
  const record = buildValidatorEvidenceAttachmentRecord({
    assignmentPreviewRecord: assignmentPreviewRecord(),
    validatorResults: [validatorResult("PKT-PASS")],
    now: new Date("2026-05-29T01:00:00.000Z")
  });

  assert.equal(record.schema, "AIOS_VALIDATOR_EVIDENCE_ATTACHMENT.v1");
  assert.equal(record.attachment_mode, "preview_evidence_record_only");
  assert.equal(record.generated_at, "2026-05-29T01:00:00.000Z");
  assert.equal(record.assignment_reference.schema, "AIOS_ASSIGNMENT_PREVIEW_PERSISTENCE.v1");
});

test("groups validator results by packet id", () => {
  const record = buildValidatorEvidenceAttachmentRecord({
    assignmentPreviewRecord: assignmentPreviewRecord(),
    validatorResults: [
      validatorResult("PKT-PASS"),
      validatorResult("PKT-PASS", { validator_id: "validator-two" })
    ]
  });

  const packetEvidence = record.packet_evidence.find(
    (item) => item.packet_id === "PKT-PASS"
  );

  assert.equal(packetEvidence?.validator_result_count, 2);
  assert.equal(packetEvidence?.passed_count, 2);
});

test("marks approval_ready true only for non-blocking passed evidence", () => {
  const record = buildValidatorEvidenceAttachmentRecord({
    assignmentPreviewRecord: assignmentPreviewRecord(),
    validatorResults: [validatorResult("PKT-PASS")]
  });

  const packetEvidence = record.packet_evidence.find(
    (item) => item.packet_id === "PKT-PASS"
  );

  assert.equal(packetEvidence?.approval_ready, true);
  assert.equal(packetEvidence?.evidence_status, "evidence_passed");
});

test("marks approval_ready false for failed evidence", () => {
  const record = buildValidatorEvidenceAttachmentRecord({
    assignmentPreviewRecord: assignmentPreviewRecord(),
    validatorResults: [
      validatorResult("PKT-PASS", {
        status: "failed",
        severity: "high"
      })
    ]
  });

  assert.equal(record.packet_evidence[0]?.approval_ready, false);
  assert.equal(record.packet_evidence[0]?.evidence_status, "evidence_failed");
});

test("marks approval_ready false for blocking evidence", () => {
  const record = buildValidatorEvidenceAttachmentRecord({
    assignmentPreviewRecord: assignmentPreviewRecord(),
    validatorResults: [
      validatorResult("PKT-PASS", {
        blocking: true
      })
    ]
  });

  assert.equal(record.packet_evidence[0]?.approval_ready, false);
  assert.equal(record.packet_evidence[0]?.blocking_count, 1);
});

test("marks approval_ready false for critical evidence", () => {
  const record = buildValidatorEvidenceAttachmentRecord({
    assignmentPreviewRecord: assignmentPreviewRecord(),
    validatorResults: [
      validatorResult("PKT-PASS", {
        severity: "critical"
      })
    ]
  });

  assert.equal(record.packet_evidence[0]?.approval_ready, false);
  assert.equal(record.packet_evidence[0]?.highest_severity, "critical");
});

test("commit_ready remains false", () => {
  const record = buildValidatorEvidenceAttachmentRecord({
    assignmentPreviewRecord: assignmentPreviewRecord(),
    validatorResults: [validatorResult("PKT-PASS")]
  });

  assert.equal(record.packet_evidence[0]?.commit_ready, false);
  assert.equal(record.summary.commit_ready_count, 0);
});

test("authorization booleans remain false", () => {
  const record = buildValidatorEvidenceAttachmentRecord({
    assignmentPreviewRecord: assignmentPreviewRecord(),
    validatorResults: [validatorResult("PKT-PASS")]
  });

  assert.equal(record.summary.approval_authorized, false);
  assert.equal(record.summary.commit_authorized, false);
  assert.equal(record.summary.runtime_mutation_authorized, false);
  assert.equal(record.summary.telemetry_mutation_authorized, false);
});

test("validateValidatorEvidenceAttachmentRecord reports tampered approval authorization", () => {
  const record = buildValidatorEvidenceAttachmentRecord({
    assignmentPreviewRecord: assignmentPreviewRecord(),
    validatorResults: [validatorResult("PKT-PASS")]
  }) as ValidatorEvidenceAttachmentRecord & {
    summary: ValidatorEvidenceAttachmentRecord["summary"] & {
      approval_authorized: boolean;
    };
  };
  record.summary.approval_authorized = true;

  const warnings = validateValidatorEvidenceAttachmentRecord(record);

  assert.ok(warnings.includes("approval_authorized must be false"));
});

test("validateValidatorEvidenceAttachmentRecord reports tampered commit readiness", () => {
  const record = buildValidatorEvidenceAttachmentRecord({
    assignmentPreviewRecord: assignmentPreviewRecord(),
    validatorResults: [validatorResult("PKT-PASS")]
  }) as ValidatorEvidenceAttachmentRecord;
  record.packet_evidence[0] = {
    ...record.packet_evidence[0],
    commit_ready: true
  } as typeof record.packet_evidence[number];

  const warnings = validateValidatorEvidenceAttachmentRecord(record);

  assert.ok(warnings.some((warning) => warning.includes("commit_ready must be false")));
});

test("serializeValidatorEvidenceAttachmentRecord returns parseable JSON with trailing newline", () => {
  const record = buildValidatorEvidenceAttachmentRecord({
    assignmentPreviewRecord: assignmentPreviewRecord(),
    validatorResults: [validatorResult("PKT-PASS")]
  });
  const serialized = serializeValidatorEvidenceAttachmentRecord(record);

  assert.equal(serialized.endsWith("\n"), true);
  assert.deepEqual(JSON.parse(serialized), record);
});

test("does not mutate input objects", () => {
  const assignmentRecord = assignmentPreviewRecord();
  const validatorResults = [validatorResult("PKT-PASS")];
  const beforeAssignment = JSON.stringify(assignmentRecord);
  const beforeResults = JSON.stringify(validatorResults);

  buildValidatorEvidenceAttachmentRecord({
    assignmentPreviewRecord: assignmentRecord,
    validatorResults
  });

  assert.equal(JSON.stringify(assignmentRecord), beforeAssignment);
  assert.equal(JSON.stringify(validatorResults), beforeResults);
});
