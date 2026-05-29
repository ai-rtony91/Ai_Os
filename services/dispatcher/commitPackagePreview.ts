import type {
  ApprovalPackagePreviewRecord
} from "./approvalPackagePreview.ts";
import type {
  PacketEvidenceStatus
} from "./validatorEvidenceAttachment.ts";

export interface CommitPackagePreviewItem {
  packet_id: string;
  proposed_commit_message: string;
  evidence_status: PacketEvidenceStatus;
  approval_status: "approval_ready";
  preview_only: true;
}

export interface PullRequestPackagePreviewItem {
  packet_id: string;
  proposed_title: string;
  proposed_summary: string;
  preview_only: true;
}

export interface CommitPackagePreviewRecord {
  schema: "AIOS_COMMIT_PACKAGE_PREVIEW.v1";
  generated_at: string;
  preview_only: true;
  source: Record<string, unknown> & {
    approval_package_schema: ApprovalPackagePreviewRecord["schema"];
    approval_package_generated_at: string;
    preview_only: true;
  };
  commit_candidates: CommitPackagePreviewItem[];
  pull_request_candidates: PullRequestPackagePreviewItem[];
  validation_summary: {
    total_candidates: number;
    approval_ready_count: number;
    commit_authorized: false;
    push_authorized: false;
    merge_authorized: false;
  };
  warnings: string[];
  human_required_next_step: string;
}

export interface CommitPackagePreviewOptions {
  approvalPackagePreviewRecord: ApprovalPackagePreviewRecord;
  now?: Date;
  source?: Record<string, unknown>;
}

const HUMAN_REQUIRED_NEXT_STEP =
  "Human commit approval is required before staging, commit, push, merge, deployment, runtime mutation, worker dispatch, packet mutation, queue mutation, telemetry mutation, trading execution, broker execution, or protected action. This record is commit package preview metadata only.";

export function buildCommitPackagePreviewRecord(
  options: CommitPackagePreviewOptions
): CommitPackagePreviewRecord {
  const generatedAt = (options.now ?? new Date()).toISOString();
  const commitCandidates = options.approvalPackagePreviewRecord.approval_items.map(
    (item) => ({
      packet_id: item.packet_id,
      proposed_commit_message: buildCommitMessage(item.packet_id),
      evidence_status: item.evidence_status,
      approval_status: "approval_ready" as const,
      preview_only: true as const
    })
  );
  const pullRequestCandidates = options.approvalPackagePreviewRecord.approval_items.map(
    (item) => ({
      packet_id: item.packet_id,
      proposed_title: buildPullRequestTitle(item.packet_id),
      proposed_summary: buildPullRequestSummary(item.packet_id, item.evidence_status),
      preview_only: true as const
    })
  );

  return {
    schema: "AIOS_COMMIT_PACKAGE_PREVIEW.v1",
    generated_at: generatedAt,
    preview_only: true,
    source: {
      ...(options.source ?? {}),
      approval_package_schema: options.approvalPackagePreviewRecord.schema,
      approval_package_generated_at:
        options.approvalPackagePreviewRecord.generated_at,
      preview_only: true
    },
    commit_candidates: commitCandidates,
    pull_request_candidates: pullRequestCandidates,
    validation_summary: {
      total_candidates: commitCandidates.length,
      approval_ready_count: options.approvalPackagePreviewRecord.summary
        .approval_ready_count,
      commit_authorized: false,
      push_authorized: false,
      merge_authorized: false
    },
    warnings: buildWarnings(options.approvalPackagePreviewRecord),
    human_required_next_step: HUMAN_REQUIRED_NEXT_STEP
  };
}

export function validateCommitPackagePreviewRecord(
  record: CommitPackagePreviewRecord
): string[] {
  const warnings: string[] = [];

  if (record.schema !== "AIOS_COMMIT_PACKAGE_PREVIEW.v1") {
    warnings.push("schema mismatch");
  }

  if (record.preview_only !== true) {
    warnings.push("record preview_only must be true");
  }

  if (record.validation_summary.commit_authorized !== false) {
    warnings.push("commit_authorized must be false");
  }

  if (record.validation_summary.push_authorized !== false) {
    warnings.push("push_authorized must be false");
  }

  if (record.validation_summary.merge_authorized !== false) {
    warnings.push("merge_authorized must be false");
  }

  for (const candidate of record.commit_candidates) {
    if (!candidate.packet_id) {
      warnings.push("commit candidate missing packet id");
    }

    if (!candidate.proposed_commit_message) {
      warnings.push(`${candidate.packet_id || "commit candidate"} missing proposed commit message`);
    }

    if (candidate.approval_status !== "approval_ready") {
      warnings.push(`${candidate.packet_id || "commit candidate"} approval_status must be approval_ready`);
    }

    if (candidate.preview_only !== true) {
      warnings.push(`${candidate.packet_id || "commit candidate"} preview_only must be true`);
    }
  }

  for (const candidate of record.pull_request_candidates) {
    if (!candidate.packet_id) {
      warnings.push("pull request candidate missing packet id");
    }

    if (!candidate.proposed_title) {
      warnings.push(`${candidate.packet_id || "pull request candidate"} missing proposed title`);
    }

    if (!candidate.proposed_summary) {
      warnings.push(`${candidate.packet_id || "pull request candidate"} missing proposed summary`);
    }

    if (candidate.preview_only !== true) {
      warnings.push(`${candidate.packet_id || "pull request candidate"} preview_only must be true`);
    }
  }

  return warnings;
}

export function serializeCommitPackagePreviewRecord(
  record: CommitPackagePreviewRecord
): string {
  return `${JSON.stringify(record, null, 2)}\n`;
}

function buildCommitMessage(packetId: string): string {
  return `Prepare preview package for ${packetId}`;
}

function buildPullRequestTitle(packetId: string): string {
  return `Review preview package for ${packetId}`;
}

function buildPullRequestSummary(
  packetId: string,
  evidenceStatus: PacketEvidenceStatus
): string {
  return `Preview-only commit package candidate for ${packetId}. Evidence status: ${evidenceStatus}. Human approval is required before staging, commit, push, merge, deployment, or protected action.`;
}

function buildWarnings(
  approvalPackagePreviewRecord: ApprovalPackagePreviewRecord
): string[] {
  const warnings = [...approvalPackagePreviewRecord.warnings];

  for (const blockedItem of approvalPackagePreviewRecord.blocked_items) {
    warnings.push(
      `${blockedItem.packet_id}: blocked from commit package preview - ${blockedItem.reason}`
    );
  }

  return warnings;
}
