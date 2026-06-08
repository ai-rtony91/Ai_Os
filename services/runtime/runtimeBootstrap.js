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
  const recovery = evaluateRecovery(previousState);

  return {
    runtimeId: config.runtimeId,
    status: "running",
    bootedAt: now,
    updatedAt: now,
    lastTickAt: null,
    tickCount: 0,
    statePath: previousState.statePath,
    ledgerPath: restoration.ledgerPath,
    previousStateStatus: recovery.previousStateStatus,
    recoveredAfterInterruption: recovery.recoveredAfterInterruption,
    recoveryReason: recovery.recoveryReason,
    recoveryWarning: recovery.recoveryWarning,
    restoration
  };
}

function evaluateRecovery(previousState) {
  if (previousState.status === "missing") {
    return {
      previousStateStatus: "none",
      recoveredAfterInterruption: false,
      recoveryReason: "no_previous_runtime_state"
    };
  }

  if (previousState.status === "invalid") {
    return {
      previousStateStatus: "invalid",
      recoveredAfterInterruption: true,
      recoveryReason: "invalid_runtime_state_recovered_from_telemetry",
      recoveryWarning: previousState.warning
    };
  }

  const previousStatus = previousState.state?.status || "unknown";
  const wasCleanShutdown = ["shutdown", "stopped"].includes(previousStatus);

  return {
    previousStateStatus: previousStatus,
    recoveredAfterInterruption: !wasCleanShutdown,
    recoveryReason: wasCleanShutdown
      ? "previous_runtime_shutdown_cleanly"
      : `previous_runtime_status_${previousStatus}`
  };
}

function tick(state) {
  const restoration = restorePacketsFromTelemetry();
  const now = new Date().toISOString();
  const updated = {
    ...state,
    status: "running",
    updatedAt: now,
    lastTickAt: now,
    ledgerPath: restoration.ledgerPath,
    tickCount: state.tickCount + 1,
    restoration
  };

  writeExecutionState(updated);
  writeHeartbeat(updated.runtimeId, updated.status, {
    statePath: updated.statePath,
    ledgerPath: restoration.ledgerPath,
    tickCount: updated.tickCount,
    lastTickAt: updated.lastTickAt,
    restoredPacketCount: restoration.restoredPackets.length,
    resumeCandidateCount: restoration.resumeCandidates.length,
    pendingApprovalCount: restoration.pendingApprovals.length,
    invalidLedgerLineCount: restoration.invalidLineCount,
    recoveryWarning: updated.recoveryWarning
  });

  console.log(
    `[AI_OS] heartbeat tick=${updated.tickCount} restored=${restoration.restoredPackets.length} resume=${restoration.resumeCandidates.length} pendingApprovals=${restoration.pendingApprovals.length} invalidLedgerLines=${restoration.invalidLineCount}`
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
    statePath: stopped.statePath,
    ledgerPath: stopped.ledgerPath,
    tickCount: stopped.tickCount,
    lastTickAt: stopped.lastTickAt,
    shutdownReason: reason
  });

  console.log(`[AI_OS] runtime shutdown complete reason=${reason}`);
}

function main() {
  const config = parseArgs(process.argv.slice(2));
  const previousState = loadExecutionState(DEFAULT_STATE_PATH);
  const restoration = restorePacketsFromTelemetry();
  let state = createRuntimeState(config, previousState, restoration);
  let shutdownStarted = false;

  writeExecutionState(state);
  writeHeartbeat(state.runtimeId, state.status, {
    statePath: state.statePath,
    ledgerPath: restoration.ledgerPath,
    tickCount: state.tickCount,
    lastTickAt: state.lastTickAt,
    recoveredAfterInterruption: state.recoveredAfterInterruption,
    recoveryReason: state.recoveryReason,
    recoveryWarning: state.recoveryWarning,
    invalidLedgerLineCount: restoration.invalidLineCount
  });

  console.log(
    `[AI_OS] runtime booted recovered=${state.recoveredAfterInterruption} reason=${state.recoveryReason} restored=${restoration.restoredPackets.length}`
  );

  const stop = (reason) => {
    if (shutdownStarted) {
      return;
    }

    shutdownStarted = true;
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
    try {
      state = tick(state);

      if (config.maxTicks > 0 && state.tickCount >= config.maxTicks) {
        clearInterval(interval);
        shutdown(state, "bounded_run_complete");
      }
    } catch (error) {
      // Endurance hardening: a transient tick failure must not kill the
      // interval or exit the process. Log, keep the previous state, and
      // continue so the next interval can recover.
      console.error("[AI_OS] TICK_ERROR", error);
    }
  }, config.tickMs);
}

try {
  main();
} catch (error) {
  console.error(`[AI_OS] runtime failed: ${error.message}`);
  process.exit(1);
}
