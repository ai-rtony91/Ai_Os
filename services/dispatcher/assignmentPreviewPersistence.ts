import type {
  WorkerResolverPreviewAssignment,
  WorkerResolverPreviewPlan,
  WorkerResolverPreviewUnmatchedAction
} from "./workerResolverPreview.ts";

export interface AssignmentPreviewPersistenceAssignment {
  packet_id: string;
  recommended_worker_id: string;
  recommended_worker_name: string;
  match_score: number;
  risk_allowed: boolean;
  status_allowed: boolean;
  lane_match: boolean;
  matched_capabilities: string[];
  missing_capabilities: string[];
  reason: string;
  preview_only: true;
  persistence_status: "recorded_preview";
}

export interface AssignmentPreviewPersistenceUnmatchedAction {
  packet_id: string;
  required_capabilities: string[];
  risk_level: WorkerResolverPreviewUnmatchedAction["risk_level"];
  reason: string;
  preview_only: true;
}

export interface AssignmentPreviewPersistenceRecord {
  schema: "AIOS_ASSIGNMENT_PREVIEW_PERSISTENCE.v1";
  generated_at: string;
  source: Record<string, unknown> & {
    resolver_schema: WorkerResolverPreviewPlan["schema"];
    resolver_generated_at: string;
    preview_only: true;
  };
  persistence_mode: "preview_record_only";
  preview_only: true;
  assignments: AssignmentPreviewPersistenceAssignment[];
  unmatched_actions: AssignmentPreviewPersistenceUnmatchedAction[];
  summary: {
    total_assignments: number;
    total_unmatched: number;
    total_preview_items: number;
    dispatch_authorized: false;
    inbox_mutation_authorized: false;
    runtime_mutation_authorized: false;
    human_approval_required: true;
  };
  warnings: string[];
  human_required_next_step: string;
}

export interface AssignmentPreviewPersistenceOptions {
  resolverPlan: WorkerResolverPreviewPlan;
  now?: Date;
  source?: Record<string, unknown>;
}

const HUMAN_REQUIRED_NEXT_STEP =
  "Human approval is required before any dispatch, worker inbox mutation, approval mutation, commit, push, or runtime execution. This record is preview evidence only.";

export function buildAssignmentPreviewPersistenceRecord(
  options: AssignmentPreviewPersistenceOptions
): AssignmentPreviewPersistenceRecord {
  const generatedAt = (options.now ?? new Date()).toISOString();
  const assignments = options.resolverPlan.assignments.map(toAssignmentRecord);
  const unmatchedActions = options.resolverPlan.unmatched_actions.map(
    toUnmatchedActionRecord
  );

  return {
    schema: "AIOS_ASSIGNMENT_PREVIEW_PERSISTENCE.v1",
    generated_at: generatedAt,
    source: {
      ...(options.source ?? {}),
      resolver_schema: options.resolverPlan.schema,
      resolver_generated_at: options.resolverPlan.generated_at,
      preview_only: true
    },
    persistence_mode: "preview_record_only",
    preview_only: true,
    assignments,
    unmatched_actions: unmatchedActions,
    summary: {
      total_assignments: assignments.length,
      total_unmatched: unmatchedActions.length,
      total_preview_items: assignments.length + unmatchedActions.length,
      dispatch_authorized: false,
      inbox_mutation_authorized: false,
      runtime_mutation_authorized: false,
      human_approval_required: true
    },
    warnings: [...options.resolverPlan.warnings],
    human_required_next_step: HUMAN_REQUIRED_NEXT_STEP
  };
}

export function validateAssignmentPreviewPersistenceRecord(
  record: AssignmentPreviewPersistenceRecord
): string[] {
  const warnings: string[] = [];

  if (record.schema !== "AIOS_ASSIGNMENT_PREVIEW_PERSISTENCE.v1") {
    warnings.push("schema mismatch");
  }

  if (record.preview_only !== true) {
    warnings.push("record preview_only must be true");
  }

  if (record.summary.dispatch_authorized !== false) {
    warnings.push("dispatch_authorized must be false");
  }

  if (record.summary.inbox_mutation_authorized !== false) {
    warnings.push("inbox_mutation_authorized must be false");
  }

  if (record.summary.runtime_mutation_authorized !== false) {
    warnings.push("runtime_mutation_authorized must be false");
  }

  if (record.summary.human_approval_required !== true) {
    warnings.push("human_approval_required must be true");
  }

  for (const assignment of record.assignments) {
    if (!assignment.packet_id) {
      warnings.push("assignment missing packet id");
    }

    if (!assignment.recommended_worker_id) {
      warnings.push("assignment missing worker id");
    }

    if (!assignment.reason) {
      warnings.push("assignment missing reason");
    }

    if (assignment.preview_only !== true) {
      warnings.push(`${assignment.packet_id || "assignment"} preview_only must be true`);
    }
  }

  for (const unmatchedAction of record.unmatched_actions) {
    if (!unmatchedAction.packet_id) {
      warnings.push("unmatched action missing packet id");
    }

    if (!unmatchedAction.reason) {
      warnings.push("unmatched action missing reason");
    }

    if (unmatchedAction.preview_only !== true) {
      warnings.push(
        `${unmatchedAction.packet_id || "unmatched action"} preview_only must be true`
      );
    }
  }

  return warnings;
}

export function serializeAssignmentPreviewPersistenceRecord(
  record: AssignmentPreviewPersistenceRecord
): string {
  return `${JSON.stringify(record, null, 2)}\n`;
}

function toAssignmentRecord(
  assignment: WorkerResolverPreviewAssignment
): AssignmentPreviewPersistenceAssignment {
  return {
    packet_id: assignment.packet_id,
    recommended_worker_id: assignment.recommended_worker_id,
    recommended_worker_name: assignment.recommended_worker_name,
    match_score: assignment.match_score,
    risk_allowed: assignment.risk_allowed,
    status_allowed: assignment.status_allowed,
    lane_match: assignment.lane_match,
    matched_capabilities: [...assignment.matched_capabilities],
    missing_capabilities: [...assignment.missing_capabilities],
    reason: assignment.reason,
    preview_only: true,
    persistence_status: "recorded_preview"
  };
}

function toUnmatchedActionRecord(
  unmatchedAction: WorkerResolverPreviewUnmatchedAction
): AssignmentPreviewPersistenceUnmatchedAction {
  return {
    packet_id: unmatchedAction.packet_id,
    required_capabilities: [...unmatchedAction.required_capabilities],
    risk_level: unmatchedAction.risk_level,
    reason: unmatchedAction.reason,
    preview_only: true
  };
}
