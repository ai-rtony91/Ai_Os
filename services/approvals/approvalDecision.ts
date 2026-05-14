import type { ApprovalRequest } from "./approvalInbox";
import { writeTelemetryEvent } from "../telemetry/telemetryWriter";

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
    writeTelemetryEvent(
      "packet_blocked",
      "approval_decision",
      `Approval mismatch for ${request.packetId}`,
      {
        packetId: request.packetId,
        approvalId: request.approvalId,
        status: "rejected",
        risk: request.risk
      }
    );

    return {
      ...request,
      status: "rejected",
      decidedAt: decision.decidedAt,
      decision: "Approval decision mismatch"
    };
  }

  const updatedRequest: ApprovalRequest = {
    ...request,
    status: decision.approved ? "approved" : "rejected",
    decidedAt: decision.decidedAt,
    decision: decision.reason ?? null
  };

  writeTelemetryEvent(
    "approval_decided",
    "approval_decision",
    `Approval ${updatedRequest.status} for ${request.packetId}`,
    {
      packetId: request.packetId,
      approvalId: request.approvalId,
      status: updatedRequest.status,
      risk: request.risk
    }
  );

  return updatedRequest;
}

export function isApprovalGranted(request: ApprovalRequest): boolean {
  return request.status === "approved";
}

export function isApprovalRejected(request: ApprovalRequest): boolean {
  return request.status === "rejected" || request.status === "expired";
}
