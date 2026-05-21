const fs = require("fs");
const path = require("path");

const DEFAULT_STATE_DIR =
  process.env.AIOS_RUNTIME_STATE_DIR || path.join("telemetry", "runtime");
const DEFAULT_STATE_PATH = path.join(DEFAULT_STATE_DIR, "runtime_state.json");
const DEFAULT_HEARTBEAT_PATH = path.join(DEFAULT_STATE_DIR, "runtime_heartbeat.json");

function ensureRuntimeStateDirectory(statePath = DEFAULT_STATE_PATH) {
  fs.mkdirSync(path.dirname(statePath), { recursive: true });
}

function loadExecutionState(statePath = DEFAULT_STATE_PATH) {
  if (!fs.existsSync(statePath)) {
    return {
      status: "missing",
      state: null,
      statePath
    };
  }

  try {
    const content = fs.readFileSync(statePath, "utf8").replace(/^\uFEFF/, "");

    return {
      status: "valid",
      state: JSON.parse(content),
      statePath
    };
  } catch (error) {
    return {
      status: "invalid",
      state: null,
      statePath,
      warning: `Existing runtime state could not be parsed: ${error.message}`
    };
  }
}

function writeJsonAtomic(targetPath, value) {
  fs.mkdirSync(path.dirname(targetPath), { recursive: true });

  const tempPath = `${targetPath}.${process.pid}.${Date.now()}.tmp`;
  fs.writeFileSync(tempPath, `${JSON.stringify(value, null, 2)}\n`, "utf8");
  fs.renameSync(tempPath, targetPath);
}

function writeExecutionState(state, statePath = DEFAULT_STATE_PATH) {
  ensureRuntimeStateDirectory(statePath);
  writeJsonAtomic(statePath, state);
}

function writeHeartbeat(runtimeId, status, details = {}, heartbeatPath = DEFAULT_HEARTBEAT_PATH) {
  writeJsonAtomic(heartbeatPath, {
    runtimeId,
    status,
    heartbeatAt: new Date().toISOString(),
    ...details
  });
}

module.exports = {
  DEFAULT_STATE_PATH,
  DEFAULT_HEARTBEAT_PATH,
  loadExecutionState,
  writeExecutionState,
  writeHeartbeat
};
