export type ApprovalStatus = "pending" | "approved" | "rejected" | "expired";
export type ApprovalRisk = "low" | "medium" | "high" | "blocked";

export interface ApprovalRequest {
  approvalId: string;
  packetId: string;
  title: string;
  actionType: "file_write" | "file_delete" | "commit" | "push" | "system_command" | "trading_action";
  risk: ApprovalRisk;
  status: ApprovalStatus;
  summary: string;
  targetFiles: string[];
  commandPreview?: string | null;
  rollbackRef?: string | null;
  requestedAt: string;
  decidedAt?: string | null;
  decision?: string | null;
}

const inbox: ApprovalRequest[] = [];

export function submitApproval(request: ApprovalRequest): ApprovalRequest {
  inbox.push(request);
  return request;
}

export function listPendingApprovals(): ApprovalRequest[] {
  return inbox.filter((request) => request.status === "pending");
}

export function getApproval(approvalId: string): ApprovalRequest | undefined {
  return inbox.find((request) => request.approvalId === approvalId);
}
