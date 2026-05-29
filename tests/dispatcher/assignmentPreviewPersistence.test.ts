import assert from "node:assert/strict";
import test from "node:test";
import {
  buildAssignmentPreviewPersistenceRecord,
  serializeAssignmentPreviewPersistenceRecord,
  validateAssignmentPreviewPersistenceRecord,
  type AssignmentPreviewPersistenceRecord
} from "../../services/dispatcher/assignmentPreviewPersistence.ts";
import type { WorkerResolverPreviewPlan } from "../../services/dispatcher/workerResolverPreview.ts";

function resolverPlan(): WorkerResolverPreviewPlan {
  return {
    schema: "AIOS_WORKER_RESOLVER_PREVIEW.v1",
    generated_at: "2026-05-29T00:00:00.000Z",
    source: {
      scheduler_plan_generated_at: "2026-05-29T00:00:00.000Z",
      scheduler_ready_packets: 2,
      worker_count: 1,
      preview_only: true
    },
    preview_mode: "read_only_preview",
    assignments: [
      {
        packet_id: "PKT-READY",
        recommended_worker_id: "dispatcher_worker",
        recommended_worker_name: "Dispatcher Worker",
        match_score: 29,
        matched_capabilities: ["dispatcher", "lane:East"],
        missing_capabilities: [],
        risk_allowed: true,
        status_allowed: true,
        lane_match: true,
        reason: "Worker matches required capability and lane signal.",
        preview_only: true
      }
    ],
    unmatched_actions: [
      {
        packet_id: "PKT-BLOCKED",
        required_capabilities: ["docs"],
        risk_level: "high",
        reason: "No active worker matched required capabilities, lane, and risk ceiling."
      }
    ],
    summary: {
      total_actions: 2,
      assigned_preview_count: 1,
      unmatched_count: 1,
      active_worker_count: 1,
      unavailable_worker_count: 0
    },
    warnings: ["PKT-BLOCKED: No active worker matched."]
  };
}

test("builds assignment preview persistence record from resolver plan", () => {
  const record = buildAssignmentPreviewPersistenceRecord({
    resolverPlan: resolverPlan(),
    now: new Date("2026-05-29T01:00:00.000Z"),
    source: {
      packet_id: "source-test"
    }
  });

  assert.equal(record.schema, "AIOS_ASSIGNMENT_PREVIEW_PERSISTENCE.v1");
  assert.equal(record.generated_at, "2026-05-29T01:00:00.000Z");
  assert.equal(record.persistence_mode, "preview_record_only");
  assert.equal(record.source.resolver_schema, "AIOS_WORKER_RESOLVER_PREVIEW.v1");
});

test("preserves assignment packet id and worker recommendation", () => {
  const record = buildAssignmentPreviewPersistenceRecord({
    resolverPlan: resolverPlan()
  });

  assert.equal(record.assignments[0]?.packet_id, "PKT-READY");
  assert.equal(
    record.assignments[0]?.recommended_worker_id,
    "dispatcher_worker"
  );
  assert.equal(record.assignments[0]?.persistence_status, "recorded_preview");
});

test("preserves unmatched actions", () => {
  const record = buildAssignmentPreviewPersistenceRecord({
    resolverPlan: resolverPlan()
  });

  assert.equal(record.unmatched_actions.length, 1);
  assert.equal(record.unmatched_actions[0]?.packet_id, "PKT-BLOCKED");
  assert.equal(record.unmatched_actions[0]?.preview_only, true);
});

test("enforces preview_only true at record level", () => {
  const record = buildAssignmentPreviewPersistenceRecord({
    resolverPlan: resolverPlan()
  });

  assert.equal(record.preview_only, true);
});

test("enforces assignment preview_only true", () => {
  const record = buildAssignmentPreviewPersistenceRecord({
    resolverPlan: resolverPlan()
  });

  assert.equal(record.assignments[0]?.preview_only, true);
});

test("enforces dispatch_authorized false", () => {
  const record = buildAssignmentPreviewPersistenceRecord({
    resolverPlan: resolverPlan()
  });

  assert.equal(record.summary.dispatch_authorized, false);
});

test("enforces inbox_mutation_authorized false", () => {
  const record = buildAssignmentPreviewPersistenceRecord({
    resolverPlan: resolverPlan()
  });

  assert.equal(record.summary.inbox_mutation_authorized, false);
});

test("enforces runtime_mutation_authorized false", () => {
  const record = buildAssignmentPreviewPersistenceRecord({
    resolverPlan: resolverPlan()
  });

  assert.equal(record.summary.runtime_mutation_authorized, false);
});

test("validateAssignmentPreviewPersistenceRecord reports tampered unsafe authorization", () => {
  const record = buildAssignmentPreviewPersistenceRecord({
    resolverPlan: resolverPlan()
  }) as AssignmentPreviewPersistenceRecord & {
    summary: AssignmentPreviewPersistenceRecord["summary"] & {
      dispatch_authorized: boolean;
    };
  };
  record.summary.dispatch_authorized = true;
  record.assignments[0] = {
    ...record.assignments[0],
    preview_only: false
  } as typeof record.assignments[number];

  const warnings = validateAssignmentPreviewPersistenceRecord(record);

  assert.ok(warnings.includes("dispatch_authorized must be false"));
  assert.ok(warnings.some((warning) => warning.includes("preview_only must be true")));
});

test("serializeAssignmentPreviewPersistenceRecord returns parseable JSON with trailing newline", () => {
  const record = buildAssignmentPreviewPersistenceRecord({
    resolverPlan: resolverPlan()
  });
  const serialized = serializeAssignmentPreviewPersistenceRecord(record);

  assert.equal(serialized.endsWith("\n"), true);
  assert.deepEqual(JSON.parse(serialized), record);
});

test("does not mutate resolverPlan input", () => {
  const input = resolverPlan();
  const before = JSON.stringify(input);

  buildAssignmentPreviewPersistenceRecord({
    resolverPlan: input
  });

  assert.equal(JSON.stringify(input), before);
});
