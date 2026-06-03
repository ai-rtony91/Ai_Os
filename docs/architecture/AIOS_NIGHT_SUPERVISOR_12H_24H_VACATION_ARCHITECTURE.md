# AI_OS Night Supervisor 12H / 24H Vacation Architecture

Status: spec-only planning architecture (reference / prototype). DRY_RUN-first, approval-gated. This document describes a model; it does not grant runtime, orchestration, scheduler, broker, or live-trading authority.

> Authority: subordinate to `AGENTS.md`, `RISK_POLICY.md`, and the existing
> `automation/orchestration/night_supervisor/` module. Where this document conflicts
> with root authority, the stricter rule wins. This is the AI_OS-native translation of
> a Base44 sandbox prototype — Base44 output is reference material only.

## Purpose

Define how AI_OS supervises itself **unattended** in two bounded, observe-only modes, and how it surfaces what happened to the operator on return — without ever crossing into autonomous execution.

- **12H Night mode (`NIGHT_12H`)** — a single overnight window (~12h). Hour-by-hour read-only observation, validation, alert previews, and a morning build-prep queue.
- **24H Vacation mode (`VACATION_24H`)** — an extended, multi-day, **paper-only** window. Same observe-only discipline, more conservative, with SOS preview escalation on blockers.

This is a **refinement** of the existing Night Supervisor, not a new brain. The active engine remains
`automation/orchestration/night_supervisor/night_supervisor_harness.py` (and its house-style
`Invoke-AiOsNightSupervisor.DRY_RUN.ps1` preview). This architecture adds the 12H/24H mode framing, the
Base44 entity contracts, the alert/robot-helper presentation model, and the dashboard view shapes.

## What this is NOT

- NOT production autonomy. NOT an executor. NOT a scheduler/service.
- NOT hardware execution (no GPIO/motor/camera/mic/speaker runtime, no real TTS/STT).
- NOT a real notification sender — every alert is a preview; `delivered` is always `false`.
- NOT broker/trading execution — vacation mode is paper-only; live broker/OANDA/real orders are blocked.
- NOT commit/push/merge authority and NOT active runtime/packet/approval/lock mutation.

## Entity model (Base44 7 entities → AI_OS schemas)

Contracts live under `schemas/aios/night_supervisor/` and `schemas/aios/pi_robot_helper/`:

| Entity | Schema | Role |
|---|---|---|
| Supervisor session | `aios_supervisor_session.schema.json` | A bounded 12H/24H supervision run. |
| Supervisor hour | `aios_supervisor_hour.schema.json` | One hour-granularity observation slice. |
| Alert event | `aios_alert_event.schema.json` | A preview alert (status / approval / blocked / progress / SOS). |
| Build-prep item | `aios_build_prep_item.schema.json` | A task *prepared* (never executed) for the operator's return. |
| Codex export packet | `aios_codex_export_packet.schema.json` | Structured tokenized work packet exported from a session. |
| Robot helper status | `aios_robot_helper_status.schema.json` | Observe-only Pi (PiCar-X) alert-assistant status. |
| Voice/audio rule | `aios_voice_audio_rule.schema.json` | Preview routing of an alert to display/voice/led/audio_tone. |

Worked sample instances of each live under the matching `schemas/aios/<domain>/examples/`.

## Alert model

Canonical alert classes (see `aios_alert_event.schema.json` `event_type`) extend the classes in
`docs/specs/AIOS_PICAR_X_ROBOT_HELPER_SPEC.md`:

- Routine / quiet: `AIOS_STATUS_OK`, `AIOS_BRIEF_READY`, `AIOS_SAFE_TO_IGNORE`, `AIOS_SESSION_START`, `AIOS_SESSION_END`, `AIOS_BUILD_PROGRESS`, `AIOS_BUILD_PREP_READY`, `AIOS_PAPER_TRADE_SUMMARY`.
- Review-worthy: `AIOS_APPROVAL_NEEDED`, `AIOS_VALIDATOR_FAILED`.
- Wake-worthy: `AIOS_BLOCKED`, `AIOS_OMEN_WAKE_FAILED`, `AIOS_SOS_CRITICAL`.

Severity ladder: `INFO < REVIEW < WARNING < CRITICAL < SOS`. `wake_worthy` gates escalation. No alert is
delivered: routing is previewed for a future approved dispatcher only.

## Presentation layer (Pi robot helper)

The Pi helper is an **alert assistant**, OBSERVE_ONLY. It maps alerts to a preview presentation
(display lines, LED color, voice text, dark-room brightness) via `aios_voice_audio_rule` records. Nothing is
spoken or actuated; `preview_only` / `spoken:false` hold throughout. Detailed responsibility/blocked lists
live in the PiCar-X spec.

## Dashboard layer

Reference UI fixtures live in `apps/dashboard/mock-data/` (`night-supervisor-12h`, `vacation-24h-paper-mode`,
`pi-robot-helper-alerts`, `build-progress-sos-alerts`). They are mock-only (`"wired": false`) and must not be
wired into `App.jsx` without a separate dashboard decision (see `docs/audits/active-system-map.md`).

## Zone ownership (East / West)

Per `docs/governance/aios-identity-and-lane-governance.md`:

- **West (Claude Code West)** owns the contracts and docs in this scaffold: `docs/`, `schemas/aios/`, and the
  `apps/dashboard/mock-data/` fixtures.
- **East (Codex East)** owns the runtime-adjacent pieces: `automation/orchestration/night_supervisor/`,
  `automation/orchestration/notifications/`, `automation/orchestration/pi_robot_helper/`, and `telemetry/`
  example promotion. Those are specified in
  `docs/workflows/AIOS_NIGHT_SUPERVISOR_EAST_LANE_CODEX_PACKET.md` and require a separate approved East packet.

## Safety boundary (permanent)

No live trading · no broker execution · no real orders/webhooks · no secrets/credentials · no commit/push/merge ·
no active runtime/packet/approval/lock mutation · no scheduler/background/service install · no hardware runtime ·
no real notification senders · LLM output is never command authority · validator PASS is evidence only.

## References

- `automation/orchestration/night_supervisor/README.md` — active Night Supervisor module.
- `automation/orchestration/night_supervisor/NIGHT_SUPERVISOR_SAFETY_POLICY.json` — blocked actions / fail-closed.
- `docs/workflows/AI_OS_OVERNIGHT_SUPERVISOR_WORKFLOW.md` — canonical overnight workflow this refines.
- `docs/specs/AIOS_PICAR_X_ROBOT_HELPER_SPEC.md` — robot helper spec.
- `docs/workflows/WORKER_TASK_LIFECYCLE_STANDARD.md` — canonical lifecycle states used by build-prep.
- Mode/alert/robot workflows: see the `docs/workflows/AIOS_*_WORKFLOW.md` set created in this scaffold.
