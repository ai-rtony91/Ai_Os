import assert from "node:assert/strict";
import test from "node:test";
import type {
  ApprovalPackagePreviewRecord
} from "../../services/dispatcher/approvalPackagePreview.ts";
import {
  buildCommitPackagePreviewRecord,
  serializeCommitPackagePreviewRecord,
  validateCommitPackagePreviewRecord,
  type CommitPackagePreviewRecord
} from "../../services/dispatcher/commitPackagePreview.ts";

function approvalPackagePreviewRecord(): ApprovalPackagePreviewRecord {
  return {
    schema: "AIOS_APPROVAL_PACKAGE_PREVIEW.v1",
    generated_at: "2026-05-29T00:00:00.000Z",
    preview_only: true,
    source: {
      validator_evidence_schema: "AIOS_VALIDATOR_EVIDENCE_ATTACHMENT.v1",
      validator_evidence_generated_at: "2026-05-29T00:00:00.000Z",
      preview_only: true
    },
    approval_items: [
      {
        packet_id: "PKT-PASS",
        approval_ready: true,
        evidence_status: "evidence_passed",
        highest_severity: "low",
        blocking_count: 0,
        recommended_action:
          "Human review may consider this packet for approval; this preview does not approve it.",
        preview_only: true
      }
    ],
    blocked_items: [
      {
        packet_id: "PKT-BLOCKED",
        reason: "Validator evidence contains failed results.",
        evidence_status: "evidence_failed",
        preview_only: true
      }
    ],
    summary: {
      total_packets: 2,
      approval_ready_count: 1,
      blocked_count: 1,
      preview_only: true,
      approval_authorized: false,
      commit_authorized: false,
      push_authorized: false
    },
    warnings: ["carried warning"],
    human_required_next_step: "Human approval decision is required."
  };
}

test("commit preview generation", () => {
  const record = buildCommitPackagePreviewRecord({
    approvalPackagePreviewRecord: approvalPackagePreviewRecord(),
    now: new Date("2026-05-29T01:00:00.000Z")
  });

  assert.equal(record.schema, "AIOS_COMMIT_PACKAGE_PREVIEW.v1");
  assert.equal(record.generated_at, "2026-05-29T01:00:00.000Z");
  assert.equal(record.commit_candidates.length, 1);
  assert.equal(record.commit_candidates[0]?.packet_id, "PKT-PASS");
  assert.equal(
    record.commit_candidates[0]?.proposed_commit_message,
    "Prepare preview package for PKT-PASS"
  );
});

test("PR preview generation", () => {
  const record = buildCommitPackagePreviewRecord({
    approvalPackagePreviewRecord: approvalPackagePreviewRecord()
  });

  assert.equal(record.pull_request_candidates.length, 1);
  assert.equal(record.pull_request_candidates[0]?.packet_id, "PKT-PASS");
  assert.equal(
    record.pull_request_candidates[0]?.proposed_title,
    "Review preview package for PKT-PASS"
  );
  assert.ok(
    record.pull_request_candidates[0]?.proposed_summary.includes(
      "Evidence status: evidence_passed"
    )
  );
});

test("preview_only enforcement", () => {
  const record = buildCommitPackagePreviewRecord({
    approvalPackagePreviewRecord: approvalPackagePreviewRecord()
  });

  assert.equal(record.preview_only, true);
  assert.equal(record.commit_candidates[0]?.preview_only, true);
  assert.equal(record.pull_request_candidates[0]?.preview_only, true);
});

test("commit_authorized false", () => {
  const record = buildCommitPackagePreviewRecord({
    approvalPackagePreviewRecord: approvalPackagePreviewRecord()
  });

  assert.equal(record.validation_summary.commit_authorized, false);
});

test("push_authorized false", () => {
  const record = buildCommitPackagePreviewRecord({
    approvalPackagePreviewRecord: approvalPackagePreviewRecord()
  });

  assert.equal(record.validation_summary.push_authorized, false);
});

test("merge_authorized false", () => {
  const record = buildCommitPackagePreviewRecord({
    approvalPackagePreviewRecord: approvalPackagePreviewRecord()
  });

  assert.equal(record.validation_summary.merge_authorized, false);
});

test("serialization validity", () => {
  const record = buildCommitPackagePreviewRecord({
    approvalPackagePreviewRecord: approvalPackagePreviewRecord()
  });
  const serialized = serializeCommitPackagePreviewRecord(record);

  assert.equal(serialized.endsWith("\n"), true);
  assert.deepEqual(JSON.parse(serialized), record);
});

test("validation catches unsafe authorization flags", () => {
  const record = buildCommitPackagePreviewRecord({
    approvalPackagePreviewRecord: approvalPackagePreviewRecord()
  }) as CommitPackagePreviewRecord & {
    validation_summary: CommitPackagePreviewRecord["validation_summary"] & {
      commit_authorized: boolean;
      push_authorized: boolean;
      merge_authorized: boolean;
    };
  };
  record.validation_summary.commit_authorized = true;
  record.validation_summary.push_authorized = true;
  record.validation_summary.merge_authorized = true;

  const warnings = validateCommitPackagePreviewRecord(record);

  assert.ok(warnings.includes("commit_authorized must be false"));
  assert.ok(warnings.includes("push_authorized must be false"));
  assert.ok(warnings.includes("merge_authorized must be false"));
});

test("function does not mutate inputs", () => {
  const input = approvalPackagePreviewRecord();
  const before = JSON.stringify(input);

  buildCommitPackagePreviewRecord({
    approvalPackagePreviewRecord: input
  });

  assert.equal(JSON.stringify(input), before);
});
