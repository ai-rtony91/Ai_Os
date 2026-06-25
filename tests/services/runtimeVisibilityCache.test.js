const assert = require("node:assert/strict");
const fs = require("node:fs");
const test = require("node:test");

const {
  createRuntimeVisibilityCache,
  buildVisibilityDependencyFingerprint
} = require("../../services/orchestrator/runtimeVisibilityCache");

function createStatReader(statsByPath) {
  return (filePath) => {
    const stat = statsByPath.get(filePath);

    if (!stat) {
      const error = new Error(`Missing test dependency: ${filePath}`);
      error.code = "ENOENT";
      throw error;
    }

    return stat;
  };
}

test("first call builds snapshot", () => {
  const statsByPath = new Map([["runtime_state.json", { size: 10, mtimeMs: 1000 }]]);
  const cache = createRuntimeVisibilityCache({
    dependencyPaths: ["runtime_state.json"],
    maxAgeMs: 1000,
    now: () => 1000,
    statSync: createStatReader(statsByPath)
  });
  let buildCount = 0;

  const snapshot = cache.getSnapshot(() => {
    buildCount += 1;
    return {
      schema: "aios.runtime_visibility_api.v1",
      mode: "READ_ONLY",
      buildCount
    };
  });

  assert.equal(buildCount, 1);
  assert.equal(snapshot.schema, "aios.runtime_visibility_api.v1");
  assert.equal(snapshot.mode, "READ_ONLY");
  assert.equal(snapshot.buildCount, 1);
});

test("second call with unchanged dependencies uses cache", () => {
  const statsByPath = new Map([["runtime_state.json", { size: 10, mtimeMs: 1000 }]]);
  const cache = createRuntimeVisibilityCache({
    dependencyPaths: ["runtime_state.json"],
    maxAgeMs: 1000,
    now: () => 1100,
    statSync: createStatReader(statsByPath)
  });
  let buildCount = 0;

  const builder = () => {
    buildCount += 1;
    return {
      schema: "aios.runtime_visibility_api.v1",
      mode: "READ_ONLY",
      buildCount
    };
  };

  const first = cache.getSnapshot(builder);
  const second = cache.getSnapshot(builder);

  assert.equal(buildCount, 1);
  assert.equal(second, first);
  assert.equal(second.buildCount, 1);
});

test("changed dependency fingerprint rebuilds", () => {
  const statsByPath = new Map([["runtime_state.json", { size: 10, mtimeMs: 1000 }]]);
  const cache = createRuntimeVisibilityCache({
    dependencyPaths: ["runtime_state.json"],
    maxAgeMs: 1000,
    now: () => 1200,
    statSync: createStatReader(statsByPath)
  });
  let buildCount = 0;

  const builder = () => {
    buildCount += 1;
    return {
      schema: "aios.runtime_visibility_api.v1",
      mode: "READ_ONLY",
      buildCount
    };
  };

  const first = cache.getSnapshot(builder);
  statsByPath.set("runtime_state.json", { size: 20, mtimeMs: 1001 });
  const second = cache.getSnapshot(builder);

  assert.equal(buildCount, 2);
  assert.notEqual(second, first);
  assert.equal(second.buildCount, 2);
});

test("TTL expiry rebuilds", () => {
  const statsByPath = new Map([["runtime_state.json", { size: 10, mtimeMs: 1000 }]]);
  let nowMs = 1000;
  const cache = createRuntimeVisibilityCache({
    dependencyPaths: ["runtime_state.json"],
    maxAgeMs: 50,
    now: () => nowMs,
    statSync: createStatReader(statsByPath)
  });
  let buildCount = 0;

  const builder = () => {
    buildCount += 1;
    return {
      schema: "aios.runtime_visibility_api.v1",
      mode: "READ_ONLY",
      buildCount
    };
  };

  const first = cache.getSnapshot(builder);
  nowMs = 1040;
  const second = cache.getSnapshot(builder);
  nowMs = 1051;
  const third = cache.getSnapshot(builder);

  assert.equal(buildCount, 2);
  assert.equal(second, first);
  assert.notEqual(third, first);
  assert.equal(third.buildCount, 2);
});

test("missing dependency is fingerprinted and safe builder model is returned", () => {
  const statSync = createStatReader(new Map());
  const dependencyFingerprint = buildVisibilityDependencyFingerprint(
    ["missing_runtime_state.json"],
    { statSync }
  );
  const cache = createRuntimeVisibilityCache({
    dependencyPaths: ["missing_runtime_state.json"],
    maxAgeMs: 1000,
    now: () => 1000,
    statSync
  });

  const snapshot = cache.getSnapshot(() => ({
    schema: "aios.runtime_visibility_api.v1",
    mode: "READ_ONLY",
    source_paths: ["missing_runtime_state.json"],
    frontend_contract: {
      display_state: "BLOCKED",
      execution_allowed: false,
      mutation_allowed: false,
      safe_for_frontend_display: true
    },
    nextSafeAction: "Review read-only runtime visibility before any protected action."
  }));

  assert.equal(dependencyFingerprint.files[0].exists, false);
  assert.equal(dependencyFingerprint.files[0].error, "ENOENT");
  assert.equal(snapshot.mode, "READ_ONLY");
  assert.equal(snapshot.frontend_contract.display_state, "BLOCKED");
  assert.equal(snapshot.frontend_contract.execution_allowed, false);
  assert.equal(snapshot.frontend_contract.mutation_allowed, false);
});

test("cache performs no write or mutation filesystem actions", () => {
  const statsByPath = new Map([["runtime_state.json", { size: 10, mtimeMs: 1000 }]]);
  const forbiddenWriteMethods = [
    "appendFileSync",
    "copyFileSync",
    "mkdirSync",
    "renameSync",
    "rmSync",
    "rmdirSync",
    "truncateSync",
    "unlinkSync",
    "writeFileSync"
  ];
  const originals = new Map();

  try {
    for (const methodName of forbiddenWriteMethods) {
      originals.set(methodName, fs[methodName]);
      fs[methodName] = () => {
        throw new Error(`Cache attempted filesystem mutation through ${methodName}.`);
      };
    }

    const cache = createRuntimeVisibilityCache({
      dependencyPaths: ["runtime_state.json"],
      maxAgeMs: 1000,
      now: () => 1000,
      statSync: createStatReader(statsByPath)
    });

    assert.doesNotThrow(() =>
      cache.getSnapshot(() => ({
        schema: "aios.runtime_visibility_api.v1",
        mode: "READ_ONLY"
      }))
    );
  } finally {
    for (const [methodName, original] of originals) {
      fs[methodName] = original;
    }
  }
});
