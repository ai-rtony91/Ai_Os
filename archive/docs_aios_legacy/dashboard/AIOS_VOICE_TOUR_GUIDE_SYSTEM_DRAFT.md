# AI_OS Voice Tour Guide System Draft

## Purpose

This draft defines a future optional voice guide architecture for the AI_OS operator cockpit. It is DRY_RUN-only and does not enable speech, startup automation, or dashboard output.

Dashboard production outputs require separate approval.

## Optional Voice Assistant

The voice guide may later become an optional assistant that explains dashboard panels, alerts, and Morning Brief context. It must remain off unless explicitly enabled in an approved future stage.

## Non-Blocking Assistant Behavior

Voice guide behavior must be non-blocking. It should not interrupt critical operator workflows, hide warnings, or prevent dashboard review.

## Contextual Voice Prompts

Contextual voice prompts may summarize PASS/WARN/FAIL state, protected-file warnings, and next safe actions when the operator requests guidance.

## Explain This Panel Concepts

The operator may later request an explanation of a panel. The response should describe what the panel shows, its data source, validation state, and safety boundary.

## Explain This Alert Concepts

The operator may later request an alert explanation. The response should state severity, affected panel, safe interpretation, and blocked actions.

## Startup Walkthrough

A future startup walkthrough may explain system status, dashboard fixture mode, validator state, protected-file status, and blocked trading execution.

## Morning Brief Narration

Morning Brief narration may summarize approved preview content only. It must not read secrets, credentials, broker data, or live trading data.

## Future Voice Command Boundaries

Future voice command boundaries must block trading execution, broker routing, credential access, report writing, telemetry persistence, startup automation, and hidden background services.

## Voice Disabled Mode

The dashboard must support voice disabled mode. All guidance should remain available as text.

## Latency-Aware Behavior

Voice guide behavior should avoid high latency, repeated narration, and noisy prompts. It should degrade cleanly to text guidance.

## Future Stage 44

Future Stage 44 may define voice guide text fixtures. No production voice assistant is approved here.
