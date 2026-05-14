export type Capability =
  | "file_read"
  | "file_write"
  | "file_delete"
  | "commit"
  | "push"
  | "system_command"
  | "network_call"
  | "trading_signal"
  | "trading_order";

export type TrustLevel = "guest" | "operator" | "maintainer" | "owner";

export interface PolicyRequest {
  actorId: string;
  trustLevel: TrustLevel;
  packetId?: string;
  capability: Capability;
  target?: string;
  risk: "low" | "medium" | "high" | "blocked";
  approvalGranted: boolean;
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
  { capability: "trading_order", minimumTrustLevel: "owner", requiresApproval: true }
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

export function evaluatePolicy(
  request: PolicyRequest,
  rules: PolicyRule[] = defaultPolicyRules
): PolicyDecision {
  if (request.risk === "blocked") {
    return {
      allowed: false,
      reason: "Request risk is blocked",
      requiresApproval: true
    };
  }

  const rule = rules.find((item) => item.capability === request.capability);

  if (!rule) {
    return {
      allowed: false,
      reason: `No policy rule for capability: ${request.capability}`,
      requiresApproval: true
    };
  }

  if (trustRank[request.trustLevel] < trustRank[rule.minimumTrustLevel]) {
    return {
      allowed: false,
      reason: `Trust level ${request.trustLevel} cannot use ${request.capability}`,
      requiresApproval: rule.requiresApproval
    };
  }

  if (targetBlocked(request.target, rule.blockedTargets)) {
    return {
      allowed: false,
      reason: `Target is blocked by policy: ${request.target}`,
      requiresApproval: true
    };
  }

  if (rule.requiresApproval && !request.approvalGranted) {
    return {
      allowed: false,
      reason: "Approval required before capability use",
      requiresApproval: true
    };
  }

  if (request.capability === "trading_order") {
    return {
      allowed: false,
      reason: "Live trading orders are disabled by default policy",
      requiresApproval: true
    };
  }

  return {
    allowed: true,
    reason: "Policy allowed request",
    requiresApproval: rule.requiresApproval
  };
}
