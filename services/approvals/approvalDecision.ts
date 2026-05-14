import type { ApprovalRequest } from "./approvalInbox";

export interface ApprovalDecision {
  approvalId: string;
  approved: boolean;
  reason?: string;
  decidedAt: string;
}

export function applyApprovalDecision(
  request: ApprovalRequest,
  decision: ApprovalDecision
): ApprovalRequest {
  return {
    ...request,
    status: decision.approved ? "approved" : "rejected",
    decidedAt: decision.decidedAt,
    decision: decision.reason ?? null
  };
}
