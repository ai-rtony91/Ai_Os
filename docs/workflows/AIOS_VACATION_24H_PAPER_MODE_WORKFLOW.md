# AI_OS Vacation 24H Paper Mode Workflow

Status: v1 workflow (reference / prototype). DRY_RUN-first, paper-only, approval-gated.

> Authority: subordinate to `AGENTS.md`, `RISK_POLICY.md`, and the Night Supervisor module.
> Stricter root rule wins. Base44 output is reference material only.

## Purpose

Supervise AI_OS over an **extended, multi-day, operator-away** window in the most conservative observe-only posture. Same hour-slice discipline as 12H mode, but **paper-only** for any trading observation and with **SOS preview escalation** when a blocker appears.

**It does NOT** trade live, connect a broker/OANDA, place real orders, send real notifications, run a scheduler/daemon, auto-approve, or mutate active state. Vacation mode never increases authority — it tightens it.

## Scope

- Mode: `VACATION_24H` (`aios_supervisor_session.schema.json`), `paper_mode_only:true` enforced.
- Rolling `aios_supervisor_hour` slices across the window; `aios_alert_event` previews; `aios_build_prep_item` queue.
- Trading observation is paper-only; `paper_trade_summary.fill_latency_ms` may be `null` until instrumented.

## Window posture

1. **Conservative observe** — read-only snapshots only; longer cadence acceptable.
2. **Blocker handling** — on validator FAIL / repo mismatch / unsafe condition: classify `AIOS_BLOCKED` or
   `AIOS_SOS_CRITICAL` (`wake_worthy:true`), set session `status:BLOCKED`, and **halt mutation by design**.
3. **SOS preview** — route SOS to preview channels (file/dashboard/screen/led/voice); `delivered` stays `false`.
4. **Prep, don't act** — accumulate build-prep items for the operator's return; never execute.
5. **Daily rollup** — per-day summary; carry blockers forward until reviewed.

## Authority boundary / stop conditions

- Any blocker halts forward mutation and waits for the operator. No self-resume past a blocker.
- Paper-only is permanent for this mode; any live-trading path is a hard stop.
- No auto-approval at any tier. Promotion to APPLY requires a separate approved packet.

## References

`AIOS_NIGHT_SUPERVISOR_12H_WORKFLOW.md` · `AIOS_NIGHT_SUPERVISOR_12H_24H_VACATION_ARCHITECTURE.md` ·
`AIOS_BUILD_PROGRESS_SOS_ALERT_WORKFLOW.md` · `NIGHT_SUPERVISOR_SAFETY_POLICY.json`.
