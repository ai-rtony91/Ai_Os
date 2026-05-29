import { readdirSync, readFileSync, statSync } from "fs";
import { basename, extname, join, relative } from "path";

export type CanonicalQueueState =
  | "proposed"
  | "queued"
  | "blocked"
  | "ready"
  | "assigned"
  | "running"
  | "validator_pending"
  | "validated"
  | "validation_failed"
  | "approval_pending"
  | "approved"
  | "rejected"
  | "completed"
  | "failed"
  | "unknown";

export interface CanonicalQueuePacket {
  packet_id: string;
  title: string;
  state: CanonicalQueueState;
  source_state?: string | null;
  source_path: string;
  lane?: string | null;
  risk_level: "low" | "medium" | "high" | "protected" | "unknown";
  dependencies: string[];
  blockers: string[];
  allowed_paths: string[];
  forbidden_paths: string[];
  scheduler_eligible: boolean;
  resolver_eligible: boolean;
  recommended_next_action: string;
  warnings: string[];
}

export interface CanonicalQueueProjection {
  schema: "AIOS_CANONICAL_QUEUE_PROJECTION.v1";
  generated_at: string;
  source: {
    packet_root: string;
    packet_count: number;
    read_only: true;
  };
  projection_mode: "read_only";
  packets: CanonicalQueuePacket[];
  summary: {
    total: number;
    ready: number;
    blocked: number;
    unknown: number;
    by_state: Record<CanonicalQueueState, number>;
  };
  warnings: string[];
}

export interface BuildCanonicalQueueProjectionOptions {
  packetRoot: string;
  now?: Date;
}

type PacketSource = Record<string, unknown>;

const CANONICAL_STATES: CanonicalQueueState[] = [
  "proposed",
  "queued",
  "blocked",
  "ready",
  "assigned",
  "running",
  "validator_pending",
  "validated",
  "validation_failed",
  "approval_pending",
  "approved",
  "rejected",
  "completed",
  "failed",
  "unknown"
];

const SCHEDULER_READY_RISK = new Set(["low", "medium"]);

export function normalizePacketState(
  input: string | undefined
): CanonicalQueueState {
  const value = normalizeToken(input);

  switch (value) {
    case "proposed":
    case "proposal":
    case "draft":
      return "proposed";
    case "active":
    case "queued":
    case "queue":
    case "retrying":
      return "queued";
    case "ready":
    case "scheduler_ready":
    case "dispatchable":
      return "ready";
    case "routed":
    case "assigned":
    case "scheduled":
    case "ASSIGNED":
      return "assigned";
    case "applying":
    case "executing":
    case "in_progress":
    case "running":
      return "running";
    case "validator_pending":
    case "validation_pending":
    case "pending_validation":
      return "validator_pending";
    case "dry_run_done":
    case "validated":
      return "validated";
    case "validation_failed":
    case "validator_failed":
      return "validation_failed";
    case "awaiting_approval":
    case "waiting_approval":
    case "approval_pending":
      return "approval_pending";
    case "approved":
      return "approved";
    case "rejected":
    case "denied":
      return "rejected";
    case "complete":
    case "completed":
    case "done":
    case "DONE":
    case "applied":
      return "completed";
    case "blocked":
    case "manual_review":
      return "blocked";
    case "failed":
    case "dead_letter":
    case "poison":
      return "failed";
    default:
      return "unknown";
  }
}

export function buildCanonicalQueueProjection(
  options: BuildCanonicalQueueProjectionOptions
): CanonicalQueueProjection {
  const generatedAt = (options.now ?? new Date()).toISOString();
  const warnings: string[] = [];
  const packetFiles = listJsonFiles(options.packetRoot, warnings);
  const packets: CanonicalQueuePacket[] = [];

  for (const packetFile of packetFiles) {
    try {
      const raw = readFileSync(packetFile, "utf8");
      const parsed = JSON.parse(raw) as unknown;

      if (!isRecord(parsed)) {
        warnings.push(`${packetFile}: packet JSON root is not an object`);
        continue;
      }

      packets.push(projectPacket(parsed, packetFile, options.packetRoot));
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      warnings.push(`${packetFile}: malformed JSON skipped: ${message}`);
    }
  }

  const summary = buildSummary(packets);

  return {
    schema: "AIOS_CANONICAL_QUEUE_PROJECTION.v1",
    generated_at: generatedAt,
    source: {
      packet_root: options.packetRoot,
      packet_count: packetFiles.length,
      read_only: true
    },
    projection_mode: "read_only",
    packets,
    summary,
    warnings
  };
}

function projectPacket(
  packet: PacketSource,
  packetFile: string,
  packetRoot: string
): CanonicalQueuePacket {
  const warnings: string[] = [];
  const sourceState = firstString(
    packet.current_state,
    packet.status,
    packet.current_status,
    packet.state,
    packet.lifecycle_state
  );
  const normalizedState = normalizePacketState(sourceState);
  const dependencies = stringArray(packet.dependencies);
  const blockers = [
    ...stringArray(packet.blockers),
    ...stringArray(packet.blocked_by)
  ];
  const riskLevel = normalizeRiskLevel(
    firstString(
      packet.risk_level,
      nestedString(packet.safety, "risk_level"),
      nestedString(packet.safety, "risk"),
      packet.risk
    )
  );
  const packetId =
    firstString(packet.packet_id, packet.packetId, packet.task_id, packet.id) ??
    basename(packetFile, extname(packetFile));
  const title =
    firstString(packet.title, packet.objective, packet.mission, packet.intent) ??
    packetId;

  if (!sourceState) {
    warnings.push("Packet has no source state; projected as unknown.");
  }

  if (riskLevel === "unknown") {
    warnings.push("Packet risk level is unknown; scheduler eligibility is blocked.");
  }

  const state = projectState(normalizedState, {
    dependencies,
    blockers,
    riskLevel
  });
  const schedulerEligible =
    state === "ready" && SCHEDULER_READY_RISK.has(riskLevel);
  const resolverEligible = schedulerEligible;

  return {
    packet_id: packetId,
    title,
    state,
    source_state: sourceState ?? null,
    source_path: normalizePath(relative(packetRoot, packetFile) || packetFile),
    lane:
      firstString(packet.lane, packet.owner_lane, packet.worker_lane) ?? null,
    risk_level: riskLevel,
    dependencies,
    blockers,
    allowed_paths: [
      ...stringArray(packet.allowed_paths),
      ...stringArray(packet.allowed_write_boundary)
    ],
    forbidden_paths: [
      ...stringArray(packet.forbidden_paths),
      ...stringArray(packet.blocked_paths)
    ],
    scheduler_eligible: schedulerEligible,
    resolver_eligible: resolverEligible,
    recommended_next_action: nextActionForState(state, {
      dependencies,
      blockers,
      riskLevel
    }),
    warnings
  };
}

function projectState(
  state: CanonicalQueueState,
  context: {
    dependencies: string[];
    blockers: string[];
    riskLevel: CanonicalQueuePacket["risk_level"];
  }
): CanonicalQueueState {
  if (state === "unknown") {
    return "unknown";
  }

  if (state === "blocked" || state === "failed") {
    return state;
  }

  if (context.blockers.length > 0 || context.riskLevel === "protected") {
    return "blocked";
  }

  if (
    state === "queued" &&
    context.dependencies.length === 0 &&
    SCHEDULER_READY_RISK.has(context.riskLevel)
  ) {
    return "ready";
  }

  return state;
}

function nextActionForState(
  state: CanonicalQueueState,
  context: {
    dependencies: string[];
    blockers: string[];
    riskLevel: CanonicalQueuePacket["risk_level"];
  }
): string {
  if (state === "ready") {
    return "Pass to scheduler preview.";
  }

  if (state === "blocked") {
    if (context.blockers.length > 0) {
      return "Resolve packet blockers before scheduling.";
    }

    if (context.riskLevel === "protected") {
      return "Human review required for protected packet risk.";
    }

    return "Human review required before queue progression.";
  }

  if (state === "queued" && context.dependencies.length > 0) {
    return "Wait for dependencies before scheduler preview.";
  }

  if (state === "unknown") {
    return "Manual review required for unknown packet state.";
  }

  return "No automatic action authorized by read-only projection.";
}

function buildSummary(
  packets: CanonicalQueuePacket[]
): CanonicalQueueProjection["summary"] {
  const byState = CANONICAL_STATES.reduce(
    (accumulator, state) => ({
      ...accumulator,
      [state]: 0
    }),
    {} as Record<CanonicalQueueState, number>
  );

  for (const packet of packets) {
    byState[packet.state] += 1;
  }

  return {
    total: packets.length,
    ready: byState.ready,
    blocked: byState.blocked,
    unknown: byState.unknown,
    by_state: byState
  };
}

function listJsonFiles(root: string, warnings: string[]): string[] {
  try {
    if (!statSync(root).isDirectory()) {
      warnings.push(`${root}: packetRoot is not a directory`);
      return [];
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    warnings.push(`${root}: packetRoot is not readable: ${message}`);
    return [];
  }

  const results: string[] = [];
  const pending = [root];

  while (pending.length > 0) {
    const current = pending.pop();

    if (!current) {
      continue;
    }

    for (const entry of readdirSync(current, { withFileTypes: true })) {
      const fullPath = join(current, entry.name);

      if (entry.isDirectory()) {
        pending.push(fullPath);
        continue;
      }

      if (entry.isFile() && extname(entry.name).toLowerCase() === ".json") {
        results.push(fullPath);
      }
    }
  }

  return results.sort((a, b) => a.localeCompare(b));
}

function normalizeToken(input: string | undefined): string {
  return (input ?? "")
    .trim()
    .replace(/[\s-]+/g, "_")
    .toLowerCase();
}

function normalizeRiskLevel(
  input: string | undefined
): CanonicalQueuePacket["risk_level"] {
  const value = normalizeToken(input);

  switch (value) {
    case "low":
    case "medium":
    case "high":
    case "protected":
      return value;
    default:
      return "unknown";
  }
}

function firstString(...values: unknown[]): string | undefined {
  for (const value of values) {
    if (typeof value === "string" && value.trim().length > 0) {
      return value.trim();
    }
  }

  return undefined;
}

function stringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    if (typeof value === "string" && value.trim().length > 0) {
      return [value.trim()];
    }

    return [];
  }

  return value
    .filter((item): item is string => typeof item === "string")
    .map((item) => item.trim())
    .filter((item) => item.length > 0);
}

function nestedString(value: unknown, key: string): string | undefined {
  if (!isRecord(value)) {
    return undefined;
  }

  return firstString(value[key]);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function normalizePath(value: string): string {
  return value.replace(/\\/g, "/");
}
