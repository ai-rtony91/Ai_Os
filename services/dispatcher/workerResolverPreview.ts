import type {
  SchedulerPreviewPlan,
  SchedulerPreviewRecommendedPacket
} from "./schedulerPreview.ts";

export type WorkerResolverRiskLevel =
  | "low"
  | "medium"
  | "high"
  | "protected"
  | "unknown";

export interface WorkerResolverPreviewWorker {
  worker_id: string;
  display_name?: string;
  lane?: string;
  capabilities: string[];
  risk_ceiling: WorkerResolverRiskLevel;
  status?: string;
  window_marker?: string | null;
  active?: boolean;
}

export interface WorkerResolverPreviewAssignment {
  packet_id: string;
  recommended_worker_id: string;
  recommended_worker_name: string;
  match_score: number;
  matched_capabilities: string[];
  missing_capabilities: string[];
  risk_allowed: boolean;
  status_allowed: boolean;
  lane_match: boolean;
  reason: string;
  preview_only: true;
}

export interface WorkerResolverPreviewUnmatchedAction {
  packet_id: string;
  required_capabilities: string[];
  risk_level: WorkerResolverRiskLevel;
  reason: string;
}

export interface WorkerResolverPreviewPlan {
  schema: "AIOS_WORKER_RESOLVER_PREVIEW.v1";
  generated_at: string;
  source: {
    scheduler_plan_generated_at: string;
    scheduler_ready_packets: number;
    worker_count: number;
    preview_only: true;
  };
  preview_mode: "read_only_preview";
  assignments: WorkerResolverPreviewAssignment[];
  unmatched_actions: WorkerResolverPreviewUnmatchedAction[];
  summary: {
    total_actions: number;
    assigned_preview_count: number;
    unmatched_count: number;
    active_worker_count: number;
    unavailable_worker_count: number;
  };
  warnings: string[];
}

export interface BuildWorkerResolverPreviewOptions {
  schedulerPlan: SchedulerPreviewPlan;
  workers: WorkerResolverPreviewWorker[];
  now?: Date;
}

export interface WorkerResolverPreviewAction {
  packet_id: string;
  risk_level: WorkerResolverRiskLevel;
  required_capabilities: string[];
  priority?: number;
  rank?: number;
  dependency_count?: number;
  scheduler_eligible?: boolean;
}

export interface WorkerResolverPreviewScore {
  score: number;
  matched_capabilities: string[];
  missing_capabilities: string[];
  risk_allowed: boolean;
  status_allowed: boolean;
  lane_match: boolean;
  reason: string;
}

const RISK_ORDER: Record<WorkerResolverRiskLevel, number> = {
  low: 0,
  medium: 1,
  high: 2,
  protected: 3,
  unknown: 4
};

const AVAILABLE_STATUSES = new Set([
  "active",
  "available",
  "idle",
  "online",
  "ready"
]);

const UNAVAILABLE_STATUSES = new Set([
  "blocked",
  "busy",
  "disabled",
  "inactive",
  "offline",
  "unavailable"
]);

export function buildWorkerResolverPreviewPlan(
  options: BuildWorkerResolverPreviewOptions
): WorkerResolverPreviewPlan {
  const generatedAt = (options.now ?? new Date()).toISOString();
  const actions = buildActions(options.schedulerPlan);
  const assignments: WorkerResolverPreviewAssignment[] = [];
  const unmatchedActions: WorkerResolverPreviewUnmatchedAction[] = [];
  const warnings = [...options.schedulerPlan.warnings];

  for (const action of actions) {
    const unmatchedReason = getActionUnmatchedReason(action);

    if (unmatchedReason) {
      unmatchedActions.push(toUnmatchedAction(action, unmatchedReason));
      continue;
    }

    const candidates = options.workers
      .map((worker) => ({
        worker,
        score: scoreWorkerForAction(worker, action)
      }))
      .filter((candidate) => candidate.score.score > 0)
      .sort((a, b) => {
        return (
          b.score.score - a.score.score ||
          a.worker.worker_id.localeCompare(b.worker.worker_id)
        );
      });

    const bestCandidate = candidates[0];

    if (!bestCandidate) {
      unmatchedActions.push(
        toUnmatchedAction(
          action,
          "No active worker matched required capabilities, lane, and risk ceiling."
        )
      );
      continue;
    }

    assignments.push({
      packet_id: action.packet_id,
      recommended_worker_id: bestCandidate.worker.worker_id,
      recommended_worker_name:
        bestCandidate.worker.display_name ?? bestCandidate.worker.worker_id,
      match_score: bestCandidate.score.score,
      matched_capabilities: bestCandidate.score.matched_capabilities,
      missing_capabilities: bestCandidate.score.missing_capabilities,
      risk_allowed: bestCandidate.score.risk_allowed,
      status_allowed: bestCandidate.score.status_allowed,
      lane_match: bestCandidate.score.lane_match,
      reason: bestCandidate.score.reason,
      preview_only: true
    });
  }

  for (const unmatchedAction of unmatchedActions) {
    warnings.push(`${unmatchedAction.packet_id}: ${unmatchedAction.reason}`);
  }

  const activeWorkerCount = options.workers.filter(isWorkerAvailable).length;

  return {
    schema: "AIOS_WORKER_RESOLVER_PREVIEW.v1",
    generated_at: generatedAt,
    source: {
      scheduler_plan_generated_at: options.schedulerPlan.generated_at,
      scheduler_ready_packets: options.schedulerPlan.ready_packets,
      worker_count: options.workers.length,
      preview_only: true
    },
    preview_mode: "read_only_preview",
    assignments,
    unmatched_actions: unmatchedActions,
    summary: {
      total_actions: actions.length,
      assigned_preview_count: assignments.length,
      unmatched_count: unmatchedActions.length,
      active_worker_count: activeWorkerCount,
      unavailable_worker_count: options.workers.length - activeWorkerCount
    },
    warnings
  };
}

export function scoreWorkerForAction(
  worker: WorkerResolverPreviewWorker,
  action: WorkerResolverPreviewAction
): WorkerResolverPreviewScore {
  const workerCapabilities = normalizeCapabilities(worker.capabilities);
  const requiredCapabilities = normalizeCapabilities(action.required_capabilities);
  const matchedCapabilities = requiredCapabilities.filter((capability) =>
    workerCapabilities.includes(capability)
  );
  const laneSignals = requiredCapabilities.filter((capability) =>
    capability.startsWith("lane:")
  );
  const laneMatch =
    laneSignals.length > 0 &&
    Boolean(worker.lane) &&
    laneSignals.includes(`lane:${worker.lane}`);
  const missingCapabilities = requiredCapabilities.filter(
    (capability) => !matchedCapabilities.includes(capability)
  );
  const riskAllowed = isRiskAllowed(worker.risk_ceiling, action.risk_level);
  const statusAllowed = isWorkerAvailable(worker);
  const hasCapabilityMatch = matchedCapabilities.length > 0 || laneMatch;

  if (!statusAllowed || !riskAllowed || !hasCapabilityMatch) {
    return {
      score: 0,
      matched_capabilities: matchedCapabilities,
      missing_capabilities: missingCapabilities,
      risk_allowed: riskAllowed,
      status_allowed: statusAllowed,
      lane_match: laneMatch,
      reason: buildScoreReason({
        hasCapabilityMatch,
        riskAllowed,
        statusAllowed,
        laneMatch,
        matchedCapabilities
      })
    };
  }

  const riskFitBonus = Math.max(
    0,
    3 - (RISK_ORDER[worker.risk_ceiling] - RISK_ORDER[action.risk_level])
  );
  const laneBonus = laneMatch ? 5 : 0;
  const completeMatchBonus = missingCapabilities.length === 0 ? 4 : 0;
  const score =
    matchedCapabilities.length * 10 +
    laneBonus +
    completeMatchBonus +
    riskFitBonus;

  return {
    score,
    matched_capabilities: matchedCapabilities,
    missing_capabilities: missingCapabilities,
    risk_allowed: riskAllowed,
    status_allowed: statusAllowed,
    lane_match: laneMatch,
    reason: buildScoreReason({
      hasCapabilityMatch,
      riskAllowed,
      statusAllowed,
      laneMatch,
      matchedCapabilities
    })
  };
}

function buildActions(
  schedulerPlan: SchedulerPreviewPlan
): WorkerResolverPreviewAction[] {
  const requirementByPacket = new Map(
    schedulerPlan.worker_capability_requirements.map((requirement) => [
      requirement.packet_id,
      requirement.required_capabilities
    ])
  );

  return schedulerPlan.recommended_order.map((action) => {
    const typedAction = action as SchedulerPreviewRecommendedPacket & {
      scheduler_eligible?: boolean;
    };

    return {
      packet_id: action.packet_id,
      risk_level: action.risk_level,
      required_capabilities: requirementByPacket.get(action.packet_id) ?? [],
      priority: action.priority,
      rank: action.rank,
      dependency_count: action.dependency_count,
      scheduler_eligible: typedAction.scheduler_eligible
    };
  });
}

function getActionUnmatchedReason(
  action: WorkerResolverPreviewAction
): string | undefined {
  if (action.scheduler_eligible === false) {
    return "Scheduler action is not eligible for worker resolution.";
  }

  if (action.risk_level === "protected") {
    return "Protected risk requires human-gated handling; no automatic worker recommendation.";
  }

  if (action.risk_level === "unknown") {
    return "Unknown risk requires manual review before worker resolution.";
  }

  if (action.required_capabilities.length === 0) {
    return "No required capabilities were provided by scheduler preview.";
  }

  return undefined;
}

function toUnmatchedAction(
  action: WorkerResolverPreviewAction,
  reason: string
): WorkerResolverPreviewUnmatchedAction {
  return {
    packet_id: action.packet_id,
    required_capabilities: [...action.required_capabilities],
    risk_level: action.risk_level,
    reason
  };
}

function isWorkerAvailable(worker: WorkerResolverPreviewWorker): boolean {
  if (worker.active !== true) {
    return false;
  }

  const status = normalizeToken(worker.status);

  if (UNAVAILABLE_STATUSES.has(status)) {
    return false;
  }

  return AVAILABLE_STATUSES.has(status);
}

function isRiskAllowed(
  riskCeiling: WorkerResolverRiskLevel,
  actionRisk: WorkerResolverRiskLevel
): boolean {
  if (actionRisk === "protected" || actionRisk === "unknown") {
    return false;
  }

  if (riskCeiling === "protected") {
    return true;
  }

  if (riskCeiling === "unknown") {
    return false;
  }

  return RISK_ORDER[riskCeiling] >= RISK_ORDER[actionRisk];
}

function normalizeCapabilities(capabilities: string[]): string[] {
  return [...new Set(capabilities.map(normalizeCapability))]
    .filter((capability) => capability.length > 0)
    .sort((a, b) => a.localeCompare(b));
}

function normalizeCapability(capability: string): string {
  if (capability.startsWith("lane:")) {
    return capability;
  }

  return normalizeToken(capability);
}

function normalizeToken(input: string | undefined): string {
  return (input ?? "")
    .trim()
    .replace(/[\s-]+/g, "_")
    .toLowerCase();
}

function buildScoreReason(context: {
  hasCapabilityMatch: boolean;
  riskAllowed: boolean;
  statusAllowed: boolean;
  laneMatch: boolean;
  matchedCapabilities: string[];
}): string {
  if (!context.statusAllowed) {
    return "Worker is not active and available for preview assignment.";
  }

  if (!context.riskAllowed) {
    return "Worker risk ceiling does not allow this packet risk.";
  }

  if (!context.hasCapabilityMatch) {
    return "Worker has no matching capability or lane signal.";
  }

  const capabilityText =
    context.matchedCapabilities.length > 0
      ? context.matchedCapabilities.join(", ")
      : "lane signal";

  if (context.laneMatch) {
    return `Worker matches required capability and lane signal: ${capabilityText}.`;
  }

  return `Worker matches required capability: ${capabilityText}.`;
}
