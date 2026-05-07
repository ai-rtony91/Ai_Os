# AI_OS Panel Docking And Floating Rules Draft

## Purpose

This draft defines future panel docking and floating behavior for AI_OS dashboard prototype planning.

Dashboard production outputs require separate approval.

## Fixed Panels

Fixed panels should hold critical always-visible regions such as system status, protected-file status, alert summary, and next safe action.

## Docked Panels

Docked panels may hold analytics, validator status, Morning Brief, repo health, cloud status, and trading readiness views.

## Floating Overlays

Floating overlays may support focused review, temporary alert detail, or comparison views. They must not hide critical FAIL or BLOCKED states.

## Pinned Widgets

Pinned widgets should preserve operator-selected priority while respecting validator-first and alert-priority-first display rules.

## Persistent Layouts

Persistent layouts may be considered later only after storage boundaries are approved. This stage does not create layout files or write settings.

## Layout Recovery Concepts

Future layout recovery should return the cockpit to a safe default with protected-file warnings and critical alerts visible.

## Focus-State Preservation

Focus-state preservation should avoid losing operator context during async rendering, panel refresh, or detached panel movement.

## Low-Latency Movement Goals

Panel docking, undocking, and movement should feel low latency while remaining GPU-aware and avoiding uncontrolled background services.

## Detached Panels

Detached panels must remain read-only dashboard surfaces. They may display fixture-driven state only until separate approval.

## Future Stage 43

Future Stage 43 may define static layout states for review. No production dashboard output is approved here.
