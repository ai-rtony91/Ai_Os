const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const { getVisibilitySnapshot } = require("../../services/orchestrator/runtimeApiService");

const repoRoot = path.resolve(__dirname, "..", "..");
const REQUIRED_DISPLAY_FIELDS = [
  "display_state",
  "authority_state",
  "source_path",
  "source_type",
  "freshness",
  "blocked_actions",
  "next_safe_action",
  "approval_required",
  "execution_allowed",
  "mutation_allowed",
  "stale_or_legacy",
  "safe_for_frontend_display"
];

function readJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(repoRoot, relativePath), "utf8"));
}

function readText(relativePath) {
  return fs.readFileSync(path.join(repoRoot, relativePath), "utf8");
}

function assertFrontendContract(contract) {
  assert.equal(typeof contract, "object");

  for (const field of REQUIRED_DISPLAY_FIELDS) {
    assert.ok(
      Object.prototype.hasOwnProperty.call(contract, field),
      `frontend contract missing ${field}`
    );
  }

  assert.equal(contract.execution_allowed, false);
  assert.equal(contract.mutation_allowed, false);
  assert.equal(contract.safe_for_frontend_display, true);
  assert.equal(typeof contract.source_path, "string");
  assert.notEqual(contract.source_path.trim(), "");
  assert.equal(typeof contract.source_type, "string");
  assert.notEqual(contract.source_type.trim(), "");
  assert.equal(typeof contract.freshness, "object");
  assert.equal(typeof contract.freshness.is_stale, "boolean");
  assert.ok(Array.isArray(contract.blocked_actions));
  assert.ok(contract.blocked_actions.includes("worker_launch"));
  assert.ok(contract.blocked_actions.includes("queue_mutation"));
  assert.ok(contract.blocked_actions.includes("live_trading"));
  assert.ok(contract.blocked_actions.includes("secret_access"));
}

function assertProjectionItems(items) {
  assert.ok(Array.isArray(items));
  assert.ok(items.length > 0);

  for (const item of items) {
    assertFrontendContract(item);
  }
}

test("wired runtime visibility fixture has frontend-safe display contract", () => {
  const fixture = readJson("apps/dashboard/mock-data/aios-runtime-visibility-v1.example.json");

  assert.equal(fixture.schema, "aios.runtime_visibility.v1");
  assert.equal(fixture.mode, "DISPLAY_ONLY");
  assert.ok(Array.isArray(fixture.source_paths));
  assert.ok(fixture.source_paths.includes("apps/dashboard/mock-data/aios-runtime-visibility-v1.example.json"));
  assertFrontendContract(fixture.frontend_contract);
  assertProjectionItems(fixture.projection_items);
});

test("runtime visibility schema requires the frontend-safe envelope", () => {
  const schema = readJson("schemas/aios/orchestration/RUNTIME_VISIBILITY_SCHEMA.json");

  assert.ok(Array.isArray(schema.required));
  assert.ok(schema.required.length > 1);
  assert.ok(schema.required.includes("schema"));
  assert.ok(schema.required.includes("frontend_contract"));
  assert.ok(schema.required.includes("source_paths"));
  assert.deepEqual(
    schema.properties.frontend_contract,
    { $ref: "#/$defs/frontend_contract" }
  );
  assert.deepEqual(
    schema.properties.projection_items.items,
    { $ref: "#/$defs/frontend_contract" }
  );
});

test("orchestrator visibility helper emits read-only frontend-safe shape", () => {
  const snapshot = getVisibilitySnapshot();

  assert.equal(snapshot.schema, "aios.runtime_visibility_api.v1");
  assert.equal(snapshot.mode, "READ_ONLY");
  assert.ok(Array.isArray(snapshot.source_paths));
  assert.ok(snapshot.source_paths.includes("telemetry/runtime/runtime_state.json"));
  assert.ok(snapshot.source_paths.includes("telemetry/work_ledger.jsonl"));
  assertFrontendContract(snapshot.frontend_contract);
  assertProjectionItems(snapshot.projection_items);
  assert.equal(snapshot.controls.startRuntime, "BLOCKED_BY_API_DEFAULT");
  assert.equal(snapshot.controls.stopRuntime, "BLOCKED_BY_API_DEFAULT");
  assert.equal(snapshot.controls.assignQueueItem, "BLOCKED_BY_API_DEFAULT");
  assert.equal(snapshot.controls.advancePacket, "BLOCKED_BY_API_DEFAULT");
});

test("dashboard client and adapter remain aligned to read-only API schema", () => {
  const client = readText("apps/dashboard/src/runtimeVisibilityClient.js");
  const adapter = readText("apps/dashboard/src/runtimeVisibilityAdapter.js");

  assert.match(client, /aios\.runtime_visibility_api\.v1/);
  assert.match(client, /const READ_ONLY_MODE = "READ_ONLY"/);
  assert.match(client, /NON_READ_ONLY_RESPONSE/);
  assert.match(adapter, /input\.schema === "aios\.runtime_visibility_api\.v1"/);
  assert.match(adapter, /LOCAL_API_READ_ONLY/);
});
