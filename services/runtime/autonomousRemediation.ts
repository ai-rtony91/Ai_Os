import type { BackpressureDecision } from "./runtimeBackpressure";
import type { SupervisorReport } from "../supervisor/runtimeSupervisor";

export type RemediationActionType =
  | "pause_runtime"
  | "throttle_scheduler"
  | "quarantine_poison_packets"
  | "reclaim_worker_packets"
  | "request_operator_review"
  | "continue_monitoring";

export interface RemediationAction {
  action: RemediationActionType;
  severity: "info" | "warning" | "critical";
  reason: string;
  requiresApproval: boolean;
}

export interface RemediationPlan {
  actions: RemediationAction[];
  generatedAt: string;
}

export function generateRemediationPlan(
  backpressure: BackpressureDecision,
  supervisor: SupervisorReport
): RemediationPlan {
  const actions: RemediationAction[] = [];

  if (backpressure.level === "blocked") {
    actions.push({
      action: "pause_runtime",
      severity: "critical",
      reason: backpressure.reason,
      requiresApproval: true
    });

    actions.push({
      action: "request_operator_review",
      severity: "critical",
      reason: "Runtime is blocked and requires operator review",
      requiresApproval: true
    });
  }

  if (backpressure.level === "hard") {
    actions.push({
      action: "throttle_scheduler",
      severity: "warning",
      reason: backpressure.reason,
      requiresApproval: false
    });
  }

  if (supervisor.health.poisonPackets > 0) {
    actions.push({
      action: "quarantine_poison_packets",
      severity: "critical",
      reason: "Poison packets detected in runtime health snapshot",
      requiresApproval: true
    });
  }

  if (supervisor.health.reclaimablePackets > 0) {
    actions.push({
      action: "reclaim_worker_packets",
      severity: "warning",
      reason: "Packets are reclaimable from expired worker leases",
      requiresApproval: true
    });
  }

  if (actions.length === 0) {
    actions.push({
      action: "continue_monitoring",
      severity: "info",
      reason: "No remediation needed",
      requiresApproval: false
    });
  }

  return {
    actions,
    generatedAt: new Date().toISOString()
  };
}
