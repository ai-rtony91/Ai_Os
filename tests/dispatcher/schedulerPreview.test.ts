import assert from "node:assert/strict";
import test from "node:test";
import type {
  CanonicalQueuePacket,
  CanonicalQueueProjection
} from "../../services/dispatcher/canonicalQueueProjection.ts";
import { buildSchedulerPreview } from "../../services/dispatcher/schedulerPreview.ts";

function packet(
  packetId: string,
  state: CanonicalQueuePacket["state"],
  overrides: Partial<CanonicalQueuePacket> = {}
): CanonicalQueuePacket {
  return {
    packet_id: packetId,
    title: packetId,
    state,
    source_state: state,
    source_path: `${packetId}.json`,
    lane: "East",
    risk_level: "low",
    dependencies: [],
    blockers: [],
    allowed_paths: ["services/dispatcher/"],
    forbidden_paths: [],
    scheduler_eligible: state === "ready",
    resolver_eligible: state === "ready",
    recommended_next_action: "Pass to scheduler preview.",
    warnings: [],
    ...overrides
  };
}

function projection(
  packets: CanonicalQueuePacket[]
): CanonicalQueueProjection {
  return {
    schema: "AIOS_CANONICAL_QUEUE_PROJECTION.v1",
    generated_at: "2026-05-29T00:00:00.000Z",
    source: {
      packet_root: "memory",
      packet_count: packets.length,
      read_only: true
    },
    projection_mode: "read_only",
    packets,
    summary: {
      total: packets.length,
      ready: packets.filter((item) => item.state === "ready").length,
      blocked: packets.filter((item) => item.state === "blocked").length,
      unknown: packets.filter((item) => item.state === "unknown").length,
      by_state: {
        proposed: 0,
        queued: 0,
        blocked: packets.filter((item) => item.state === "blocked").length,
        ready: packets.filter((item) => item.state === "ready").length,
        assigned: 0,
        running: 0,
        validator_pending: 0,
        validated: 0,
        validation_failed: 0,
        approval_pending: 0,
        approved: 0,
        rejected: 0,
        completed: 0,
        failed: packets.filter((item) => item.state === "failed").length,
        unknown: packets.filter((item) => item.state === "unknown").length
      }
    },
    warnings: []
  };
}

test("schedules ready packets", () => {
  const plan = buildSchedulerPreview({
    projection: projection([packet("PKT-READY", "ready")]),
    now: new Date("2026-05-29T00:00:00.000Z")
  });

  assert.equal(plan.total_packets, 1);
  assert.equal(plan.ready_packets, 1);
  assert.deepEqual(
    plan.recommended_order.map((item) => item.packet_id),
    ["PKT-READY"]
  );
});

test("excludes blocked packets", () => {
  const plan = buildSchedulerPreview({
    projection: projection([
      packet("PKT-READY", "ready"),
      packet("PKT-BLOCKED", "blocked")
    ])
  });

  assert.equal(plan.blocked_packets, 1);
  assert.deepEqual(
    plan.recommended_order.map((item) => item.packet_id),
    ["PKT-READY"]
  );
});

test("excludes failed packets", () => {
  const plan = buildSchedulerPreview({
    projection: projection([
      packet("PKT-FAILED", "failed"),
      packet("PKT-READY", "ready")
    ])
  });

  assert.deepEqual(
    plan.recommended_order.map((item) => item.packet_id),
    ["PKT-READY"]
  );
});

test("orders packets by priority then dependency count", () => {
  const plan = buildSchedulerPreview({
    projection: projection([
      packet("PKT-LOW", "ready", {
        dependencies: ["PKT-A"]
      }) as CanonicalQueuePacket & { priority: number },
      {
        ...packet("PKT-HIGH", "ready"),
        priority: 10
      } as CanonicalQueuePacket & { priority: number },
      {
        ...packet("PKT-MED", "ready"),
        priority: 5
      } as CanonicalQueuePacket & { priority: number }
    ])
  });

  assert.deepEqual(
    plan.recommended_order.map((item) => item.packet_id),
    ["PKT-HIGH", "PKT-MED", "PKT-LOW"]
  );
});

test("consumes projection warnings and derives worker capabilities", () => {
  const input = projection([
    packet("PKT-DOCS", "ready", {
      allowed_paths: ["docs/reports/", "tests/dispatcher/"],
      lane: "East"
    })
  ]);
  input.warnings.push("projection warning");

  const plan = buildSchedulerPreview({ projection: input });

  assert.deepEqual(plan.warnings, ["projection warning"]);
  assert.deepEqual(plan.worker_capability_requirements[0], {
    packet_id: "PKT-DOCS",
    required_capabilities: ["docs", "lane:East", "tests"],
    reason: "Derived from packet lane and allowed paths for preview only."
  });
});

test("does not mutate projection input", () => {
  const input = projection([packet("PKT-READY", "ready")]);
  const before = JSON.stringify(input);

  buildSchedulerPreview({ projection: input });

  assert.equal(JSON.stringify(input), before);
});
