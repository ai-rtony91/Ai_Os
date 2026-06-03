# AI_OS Screen / Voice / Audio Alert Workflow

Status: v1 workflow (reference / prototype). Preview-only presentation layer.

> Authority: subordinate to `AGENTS.md` and the Night Supervisor module. Stricter rule wins.
> Base44 output is reference material only.

## Purpose

Define the **presentation contract** for turning an `aios_alert_event` into a screen render, an LED state, and a
voice/audio *text* line — across normal, dark-room, and quiet-hours conditions — without ever producing real audio
or driving real hardware.

**It does NOT** emit real TTS, play audio, drive a physical screen/LED, or send a notification. It produces a
**preview object** describing what *would* be shown/said.

## Scope

- Inputs: `aios_alert_event` + matching `aios_voice_audio_rule`.
- Output: a screen-preview object (see `schemas/aios/pi_robot_helper/examples/screen_preview.sample.json`).
- Channels: `display`, `voice` (text), `led`, `audio_tone` (described, not played).

## Rendering rules

1. **Severity → style**: `INFO/REVIEW` quiet; `WARNING` amber; `CRITICAL/SOS` red + `pulse_red` LED.
2. **Dark room**: clamp `brightness_percent` to the rule's `dark_room_brightness` (e.g. 15%).
3. **Quiet hours**: suppress presentations below `suppress_below_severity`; `SOS`/`CRITICAL` may bypass.
4. **Voice line**: build `voice_line_text` from `message_template` with `{trigger}` substitution. `spoken:false`.
5. **Compose preview**: display lines (short, glanceable), led color, voice text, `preview_only:true`.

## Authority boundary / stop conditions

- Output is inert preview data. No device, audio, or notification path is exercised.
- A real presentation layer would require a separate approved East/hardware packet and is out of scope here.

## References

`AIOS_PI_ROBOT_HELPER_ALERT_WORKFLOW.md` · `aios_alert_event.schema.json` · `aios_voice_audio_rule.schema.json`.
