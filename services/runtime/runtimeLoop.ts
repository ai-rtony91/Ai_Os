import { runtimeEventBus } from "./eventBus";
import { registerRuntimeAutomationHandlers } from "./runtimeAutomationHandlers";
import { registerRuntimeAutomationDispatcher } from "./runtimeAutomationDispatcher";
import { processAutomationQueue } from "./runtimeAutomationExecutor";

import { createRuntimeContext, type RuntimeContext } from "./runtimeContext";
import { runRuntimeTick } from "./runtimeTick";

import type { DeadLetterQueueState } from "../dispatcher/deadLetterQueue";
import type { WorkerLeaseResult } from "../dispatcher/workerLeaseEngine";

export interface RuntimeLoopConfig {
  runtimeId: string;
  tickIntervalMs: number;
  maxConcurrentPackets: number;
}

export interface RuntimeLoopDependencies {
  deadLetterQueue: DeadLetterQueueState;
  workerLeases: WorkerLeaseResult;
}

export class RuntimeLoop {
  private context: RuntimeContext;
  private interval?: ReturnType<typeof setInterval>;

  constructor(
    private readonly config: RuntimeLoopConfig,
    private readonly dependencies: RuntimeLoopDependencies
  ) {
    this.context = createRuntimeContext(config.runtimeId);

    registerRuntimeAutomationHandlers();
    registerRuntimeAutomationDispatcher();
  }

  public start(): void {
    if (this.interval) {
      return;
    }

    this.context.status = "running";

    runtimeEventBus.emit("runtime_started", {
      runtimeId: this.config.runtimeId
    });

    this.interval = setInterval(() => {
      try {
        this.context = runRuntimeTick({
          context: this.context,
          deadLetterQueue: this.dependencies.deadLetterQueue,
          workerLeases: this.dependencies.workerLeases,
          maxConcurrentPackets: this.config.maxConcurrentPackets
        });

        processAutomationQueue(this.config.maxConcurrentPackets);
      } catch (error) {
        // Endurance hardening: a transient tick failure must not kill the
        // interval (and therefore the process). Log and continue; the
        // previous context is preserved so the next tick can recover.
        console.error("[aios-runtime] TICK_ERROR", error);
        return;
      }
    }, this.config.tickIntervalMs);
  }

  public stop(): void {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = undefined;
    }

    this.context.status = "paused";

    runtimeEventBus.emit("runtime_stopped", {
      runtimeId: this.config.runtimeId
    });
  }

  public getContext(): RuntimeContext {
    return this.context;
  }
}
