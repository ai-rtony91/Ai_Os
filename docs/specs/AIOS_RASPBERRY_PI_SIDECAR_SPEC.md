# AI_OS Raspberry Pi 5 / PiCar-X Sidecar Spec

Status: spec-only planning

Packet: `AIOS-24H-LOOP-CODEX5-PI5-PICAR-SIDECAR-SPEC-APPLY-001`

## Purpose

This document defines the first safe role boundary for a Raspberry Pi 5 / PiCar-X sidecar that supports AI_OS overnight and morning operation without moving AI_OS core execution off the Omen workstation.

The sidecar is a local wake, watch, alert, and presence surface. It is not a second AI_OS runtime, not a repo worker, not an approval authority, and not a trading system.

## Operating Principle

The Omen remains the command machine.

The Pi sidecar may help the operator notice, wake, and inspect AI_OS state, but it must not become a parallel source of truth or execution lane. The sidecar should consume approved status/brief evidence and present it through low-friction physical outputs such as voice, display, LED, or PiCar-X movement cues.

## Current Authority Boundary

Authoritative AI_OS execution remains on:

- repo: `ai-rtony91/Ai_Os`
- branch: `main`
- active local repo: `C:\Dev\Ai.Os`
- primary machine: Omen workstation

The Pi sidecar must treat the Omen and the repo as upstream authority. If the Omen is offline or unreachable, the sidecar reports that condition instead of trying to replace the Omen.

## Actual Robot Hardware

The planned robot hardware is:

- product: SunFounder PiCar-X AI Video Robot Car Kit
- ASIN: `B0CGLPF29H`
- model: `PiCarX`
- Raspberry Pi board included: no
- compatible Raspberry Pi boards:
  - Raspberry Pi 5
  - Raspberry Pi 4
  - Raspberry Pi 3B+
  - Raspberry Pi 3B
  - Raspberry Pi Zero 2W

The kit is treated as a sidecar hardware platform only. It may support future physical alert, camera, sensor, voice, and robot-presence workflows after separate approval. It does not change AI_OS repo, runtime, approval, scheduler, credential, or trading authority.

Known kit capabilities and components:

- camera module for AI/video workflows.
- ultrasonic sensor for obstacle distance sensing.
- grayscale sensors for line and surface detection.
- line-following support.
- obstacle-avoidance support.
- object-following support.
- SunFounder Robot HAT.
- three 9g servos.
- two motors.
- rechargeable batteries.
- Python support.
- Scratch support.

## Sidecar Responsibilities

The Raspberry Pi 5 / PiCar-X sidecar may be designed to perform these responsibilities after separate implementation approval:

1. Wake-on-LAN assist:
   - send an approved Wake-on-LAN packet to the Omen.
   - retry only within a documented retry limit.
   - report whether the Omen became reachable.

2. Watchdog observation:
   - check whether the Omen appears reachable.
   - check whether an approved AI_OS status or morning brief artifact is available.
   - classify stale or missing evidence as `UNKNOWN`, `STALE`, or `BLOCKED` instead of guessing.

3. Morning brief alert:
   - announce or display that a morning brief is ready.
   - summarize only approved brief fields such as `STATUS`, `NEEDS APPROVAL`, and `SAFE NEXT ACTION`.
   - avoid long-form repo or system details unless the operator requests them through an approved UI/flow.

4. Robot/voice notification:
   - use speaker, text-to-speech, display, LED, or PiCar-X movement cues to notify the operator.
   - distinguish routine status from wake-worthy blockers.
   - keep routine alerts quiet during night or dark-room operation.

5. Dark-room operation:
   - provide low-brightness or no-brightness status.
   - avoid forcing the Omen monitor on for routine status.
   - use short voice or physical cues for urgent status.

6. Integration compatibility:
   - remain compatible with future Tasker and Telegram notification contracts.
   - treat Tasker and Telegram as notification paths, not autonomous execution authority.

## Blocked Responsibilities

The Pi sidecar must not:

- run AI_OS repo commits, merges, pushes, pull requests, branch changes, staging, reset, clean, or GitHub automation.
- mutate work packets, approvals, queues, locks, validator state, runtime state, telemetry, or governance authority.
- run AI_OS core execution, supervisor loops, schedulers, or worker launchers unless a later packet explicitly approves a bounded helper and stop point.
- store, print, transmit, or manage secrets, API keys, broker credentials, Telegram bot tokens, chat identifiers, webhook URLs, or vault data.
- create startup tasks, scheduled tasks, daemons, services, or background persistence without separate Human Owner approval.
- execute broker, OANDA, webhook, live trading, real order, or live route behavior.
- use LLM output as command authority.
- override Omen state, repo state, validator output, approval gates, or Human Owner approval.
- become a second source of truth for AI_OS architecture, governance, runtime, or trading state.

## Wake-on-LAN Flow

The proposed WOL flow is:

1. Trigger source:
   - operator presses a physical or local sidecar control, or
   - an approved future schedule/trigger requests Omen wake, or
   - a future approved Tasker/Telegram notification flow requests wake.

2. Preflight:
   - verify WOL is enabled in the Omen BIOS/UEFI and network adapter settings.
   - verify the Omen MAC address and LAN broadcast target are configured outside the repo or in an approved non-secret local config.
   - verify the trigger is permitted by the current sidecar mode.

3. Wake attempt:
   - send one WOL packet.
   - wait a configured interval.
   - perform a reachability check.
   - retry only within the approved retry limit.

4. Result:
   - if Omen is reachable, report `OMEN_AWAKE`.
   - if Omen remains unreachable, report `OMEN_WAKE_FAILED`.
   - if config is missing or invalid, report `WOL_BLOCKED_CONFIG`.
   - if the action is not approved, report `WOL_BLOCKED_APPROVAL`.

5. Stop point:
   - do not start AI_OS runtime, open terminals, launch workers, schedule tasks, or perform repo actions from the Pi.

## Omen Awake And Dark-Room Rules

The Omen should remain the execution host while the Pi handles low-friction operator awareness.

Rules:

- Omen awake does not mean AI_OS may run protected actions.
- Omen awake does not approve runtime loops, commits, pushes, merges, GitHub actions, trading actions, or scheduler work.
- The sidecar should avoid forcing a bright monitor state during dark-room operation.
- Routine successful status should stay quiet.
- Wake-worthy status should be limited to `BLOCKED`, `NEEDS_APPROVAL`, `OMEN_WAKE_FAILED`, or another separately approved urgent class.
- The Pi should prefer dim display, LED, or short voice output before escalating to phone/Telegram/Tasker channels.

## Morning Notification Flow

The proposed morning notification flow is:

1. Omen produces or exposes approved morning status/brief evidence.
2. Pi sidecar reads only the approved status/brief surface.
3. Pi renders a compact state:
   - `STATUS`
   - `WHAT CHANGED`
   - `NEEDS ANTHONY APPROVAL`
   - `SAFE NEXT ACTION`
   - `SAFE TO IGNORE`
4. Pi uses dark-room-safe output:
   - display if the operator is nearby.
   - voice if an audible cue is appropriate.
   - LED or PiCar-X movement cue for simple status.
5. Pi escalates only when the status is urgent and the relevant channel has been separately approved.

Morning notification must remain report/display behavior. It must not approve or execute the next action.

## Tasker And Telegram Compatibility

Tasker and Telegram are governed by the existing API and notification safety boundaries. The sidecar spec does not approve live Telegram, Tasker, bot token, chat ID, webhook, phone automation, or two-way approval execution.

Compatible future message classes:

| Message class | Meaning | Wake-worthy by default |
|---|---|---|
| `AIOS_BRIEF_READY` | Morning brief is available | No |
| `AIOS_STATUS_OK` | No action needed | No |
| `AIOS_APPROVAL_NEEDED` | Human approval is required before mutation or protected action | Maybe, based on severity |
| `AIOS_BLOCKED` | AI_OS stopped on a blocker | Yes, if severity is high |
| `AIOS_OMEN_WAKE_FAILED` | Pi could not wake or reach the Omen | Yes |
| `AIOS_SAFE_TO_IGNORE` | Status is informational only | No |

Compatibility rules:

- Tasker starts notification-only.
- Telegram starts notification-only unless a separate approval-gated executor design is approved.
- Phone-side automation must be configured by the operator, not Codex.
- Secrets must stay outside the repo and outside prompts.
- Sidecar message payloads must avoid secret values and protected-action commands.
- Any two-way approval bridge must preserve the existing approval boundary: Human Owner approval is required, validator output is evidence only, and protected actions remain separately gated.

## Watchdog Model

The sidecar watchdog should answer only these questions:

- Is the Omen reachable?
- Is AI_OS status evidence available?
- Is the evidence fresh enough to trust?
- Is there a blocker or approval-needed signal?
- What is the next safe operator-visible message?

The watchdog must not:

- repair the repo.
- move packet state.
- mutate approval state.
- restart AI_OS runtime.
- start a scheduler or loop.
- promote stale evidence to truth.

If evidence is missing or stale, the watchdog reports `UNKNOWN` or `STALE` and stops at notification.

## Stop Conditions

The Pi sidecar lane must stop when:

- Omen identity, MAC address, or LAN target is unknown.
- WOL enablement has not been manually verified.
- network behavior would be changed.
- a requested action requires secrets or credentials.
- Telegram, Tasker, webhook, or phone automation is requested without separate approval.
- a requested action would create a scheduler, daemon, service, startup item, or persistent loop.
- a requested action would mutate repo, runtime, telemetry, packet, approval, queue, lock, Git, GitHub, trading, broker, OANDA, or live webhook state.
- AI_OS status evidence is stale, missing, or contradictory.
- a protected action appears in a notification as if it were already approved.

## Future Approval Gates

Each future phase requires its own packet, allowed paths, validator chain, and Human Owner approval:

1. Sidecar topology spec update:
   - document exact local network assumptions and operator-visible success conditions.

2. Local config design:
   - define config shape without storing secrets in the repo.

3. WOL DRY_RUN helper:
   - preview target and validation only, no packet sent.

4. WOL APPLY helper:
   - send WOL only after explicit approval and hardware/network preflight.

5. Read-only status adapter:
   - read approved Omen status/brief evidence only.

6. Local display/voice prototype:
   - render local alert output only.

7. Tasker/Telegram notification adapter:
   - follow existing notification bridge operator steps and API integration safety workflow.

8. Scheduler or persistence review:
   - separate high-risk packet only after sidecar behavior is proven manually.

## Explicit Non-Goals

- No repo migration to Raspberry Pi.
- No AI_OS core runtime migration to Raspberry Pi.
- No autonomous approval path.
- No protected repo action from Raspberry Pi.
- No live trading.
- No broker or OANDA integration.
- No secret handling.
- No scheduler creation in this spec.
- No hardware commands in this spec.

## Operator-Visible Success Condition

The sidecar lane is successful when a future approved implementation lets the operator see or hear this kind of compact status without waking the Omen display:

```text
AI_OS STATUS: NEEDS_APPROVAL
OMEN: AWAKE
MORNING BRIEF: READY
NEXT SAFE ACTION: Review approval inbox from Omen main control.
```

The sidecar is not successful merely because a process runs. It is successful only when the operator can safely understand whether the Omen is awake, whether AI_OS needs attention, and what the next safe human action is.

## References

- `AGENTS.md`
- `README.md`
- `docs/governance/source-of-truth-map.md`
- `docs/audits/active-system-map.md`
- `docs/workflows/AI_OS_API_INTEGRATION_SAFETY_WORKFLOW.md`
- `docs/workflows/AI_OS_OVERNIGHT_SUPERVISOR_WORKFLOW.md`
- `docs/governance/NOTIFICATION_BRIDGE_OPERATOR_STEPS.md`
