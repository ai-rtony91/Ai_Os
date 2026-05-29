import type {
  AssignmentPreviewPersistenceRecord
} from "./assignmentPreviewPersistence.ts";

export type ValidatorEvidenceStatus =
  | "passed"
  | "failed"
  | "warning"
  | "skipped"
  | "unknown";

export type ValidatorEvidenceSeverity =
  | "info"
  | "low"
  | "medium"
  | "high"
  | "critical"
  | "unknown";

export type PacketEvidenceStatus =
  | "evidence_passed"
  | "evidence_failed"
  | "evidence_warning"
  | "evidence_incomplete"
  | "evidence_unknown";

export interface ValidatorEvidenceResult {
  validator_id: string;
  validator_name: string;
  packet_id: string;
  status: ValidatorEvidenceStatus;
  severity: ValidatorEvidenceSeverity;
  evidence_ref: string;
  message: string;
  ran_at: string;
  blocking: boolean;
}

export interface ValidatorPacketEvidence {
  packet_id: string;
  assignment_preview_refs: string[];
  validator_result_count: number;
  passed_count: number;
  failed_count: number;
  warning_count: number;
  skipped_count: number;
  blocking_count: number;
  highest_severity: ValidatorEvidenceSeverity;
  evidence_status: PacketEvidenceStatus;
  approval_ready: boolean;
  commit_ready: false;
  preview_only: true;
}

export interface ValidatorEvidenceAttachmentRecord {
  schema: "AIOS_VALIDATOR_EVIDENCE_ATTACHMENT.v1";
  generated_at: string;
  source: Record<string, unknown>;
  attachment_mode: "preview_evidence_record_only";
  preview_only: true;
  assignment_reference: {
    schema: AssignmentPreviewPersistenceRecord["schema"];
    generated_at: string;
    persistence_mode: AssignmentPreviewPersistenceRecord["persistence_mode"];
    preview_only: true;
  };
  validator_results: ValidatorEvidenceResult[];
  packet_evidence: ValidatorPacketEvidence[];
  summary: {
    total_packets: number;
    total_validator_results: number;
    packets_with_passed_evidence: number;
    packets_with_failed_evidence: number;
    packets_with_blocking_evidence: number;
    approval_ready_count: number;
    commit_ready_count: 0;
    preview_only: true;
    approval_authorized: false;
    commit_authorized: false;
    runtime_mutation_authorized: false;
    telemetry_mutation_authorized: false;
  };
  warnings: string[];
  human_required_next_step: string;
}

export interface ValidatorEvidenceAttachmentOptions {
  assignmentPreviewRecord: AssignmentPreviewPersistenceRecord;
  validatorResults: ValidatorEvidenceResult[];
  now?: Date;
  source?: Record<string, unknown>;
}

const HUMAN_REQUIRED_NEXT_STEP =
  "Human approval is required before any approval package, commit package, commit, push, runtime execution, validator execution, worker dispatch, inbox mutation, packet mutation, queue mutation, broker execution, trading execution, or secret access. This record is preview validator evidence only.";

const VALID_STATUSES = new Set<ValidatorEvidenceStatus>([
  "passed",
  "failed",
  "warning",
  "skipped",
  "unknown"
]);

const VALID_SEVERITIES = new Set<ValidatorEvidenceSeverity>([
  "info",
  "low",
  "medium",
  "high",
  "critical",
  "unknown"
]);

const SEVERITY_RANK: Record<ValidatorEvidenceSeverity, number> = {
  info: 0,
  low: 1,
  medium: 2,
  high: 3,
  critical: 4,
  unknown: 5
};

export function buildValidatorEvidenceAttachmentRecord(
  options: ValidatorEvidenceAttachmentOptions
): ValidatorEvidenceAttachmentRecord {
  const generatedAt = (options.now ?? new Date()).toISOString();
  const validatorResults = options.validatorResults.map(copyValidatorResult);
  const packetIds = collectPacketIds(
    options.assignmentPreviewRecord,
    validatorResults
  );
  const packetEvidence = packetIds.map((packetId) =>
    buildPacketEvidence(
      packetId,
      options.assignmentPreviewRecord,
      validatorResults
    )
  );
  const warnings = [
    ...options.assignmentPreviewRecord.warnings,
    ...buildInputWarnings(validatorResults)
  ];

  return {
    schema: "AIOS_VALIDATOR_EVIDENCE_ATTACHMENT.v1",
    generated_at: generatedAt,
    source: {
      ...(options.source ?? {}),
      assignment_schema: options.assignmentPreviewRecord.schema,
      assignment_generated_at: options.assignmentPreviewRecord.generated_at,
      preview_only: true
    },
    attachment_mode: "preview_evidence_record_only",
    preview_only: true,
    assignment_reference: {
      schema: options.assignmentPreviewRecord.schema,
      generated_at: options.assignmentPreviewRecord.generated_at,
      persistence_mode: options.assignmentPreviewRecord.persistence_mode,
      preview_only: true
    },
    validator_results: validatorResults,
    packet_evidence: packetEvidence,
    summary: {
      total_packets: packetEvidence.length,
      total_validator_results: validatorResults.length,
      packets_with_passed_evidence: packetEvidence.filter(
        (item) => item.evidence_status === "evidence_passed"
      ).length,
      packets_with_failed_evidence: packetEvidence.filter(
        (item) => item.evidence_status === "evidence_failed"
      ).length,
      packets_with_blocking_evidence: packetEvidence.filter(
        (item) => item.blocking_count > 0
      ).length,
      approval_ready_count: packetEvidence.filter((item) => item.approval_ready)
        .length,
      commit_ready_count: 0,
      preview_only: true,
      approval_authorized: false,
      commit_authorized: false,
      runtime_mutation_authorized: false,
      telemetry_mutation_authorized: false
    },
    warnings,
    human_required_next_step: HUMAN_REQUIRED_NEXT_STEP
  };
}

export function validateValidatorEvidenceAttachmentRecord(
  record: ValidatorEvidenceAttachmentRecord
): string[] {
  const warnings: string[] = [];

  if (record.schema !== "AIOS_VALIDATOR_EVIDENCE_ATTACHMENT.v1") {
    warnings.push("schema mismatch");
  }

  if (record.preview_only !== true) {
    warnings.push("record preview_only must be true");
  }

  if (record.attachment_mode !== "preview_evidence_record_only") {
    warnings.push("attachment_mode must be preview_evidence_record_only");
  }

  if (record.summary.approval_authorized !== false) {
    warnings.push("approval_authorized must be false");
  }

  if (record.summary.commit_authorized !== false) {
    warnings.push("commit_authorized must be false");
  }

  if (record.summary.runtime_mutation_authorized !== false) {
    warnings.push("runtime_mutation_authorized must be false");
  }

  if (record.summary.telemetry_mutation_authorized !== false) {
    warnings.push("telemetry_mutation_authorized must be false");
  }

  for (const packetEvidence of record.packet_evidence) {
    if (!packetEvidence.packet_id) {
      warnings.push("packet evidence missing packet id");
    }

    if (packetEvidence.preview_only !== true) {
      warnings.push(
        `${packetEvidence.packet_id || "packet evidence"} preview_only must be true`
      );
    }

    if (packetEvidence.commit_ready === true) {
      warnings.push(`${packetEvidence.packet_id || "packet evidence"} commit_ready must be false`);
    }

    if (
      packetEvidence.highest_severity === "critical" &&
      packetEvidence.approval_ready
    ) {
      warnings.push(
        `${packetEvidence.packet_id || "packet evidence"} critical severity cannot be approval ready`
      );
    }

    if (packetEvidence.blocking_count > 0 && packetEvidence.approval_ready) {
      warnings.push(
        `${packetEvidence.packet_id || "packet evidence"} blocking evidence cannot be approval ready`
      );
    }
  }

  for (const result of record.validator_results) {
    if (!result.packet_id) {
      warnings.push("validator result missing packet id");
    }

    if (!result.validator_id) {
      warnings.push("validator result missing validator id");
    }

    if (!VALID_STATUSES.has(result.status)) {
      warnings.push(`${result.packet_id || "validator result"} has unknown validator status`);
    }

    if (!VALID_SEVERITIES.has(result.severity)) {
      warnings.push(`${result.packet_id || "validator result"} has unknown validator severity`);
    }
  }

  return warnings;
}

export function serializeValidatorEvidenceAttachmentRecord(
  record: ValidatorEvidenceAttachmentRecord
): string {
  return `${JSON.stringify(record, null, 2)}\n`;
}

function buildPacketEvidence(
  packetId: string,
  assignmentPreviewRecord: AssignmentPreviewPersistenceRecord,
  validatorResults: ValidatorEvidenceResult[]
): ValidatorPacketEvidence {
  const results = validatorResults.filter((result) => result.packet_id === packetId);
  const passedCount = results.filter((result) => result.status === "passed").length;
  const failedCount = results.filter((result) => result.status === "failed").length;
  const warningCount = results.filter((result) => result.status === "warning").length;
  const skippedCount = results.filter((result) => result.status === "skipped").length;
  const blockingCount = results.filter((result) => result.blocking).length;
  const highestSeverity = getHighestSeverity(results);
  const evidenceStatus = getEvidenceStatus({
    resultCount: results.length,
    failedCount,
    warningCount,
    skippedCount,
    highestSeverity
  });
  const approvalReady =
    results.length > 0 &&
    failedCount === 0 &&
    blockingCount === 0 &&
    highestSeverity !== "critical";

  return {
    packet_id: packetId,
    assignment_preview_refs: getAssignmentPreviewRefs(
      packetId,
      assignmentPreviewRecord
    ),
    validator_result_count: results.length,
    passed_count: passedCount,
    failed_count: failedCount,
    warning_count: warningCount,
    skipped_count: skippedCount,
    blocking_count: blockingCount,
    highest_severity: highestSeverity,
    evidence_status: evidenceStatus,
    approval_ready: approvalReady,
    commit_ready: false,
    preview_only: true
  };
}

function collectPacketIds(
  assignmentPreviewRecord: AssignmentPreviewPersistenceRecord,
  validatorResults: ValidatorEvidenceResult[]
): string[] {
  const packetIds = new Set<string>();

  for (const assignment of assignmentPreviewRecord.assignments) {
    packetIds.add(assignment.packet_id);
  }

  for (const unmatchedAction of assignmentPreviewRecord.unmatched_actions) {
    packetIds.add(unmatchedAction.packet_id);
  }

  for (const result of validatorResults) {
    if (result.packet_id) {
      packetIds.add(result.packet_id);
    }
  }

  return [...packetIds].sort((a, b) => a.localeCompare(b));
}

function getAssignmentPreviewRefs(
  packetId: string,
  assignmentPreviewRecord: AssignmentPreviewPersistenceRecord
): string[] {
  const refs: string[] = [];

  for (const assignment of assignmentPreviewRecord.assignments) {
    if (assignment.packet_id === packetId) {
      refs.push(`${assignment.packet_id}:${assignment.recommended_worker_id}`);
    }
  }

  for (const unmatchedAction of assignmentPreviewRecord.unmatched_actions) {
    if (unmatchedAction.packet_id === packetId) {
      refs.push(`${unmatchedAction.packet_id}:unmatched`);
    }
  }

  return refs;
}

function getHighestSeverity(
  results: ValidatorEvidenceResult[]
): ValidatorEvidenceSeverity {
  if (results.length === 0) {
    return "unknown";
  }

  return results
    .map((result) => result.severity)
    .sort((a, b) => SEVERITY_RANK[b] - SEVERITY_RANK[a])[0] ?? "unknown";
}

function getEvidenceStatus(context: {
  resultCount: number;
  failedCount: number;
  warningCount: number;
  skippedCount: number;
  highestSeverity: ValidatorEvidenceSeverity;
}): PacketEvidenceStatus {
  if (context.resultCount === 0) {
    return "evidence_incomplete";
  }

  if (context.failedCount > 0 || context.highestSeverity === "critical") {
    return "evidence_failed";
  }

  if (context.warningCount > 0) {
    return "evidence_warning";
  }

  if (context.skippedCount > 0) {
    return "evidence_incomplete";
  }

  if (context.highestSeverity === "unknown") {
    return "evidence_unknown";
  }

  return "evidence_passed";
}

function copyValidatorResult(
  result: ValidatorEvidenceResult
): ValidatorEvidenceResult {
  return {
    validator_id: result.validator_id,
    validator_name: result.validator_name,
    packet_id: result.packet_id,
    status: result.status,
    severity: result.severity,
    evidence_ref: result.evidence_ref,
    message: result.message,
    ran_at: result.ran_at,
    blocking: result.blocking
  };
}

function buildInputWarnings(results: ValidatorEvidenceResult[]): string[] {
  const warnings: string[] = [];

  for (const result of results) {
    if (!VALID_STATUSES.has(result.status)) {
      warnings.push(`${result.packet_id || "validator result"}: unknown validator status`);
    }

    if (!VALID_SEVERITIES.has(result.severity)) {
      warnings.push(`${result.packet_id || "validator result"}: unknown validator severity`);
    }
  }

  return warnings;
}
