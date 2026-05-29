import assert from "node:assert/strict";
import test from "node:test";
import {
  buildApprovalPackagePreviewRecord,
  serializeApprovalPackagePreviewRecord,
  validateApprovalPackagePreviewRecord,
  type ApprovalPackagePreviewRecord
} from "../../services/dispatcher/approvalPackagePreview.ts";
import type {
  ValidatorEvidenceAttachmentRecord
} from "../../services/dispatcher/validatorEvidenceAttachment.ts";

function validatorEvidenceRecord(): ValidatorEvidenceAttachmentRecord {
  return {
    schema: "AIOS_VALIDATOR_EVIDENCE_ATTACHMENT.v1",
    generated_at: "2026-05-29T00:00:00.000Z",
    source: {
      assignment_schema: "AIOS_ASSIGNMENT_PREVIEW_PERSISTENCE.v1",
      assignment_generated_at: "2026-05-29T00:00:00.000Z",
      preview_only: true
    },
    attachment_mode: "preview_evidence_record_only",
    preview_only: true,
    assignment_reference: {
      schema: "AIOS_ASSIGNMENT_PREVIEW_PERSISTENCE.v1",
      generated_at: "2026-05-29T00:00:00.000Z",
      persistence_mode: "preview_record_only",
      preview_only: true
    },
    validator_results: [],
    packet_evidence: [
      {
        packet_id: "PKT-PASS",
        assignment_preview_refs: ["PKT-PASS:dispatcher_worker"],
        validator_result_count: 1,
        passed_count: 1,
        failed_count: 0,
        warning_count: 0,
        skipped_count: 0,
        blocking_count: 0,
        highest_severity: "low",
        evidence_status: "evidence_passed",
        approval_ready: true,
        commit_ready: false,
        preview_only: true
      },
      {
        packet_id: "PKT-BLOCKED",
        assignment_preview_refs: ["PKT-BLOCKED:dispatcher_worker"],
        validator_result_count: 1,
        passed_count: 0,
        failed_count: 1,
        warning_count: 0,
        skipped_count: 0,
        blocking_count: 0,
        highest_severity: "high",
        evidence_status: "evidence_failed",
        approval_ready: false,
        commit_ready: false,
        preview_only: true
      }
    ],
    summary: {
      total_packets: 2,
      total_validator_results: 2,
      packets_with_passed_evidence: 1,
      packets_with_failed_evidence: 1,
      packets_with_blocking_evidence: 0,
      approval_ready_count: 1,
      commit_ready_count: 0,
      preview_only: true,
      approval_authorized: false,
      commit_authorized: false,
      runtime_mutation_authorized: false,
      telemetry_mutation_authorized: false
    },
    warnings: ["carried warning"],
    human_required_next_step: "Human approval required."
  };
}

test("approval-ready packet enters approval_items", () => {
  const record = buildApprovalPackagePreviewRecord({
    validatorEvidenceRecord: validatorEvidenceRecord(),
    now: new Date("2026-05-29T01:00:00.000Z")
  });

  assert.equal(record.schema, "AIOS_APPROVAL_PACKAGE_PREVIEW.v1");
  assert.equal(record.generated_at, "2026-05-29T01:00:00.000Z");
  assert.equal(record.approval_items.length, 1);
  assert.equal(record.approval_items[0]?.packet_id, "PKT-PASS");
  assert.equal(record.approval_items[0]?.approval_ready, true);
});

test("blocked evidence enters blocked_items", () => {
  const record = buildApprovalPackagePreviewRecord({
    validatorEvidenceRecord: validatorEvidenceRecord()
  });

  assert.equal(record.blocked_items.length, 1);
  assert.equal(record.blocked_items[0]?.packet_id, "PKT-BLOCKED");
  assert.equal(record.blocked_items[0]?.reason, "Validator evidence contains failed results.");
});

test("approval_authorized remains false", () => {
  const record = buildApprovalPackagePreviewRecord({
    validatorEvidenceRecord: validatorEvidenceRecord()
  });

  assert.equal(record.summary.approval_authorized, false);
});

test("commit_authorized remains false", () => {
  const record = buildApprovalPackagePreviewRecord({
    validatorEvidenceRecord: validatorEvidenceRecord()
  });

  assert.equal(record.summary.commit_authorized, false);
});

test("push_authorized remains false", () => {
  const record = buildApprovalPackagePreviewRecord({
    validatorEvidenceRecord: validatorEvidenceRecord()
  });

  assert.equal(record.summary.push_authorized, false);
});

test("serialization returns parseable JSON", () => {
  const record = buildApprovalPackagePreviewRecord({
    validatorEvidenceRecord: validatorEvidenceRecord()
  });
  const serialized = serializeApprovalPackagePreviewRecord(record);

  assert.equal(serialized.endsWith("\n"), true);
  assert.deepEqual(JSON.parse(serialized), record);
});

test("validation catches unsafe authorization flags", () => {
  const record = buildApprovalPackagePreviewRecord({
    validatorEvidenceRecord: validatorEvidenceRecord()
  }) as ApprovalPackagePreviewRecord & {
    summary: ApprovalPackagePreviewRecord["summary"] & {
      approval_authorized: boolean;
      commit_authorized: boolean;
      push_authorized: boolean;
    };
  };
  record.summary.approval_authorized = true;
  record.summary.commit_authorized = true;
  record.summary.push_authorized = true;

  const warnings = validateApprovalPackagePreviewRecord(record);

  assert.ok(warnings.includes("approval_authorized must be false"));
  assert.ok(warnings.includes("commit_authorized must be false"));
  assert.ok(warnings.includes("push_authorized must be false"));
});

test("function does not mutate input objects", () => {
  const input = validatorEvidenceRecord();
  const before = JSON.stringify(input);

  buildApprovalPackagePreviewRecord({
    validatorEvidenceRecord: input
  });

  assert.equal(JSON.stringify(input), before);
});
