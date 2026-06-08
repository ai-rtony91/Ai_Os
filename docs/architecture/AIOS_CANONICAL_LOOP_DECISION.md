# ADR: The Canonical AI_OS Unattended Loop

- Status: ACCEPTED (evidence-and-planning record; not an APPLY authorization)
- Date: 2026-06-08
- Branch: claude/repo-overview-D1GBF
- Decision class: Architecture Decision Record (Tier 0, item T0.4 of the Endurance Hardening Roadmap)
- Source of truth: `docs/roadmap/AIOS_ENDURANCE_HARDENING_ROADMAP.md`

## Decision (one line)

The PowerShell night cycle, `automation/orchestration/Invoke-AiOsNightCycle.ps1`, is the **canonical runnable unattended loop**. The TypeScript runtime in `services/runtime/` is **non-runnable today and is SHELVED**; it must not be started in production until it is rebuilt against the un-shelve criteria below.

## Context: two parallel loops exist

AI_OS currently carries two independent loop implementations that both claim to be "the runtime loop." The Endurance Hardening Roadmap calls this out directly in its "Two runtime lanes" section and as loop-killer A4. Only one of them actually runs end to end.

### Lane 1 — PowerShell night cycle (canonical)

File: `automation/orchestration/Invoke-AiOsNightCycle.ps1`

Evidence that it is the real, runnable driver:

- It has a genuine top-level driver loop: `do { Stop-AiOsNightCycleIfRequested; Invoke-AiOsNightCycleOnce; ... } while ($Watch)` (lines 374-387).
- It runs a complete, ordered phase list (`$script:AiOsPhaseNames`, lines 45-58): hygiene, clear-stale-approvals, pull-backlog, relay-runner, approval-resume, relay-runner-resume-drain, self-continuation, night-supervisor, autonomy-bridge, morning-brief, sos-file-notifier, pr-watch.
- It is mode-gated (`Get-AiOsActiveMode.ps1`): OFF exits cleanly, DAY_OBSERVER throttles to 1800s and skips APPLY phases, NIGHT_AUTOPILOT runs the full APPLY-eligible cycle at 300s (lines 293-340).
- It honors a file kill-switch checked before, during, and after each sleep: `control/self_continuation/STOP` (`Stop-AiOsNightCycleIfRequested`, lines 196-208, 374-386).
- It is DRY_RUN by default; `-Apply` is passed only to child steps that already support APPLY gates, and only when the resolved mode is not observe-only (`$effectiveApply = ($Apply -and -not $observeOnly)`, line 301).
- It writes a cycle checkpoint marker atomically (temp file + `Move-Item`) at `control/cycle/last_marker.json` (`Write-CycleMarker`, lines 184-186).
- Its own header states the hard limits it never crosses: it never runs git, schtasks, `Register-ScheduledTask`, `New-Service`, `sc.exe`, secret readers, or broker/live trading (lines 11-13).

This is the loop that "would actually run" per the roadmap.

### Lane 2 — TypeScript runtime (shelved)

Files: `services/runtime/index.ts`, `services/runtime/runtimeLoop.ts` (plus the dispatcher, telemetry, and supervisor modules it imports).

Evidence that it is non-runnable today:

- **Wiring bug at construction (roadmap A4).** `services/runtime/index.ts` constructs the loop with `deadLetterQueue: { entries: [] }` and `workerLeases: { leases: [] }` (lines 9-12), but downstream tick consumers read different shapes — `.packets` / `.expiredWorkers`, and an `invalidPacketStatuses` field that does not exist on `RebuiltDispatcherState`. The roadmap traces this to a TypeError on the first tick of every run (`runtimeTick.ts:39`, `packetResumeEngine.ts:55`, `runtimeSupervisor.ts:67`).
- **Not compiled.** There is no build artifact and no compile step in the canonical cycle. The `.ts` is not transpiled or executed by any phase of the night cycle.
- **Not autostarted.** Nothing launches `services/runtime/index.ts`. The night cycle never references it. Autostart is a documented gap (roadmap A3); the only TS entry point relies on a human running it directly.
- **Partial hardening only.** Note for accuracy: the current `services/runtime/runtimeLoop.ts` *does* wrap the tick body in a `try/catch` that logs and continues (lines 48-65), which is the shape roadmap T0.3 calls for. That single in-loop guard does not un-shelve the lane, because the A4 construction bug throws before a stable tick is ever reached, the lane is still uncompiled and unwired to autostart, and there is still no external watchdog. The error boundary is necessary but not sufficient.

## Decision rationale

1. **Only one loop runs today, and it is the PowerShell one.** Choosing it as canonical is choosing the implementation that already survives a real cycle, is mode-gated, has a kill-switch, and writes an atomic checkpoint marker. The TS lane cannot complete a single tick as constructed.
2. **Running both is a hazard.** Two loops sharing the same `relay/`, `telemetry/`, and state files with no mutual exclusion (roadmap B8) risks double-execution and state corruption. Designating one canonical lane removes that ambiguity.
3. **Shelving is cheaper and safer than racing to fix the TS lane.** Tier 0's job is to make a supervised first run *safe*, not to have two loops. The TS lane's crash surface (A4, plus the resource bombs C1/C2/C4/C5 that live in its telemetry and dispatcher modules) is exactly what an endurance inspection probes for. It does not belong in a production path until rebuilt.

## Consequences

### Positive

- There is one unambiguous answer to "what is the loop": `Invoke-AiOsNightCycle.ps1`.
- Tier 0 through Tier 3 hardening work targets the PowerShell lane and the Python supervisor it invokes, not a parallel TS rewrite.
- The TS lane can be developed and tested off the production path without endangering an unattended run.

### Negative / accepted

- The TS runtime's design intent (event bus, dispatcher, worker leases, dead-letter queue) is parked. Any capability there must, for now, be reached through the PowerShell cycle and the Python supervisor.
- Some endurance fixes in the roadmap reference TS files (for example C1 `telemetryWriter.ts`, C2 `packetRestoration.js`, B6 `runtimeAutomationExecutor.ts`). Those fixes are only load-bearing if and when the TS lane is un-shelved; until then they are latent and out of the canonical run path.

### Operational rule

- Do not start `services/runtime/index.ts` (or any wrapper that boots `RuntimeLoop`) in production or in an unattended/scheduled context.
- The canonical unattended entry point is `Invoke-AiOsNightCycle.ps1 -Watch`, launched only under the Tier 0 operator safety gate (one live SOS channel armed and a dead-man watchdog running — see `docs/workflows/AIOS_SOS_ARMING_RUNBOOK.md` and the roadmap Operator safety rule).

## Conditions to un-shelve the TS runtime loop

The TS lane may be reconsidered as a runnable loop only when **all** of the following are demonstrably true, each with evidence:

1. **It compiles.** A clean TypeScript build of `services/runtime/` and its imports, with no type errors. The A4 shape mismatch is resolved: `index.ts` constructs `deadLetterQueue` / `workerLeases` in the exact shapes the tick consumers read (`.packets`, `.expiredWorkers`), and `invalidPacketStatuses` exists on `RebuiltDispatcherState` or is removed from consumers.
2. **It passes tick 1.** The loop completes its first tick (and a sustained run of ticks) without a TypeError or uncaught exception, against a representative `work_ledger.jsonl`.
3. **Every tick body has a try/catch error boundary.** Confirmed in `runtimeLoop.ts` (present today) and in any other timer/interval entry point it uses (for example `runtimeBootstrap.js:189`, flagged by roadmap A5 as still unguarded). A throw in a timer must log and continue, never exit the process.
4. **A watchdog is wired.** An external dead-man watchdog (roadmap T0.2 / A2) monitors the TS loop's heartbeat and pages the operator if it goes stale, and a process watchdog (roadmap B5/T1.4) restarts it on death or hang.
5. **Resource bombs are defused.** Before any unattended TS run beyond a supervised demo, the latent killers in its modules are fixed: bounded `memoryLedger` (C1), incremental ledger read (C2), null-line-tolerant restoration (C4), and guarded per-tick FS writes (C5).
6. **Mutual exclusion with the PowerShell lane.** The two loops cannot run concurrently against shared state (roadmap B8). Un-shelving requires either a single-active-loop interlock or a clean hand-off that retires the PowerShell driver.

Until all six hold, the TS lane stays SHELVED and this ADR's operational rule applies.

## References

- `docs/roadmap/AIOS_ENDURANCE_HARDENING_ROADMAP.md` — Two runtime lanes; loop-killers A3, A4, A5, B5, B6, B8, C1, C2, C4, C5; Tier 0 item T0.4; Operator safety rule.
- `automation/orchestration/Invoke-AiOsNightCycle.ps1` — the canonical driver.
- `services/runtime/index.ts`, `services/runtime/runtimeLoop.ts` — the shelved lane.

## Authority

This document is evidence and planning material only. It does not approve APPLY, scheduler registration, live-send, ADB execution, or live trading, and it does not start any loop. It records an architecture decision for review. Human Owner approval gates remain final, and this ADR does not weaken AI_OS validators, approvals, locks, stop points, or any protected safety boundary defined by `AGENTS.md` and `RISK_POLICY.md`.
