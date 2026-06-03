# AI_OS Build Progress / SOS Alert Workflow

Status: v1 workflow (reference / prototype). Preview-only alerting.

> Authority: subordinate to `AGENTS.md` and the Night Supervisor module. Stricter rule wins.
> Base44 output is reference material only.

## Purpose

Define two alert lanes raised during 12H/24H supervision:

- **Build progress** — low-urgency signal that prepared work advanced (e.g. items reached
  `ready_for_runner_preview`, prep queue grew).
- **SOS** — high-urgency, wake-worthy signal that something is blocked and the operator should look.

**It does NOT** deliver notifications, escalate to a human via a real channel, auto-execute prepared work, or
mutate state. `delivered` is always `false`.

## Scope

- Build progress: `AIOS_BUILD_PROGRESS`, `AIOS_BUILD_PREP_READY` (severity `INFO`, `wake_worthy:false`).
- SOS: `AIOS_SOS_CRITICAL`, `AIOS_BLOCKED`, `AIOS_OMEN_WAKE_FAILED` (severity `CRITICAL`/`SOS`, `wake_worthy:true`).
- Backing data: `aios_alert_event` + `aios_build_prep_item`.

## Triggers

| Condition | Event type | Severity | Wake-worthy |
|---|---|---|---|
| Prep item reached `ready_for_runner_preview` | `AIOS_BUILD_PROGRESS` | INFO | no |
| Prep queue crossed a threshold | `AIOS_BUILD_PREP_READY` | INFO | no |
| Validator FAIL / repo integrity fail | `AIOS_SOS_CRITICAL` | SOS | yes |
| Forbidden-write attempt / unsafe condition | `AIOS_BLOCKED` | CRITICAL | yes |
| Omen unreachable for wake | `AIOS_OMEN_WAKE_FAILED` | WARNING/CRITICAL | yes |

## Routing (preview)

SOS routes to all preview channels (`file`, `dashboard`, `screen`, `led`, `voice`); build-progress routes quietly
(`file`, `dashboard`). Routing is recorded in `channels_planned`; nothing is contacted.

## Authority boundary / stop conditions

- SOS halts forward mutation (supervision waits for the operator); it never triggers an automated remediation.
- No alert authorizes APPLY, commit, push, merge, worker launch, scheduler, or trade.

## References

`AIOS_NIGHT_SUPERVISOR_12H_WORKFLOW.md` · `AIOS_VACATION_24H_PAPER_MODE_WORKFLOW.md` ·
`aios_alert_event.schema.json` · `aios_build_prep_item.schema.json`.
