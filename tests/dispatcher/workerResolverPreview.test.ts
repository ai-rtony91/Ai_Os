import assert from "node:assert/strict";
import test from "node:test";
import type {
  SchedulerPreviewPlan,
  SchedulerPreviewRecommendedPacket
} from "../../services/dispatcher/schedulerPreview.ts";
import {
  buildWorkerResolverPreviewPlan,
  type WorkerResolverPreviewWorker
} from "../../services/dispatcher/workerResolverPreview.ts";

function schedulerPlan(
  actions: Array<
    SchedulerPreviewRecommendedPacket & { scheduler_eligible?: boolean }
  >,
  capabilitiesByPacket: Record<string, string[]>
): SchedulerPreviewPlan {
  return {
    generated_at: "2026-05-29T00:00:00.000Z",
    total_packets: actions.length,
    ready_packets: actions.filter(
      (action) => action.scheduler_eligible !== false
    ).length,
    blocked_packets: actions.filter(
      (action) => action.scheduler_eligible === false
    ).length,
    recommended_order: actions,
    worker_capability_requirements: actions.map((action) => ({
      packet_id: action.packet_id,
      required_capabilities: capabilitiesByPacket[action.packet_id] ?? [],
      reason: "test"
    })),
    warnings: []
  };
}

function action(
  packetId: string,
  overrides: Partial<
    SchedulerPreviewRecommendedPacket & { scheduler_eligible?: boolean }
  > = {}
): SchedulerPreviewRecommendedPacket & { scheduler_eligible?: boolean } {
  return {
    packet_id: packetId,
    rank: 1,
    priority: 0,
    risk_level: "low",
    dependency_count: 0,
    reason: "test",
    ...overrides
  };
}

function worker(
  workerId: string,
  overrides: Partial<WorkerResolverPreviewWorker> = {}
): WorkerResolverPreviewWorker {
  return {
    worker_id: workerId,
    display_name: workerId,
    lane: "East",
    capabilities: ["dispatcher", "lane:East"],
    risk_ceiling: "medium",
    status: "available",
    active: true,
    ...overrides
  };
}

test("matches ready scheduler action to capable active worker", () => {
  const plan = buildWorkerResolverPreviewPlan({
    schedulerPlan: schedulerPlan([action("PKT-READY")], {
      "PKT-READY": ["dispatcher", "lane:East"]
    }),
    workers: [worker("dispatcher_worker")],
    now: new Date("2026-05-29T00:00:00.000Z")
  });

  assert.equal(plan.schema, "AIOS_WORKER_RESOLVER_PREVIEW.v1");
  assert.equal(plan.preview_mode, "read_only_preview");
  assert.equal(plan.assignments.length, 1);
  assert.equal(
    plan.assignments[0]?.recommended_worker_id,
    "dispatcher_worker"
  );
  assert.equal(plan.assignments[0]?.preview_only, true);
  assert.equal(plan.unmatched_actions.length, 0);
});

test("does not assign blocked or non-ready scheduler action", () => {
  const plan = buildWorkerResolverPreviewPlan({
    schedulerPlan: schedulerPlan(
      [action("PKT-BLOCKED", { scheduler_eligible: false })],
      {
        "PKT-BLOCKED": ["dispatcher"]
      }
    ),
    workers: [worker("dispatcher_worker")]
  });

  assert.equal(plan.assignments.length, 0);
  assert.equal(plan.unmatched_actions.length, 1);
  assert.match(
    plan.unmatched_actions[0]?.reason ?? "",
    /not eligible for worker resolution/
  );
});

test("excludes inactive worker", () => {
  const plan = buildWorkerResolverPreviewPlan({
    schedulerPlan: schedulerPlan([action("PKT-READY")], {
      "PKT-READY": ["dispatcher"]
    }),
    workers: [worker("inactive_worker", { active: false })]
  });

  assert.equal(plan.assignments.length, 0);
  assert.equal(plan.summary.unavailable_worker_count, 1);
  assert.match(
    plan.unmatched_actions[0]?.reason ?? "",
    /No active worker matched/
  );
});

test("risk ceiling blocks high-risk packet", () => {
  const plan = buildWorkerResolverPreviewPlan({
    schedulerPlan: schedulerPlan(
      [action("PKT-HIGH", { risk_level: "high" })],
      {
        "PKT-HIGH": ["dispatcher"]
      }
    ),
    workers: [worker("medium_worker", { risk_ceiling: "medium" })]
  });

  assert.equal(plan.assignments.length, 0);
  assert.equal(plan.unmatched_actions.length, 1);
});

test("records unmatched action when no worker capabilities match", () => {
  const plan = buildWorkerResolverPreviewPlan({
    schedulerPlan: schedulerPlan([action("PKT-DOCS")], {
      "PKT-DOCS": ["docs"]
    }),
    workers: [worker("dispatcher_worker", { capabilities: ["dispatcher"] })]
  });

  assert.equal(plan.assignments.length, 0);
  assert.equal(plan.unmatched_actions[0]?.packet_id, "PKT-DOCS");
});

test("ranking prefers stronger capability and lane fit", () => {
  const plan = buildWorkerResolverPreviewPlan({
    schedulerPlan: schedulerPlan([action("PKT-DISPATCH")], {
      "PKT-DISPATCH": ["dispatcher", "lane:East"]
    }),
    workers: [
      worker("generic_worker", {
        lane: "West",
        capabilities: ["dispatcher"],
        risk_ceiling: "high"
      }),
      worker("lane_worker", {
        lane: "East",
        capabilities: ["dispatcher", "lane:East"],
        risk_ceiling: "medium"
      })
    ]
  });

  assert.equal(plan.assignments[0]?.recommended_worker_id, "lane_worker");
  assert.equal(plan.assignments[0]?.lane_match, true);
});

test("does not mutate scheduler plan or workers input", () => {
  const inputPlan = schedulerPlan([action("PKT-READY")], {
    "PKT-READY": ["dispatcher"]
  });
  const workers = [worker("dispatcher_worker")];
  const beforePlan = JSON.stringify(inputPlan);
  const beforeWorkers = JSON.stringify(workers);

  buildWorkerResolverPreviewPlan({
    schedulerPlan: inputPlan,
    workers
  });

  assert.equal(JSON.stringify(inputPlan), beforePlan);
  assert.equal(JSON.stringify(workers), beforeWorkers);
});
