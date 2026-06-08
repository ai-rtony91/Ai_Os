# AIOS Endurance Hardening Roadmap

## Purpose

This document answers one question: **what crashes a fully automatic AIOS loop running unattended for 24 hours, then 48 hours, then a week, then weeks, then a month?**

It is the pre-inspection endurance audit. It catalogs every loop-killer found by a five-dimension deep scan of the runtime, then sequences the fixes into endurance tiers mapped to real survival milestones, with effort estimates.

Goal posture: move from "the loop runs in a demo" to "semi-autonomy that survives unattended," then toward "closer to full autonomy." The operator monitors SOS alerts only.

This is evidence and planning material. It does not approve APPLY, bypass governance, or override RISK_POLICY.md, AGENTS.md, or Human Owner authority.

## Headline

The loop today would **survive its first crash only by accident**, and the operator **would never be woken** when it dies, because the SOS alert dead-ends at a local file nobody reads. The planning, severity, and graceful-stop layers are genuinely well-built. The self-sustaining layers (autostart, watchdog, atomic writes, resume-on-restart, backoff, lock release, alert delivery, log rotation) are missing or simulated.

Critical context: the runtime is near-empty right now (`work_ledger.jsonl` is 2 lines, heartbeat is 7 days stale). The resource bombs are **latent, not yet triggered**. The loop would pass a 5-minute demo and die at hour 30. That is exactly what an inspection probes for.

## Two runtime lanes

- **PowerShell night-cycle lane** (`automation/orchestration/Invoke-AiOsNightCycle.ps1`): the real, runnable unattended loop. A genuine `do { Invoke-AiOsNightCycleOnce } while ($Watch)` driver with STOP kill-switch, mode gating, cycle markers. This is what would actually run.
- **TypeScript/JS runtime lane** (`services/runtime/`): a second, parallel loop. Not compiled, not wired to autostart, and crashes on the first tick as currently constructed. Do not run it until rebuilt.

The Python Night-Supervisor lane (`services/python_supervisor/`) is mostly fail-closed and safe; it is preview/DRY_RUN and not the driver.

---

## THE COMPLETE LOOP-KILLER LIST

Organized by when the failure manifests under continuous operation.

### A. Blocks ANY unattended run (manifests immediately / at startup)

| # | Killer | Detail | Location |
|---|---|---|---|
| A1 | SOS alert cannot reach the operator | Only the file channel is enabled. A 02:00 CRITICAL writes a markdown file to `relay/reports/SOS_OUTBOX/` and stops. Webhook and Telegram are coded but disabled and uncredentialed; `notifier.py` hard-blocks live Telegram. The working Android push is unwired. | `services/python_supervisor/notifier.py:223`, `automation/orchestration/notifications/Send-AiOsNotification.ps1`, `tools/android/Send-AiosAdbSosWake.ps1` |
| A2 | No dead-man watchdog | If the loop process dies, nothing fires. Failure is silent. The operator monitoring "SOS only" gets no SOS when the monitor itself stops. | (missing) |
| A3 | No autostart | The scheduler trigger is a proposal only (`schtasks` commented out, no cron/systemd). A human must launch `-Watch` and keep the terminal open. An unattended loop does not start itself. | `automation/orchestration/scheduler/SCHEDULED_TRIGGER_PROPOSAL.md` |
| A4 | TS runtime loop crashes on tick 1 | `index.ts` constructs the loop with `deadLetterQueue: { entries: [] }` and `workerLeases: { leases: [] }`, but consumers read `.packets` / `.expiredWorkers` (undefined). Plus `invalidPacketStatuses` does not exist on `RebuiltDispatcherState`. TypeError on first tick, every run. | `services/runtime/index.ts:9-12`, `runtimeTick.ts:39`, `packetResumeEngine.ts:55`, `runtimeSupervisor.ts:67` |
| A5 | No error boundary inside the tick | Neither `setInterval` (`runtimeLoop.ts:48`, `runtimeBootstrap.js:189`) wraps its body in try/catch. Any throw in a timer is an uncaught exception, Node exits, no restart. This converts every transient error into a permanent loop death. | `services/runtime/runtimeLoop.ts:48`, `services/runtime/runtimeBootstrap.js:189` |

### B. Fails at the first crash (hour-scale, unpredictable)

| # | Killer | Detail | Location |
|---|---|---|---|
| B1 | Double-execution of APPLY work on restart | A fresh `cycle_id` GUID is minted every process start, so the cycle marker's `completed_phases` never matches and is discarded. A restart re-runs every phase from phase 1, including APPLY phases (relay-runner, approval-resume, clear-stale-approvals). Non-idempotent side effects double-fire. | `Invoke-AiOsNightCycle.ps1:37,39,117,374-387` |
| B2 | Resume capability built but unwired | `Resume-AiOsCycle.ps1` reads the marker and computes the first incomplete phase, but has zero callers. The loop never invokes it. | `automation/recovery/Resume-AiOsCycle.ps1` (0 callers) |
| B3 | Corrupt-JSON crash loop | Hot-path state writers use in-place `Set-Content` (runtime state, packet advancement, worker heartbeats). Their readers `throw` on invalid JSON. A crash mid-write leaves a truncated file, and the next start hard-crashes, repeatedly. | `Write-AiOsRuntimeState.ps1:26`, `Update-AIOSWorkerHeartbeat.ps1:59`, `Assign-AIOSPacket.ps1:44` |
| B4 | Orphaned in-flight tasks stranded | If the process dies with a task in `relay/running/`, nothing sweeps it on restart. The reclaimer (`Reclaim-AiOsOrphans.ps1`) is functional but not in the phase list and has zero callers. | `Invoke-AiOsRelayRunner.ps1:371-400`, `Reclaim-AiOsOrphans.ps1` (0 callers) |
| B5 | No process watchdog / restart | Health checks only print warnings and `exit 0`. Nothing restarts the driver on death or hang. | `scripts/control/Get-AiOsRuntimeHealth.ps1`, `services/supervisor/runtimeSupervisor.ts` (report-only) |
| B6 | No retry backoff | Retries have caps but zero delay between attempts. A fast-failing task burns its entire retry budget instantly (hot-loop). | `services/runtime/runtimeAutomationExecutor.ts:232`, `services/dispatcher/deadLetterQueue.ts:46` |
| B7 | git calls without timeout | `night_supervisor_harness.resolve_repo_root` and phase `_git` calls run `git` with no timeout. A hung git (index lock, network FS stall) blocks the run indefinitely. | `night_supervisor_harness.py:84-87` |
| B8 | No runtime mutual exclusion | The PID instance-lock exists but the loop never acquires it (two concurrent loops not prevented). `Test-AiOsFileLock.ps1` is a "modified in last 300s?" heuristic, not a lock. State files have zero write-concurrency protection. | `Test-AiOsInstanceLock.ps1` (uncalled), `Test-AiOsFileLock.ps1:27-36` |

### C. Fails at 24 hours to one week (resource accumulation)

| # | Killer | Detail | Location |
|---|---|---|---|
| C1 | Unbounded in-memory ledger | `memoryLedger` array appends a string on every telemetry event, never cleared. RSS climbs to OOM. Most likely killer of a 24h-to-week JS loop. | `services/telemetry/telemetryWriter.ts:5,26` |
| C2 | Full-ledger re-read every tick | Every 5s tick reads and parses the entire `work_ledger.jsonl` and rebuilds Maps. As the ledger grows, each tick gets slower; self-amplifying with C3. | `services/dispatcher/packetRestoration.js:20` |
| C3 | No `.jsonl` rotation anywhere | `Rotate-AiOsLogs.ps1` filters `*.log` only. Every ledger (`work_ledger`, `night_ledger`, `cost_ledger`, productivity, forex journals) grows unbounded. At 5s ticks ~17k lines/day, GB-scale in a month. | `automation/orchestration/hygiene/Rotate-AiOsLogs.ps1:41` |
| C4 | Null/bad ledger line crashes restoration | A telemetry line that is valid JSON but `null` makes `null.packetId` throw, poisoning every future tick. The ledger is append-only, so one bad writer anywhere is permanent. | `services/dispatcher/packetRestoration.js:57-61` |
| C5 | Per-tick FS write can throw | `appendFileSync`/`writeFileSync`/`renameSync` run every tick with no error handling. ENOSPC/EACCES (more likely as the unrotated ledger grows) throws into the unguarded tick and kills the process. | `services/telemetry/telemetryWriter.ts:29`, `services/runtime/runtimeStateStore.js:44` |
| C6 | Linux disk-space backstop is dead | `Watch-AiOsDiskSpace.ps1` only alerts (never frees space) and checks Windows drives C/D. On Linux it finds no PSDrive and silently reports MISSING. No disk-fill backstop on Linux. | `automation/orchestration/hygiene/Watch-AiOsDiskSpace.ps1:57-60` |

### D. Fails at weeks to a month (slow accumulation, scan degradation)

| # | Killer | Detail | Location |
|---|---|---|---|
| D1 | Per-packet relay files accumulate | Approval/handoff/task/report/error files written per packet, no retention. Accumulate in `relay/` forever. | `Invoke-AiOsRelayWorker.ps1:166,183,190`, `Invoke-AiOsRelayRunner.ps1:181,221,324` |
| D2 | Growing directory scans | `rglob("*.json")` over `automation/orchestration` (capped at 400 parses but enumerates all) and `telemetry/night_supervisor/**/*.json` (grows ~4 files/day) slow every cycle as files accumulate. | `night_supervisor_harness.py:455`, `autonomy_bridge.py:413` |
| D3 | Forex daily journals never pruned | New `forex_paper_journal_YYYYMMDD.jsonl` per day, each appends per trade event. One file/day forever plus intra-day unbounded append. | `automation/forex_engine/journal.py:19,28` |
| D4 | No retention/prune anywhere | Zero cleanup logic across `telemetry/`, `reports/`, `relay/`, `checkpoints/`, `archive/`. The only `Remove-Item` is in the `.log`-only rotation. `archive/` already holds 1185 files. | (missing) |
| D5 | Validator 400-file silent cap | Validation caps JSON parse at 400 files; files beyond are silently unvalidated. Coverage gap grows as the repo grows. | `night_supervisor_harness.py:455` |

### E. Cross-cutting silent corruption / masking

| # | Killer | Detail | Location |
|---|---|---|---|
| E1 | Stale locks/leases detected but never released | `workerLeaseEngine.ts` computes expiry but releases nothing. Lock status is DRY_RUN-only. A dead worker holding a lock blocks APPLY until a human intervenes. | `services/dispatcher/workerLeaseEngine.ts:61`, `locks/Get-AiOsWorkerLockStatus.DRY_RUN.ps1` |
| E2 | Dead-letter queue never drained | Poison tasks are classified and a critical alert is raised, but nothing drains or quarantines them autonomously. They pile up. | `services/dispatcher/deadLetterQueue.ts`, `autonomousScheduler.ts:133` |
| E3 | Worker-assignment fail-open | `load_worker_profiles` swallows all errors and returns `[]`. A corrupt `AIOS_WORKER_PROFILES.json` silently routes everything to one fallback worker with no signal. | `services/python_supervisor/worker_assignment.py:93` |
| E4 | Resume records are dead telemetry | Written every night, read by nothing (only counted). | `night_supervisor_harness.py:601-628` |
| E5 | Health detection not wired to alerts | `Test-AiOsRuntimeHealth` returning BLOCKED triggers no notification. Health and alerting are disconnected systems. | `automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1` |
| E6 | Python malformed-input crashes | `morning_brief_synthesizer.py:185` and `queue_reader.py:33` call `.get` on values that may be strings/lists, raising AttributeError on malformed evidence. | `morning_brief_synthesizer.py:185`, `queue_reader.py:33` |

### What is already good (defensible at inspection)

- The Night-Supervisor Python lane is fail-closed: wrapped JSON reads return safe defaults, the harness exits non-zero on BLOCKED and sandboxes all writes.
- Subprocess calls in the Python lane have bounded timeouts (60s, 20s) and catch TimeoutExpired.
- Graceful shutdown exists: SIGTERM/SIGINT handling in JS, a file kill-switch checked before/after/mid-sleep in PowerShell, with cycle checkpoint markers.
- The SOS severity model is correctly quiet-by-default: only BLOCKED wakes the operator, NEEDS_APPROVAL explicitly does not, with de-duplication, rate-limiting, and quiet-hours with CRITICAL bypass.
- Date-keyed outputs (night summaries, resume, alerts, morning brief) overwrite daily and are bounded.
- Atomic writes are already used in several places (cycle marker, dashboard state, instance lock, orphan reclaimer) and are the pattern to extend.

---

## ENDURANCE-TIERED ROADMAP

Each tier is gated: do not attempt the next survival milestone until the current tier is complete. Effort estimates assume one focused engineer (or a supervised Claude Code session) and are calendar-time ranges.

### Tier 0 — Pre-flight: do not run blind (target: a supervised first run)

The minimum to make any unattended run safe to attempt. Without these, the operator is flying blind.

- [ ] T0.1 Wire one live SOS channel end to end. Enable exactly one of Telegram/webhook/ADB push, provision the credential, remove the live-send block for that channel, and confirm a synthetic BLOCKED reaches the phone. (A1)
- [ ] T0.2 Build a dead-man watchdog: an external check that pages the operator if the cycle heartbeat marker goes stale beyond N minutes. The inverse alert: "the monitor stopped." (A2)
- [ ] T0.3 Add a try/catch error boundary around every loop tick body (log-and-continue). Highest-value single fix. (A5)
- [ ] T0.4 Decide the canonical loop. The PowerShell night cycle is the runnable one; shelve or rebuild the TS runtime loop (it cannot survive tick 1). Do not start the TS loop until A4 is fixed. (A4)

Estimate: 2 to 4 days. Outcome: you can run a supervised first cycle and be woken if it dies.

### Tier 1 — Survive 24 hours: survive the first crash

A 24h loop will be interrupted at least once. Make restart safe.

- [ ] T1.1 Wire `Resume-AiOsCycle.ps1` into loop startup so a restart resumes from the first incomplete phase instead of re-running APPLY phases. (B1, B2)
- [ ] T1.2 Convert all hot-path state writers to atomic write (temp file + rename). Extend the pattern already used by the cycle marker. (B3)
- [ ] T1.3 Make throwing readers tolerant: missing or corrupt state file returns a safe default plus a flag, not an exception. (B3)
- [ ] T1.4 Add a process watchdog that restarts the driver on death or hang. (B5)
- [ ] T1.5 Add exponential backoff between retries so a fast-failing task cannot hot-loop. (B6)
- [ ] T1.6 Add timeouts to all git invocations in the harness. (B7)

Estimate: about 1 week. Outcome: 24h unattended survival across at least one crash.

### Tier 2 — Survive 48 hours to one week: defuse the resource bombs

These are latent today and detonate in the 24h-to-week window.

- [ ] T2.1 Bound the in-memory `memoryLedger` (ring buffer or remove). (C1)
- [ ] T2.2 Replace the per-tick full-ledger re-read with an incremental tail read or offset cursor. (C2)
- [ ] T2.3 Add `.jsonl` rotation (size and age) for all ledgers; extend `Rotate-AiOsLogs.ps1` beyond `*.log`. (C3)
- [ ] T2.4 Harden ledger parsing: skip and log non-object or null lines instead of crashing. (C4)
- [ ] T2.5 Wire `Reclaim-AiOsOrphans.ps1` into the cycle phase list so stranded tasks are swept each cycle. (B4)
- [ ] T2.6 Implement real stale-lock and lease release (TTL enforcement), not detection-only. (E1)
- [ ] T2.7 Drain the dead-letter queue: quarantine poison tasks and surface them to the operator. (E2)
- [ ] T2.8 Fix the disk-space backstop for Linux (cross-platform check) and act on it, not just alert. (C6)

Estimate: 1 to 2 weeks. Outcome: 1 week unattended survival.

### Tier 3 — Survive weeks to a month: retention, idempotency, concurrency

Slow accumulation and concurrency hazards that bite over a month.

- [ ] T3.1 Retention/prune policy for `telemetry/`, `reports/`, `relay/`, `checkpoints/`. (D1, D4)
- [ ] T3.2 Add idempotency keys to packet advancement (a processed-ledger check) so no operation double-executes. (B1 deepening)
- [ ] T3.3 Real mutual exclusion: acquire the instance PID lock in the loop; add real file locks for shared state. (B8)
- [ ] T3.4 Fix worker-assignment fail-open: signal loudly on a corrupt profiles file instead of silent single-fallback routing. (E3)
- [ ] T3.5 Replace the validator 400-file cap with chunked or incremental validation. (D5)
- [ ] T3.6 Bound the growing directory scans with an incremental index. (D2, D3)

Estimate: 2 to 4 weeks. Outcome: weeks-to-month unattended survival.

### Tier 4 — Closer to full autonomy: self-healing and governed APPLY

With endurance proven, extend autonomy under the permanent human approval ceiling.

- [ ] T4.1 Self-heal APPLY mode: auto-create missing dirs and initial state. (E4 area)
- [ ] T4.2 Wire health detection to the alert path: BLOCKED health pages the operator. (E5)
- [ ] T4.3 Route `escalation_engine` BLOCKED items to the notifier. (alerting deepening)
- [ ] T4.4 Connect the governed APPLY lane with explicit APPROVE_COMMIT / APPROVE_PUSH markers (from the Full Autonomy Bridge Map, Phases 2 to 4).
- [ ] T4.5 Close the copy-paste loop and enforce governance in code (Bridge Map Phases 2 and 3).

Estimate: multi-week and ongoing. Outcome: sustained semi-autonomy approaching full, with merge/secrets/broker remaining a permanent human HARD GATE per AI_OS_AUTONOMY_LEVELS.md L5.

---

## Timeline summary

| Milestone | Tier | Calendar estimate | Gate to advance |
|---|---|---|---|
| Supervised first run | Tier 0 | 2 to 4 days | SOS reaches phone; tick has error boundary |
| 24 hours unattended | Tier 1 | about 1 week | Survives one crash without double-APPLY |
| 1 week unattended | Tier 2 | 1 to 2 weeks | No resource bomb detonates; orphans swept |
| Weeks to a month | Tier 3 | 2 to 4 weeks | Retention + idempotency + concurrency safe |
| Closer to full autonomy | Tier 4 | multi-week, ongoing | Self-heal + governed APPLY under human gate |

Cumulative to a month-survivable loop: roughly 5 to 9 weeks of focused work, tier by tier, validated at each milestone before advancing.

## Operator safety rule

Do not register the unattended scheduler until Tier 0 is complete. Today a 02:00 CRITICAL would write a file to `relay/reports/SOS_OUTBOX/` and stop there, and a loop death would be silent. Tier 0 closes both gaps. Every tier after that is validated by actually running to its milestone before advancing.

## Authority

This document is evidence and planning material only. It does not approve APPLY, ADB execution, scheduler registration, live trading, or autonomous mutation. Human Owner approval gates remain final.

## Generated

- Date: 2026-06-08
- Branch: claude/repo-overview-D1GBF
- Method: five parallel deep-scan agents across crash surfaces, resource exhaustion, state durability, loop control, and SOS alerting
- Scope: the runtime loop lanes (PowerShell night cycle, TS/JS runtime, Python supervisor)
