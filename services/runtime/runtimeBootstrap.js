const { restorePacketsFromTelemetry } = require("../dispatcher/packetRestoration");
const {
  DEFAULT_STATE_PATH,
  loadExecutionState,
  writeExecutionState,
  writeHeartbeat
} = require("./runtimeStateStore");

function parseArgs(argv) {
  const config = {
    runtimeId: "aios-runtime-local",
    tickMs: 5000,
    once: false,
    maxTicks: 0
  };

  for (let index = 0; index < argv.length; index += 1) {
    const item = argv[index];

    if (item === "--runtime-id") {
      config.runtimeId = argv[index + 1] || config.runtimeId;
      index += 1;
    } else if (item === "--tick-ms") {
      config.tickMs = Number(argv[index + 1] || config.tickMs);
      index += 1;
    } else if (item === "--once") {
      config.once = true;
    } else if (item === "--max-ticks") {
      config.maxTicks = Number(argv[index + 1] || 0);
      index += 1;
    }
  }

  if (!Number.isFinite(config.tickMs) || config.tickMs < 250) {
    throw new Error("Tick interval must be at least 250ms.");
  }

  return config;
}

function createRuntimeState(config, previousState, restoration) {
  const now = new Date().toISOString();

  return {
    runtimeId: config.runtimeId,
    status: "running",
    bootedAt: now,
    updatedAt: now,
    tickCount: 0,
    previousStateStatus: previousState ? previousState.status : "none",
    recoveredAfterInterruption:
      Boolean(previousState) && !["shutdown", "stopped"].includes(previousState.status),
    restoration
  };
}

function tick(state) {
  const restoration = restorePacketsFromTelemetry();
  const updated = {
    ...state,
    status: "running",
    updatedAt: new Date().toISOString(),
    tickCount: state.tickCount + 1,
    restoration
  };

  writeExecutionState(updated);
  writeHeartbeat(updated.runtimeId, updated.status, {
    tickCount: updated.tickCount,
    restoredPacketCount: restoration.restoredPackets.length,
    resumeCandidateCount: restoration.resumeCandidates.length,
    pendingApprovalCount: restoration.pendingApprovals.length
  });

  console.log(
    `[AI_OS] heartbeat tick=${updated.tickCount} restored=${restoration.restoredPackets.length} resume=${restoration.resumeCandidates.length} pendingApprovals=${restoration.pendingApprovals.length}`
  );

  return updated;
}

function shutdown(state, reason = "shutdown") {
  const stopped = {
    ...state,
    status: "shutdown",
    shutdownReason: reason,
    shutdownAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };

  writeExecutionState(stopped);
  writeHeartbeat(stopped.runtimeId, stopped.status, {
    tickCount: stopped.tickCount,
    shutdownReason: reason
  });

  console.log(`[AI_OS] runtime shutdown complete reason=${reason}`);
}

function main() {
  const config = parseArgs(process.argv.slice(2));
  const previousState = loadExecutionState(DEFAULT_STATE_PATH);
  const restoration = restorePacketsFromTelemetry();
  let state = createRuntimeState(config, previousState, restoration);

  writeExecutionState(state);
  writeHeartbeat(state.runtimeId, state.status, {
    tickCount: state.tickCount,
    recoveredAfterInterruption: state.recoveredAfterInterruption
  });

  console.log(
    `[AI_OS] runtime booted recovered=${state.recoveredAfterInterruption} restored=${restoration.restoredPackets.length}`
  );

  const stop = (reason) => {
    shutdown(state, reason);
    process.exit(0);
  };

  process.on("SIGINT", () => stop("SIGINT"));
  process.on("SIGTERM", () => stop("SIGTERM"));

  state = tick(state);

  if (config.once || config.maxTicks === 1) {
    shutdown(state, "bounded_run_complete");
    return;
  }

  const interval = setInterval(() => {
    state = tick(state);

    if (config.maxTicks > 0 && state.tickCount >= config.maxTicks) {
      clearInterval(interval);
      shutdown(state, "bounded_run_complete");
    }
  }, config.tickMs);
}

try {
  main();
} catch (error) {
  console.error(`[AI_OS] runtime failed: ${error.message}`);
  process.exit(1);
}
