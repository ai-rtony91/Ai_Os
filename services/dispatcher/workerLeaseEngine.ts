export interface WorkerHeartbeat {
  workerId: string;
  packetId?: string;
  status: "idle" | "assigned" | "running" | "stale" | "expired";
  lastHeartbeatAt: string;
  leaseExpiresAt?: string;
}

export interface WorkerLeaseResult {
  activeWorkers: string[];
  staleWorkers: string[];
  expiredWorkers: string[];
  reclaimablePackets: string[];
  duplicateWorkers: string[];
  applyBlockedWorkers: string[];
  checkedAt: string;
}

export function evaluateWorkerLeases(
  workers: WorkerHeartbeat[],
  now: Date = new Date()
): WorkerLeaseResult {
  const activeWorkers: string[] = [];
  const staleWorkers: string[] = [];
  const expiredWorkers: string[] = [];
  const reclaimablePackets: string[] = [];
  const duplicateWorkers: string[] = [];
  const applyBlockedWorkers: string[] = [];
  const seenWorkers = new Set<string>();

  for (const worker of workers) {
    if (seenWorkers.has(worker.workerId)) {
      duplicateWorkers.push(worker.workerId);
      applyBlockedWorkers.push(worker.workerId);
      continue;
    }

    seenWorkers.add(worker.workerId);

    const leaseExpiresAt = worker.leaseExpiresAt
      ? new Date(worker.leaseExpiresAt)
      : null;

    if (worker.leaseExpiresAt && Number.isNaN(leaseExpiresAt?.getTime())) {
      staleWorkers.push(worker.workerId);
      applyBlockedWorkers.push(worker.workerId);
      continue;
    }

    if (worker.status === "expired") {
      expiredWorkers.push(worker.workerId);
      applyBlockedWorkers.push(worker.workerId);

      if (worker.packetId) {
        reclaimablePackets.push(worker.packetId);
      }

      continue;
    }

    if (leaseExpiresAt && leaseExpiresAt.getTime() <= now.getTime()) {
      expiredWorkers.push(worker.workerId);
      applyBlockedWorkers.push(worker.workerId);

      if (worker.packetId) {
        reclaimablePackets.push(worker.packetId);
      }

      continue;
    }

    if (worker.status === "stale") {
      staleWorkers.push(worker.workerId);
      applyBlockedWorkers.push(worker.workerId);
      continue;
    }

    activeWorkers.push(worker.workerId);
  }

  return {
    activeWorkers: [...new Set(activeWorkers)],
    staleWorkers: [...new Set(staleWorkers)],
    expiredWorkers: [...new Set(expiredWorkers)],
    reclaimablePackets: [...new Set(reclaimablePackets)],
    duplicateWorkers: [...new Set(duplicateWorkers)],
    applyBlockedWorkers: [...new Set(applyBlockedWorkers)],
    checkedAt: now.toISOString()
  };
}

export function isPacketReclaimable(
  packetId: string,
  leaseResult: WorkerLeaseResult
): boolean {
  return leaseResult.reclaimablePackets.includes(packetId);
}

export function workerCanApply(
  workerId: string,
  leaseResult: WorkerLeaseResult
): boolean {
  return (
    leaseResult.activeWorkers.includes(workerId) &&
    !leaseResult.applyBlockedWorkers.includes(workerId) &&
    !leaseResult.staleWorkers.includes(workerId) &&
    !leaseResult.expiredWorkers.includes(workerId) &&
    !leaseResult.duplicateWorkers.includes(workerId)
  );
}
