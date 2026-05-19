export type PacketStatus =
  | "queued"
  | "dry_run"
  | "waiting_approval"
  | "approved"
  | "applied"
  | "blocked";

export type PacketExecutionStatus =
  | "queued"
  | "scheduled"
  | "executing"
  | "retrying"
  | "failed"
  | "blocked"
  | "completed"
  | "rolled_back";

export type PacketQueueStatus =
  | PacketStatus
  | PacketExecutionStatus
  | "dead_letter"
  | "manual_review";

export interface PacketIdentity {
  packetId: string;
  idempotencyKey?: string | null;
}

export interface PacketQueueRecord<TPacket extends PacketIdentity = PacketIdentity> {
  packetId: string;
  idempotencyKey?: string | null;
  packet: TPacket;
  status: PacketQueueStatus;
  queuedAt: string;
  updatedAt: string;
  claimedBy?: string | null;
  claimedAt?: string | null;
  completedAt?: string | null;
  failedAt?: string | null;
  deadLetteredAt?: string | null;
  retryCount: number;
  failureCount: number;
  maxRetries?: number;
  lastReason?: string;
}

export interface PacketQueueState<TPacket extends PacketIdentity = PacketIdentity> {
  records: PacketQueueRecord<TPacket>[];
  generatedAt: string;
}

export interface PacketQueueCounters {
  total: number;
  queued: number;
  scheduled: number;
  executing: number;
  retrying: number;
  waitingForApproval: number;
  approved: number;
  dryRun: number;
  applied: number;
  completed: number;
  failed: number;
  blocked: number;
  rolledBack: number;
  deadLetter: number;
  manualReview: number;
  claimable: number;
}

export interface PacketQueueSnapshot<TPacket extends PacketIdentity = PacketIdentity> {
  source: "packet_queue";
  generatedAt: string;
  counters: PacketQueueCounters;
  records: PacketQueueRecord<TPacket>[];
}

export interface EnqueuePacketOptions {
  status?: PacketQueueStatus;
  idempotencyKey?: string | null;
  maxRetries?: number;
  reason?: string;
  now?: Date;
}

export interface ClaimPacketOptions {
  workerId: string;
  maxPackets: number;
  now?: Date;
}

export interface PacketQueueResult<TPacket extends PacketIdentity = PacketIdentity> {
  state: PacketQueueState<TPacket>;
  record?: PacketQueueRecord<TPacket>;
  records?: PacketQueueRecord<TPacket>[];
  changed: boolean;
  reason: string;
}

const CLAIMABLE_STATUSES = new Set<PacketQueueStatus>([
  "queued",
  "scheduled",
  "retrying"
]);

function nowIso(now?: Date): string {
  return (now ?? new Date()).toISOString();
}

function cloneRecord<TPacket extends PacketIdentity>(
  record: PacketQueueRecord<TPacket>
): PacketQueueRecord<TPacket> {
  return {
    ...record,
    packet: { ...record.packet }
  };
}

function cloneState<TPacket extends PacketIdentity>(
  state: PacketQueueState<TPacket>,
  generatedAt = nowIso()
): PacketQueueState<TPacket> {
  return {
    records: state.records.map(cloneRecord),
    generatedAt
  };
}

function sameIdentity<TPacket extends PacketIdentity>(
  record: PacketQueueRecord<TPacket>,
  packet: PacketIdentity,
  idempotencyKey?: string | null
): boolean {
  if (idempotencyKey && record.idempotencyKey === idempotencyKey) {
    return true;
  }

  if (packet.idempotencyKey && record.idempotencyKey === packet.idempotencyKey) {
    return true;
  }

  return record.packetId === packet.packetId;
}

export function createPacketQueueState<
  TPacket extends PacketIdentity = PacketIdentity
>(): PacketQueueState<TPacket> {
  return {
    records: [],
    generatedAt: nowIso()
  };
}

export function movePacketStatus<TPacket extends { status?: PacketQueueStatus }>(
  packet: TPacket,
  status: NonNullable<TPacket["status"]>
): TPacket {
  return {
    ...packet,
    status
  };
}

export function movePacketExecutionState<
  TPacket extends { state?: PacketExecutionStatus }
>(packet: TPacket, state: NonNullable<TPacket["state"]>): TPacket {
  return {
    ...packet,
    state
  };
}

export function enqueuePacket<TPacket extends PacketIdentity>(
  state: PacketQueueState<TPacket>,
  packet: TPacket,
  options: EnqueuePacketOptions = {}
): PacketQueueResult<TPacket> {
  const timestamp = nowIso(options.now);
  const idempotencyKey = options.idempotencyKey ?? packet.idempotencyKey ?? null;
  const existing = state.records.find((record) =>
    sameIdentity(record, packet, idempotencyKey)
  );

  if (existing) {
    return {
      state: cloneState(state, timestamp),
      record: cloneRecord(existing),
      changed: false,
      reason: "Packet already exists in queue"
    };
  }

  const record: PacketQueueRecord<TPacket> = {
    packetId: packet.packetId,
    idempotencyKey,
    packet: { ...packet },
    status: options.status ?? "queued",
    queuedAt: timestamp,
    updatedAt: timestamp,
    claimedBy: null,
    claimedAt: null,
    retryCount: 0,
    failureCount: 0,
    maxRetries: options.maxRetries,
    lastReason: options.reason
  };

  return {
    state: {
      records: [...state.records.map(cloneRecord), record],
      generatedAt: timestamp
    },
    record: cloneRecord(record),
    changed: true,
    reason: "Packet enqueued"
  };
}

export function claimPackets<TPacket extends PacketIdentity>(
  state: PacketQueueState<TPacket>,
  options: ClaimPacketOptions
): PacketQueueResult<TPacket> {
  const timestamp = nowIso(options.now);
  const limit = Math.max(0, options.maxPackets);
  const claimed: PacketQueueRecord<TPacket>[] = [];
  const records = state.records.map((record) => {
    if (claimed.length >= limit) {
      return cloneRecord(record);
    }

    if (record.claimedBy || !CLAIMABLE_STATUSES.has(record.status)) {
      return cloneRecord(record);
    }

    const nextRecord: PacketQueueRecord<TPacket> = {
      ...cloneRecord(record),
      status: "scheduled",
      claimedBy: options.workerId,
      claimedAt: timestamp,
      updatedAt: timestamp
    };

    claimed.push(cloneRecord(nextRecord));
    return nextRecord;
  });

  return {
    state: {
      records,
      generatedAt: timestamp
    },
    records: claimed,
    changed: claimed.length > 0,
    reason: claimed.length > 0 ? "Packets claimed" : "No claimable packets"
  };
}

export function releasePacketClaims<TPacket extends PacketIdentity>(
  state: PacketQueueState<TPacket>,
  workerId: string,
  now?: Date
): PacketQueueResult<TPacket> {
  const timestamp = nowIso(now);
  let changed = false;
  const records = state.records.map((record) => {
    if (record.claimedBy !== workerId) {
      return cloneRecord(record);
    }

    changed = true;
    return {
      ...cloneRecord(record),
      status:
        record.status === "scheduled" || record.status === "executing"
          ? "queued"
          : record.status,
      claimedBy: null,
      claimedAt: null,
      updatedAt: timestamp
    };
  });

  return {
    state: {
      records,
      generatedAt: timestamp
    },
    changed,
    reason: changed ? "Packet claims released" : "No packet claims for worker"
  };
}

export function completePacket<TPacket extends PacketIdentity>(
  state: PacketQueueState<TPacket>,
  packetId: string,
  workerId: string,
  status: PacketQueueStatus = "completed",
  now?: Date
): PacketQueueResult<TPacket> {
  const timestamp = nowIso(now);
  let completed: PacketQueueRecord<TPacket> | undefined;
  let changed = false;

  const records = state.records.map((record) => {
    if (record.packetId !== packetId) {
      return cloneRecord(record);
    }

    if (record.claimedBy && record.claimedBy !== workerId) {
      completed = cloneRecord(record);
      return cloneRecord(record);
    }

    changed = true;
    completed = {
      ...cloneRecord(record),
      status,
      claimedBy: null,
      claimedAt: null,
      completedAt: timestamp,
      updatedAt: timestamp
    };

    return completed;
  });

  return {
    state: {
      records,
      generatedAt: timestamp
    },
    record: completed ? cloneRecord(completed) : undefined,
    changed,
    reason: changed ? "Packet completed" : "Packet not completed"
  };
}

export function setPacketQueueStatus<TPacket extends PacketIdentity>(
  state: PacketQueueState<TPacket>,
  packetId: string,
  status: PacketQueueStatus,
  reason?: string,
  now?: Date
): PacketQueueResult<TPacket> {
  const timestamp = nowIso(now);
  let updated: PacketQueueRecord<TPacket> | undefined;
  let changed = false;

  const records = state.records.map((record) => {
    if (record.packetId !== packetId) {
      return cloneRecord(record);
    }

    changed = true;
    updated = {
      ...cloneRecord(record),
      status,
      updatedAt: timestamp,
      lastReason: reason ?? record.lastReason
    };

    return updated;
  });

  return {
    state: {
      records,
      generatedAt: timestamp
    },
    record: updated ? cloneRecord(updated) : undefined,
    changed,
    reason: changed ? "Packet status updated" : "Packet not found"
  };
}

export function failPacket<TPacket extends PacketIdentity>(
  state: PacketQueueState<TPacket>,
  packetId: string,
  reason: string,
  now?: Date
): PacketQueueResult<TPacket> {
  const timestamp = nowIso(now);
  let failed: PacketQueueRecord<TPacket> | undefined;
  let changed = false;

  const records = state.records.map((record) => {
    if (record.packetId !== packetId) {
      return cloneRecord(record);
    }

    changed = true;
    failed = {
      ...cloneRecord(record),
      status: "failed",
      failedAt: timestamp,
      updatedAt: timestamp,
      failureCount: record.failureCount + 1,
      lastReason: reason
    };

    return failed;
  });

  return {
    state: {
      records,
      generatedAt: timestamp
    },
    record: failed ? cloneRecord(failed) : undefined,
    changed,
    reason: changed ? "Packet failed" : "Packet not found"
  };
}

export function retryPacket<TPacket extends PacketIdentity>(
  state: PacketQueueState<TPacket>,
  packetId: string,
  reason: string,
  now?: Date
): PacketQueueResult<TPacket> {
  const timestamp = nowIso(now);
  let retried: PacketQueueRecord<TPacket> | undefined;
  let changed = false;

  const records = state.records.map((record) => {
    if (record.packetId !== packetId) {
      return cloneRecord(record);
    }

    const retryCount = record.retryCount + 1;
    const maxRetries = record.maxRetries ?? Number.POSITIVE_INFINITY;
    const nextStatus: PacketQueueStatus =
      retryCount > maxRetries ? "dead_letter" : "retrying";

    changed = true;
    retried = {
      ...cloneRecord(record),
      status: nextStatus,
      retryCount,
      claimedBy: null,
      claimedAt: null,
      updatedAt: timestamp,
      deadLetteredAt: nextStatus === "dead_letter" ? timestamp : record.deadLetteredAt,
      lastReason: reason
    };

    return retried;
  });

  return {
    state: {
      records,
      generatedAt: timestamp
    },
    record: retried ? cloneRecord(retried) : undefined,
    changed,
    reason: changed ? "Packet retry recorded" : "Packet not found"
  };
}

export function deadLetterPacket<TPacket extends PacketIdentity>(
  state: PacketQueueState<TPacket>,
  packetId: string,
  reason: string,
  now?: Date
): PacketQueueResult<TPacket> {
  const timestamp = nowIso(now);
  let deadLettered: PacketQueueRecord<TPacket> | undefined;
  let changed = false;

  const records = state.records.map((record) => {
    if (record.packetId !== packetId) {
      return cloneRecord(record);
    }

    changed = true;
    deadLettered = {
      ...cloneRecord(record),
      status: "dead_letter",
      claimedBy: null,
      claimedAt: null,
      deadLetteredAt: timestamp,
      updatedAt: timestamp,
      lastReason: reason
    };

    return deadLettered;
  });

  return {
    state: {
      records,
      generatedAt: timestamp
    },
    record: deadLettered ? cloneRecord(deadLettered) : undefined,
    changed,
    reason: changed ? "Packet moved to dead letter" : "Packet not found"
  };
}

export function removeTerminalPackets<TPacket extends PacketIdentity>(
  state: PacketQueueState<TPacket>,
  terminalStatuses: PacketQueueStatus[] = [
    "completed",
    "blocked",
    "failed",
    "rolled_back",
    "applied",
    "dead_letter"
  ],
  now?: Date
): PacketQueueState<TPacket> {
  const terminal = new Set(terminalStatuses);

  return {
    records: state.records.filter((record) => !terminal.has(record.status)).map(cloneRecord),
    generatedAt: nowIso(now)
  };
}

export function listQueueRecords<TPacket extends PacketIdentity>(
  state: PacketQueueState<TPacket>
): PacketQueueRecord<TPacket>[] {
  return state.records.map(cloneRecord);
}

export function listClaimablePackets<TPacket extends PacketIdentity>(
  state: PacketQueueState<TPacket>
): PacketQueueRecord<TPacket>[] {
  return state.records
    .filter((record) => !record.claimedBy && CLAIMABLE_STATUSES.has(record.status))
    .map(cloneRecord);
}

export function listWaitingApprovalPackets<TPacket extends PacketIdentity>(
  state: PacketQueueState<TPacket>
): PacketQueueRecord<TPacket>[] {
  return state.records
    .filter((record) => record.status === "waiting_approval")
    .map(cloneRecord);
}

export function listFailedPackets<TPacket extends PacketIdentity>(
  state: PacketQueueState<TPacket>
): PacketQueueRecord<TPacket>[] {
  return state.records
    .filter((record) => record.status === "failed" || record.status === "dead_letter")
    .map(cloneRecord);
}

export function getQueueCounters<TPacket extends PacketIdentity>(
  state: PacketQueueState<TPacket>
): PacketQueueCounters {
  const counters: PacketQueueCounters = {
    total: state.records.length,
    queued: 0,
    scheduled: 0,
    executing: 0,
    retrying: 0,
    waitingForApproval: 0,
    approved: 0,
    dryRun: 0,
    applied: 0,
    completed: 0,
    failed: 0,
    blocked: 0,
    rolledBack: 0,
    deadLetter: 0,
    manualReview: 0,
    claimable: 0
  };

  for (const record of state.records) {
    if (!record.claimedBy && CLAIMABLE_STATUSES.has(record.status)) {
      counters.claimable += 1;
    }

    switch (record.status) {
      case "queued":
        counters.queued += 1;
        break;
      case "scheduled":
        counters.scheduled += 1;
        break;
      case "executing":
        counters.executing += 1;
        break;
      case "retrying":
        counters.retrying += 1;
        break;
      case "waiting_approval":
        counters.waitingForApproval += 1;
        break;
      case "approved":
        counters.approved += 1;
        break;
      case "dry_run":
        counters.dryRun += 1;
        break;
      case "applied":
        counters.applied += 1;
        break;
      case "completed":
        counters.completed += 1;
        break;
      case "failed":
        counters.failed += 1;
        break;
      case "blocked":
        counters.blocked += 1;
        break;
      case "rolled_back":
        counters.rolledBack += 1;
        break;
      case "dead_letter":
        counters.deadLetter += 1;
        break;
      case "manual_review":
        counters.manualReview += 1;
        break;
    }
  }

  return counters;
}

export function getQueueSnapshot<TPacket extends PacketIdentity>(
  state: PacketQueueState<TPacket>
): PacketQueueSnapshot<TPacket> {
  return {
    source: "packet_queue",
    generatedAt: state.generatedAt,
    counters: getQueueCounters(state),
    records: listQueueRecords(state)
  };
}
