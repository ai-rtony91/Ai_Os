export type PacketQueueSource = "observed" | "reconstructed" | "inferred" | "fixture";

export interface PacketQueueCounters {
  queued: number;
  running: number;
  waitingApproval: number;
  retryable: number;
  manualReview: number;
  blocked: number;
  applied: number;
}

export interface PacketQueueVisibility {
  source: PacketQueueSource;
  counters: PacketQueueCounters;
  generatedAt: string;
  stale: boolean;
  warnings: string[];
}

export function createEmptyPacketQueueVisibility(
  source: PacketQueueSource = "observed"
): PacketQueueVisibility {
  return {
    source,
    counters: {
      queued: 0,
      running: 0,
      waitingApproval: 0,
      retryable: 0,
      manualReview: 0,
      blocked: 0,
      applied: 0
    },
    generatedAt: new Date().toISOString(),
    stale: false,
    warnings: []
  };
}
