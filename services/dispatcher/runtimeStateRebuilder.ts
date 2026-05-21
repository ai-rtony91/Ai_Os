import type { ReplayedRuntimeState } from "../telemetry/telemetryReplay";
import {
  createPacketQueueState,
  enqueuePacket,
  getQueueSnapshot,
  type PacketQueueSnapshot,
  type PacketStatus
} from "./packetQueue";

export interface RebuiltDispatcherState {
  queuedPackets: string[];
  waitingApprovalPackets: string[];
  approvedPackets: string[];
  blockedPackets: string[];
  appliedPackets: string[];
  pendingApprovals: string[];
  rebuiltAt: string;
  sourceEventCount: number;
  reconstructedQueueSnapshot: PacketQueueSnapshot;
}

function isPacketStatus(status: string): status is PacketStatus {
  return [
    "queued",
    "dry_run",
    "waiting_approval",
    "approved",
    "applied",
    "blocked"
  ].includes(status);
}

export function rebuildDispatcherState(
  replayed: ReplayedRuntimeState
): RebuiltDispatcherState {
  const queuedPackets: string[] = [];
  const waitingApprovalPackets: string[] = [];
  const approvedPackets: string[] = [];
  const blockedPackets = [...replayed.blockedPackets];
  const appliedPackets = [...replayed.appliedPackets];
  const pendingApprovals: string[] = [];
  let reconstructedQueue = createPacketQueueState();

  for (const packet of Object.values(replayed.packets)) {
    const status = isPacketStatus(packet.status) ? packet.status : "queued";
    reconstructedQueue = enqueuePacket(
      reconstructedQueue,
      {
        packetId: packet.packetId
      },
      {
        status,
        reason: `Reconstructed from telemetry event ${packet.lastEventType}`
      }
    ).state;

    switch (packet.status) {
      case "queued":
        queuedPackets.push(packet.packetId);
        break;

      case "waiting_approval":
        waitingApprovalPackets.push(packet.packetId);
        break;

      case "approved":
        approvedPackets.push(packet.packetId);
        break;

      case "blocked":
      case "failed":
        blockedPackets.push(packet.packetId);
        break;

      case "applied":
      case "dry_run":
      case "completed":
      case "rolled_back":
        appliedPackets.push(packet.packetId);
        break;
    }
  }

  for (const approval of Object.values(replayed.approvals)) {
    if (approval.status === "pending" || approval.status === "waiting_approval") {
      pendingApprovals.push(approval.approvalId);
    }
  }

  return {
    queuedPackets: [...new Set(queuedPackets)],
    waitingApprovalPackets: [...new Set(waitingApprovalPackets)],
    approvedPackets: [...new Set(approvedPackets)],
    blockedPackets: [...new Set(blockedPackets)],
    appliedPackets: [...new Set(appliedPackets)],
    pendingApprovals: [...new Set(pendingApprovals)],
    rebuiltAt: new Date().toISOString(),
    sourceEventCount: replayed.eventCount,
    reconstructedQueueSnapshot: getQueueSnapshot(reconstructedQueue)
  };
}
