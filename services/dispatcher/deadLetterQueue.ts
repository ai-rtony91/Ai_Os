export interface DeadLetterPacket {
  packetId: string;
  reason: string;
  failureCount: number;
  lastFailedAt: string;
  retryable: boolean;
  source: string;
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
  retryable = true
): DeadLetterPacket {
  return {
    packetId,
    reason,
    failureCount,
    lastFailedAt: new Date().toISOString(),
    retryable,
    source
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
          ? {
              ...item,
              reason: packet.reason,
              failureCount: item.failureCount + packet.failureCount,
              lastFailedAt: packet.lastFailedAt,
              retryable: packet.retryable,
              source: packet.source
            }
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
    (packet) => packet.retryable && packet.failureCount <= maxFailures
  );
}

export function listPoisonPackets(
  state: DeadLetterQueueState,
  maxFailures = 3
): DeadLetterPacket[] {
  return state.packets.filter(
    (packet) => !packet.retryable || packet.failureCount > maxFailures
  );
}
