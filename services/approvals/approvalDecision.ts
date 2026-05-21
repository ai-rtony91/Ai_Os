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
    request.status = "rejected";
    request.decidedAt = decision.decidedAt;
    request.decision = "Approval decision mismatch";

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

    return { ...request };
  }

  request.status = decision.approved ? "approved" : "rejected";
  request.decidedAt = decision.decidedAt;
  request.decision = decision.reason ?? null;

  writeTelemetryEvent(
    "approval_decided",
    "approval_decision",
    `Approval ${request.status} for ${request.packetId}`,
    {
      packetId: request.packetId,
      approvalId: request.approvalId,
      status: request.status,
      risk: request.risk
    }
  );

  return { ...request };
}

export function isApprovalGranted(request: ApprovalRequest): boolean {
  return request.status === "approved";
}

export function isApprovalRejected(request: ApprovalRequest): boolean {
  return request.status === "rejected" || request.status === "expired";
}
