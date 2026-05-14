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
  if (request.approvalId !== decision.approvalId) {
    return {
      ...request,
      status: "rejected",
      decidedAt: decision.decidedAt,
      decision: "Approval decision mismatch"
    };
  }

  return {
    ...request,
    status: decision.approved ? "approved" : "rejected",
    decidedAt: decision.decidedAt,
    decision: decision.reason ?? null
  };
}

export function isApprovalGranted(request: ApprovalRequest): boolean {
  return request.status === "approved";
}

export function isApprovalRejected(request: ApprovalRequest): boolean {
  return request.status === "rejected" || request.status === "expired";
}
