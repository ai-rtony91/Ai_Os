import { writeTelemetryEvent } from "../telemetry/telemetryWriter";

export type Capability =
  | "file_read"
  | "file_write"
  | "file_delete"
  | "commit"
  | "push"
  | "system_command"
  | "network_call"
  | "trading_signal"
  | "trading_order"
  | "runtime_remediation"
  | "policy_review";

export type TrustLevel = "guest" | "operator" | "maintainer" | "owner";

export interface PolicyRequest {
  actorId: string;
  trustLevel: TrustLevel;
  packetId?: string;
  capability: Capability;
  target?: string;
  risk: "low" | "medium" | "high" | "blocked";
  approvalGranted: boolean;
  executionCount?: number;
  retryCount?: number;
  maxExecutions?: number;
  maxRetries?: number;
  rollbackPrepared?: boolean;
}

export interface PolicyRule {
  capability: Capability;
  minimumTrustLevel: TrustLevel;
  requiresApproval: boolean;
  blockedTargets?: string[];
}

export interface PolicyDecision {
  allowed: boolean;
  reason: string;
  requiresApproval: boolean;
}

const trustRank: Record<TrustLevel, number> = {
  guest: 0,
  operator: 1,
  maintainer: 2,
  owner: 3
};

export const defaultPolicyRules: PolicyRule[] = [
  { capability: "file_read", minimumTrustLevel: "guest", requiresApproval: false },
  { capability: "file_write", minimumTrustLevel: "operator", requiresApproval: true },
  { capability: "file_delete", minimumTrustLevel: "maintainer", requiresApproval: true },
  { capability: "commit", minimumTrustLevel: "maintainer", requiresApproval: true },
  { capability: "push", minimumTrustLevel: "owner", requiresApproval: true },
  { capability: "system_command", minimumTrustLevel: "maintainer", requiresApproval: true },
  { capability: "network_call", minimumTrustLevel: "operator", requiresApproval: true },
  { capability: "trading_signal", minimumTrustLevel: "operator", requiresApproval: true },
  { capability: "trading_order", minimumTrustLevel: "owner", requiresApproval: true },
  { capability: "runtime_remediation", minimumTrustLevel: "maintainer", requiresApproval: true },
  { capability: "policy_review", minimumTrustLevel: "operator", requiresApproval: true }
];

function targetBlocked(target: string | undefined, patterns: string[] = []): boolean {
  if (!target) {
    return false;
  }

  return patterns.some((pattern) => {
    const regex = new RegExp(
      `^${pattern.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*")}$`
    );

    return regex.test(target);
  });
}

function emitPolicyTelemetry(
  request: PolicyRequest,
  decision: PolicyDecision
): void {
  writeTelemetryEvent(
    "policy_decision",
    "policyEngine",
    decision.reason,
    {
      packetId: request.packetId,
      status: decision.allowed ? "allowed" : "denied",
      risk: request.risk,
      metadata: {
        actorId: request.actorId,
        capability: request.capability,
        trustLevel: request.trustLevel,
        target: request.target,
        requiresApproval: decision.requiresApproval
      }
    }
  );
}

export function evaluatePolicy(
  request: PolicyRequest,
  rules: PolicyRule[] = defaultPolicyRules
): PolicyDecision {
  if ((request.executionCount ?? 0) >= (request.maxExecutions ?? 1)) {
    const decision: PolicyDecision = {
      allowed: false,
      reason: "Execution ceiling reached",
      requiresApproval: true
    };

    emitPolicyTelemetry(request, decision);
    return decision;
  }

  if ((request.retryCount ?? 0) > (request.maxRetries ?? 0)) {
    const decision: PolicyDecision = {
      allowed: false,
      reason: "Retry ceiling reached",
      requiresApproval: true
    };

    emitPolicyTelemetry(request, decision);
    return decision;
  }

  if (request.risk === "blocked") {
    const decision: PolicyDecision = {
      allowed: false,
      reason: "Request risk is blocked",
      requiresApproval: true
    };

    emitPolicyTelemetry(request, decision);
    return decision;
  }

  const rule = rules.find((item) => item.capability === request.capability);

  if (!rule) {
    const decision: PolicyDecision = {
      allowed: false,
      reason: `No policy rule for capability: ${request.capability}`,
      requiresApproval: true
    };

    emitPolicyTelemetry(request, decision);
    return decision;
  }

  if (trustRank[request.trustLevel] < trustRank[rule.minimumTrustLevel]) {
    const decision: PolicyDecision = {
      allowed: false,
      reason: `Trust level ${request.trustLevel} cannot use ${request.capability}`,
      requiresApproval: rule.requiresApproval
    };

    emitPolicyTelemetry(request, decision);
    return decision;
  }

  if (targetBlocked(request.target, rule.blockedTargets)) {
    const decision: PolicyDecision = {
      allowed: false,
      reason: `Target is blocked by policy: ${request.target}`,
      requiresApproval: true
    };

    emitPolicyTelemetry(request, decision);
    return decision;
  }

  if (request.capability === "trading_order") {
    const decision: PolicyDecision = {
      allowed: false,
      reason: "Live trading orders are disabled by default policy",
      requiresApproval: true
    };

    emitPolicyTelemetry(request, decision);
    return decision;
  }

  if (rule.requiresApproval && !request.approvalGranted) {
    const decision: PolicyDecision = {
      allowed: false,
      reason: "Approval required before capability use",
      requiresApproval: true
    };

    emitPolicyTelemetry(request, decision);
    return decision;
  }

  if (!request.rollbackPrepared && request.capability !== "file_read") {
    const decision: PolicyDecision = {
      allowed: false,
      reason: "Rollback metadata must be prepared before execution",
      requiresApproval: true
    };

    emitPolicyTelemetry(request, decision);
    return decision;
  }

  const decision: PolicyDecision = {
    allowed: true,
    reason: "Policy allowed request",
    requiresApproval: rule.requiresApproval
  };

  emitPolicyTelemetry(request, decision);
  return decision;
}

export function executionAllowed(
  request: PolicyRequest,
  rules: PolicyRule[] = defaultPolicyRules
): PolicyDecision {
  return evaluatePolicy(request, rules);
}
