export interface DeadLetterPacket {
  packetId: string;
  reason: string;
  failureCount: number;
  lastFailedAt: string;
  retryable: boolean;
  source: string;
  severity: "warning" | "critical";
  manualReviewRequired: boolean;
  escalationRequired: boolean;
  lastAction?: string;
}

export interface DeadLetterQueueState {
  packets: DeadLetterPacket[];
  checkedAt: string;
}

export function createDeadLetterPacket(
  packetId: string,
  reason: string,
  source: string,
  failureCount = 1,
  retryable = true,
  lastAction?: string
): DeadLetterPacket {
  const poison = !retryable || failureCount >= 3;

  return {
    packetId,
    reason,
    failureCount,
    lastFailedAt: new Date().toISOString(),
    retryable: retryable && !poison,
    source,
    severity: poison ? "critical" : "warning",
    manualReviewRequired: poison,
    escalationRequired: poison,
    lastAction
  };
}

export function addToDeadLetterQueue(
  state: DeadLetterQueueState,
  packet: DeadLetterPacket
): DeadLetterQueueState {
  const existing = state.packets.find((item) => item.packetId === packet.packetId);

  if (existing) {
    return {
      packets: state.packets.map((item) =>
        item.packetId === packet.packetId
          ? mergeDeadLetterPacket(item, packet)
          : item
      ),
      checkedAt: new Date().toISOString()
    };
  }

  return {
    packets: [...state.packets, packet],
    checkedAt: new Date().toISOString()
  };
}

export function listRetryableDeadLetters(
  state: DeadLetterQueueState,
  maxFailures = 3
): DeadLetterPacket[] {
  return state.packets.filter(
    (packet) =>
      packet.retryable &&
      !packet.manualReviewRequired &&
      packet.failureCount < maxFailures
  );
}

export function listPoisonPackets(
  state: DeadLetterQueueState,
  maxFailures = 3
): DeadLetterPacket[] {
  return state.packets.filter(
    (packet) =>
      !packet.retryable ||
      packet.manualReviewRequired ||
      packet.escalationRequired ||
      packet.failureCount >= maxFailures
  );
}

function mergeDeadLetterPacket(
  existing: DeadLetterPacket,
  next: DeadLetterPacket,
  maxFailures = 3
): DeadLetterPacket {
  const failureCount = existing.failureCount + next.failureCount;
  const poison =
    !existing.retryable ||
    !next.retryable ||
    failureCount >= maxFailures ||
    existing.manualReviewRequired ||
    next.manualReviewRequired;

  return {
    ...existing,
    reason: next.reason,
    failureCount,
    lastFailedAt: next.lastFailedAt,
    retryable: !poison,
    source: next.source,
    severity: poison ? "critical" : "warning",
    manualReviewRequired: poison,
    escalationRequired: poison,
    lastAction: next.lastAction ?? existing.lastAction
  };
}
