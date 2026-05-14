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
  private interval?: NodeJS.Timeout;

  constructor(
    private readonly config: RuntimeLoopConfig,
    private readonly dependencies: RuntimeLoopDependencies
  ) {
    this.context = createRuntimeContext(config.runtimeId);
  }

  public start(): void {
    if (this.interval) {
      return;
    }

    this.context.status = "running";

    this.interval = setInterval(() => {
      this.context = runRuntimeTick({
        context: this.context,
        deadLetterQueue: this.dependencies.deadLetterQueue,
        workerLeases: this.dependencies.workerLeases,
        maxConcurrentPackets: this.config.maxConcurrentPackets
      });
    }, this.config.tickIntervalMs);
  }

  public stop(): void {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = undefined;
    }

    this.context.status = "paused";
  }

  public getContext(): RuntimeContext {
    return this.context;
  }
}
