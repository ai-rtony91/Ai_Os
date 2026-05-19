export type ApprovalStatus = "pending" | "approved" | "rejected" | "expired";
export type ApprovalRisk = "low" | "medium" | "high" | "blocked";
export type ApprovalActionType =
  | "file_write"
  | "file_delete"
  | "commit"
  | "push"
  | "system_command"
  | "runtime_remediation"
  | "policy_review"
  | "trading_action";

export interface ApprovalExecutionLimits {
  maxRetries: number;
  maxExecutions: number;
}

export interface ApprovalRequest {
  approvalId: string;
  packetId: string;
  title: string;
  actionType: ApprovalActionType;
  risk: ApprovalRisk;
  status: ApprovalStatus;
  summary: string;
  targetFiles: string[];
  commandPreview?: string | null;
  rollbackRef?: string | null;
  rollbackPrepared?: boolean;
  executionLimits?: ApprovalExecutionLimits;
  requestedAt: string;
  decidedAt?: string | null;
  decision?: string | null;
}

const inbox: ApprovalRequest[] = [];

export function submitApproval(request: ApprovalRequest): ApprovalRequest {
  const existing = inbox.find((item) => item.approvalId === request.approvalId);

  if (existing) {
    return existing;
  }

  inbox.push(request);
  return request;
}

export function listPendingApprovals(): ApprovalRequest[] {
  return inbox.filter((request) => request.status === "pending");
}

export function getApproval(approvalId: string): ApprovalRequest | undefined {
  return inbox.find((request) => request.approvalId === approvalId);
}
