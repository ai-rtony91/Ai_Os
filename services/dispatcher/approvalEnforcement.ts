import { getApproval } from "../approvals/approvalInbox";
import { isApprovalGranted, isApprovalRejected } from "../approvals/approvalDecision";
import type { WorkPacket } from "./dispatcher";

const approvalFreshnessMs = 24 * 60 * 60 * 1000;

export interface PacketDecisionResult {
  packet: WorkPacket;
  nextAction: "dry_run" | "apply" | "wait_for_approval" | "blocked";
  reason: string;
}

function blockPacket(packet: WorkPacket, reason: string): PacketDecisionResult {
  return {
    packet: { ...packet, status: "blocked" },
    nextAction: "blocked",
    reason
  };
}

function approvalExpired(decidedAt?: string | null, now: Date = new Date()): boolean {
  if (!decidedAt) {
    return false;
  }

  const decidedTime = new Date(decidedAt).getTime();

  if (Number.isNaN(decidedTime)) {
    return true;
  }

  return now.getTime() - decidedTime > approvalFreshnessMs;
}

function packetTouchesBlockedFiles(packet: WorkPacket): boolean {
  if (packet.blockedFiles.length === 0) {
    return false;
  }

  return packet.allowedFiles.some((allowedFile) =>
    packet.blockedFiles.some((blockedFile) => allowedFile === blockedFile)
  );
}

export function enforceApprovalDecision(
  packet: WorkPacket,
  approvalRequestId?: string
): PacketDecisionResult {
  if (!packet.requiresApproval) {
    return {
      packet: { ...packet, status: "dry_run" },
      nextAction: "dry_run",
      reason: "Packet does not require approval"
    };
  }

  if (!approvalRequestId) {
    return blockPacket(packet, "Missing approval request id");
  }

  const approval = getApproval(approvalRequestId);

  if (!approval) {
    return {
      packet: { ...packet, status: "waiting_approval" },
      nextAction: "wait_for_approval",
      reason: "Approval request not found yet"
    };
  }

  if (isApprovalRejected(approval)) {
    return blockPacket(packet, "Approval was rejected or expired");
  }

  if (isApprovalGranted(approval)) {
    if (approval.packetId !== packet.packetId) {
      return blockPacket(packet, "Approval packet id does not match work packet");
    }

    if (approvalExpired(approval.decidedAt)) {
      return blockPacket(packet, "Approval decision is stale or invalid");
    }

    if (packetTouchesBlockedFiles(packet)) {
      return blockPacket(packet, "Packet allowed files overlap blocked files");
    }

    if (!approval.rollbackPrepared) {
      return blockPacket(packet, "Approval lacks rollback preparation metadata");
    }

    if (
      approval.executionLimits &&
      (approval.executionLimits.maxExecutions < 1 || approval.executionLimits.maxRetries < 0)
    ) {
      return blockPacket(packet, "Approval execution limits are invalid");
    }

    return {
      packet: { ...packet, status: "approved" },
      nextAction: "apply",
      reason: "Approval granted"
    };
  }

  return {
    packet: { ...packet, status: "waiting_approval" },
    nextAction: "wait_for_approval",
    reason: "Approval still pending"
  };
}
