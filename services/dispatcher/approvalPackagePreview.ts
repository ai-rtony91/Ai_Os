import type {
  PacketEvidenceStatus,
  ValidatorEvidenceAttachmentRecord,
  ValidatorEvidenceSeverity
} from "./validatorEvidenceAttachment.ts";

export interface ApprovalPackagePreviewItem {
  packet_id: string;
  approval_ready: true;
  evidence_status: PacketEvidenceStatus;
  highest_severity: ValidatorEvidenceSeverity;
  blocking_count: number;
  recommended_action: string;
  preview_only: true;
}

export interface ApprovalPackagePreviewBlockedItem {
  packet_id: string;
  reason: string;
  evidence_status: PacketEvidenceStatus;
  preview_only: true;
}

export interface ApprovalPackagePreviewRecord {
  schema: "AIOS_APPROVAL_PACKAGE_PREVIEW.v1";
  generated_at: string;
  preview_only: true;
  source: Record<string, unknown> & {
    validator_evidence_schema: ValidatorEvidenceAttachmentRecord["schema"];
    validator_evidence_generated_at: string;
    preview_only: true;
  };
  approval_items: ApprovalPackagePreviewItem[];
  blocked_items: ApprovalPackagePreviewBlockedItem[];
  summary: {
    total_packets: number;
    approval_ready_count: number;
    blocked_count: number;
    preview_only: true;
    approval_authorized: false;
    commit_authorized: false;
    push_authorized: false;
  };
  warnings: string[];
  human_required_next_step: string;
}

export interface ApprovalPackagePreviewOptions {
  validatorEvidenceRecord: ValidatorEvidenceAttachmentRecord;
  now?: Date;
  source?: Record<string, unknown>;
}

const HUMAN_REQUIRED_NEXT_STEP =
  "Human approval decision is required. This preview does not authorize approval, commit, push, merge, runtime mutation, worker dispatch, packet mutation, queue mutation, telemetry mutation, trading execution, broker execution, or secret access.";

const RECOMMENDED_ACTION =
  "Human review may consider this packet for approval; this preview does not approve it.";

export function buildApprovalPackagePreviewRecord(
  options: ApprovalPackagePreviewOptions
): ApprovalPackagePreviewRecord {
  const generatedAt = (options.now ?? new Date()).toISOString();
  const approvalItems: ApprovalPackagePreviewItem[] = [];
  const blockedItems: ApprovalPackagePreviewBlockedItem[] = [];

  for (const packetEvidence of options.validatorEvidenceRecord.packet_evidence) {
    if (packetEvidence.approval_ready === true) {
      approvalItems.push({
        packet_id: packetEvidence.packet_id,
        approval_ready: true,
        evidence_status: packetEvidence.evidence_status,
        highest_severity: packetEvidence.highest_severity,
        blocking_count: packetEvidence.blocking_count,
        recommended_action: RECOMMENDED_ACTION,
        preview_only: true
      });
      continue;
    }

    blockedItems.push({
      packet_id: packetEvidence.packet_id,
      reason: getBlockedReason(packetEvidence),
      evidence_status: packetEvidence.evidence_status,
      preview_only: true
    });
  }

  return {
    schema: "AIOS_APPROVAL_PACKAGE_PREVIEW.v1",
    generated_at: generatedAt,
    preview_only: true,
    source: {
      ...(options.source ?? {}),
      validator_evidence_schema: options.validatorEvidenceRecord.schema,
      validator_evidence_generated_at: options.validatorEvidenceRecord.generated_at,
      preview_only: true
    },
    approval_items: approvalItems,
    blocked_items: blockedItems,
    summary: {
      total_packets: options.validatorEvidenceRecord.packet_evidence.length,
      approval_ready_count: approvalItems.length,
      blocked_count: blockedItems.length,
      preview_only: true,
      approval_authorized: false,
      commit_authorized: false,
      push_authorized: false
    },
    warnings: [...options.validatorEvidenceRecord.warnings],
    human_required_next_step: HUMAN_REQUIRED_NEXT_STEP
  };
}

export function validateApprovalPackagePreviewRecord(
  record: ApprovalPackagePreviewRecord
): string[] {
  const warnings: string[] = [];

  if (record.schema !== "AIOS_APPROVAL_PACKAGE_PREVIEW.v1") {
    warnings.push("schema mismatch");
  }

  if (record.preview_only !== true) {
    warnings.push("record preview_only must be true");
  }

  if (record.summary.preview_only !== true) {
    warnings.push("summary preview_only must be true");
  }

  if (record.summary.approval_authorized !== false) {
    warnings.push("approval_authorized must be false");
  }

  if (record.summary.commit_authorized !== false) {
    warnings.push("commit_authorized must be false");
  }

  if (record.summary.push_authorized !== false) {
    warnings.push("push_authorized must be false");
  }

  for (const item of record.approval_items) {
    if (!item.packet_id) {
      warnings.push("approval item missing packet id");
    }

    if (item.approval_ready !== true) {
      warnings.push(`${item.packet_id || "approval item"} approval_ready must be true`);
    }

    if (item.preview_only !== true) {
      warnings.push(`${item.packet_id || "approval item"} preview_only must be true`);
    }
  }

  for (const item of record.blocked_items) {
    if (!item.packet_id) {
      warnings.push("blocked item missing packet id");
    }

    if (!item.reason) {
      warnings.push(`${item.packet_id || "blocked item"} missing reason`);
    }

    if (item.preview_only !== true) {
      warnings.push(`${item.packet_id || "blocked item"} preview_only must be true`);
    }
  }

  return warnings;
}

export function serializeApprovalPackagePreviewRecord(
  record: ApprovalPackagePreviewRecord
): string {
  return `${JSON.stringify(record, null, 2)}\n`;
}

function getBlockedReason(
  packetEvidence: ValidatorEvidenceAttachmentRecord["packet_evidence"][number]
): string {
  if (!packetEvidence.packet_id) {
    return "Packet evidence is missing packet id.";
  }

  if (packetEvidence.validator_result_count === 0) {
    return "No validator evidence is attached for this packet.";
  }

  if (packetEvidence.failed_count > 0) {
    return "Validator evidence contains failed results.";
  }

  if (packetEvidence.blocking_count > 0) {
    return "Validator evidence contains blocking results.";
  }

  if (packetEvidence.highest_severity === "critical") {
    return "Validator evidence contains critical severity.";
  }

  if (packetEvidence.evidence_status !== "evidence_passed") {
    return `Validator evidence status is ${packetEvidence.evidence_status}.`;
  }

  return "Validator evidence is not approval ready.";
}
