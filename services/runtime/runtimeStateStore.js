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
    return null;
  }

  try {
    return JSON.parse(fs.readFileSync(statePath, "utf8"));
  } catch (error) {
    return {
      runtimeId: "unknown",
      status: "degraded",
      loadedAt: new Date().toISOString(),
      recoveryWarning: `Existing runtime state could not be parsed: ${error.message}`
    };
  }
}

function writeExecutionState(state, statePath = DEFAULT_STATE_PATH) {
  ensureRuntimeStateDirectory(statePath);
  fs.writeFileSync(statePath, `${JSON.stringify(state, null, 2)}\n`, "utf8");
}

function writeHeartbeat(runtimeId, status, details = {}, heartbeatPath = DEFAULT_HEARTBEAT_PATH) {
  fs.mkdirSync(path.dirname(heartbeatPath), { recursive: true });
  fs.writeFileSync(
    heartbeatPath,
    `${JSON.stringify(
      {
        runtimeId,
        status,
        heartbeatAt: new Date().toISOString(),
        ...details
      },
      null,
      2
    )}\n`,
    "utf8"
  );
}

module.exports = {
  DEFAULT_STATE_PATH,
  DEFAULT_HEARTBEAT_PATH,
  loadExecutionState,
  writeExecutionState,
  writeHeartbeat
};
