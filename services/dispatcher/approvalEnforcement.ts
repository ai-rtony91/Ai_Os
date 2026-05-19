import { getApproval } from "../approvals/approvalInbox";
import { isApprovalGranted, isApprovalRejected } from "../approvals/approvalDecision";
import type { WorkPacket } from "./dispatcher";
import { movePacketStatus } from "./packetQueue";

export interface PacketDecisionResult {
  packet: WorkPacket;
  nextAction: "dry_run" | "apply" | "wait_for_approval" | "blocked";
  reason: string;
}

export function enforceApprovalDecision(
  packet: WorkPacket,
  approvalRequestId?: string
): PacketDecisionResult {
  if (!packet.requiresApproval) {
    return {
      packet: movePacketStatus(packet, "dry_run"),
      nextAction: "dry_run",
      reason: "Packet does not require approval"
    };
  }

  if (!approvalRequestId) {
    return {
      packet: movePacketStatus(packet, "blocked"),
      nextAction: "blocked",
      reason: "Missing approval request id"
    };
  }

  const approval = getApproval(approvalRequestId);

  if (!approval) {
    return {
      packet: movePacketStatus(packet, "waiting_approval"),
      nextAction: "wait_for_approval",
      reason: "Approval request not found yet"
    };
  }

  if (isApprovalRejected(approval)) {
    return {
      packet: movePacketStatus(packet, "blocked"),
      nextAction: "blocked",
      reason: "Approval was rejected or expired"
    };
  }

  if (isApprovalGranted(approval)) {
    return {
      packet: movePacketStatus(packet, "approved"),
      nextAction: "apply",
      reason: "Approval granted"
    };
  }

  return {
    packet: movePacketStatus(packet, "waiting_approval"),
    nextAction: "wait_for_approval",
    reason: "Approval still pending"
  };
}
