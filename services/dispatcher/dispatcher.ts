import { routePacketApproval } from "./approvalRouter";

export type PacketStatus =
  | "queued"
  | "dry_run"
  | "waiting_approval"
  | "approved"
  | "applied"
  | "blocked";

export interface WorkPacket {
  packetId: string;
  title: string;
  goal: string;
  status: PacketStatus;
  risk: "low" | "medium" | "high";
  requiresApproval: boolean;
  allowedFiles: string[];
  blockedFiles: string[];
  validation: string[];
}

export interface DispatchResult {
  packet: WorkPacket;
  approvalRequestId?: string;
  nextAction: "dry_run" | "wait_for_approval" | "blocked";
}

export function dispatchPacket(packet: WorkPacket): DispatchResult {
  if (packet.risk === "high") {
    const approval = routePacketApproval(packet);

    return {
      packet: { ...packet, status: "waiting_approval" },
      approvalRequestId: approval?.approvalId,
      nextAction: "wait_for_approval"
    };
  }

  if (packet.requiresApproval) {
    const approval = routePacketApproval(packet);

    return {
      packet: { ...packet, status: "waiting_approval" },
      approvalRequestId: approval?.approvalId,
      nextAction: "wait_for_approval"
    };
  }

  return {
    packet: { ...packet, status: "dry_run" },
    nextAction: "dry_run"
  };
}
