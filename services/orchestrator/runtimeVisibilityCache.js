const fs = require("fs");

const DEFAULT_MAX_AGE_MS = 1000;

function normalizeMaxAgeMs(value) {
  if (value === undefined || value === null) {
    return DEFAULT_MAX_AGE_MS;
  }

  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : DEFAULT_MAX_AGE_MS;
}

function normalizeNowMs(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : Date.now();
}

function uniqueSortedPaths(paths) {
  return [...new Set(paths.filter(Boolean).map((filePath) => String(filePath)))].sort();
}

function getFileFingerprint(filePath, options = {}) {
  const normalizedPath = String(filePath || "");
  const statSync = typeof options.statSync === "function" ? options.statSync : fs.statSync;

  if (!normalizedPath) {
    return {
      path: normalizedPath,
      exists: false,
      size: null,
      mtimeMs: null,
      error: "EMPTY_PATH"
    };
  }

  try {
    const stat = statSync(normalizedPath);

    return {
      path: normalizedPath,
      exists: true,
      size: stat.size,
      mtimeMs: Number(stat.mtimeMs),
      error: null
    };
  } catch (error) {
    return {
      path: normalizedPath,
      exists: false,
      size: null,
      mtimeMs: null,
      error: error?.code || "STAT_FAILED"
    };
  }
}

function buildVisibilityDependencyFingerprint(paths, options = {}) {
  const files = uniqueSortedPaths(Array.isArray(paths) ? paths : []).map((filePath) =>
    getFileFingerprint(filePath, options)
  );
  const fingerprint = JSON.stringify(
    files.map(({ path, exists, size, mtimeMs, error }) => ({
      path,
      exists,
      size,
      mtimeMs,
      error
    }))
  );

  return {
    fingerprint,
    files
  };
}

function createRuntimeVisibilityCache(options = {}) {
  const defaultDependencyPaths = Array.isArray(options.dependencyPaths)
    ? options.dependencyPaths
    : [];
  const defaultMaxAgeMs = normalizeMaxAgeMs(options.maxAgeMs);
  const now = typeof options.now === "function" ? options.now : Date.now;
  const fingerprintOptions = {
    statSync: options.statSync
  };

  let cachedSnapshot = null;
  let cachedFingerprint = null;
  let cachedAtMs = null;

  function clear() {
    cachedSnapshot = null;
    cachedFingerprint = null;
    cachedAtMs = null;
  }

  function getSnapshot(builder, readOptions = {}) {
    if (typeof builder !== "function") {
      throw new TypeError("Runtime visibility cache requires a snapshot builder function.");
    }

    const dependencyPaths = Array.isArray(readOptions.dependencyPaths)
      ? readOptions.dependencyPaths
      : defaultDependencyPaths;
    const hasMaxAgeOverride =
      Object.prototype.hasOwnProperty.call(readOptions, "maxAgeMs") &&
      readOptions.maxAgeMs !== undefined &&
      readOptions.maxAgeMs !== null;
    const maxAgeMs = normalizeMaxAgeMs(
      hasMaxAgeOverride ? readOptions.maxAgeMs : defaultMaxAgeMs
    );
    const dependencyFingerprint = buildVisibilityDependencyFingerprint(
      dependencyPaths,
      fingerprintOptions
    );
    const nowMs = normalizeNowMs(now());
    const ageMs = cachedAtMs === null ? Number.POSITIVE_INFINITY : nowMs - cachedAtMs;
    const canUseCache =
      cachedSnapshot !== null &&
      cachedFingerprint === dependencyFingerprint.fingerprint &&
      ageMs >= 0 &&
      ageMs <= maxAgeMs;

    if (canUseCache) {
      return cachedSnapshot;
    }

    cachedSnapshot = builder({
      dependencyFingerprint
    });
    cachedFingerprint = dependencyFingerprint.fingerprint;
    cachedAtMs = nowMs;

    return cachedSnapshot;
  }

  function getState() {
    return {
      hasSnapshot: cachedSnapshot !== null,
      cachedFingerprint,
      cachedAtMs
    };
  }

  return {
    getSnapshot,
    clear,
    getState
  };
}

module.exports = {
  createRuntimeVisibilityCache,
  getFileFingerprint,
  buildVisibilityDependencyFingerprint
};
