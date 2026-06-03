# AI_OS Pi Robot Helper Alert Workflow

Status: v1 workflow (reference / prototype). OBSERVE_ONLY, preview-only.

> Authority: subordinate to `AGENTS.md` and `docs/specs/AIOS_PICAR_X_ROBOT_HELPER_SPEC.md`.
> Stricter rule wins. Base44 output is reference material only.

## Purpose

Define how the Pi (PiCar-X) **alert assistant** consumes AI_OS alert events and presents them as a preview
(display / LED / voice text), including dark-room and quiet-hours behavior — so an away operator gets a glanceable
signal without the workstation.

**It does NOT** drive GPIO, motors, camera, microphone, or speaker runtime; perform real TTS/STT; commit/push;
mutate AI_OS state; or treat any LLM output as a command. The helper announces; it never acts.

## Scope

- Inputs: `aios_alert_event` records + `aios_voice_audio_rule` records.
- Output: `aios_robot_helper_status` snapshots and screen previews (see `screen_preview.sample.json`).
- Roles (from spec): wake-on-LAN *status check* (no execution), watchdog observation, brief announce, voice/audio
  notification preview, dark-room operation.

## Flow

1. **Receive** alert event (preview; `delivered:false`).
2. **Match** the highest-priority enabled `aios_voice_audio_rule` for the `event_type` + `severity`.
3. **Gate** on quiet hours and `wake_worthy`: suppress below threshold; SOS/CRITICAL may bypass suppression.
4. **Present (preview)** — set `display_state`, `led_state`, dark-room brightness, and a `voice_line_text`
   (text only, `spoken:false`).
5. **Record** an `aios_robot_helper_status` snapshot.

## Authority boundary / stop conditions

- Preview only: `preview_only:true`, `spoken:false`, no actuation.
- Unreachable Omen → `AIOS_OMEN_WAKE_FAILED` preview; the helper never forces a wake action.
- No hardware runtime code is in scope for this workflow or the West scaffold.

## References

`AIOS_SCREEN_VOICE_AUDIO_ALERT_WORKFLOW.md` · `aios_robot_helper_status.schema.json` ·
`aios_voice_audio_rule.schema.json` · `AIOS_PICAR_X_ROBOT_HELPER_SPEC.md`.
