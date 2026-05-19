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
  staleAssignedPackets?: string[];
  expiredWorkers: string[];
  reclaimablePackets: string[];
  checkedAt: string;
}

export function evaluateWorkerLeases(
  workers: WorkerHeartbeat[],
  now: Date = new Date()
): WorkerLeaseResult {
  const activeWorkers: string[] = [];
  const staleWorkers: string[] = [];
  const staleAssignedPackets: string[] = [];
  const expiredWorkers: string[] = [];
  const reclaimablePackets: string[] = [];

  for (const worker of workers) {
    const leaseExpiresAt = worker.leaseExpiresAt
      ? new Date(worker.leaseExpiresAt)
      : null;

    if (worker.status === "expired") {
      expiredWorkers.push(worker.workerId);

      if (worker.packetId) {
        reclaimablePackets.push(worker.packetId);
      }

      continue;
    }

    if (leaseExpiresAt && leaseExpiresAt.getTime() <= now.getTime()) {
      expiredWorkers.push(worker.workerId);

      if (worker.packetId) {
        reclaimablePackets.push(worker.packetId);
      }

      continue;
    }

    if (worker.status === "stale") {
      staleWorkers.push(worker.workerId);

      if (worker.packetId) {
        staleAssignedPackets.push(worker.packetId);
      }

      continue;
    }

    activeWorkers.push(worker.workerId);
  }

  return {
    activeWorkers: [...new Set(activeWorkers)],
    staleWorkers: [...new Set(staleWorkers)],
    staleAssignedPackets: [...new Set(staleAssignedPackets)],
    expiredWorkers: [...new Set(expiredWorkers)],
    reclaimablePackets: [...new Set(reclaimablePackets)],
    checkedAt: now.toISOString()
  };
}

export function isPacketReclaimable(
  packetId: string,
  leaseResult: WorkerLeaseResult
): boolean {
  return leaseResult.reclaimablePackets.includes(packetId);
}
