import type {
  CanonicalQueuePacket,
  CanonicalQueueProjection
} from "./canonicalQueueProjection.ts";

export interface SchedulerPreviewRecommendedPacket {
  packet_id: string;
  rank: number;
  priority: number;
  risk_level: CanonicalQueuePacket["risk_level"];
  dependency_count: number;
  reason: string;
}

export interface WorkerCapabilityRequirement {
  packet_id: string;
  required_capabilities: string[];
  reason: string;
}

export interface SchedulerPreviewPlan {
  generated_at: string;
  total_packets: number;
  ready_packets: number;
  blocked_packets: number;
  recommended_order: SchedulerPreviewRecommendedPacket[];
  worker_capability_requirements: WorkerCapabilityRequirement[];
  warnings: string[];
}

export interface BuildSchedulerPreviewOptions {
  projection: CanonicalQueueProjection;
  now?: Date;
}

type PacketWithPriority = CanonicalQueuePacket & {
  priority?: unknown;
};

const UNSCHEDULABLE_STATES = new Set([
  "blocked",
  "failed",
  "unknown",
  "approval_pending",
  "approved",
  "completed"
]);

export function buildSchedulerPreview(
  options: BuildSchedulerPreviewOptions
): SchedulerPreviewPlan {
  const generatedAt = (options.now ?? new Date()).toISOString();
  const packets = [...options.projection.packets];
  const warnings = [...options.projection.warnings];
  const readyPackets = packets.filter((packet) => packet.state === "ready");
  const blockedPackets = packets.filter((packet) =>
    UNSCHEDULABLE_STATES.has(packet.state)
  );

  for (const packet of packets) {
    if (packet.state !== "ready" && packet.warnings.length > 0) {
      warnings.push(
        `${packet.packet_id}: ${packet.warnings.join("; ")}`
      );
    }
  }

  const rankedPackets = readyPackets
    .map((packet) => ({
      packet,
      priority: getPacketPriority(packet),
      dependencyCount: packet.dependencies.length
    }))
    .sort((a, b) => {
      return (
        b.priority - a.priority ||
        riskRank(a.packet.risk_level) - riskRank(b.packet.risk_level) ||
        a.dependencyCount - b.dependencyCount ||
        a.packet.packet_id.localeCompare(b.packet.packet_id)
      );
    });

  const recommendedOrder = rankedPackets.map((entry, index) => ({
    packet_id: entry.packet.packet_id,
    rank: index + 1,
    priority: entry.priority,
    risk_level: entry.packet.risk_level,
    dependency_count: entry.dependencyCount,
    reason: "Packet is ready in canonical queue projection."
  }));

  return {
    generated_at: generatedAt,
    total_packets: packets.length,
    ready_packets: readyPackets.length,
    blocked_packets: blockedPackets.length,
    recommended_order: recommendedOrder,
    worker_capability_requirements: rankedPackets.map((entry) =>
      buildCapabilityRequirement(entry.packet)
    ),
    warnings
  };
}

function getPacketPriority(packet: CanonicalQueuePacket): number {
  const priority = (packet as PacketWithPriority).priority;

  if (typeof priority === "number" && Number.isFinite(priority)) {
    return priority;
  }

  if (typeof priority === "string") {
    const parsed = Number.parseInt(priority, 10);

    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }

  return 0;
}

function riskRank(riskLevel: CanonicalQueuePacket["risk_level"]): number {
  switch (riskLevel) {
    case "low":
      return 0;
    case "medium":
      return 1;
    case "high":
      return 2;
    case "protected":
      return 3;
    case "unknown":
      return 4;
  }
}

function buildCapabilityRequirement(
  packet: CanonicalQueuePacket
): WorkerCapabilityRequirement {
  const capabilities = new Set<string>();

  if (packet.lane) {
    capabilities.add(`lane:${packet.lane}`);
  }

  for (const targetPath of packet.allowed_paths) {
    const normalized = targetPath.replace(/\\/g, "/").toLowerCase();

    if (normalized.startsWith("docs/")) {
      capabilities.add("docs");
    }

    if (normalized.startsWith("tests/")) {
      capabilities.add("tests");
    }

    if (normalized.startsWith("schemas/")) {
      capabilities.add("schema");
    }

    if (normalized.startsWith("services/dispatcher/")) {
      capabilities.add("dispatcher");
    }
  }

  if (capabilities.size === 0) {
    capabilities.add("manual_review");
  }

  return {
    packet_id: packet.packet_id,
    required_capabilities: [...capabilities].sort((a, b) =>
      a.localeCompare(b)
    ),
    reason: "Derived from packet lane and allowed paths for preview only."
  };
}
