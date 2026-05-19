export type RuntimeEventType =
  | "runtime_started"
  | "runtime_stopped"
  | "runtime_tick_started"
  | "runtime_tick_completed"
  | "runtime_blocked"
  | "runtime_degraded"
  | "policy_decision";

export interface RuntimeEvent<TPayload = unknown> {
  type: RuntimeEventType;
  timestamp: string;
  payload: TPayload;
}

export type RuntimeEventHandler<TPayload = unknown> = (
  event: RuntimeEvent<TPayload>
) => void;

export class RuntimeEventBus {
  private readonly listeners = new Map<
    RuntimeEventType,
    RuntimeEventHandler[]
  >();

  public subscribe<TPayload>(
    type: RuntimeEventType,
    handler: RuntimeEventHandler<TPayload>
  ): () => void {
    const handlers = this.listeners.get(type) ?? [];

    handlers.push(handler as RuntimeEventHandler);
    this.listeners.set(type, handlers);

    return () => {
      const currentHandlers = this.listeners.get(type) ?? [];

      this.listeners.set(
        type,
        currentHandlers.filter((item) => item !== handler)
      );
    };
  }

  public emit<TPayload>(
    type: RuntimeEventType,
    payload: TPayload
  ): void {
    const handlers = this.listeners.get(type) ?? [];

    const event: RuntimeEvent<TPayload> = {
      type,
      timestamp: new Date().toISOString(),
      payload
    };

    for (const handler of handlers) {
      handler(event);
    }
  }

  public listenerCount(type: RuntimeEventType): number {
    return (this.listeners.get(type) ?? []).length;
  }

  public clear(): void {
    this.listeners.clear();
  }
}

export const runtimeEventBus = new RuntimeEventBus();
