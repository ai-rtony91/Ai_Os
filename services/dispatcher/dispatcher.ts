import { routePacketApproval } from "./approvalRouter";
import { writeTelemetryEvent } from "../telemetry/telemetryWriter";
import { movePacketStatus, type PacketStatus } from "./packetQueue";

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
  writeTelemetryEvent(
    "packet_dispatched",
    "dispatcher",
    `Dispatch started for ${packet.packetId}`,
    {
      packetId: packet.packetId,
      risk: packet.risk,
      status: packet.status
    }
  );

  if (packet.risk === "high") {
    const approval = routePacketApproval(packet);

    writeTelemetryEvent(
      "approval_requested",
      "dispatcher",
      `Approval required for high-risk packet ${packet.packetId}`,
      {
        packetId: packet.packetId,
        approvalId: approval?.approvalId,
        risk: packet.risk,
        status: "waiting_approval"
      }
    );

    return {
      packet: movePacketStatus(packet, "waiting_approval"),
      approvalRequestId: approval?.approvalId,
      nextAction: "wait_for_approval"
    };
  }

  if (packet.requiresApproval) {
    const approval = routePacketApproval(packet);

    writeTelemetryEvent(
      "approval_requested",
      "dispatcher",
      `Approval requested for packet ${packet.packetId}`,
      {
        packetId: packet.packetId,
        approvalId: approval?.approvalId,
        risk: packet.risk,
        status: "waiting_approval"
      }
    );

    return {
      packet: movePacketStatus(packet, "waiting_approval"),
      approvalRequestId: approval?.approvalId,
      nextAction: "wait_for_approval"
    };
  }

  writeTelemetryEvent(
    "packet_applied",
    "dispatcher",
    `Packet ${packet.packetId} advanced to dry run`,
    {
      packetId: packet.packetId,
      risk: packet.risk,
      status: "dry_run"
    }
  );

  return {
    packet: movePacketStatus(packet, "dry_run"),
    nextAction: "dry_run"
  };
}
