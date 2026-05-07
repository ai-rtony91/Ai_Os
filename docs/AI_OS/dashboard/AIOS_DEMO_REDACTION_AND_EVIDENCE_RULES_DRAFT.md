# AI_OS Demo Redaction And Evidence Rules Draft

## Purpose

This draft defines safe evidence capture and redaction rules for future AI_OS dashboard demos.

Dashboard production outputs require separate approval.

## Evidence Scope

Future evidence may include approved mock/fixture state only, static prototype review notes, and validator outputs. Evidence must clearly indicate whether content is fixture-only, read-only, and not production dashboard output.

## Redaction Rules

Future demo evidence should redact username/path if needed and must exclude:

- credentials
- tokens
- live trading data
- account identifiers
- private keys
- recovery keys
- broker execution view
- uncontrolled screen contents

## Approved Mock/Fixture State Only

Demo evidence must use approved mock/fixture state only. It must not use broker systems, trading execution views, startup automation, report writers, telemetry writers, or hidden background services.

## Evidence Notes

Evidence notes should state what was shown, which fixture was used, which validator passed, what was redacted, and whether any warning remained.

## Future Stage 47

Future Stage 47 may define a demo evidence checklist fixture. No screenshot, video, or dashboard output is created here.
