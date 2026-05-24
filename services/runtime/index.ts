import { RuntimeLoop } from "./runtimeLoop";

const loop = new RuntimeLoop(
  {
    runtimeId: process.env.AIOS_RUNTIME_ID ?? "aios-runtime-local",
    tickIntervalMs: Number(process.env.AIOS_TICK_MS ?? 5000),
    maxConcurrentPackets: Number(process.env.AIOS_MAX_PACKETS ?? 4)
  },
  {
    deadLetterQueue: { entries: [] },
    workerLeases: { leases: [] }
  }
);

loop.start();

console.log("[aios-runtime] started");

process.on("SIGINT", () => {
  loop.stop();
  console.log("[aios-runtime] stopped");
  process.exit(0);
});
