# AI_OS Dashboard Navigation Information Architecture Draft

## Purpose

Define the Phase 13 dashboard navigation model for one interactive AI_OS command-center shell.

## Main Navigation

1. Command Center
2. Current Project / About
3. Progress
4. Reports + Telemetry
5. Validators
6. Safety
7. AI Assistance
8. Work Table AI
9. Apps / Admin

## Navigation Rules

- Only one major panel should be active at a time.
- Top navigation and drawer navigation should point into the same panel model.
- Buttons should reveal related panels, widgets, or detail popups inside the same dashboard shell.
- No separate dashboard pages or folders are required.
- Reports and Telemetry share one top-level group but remain separately labeled inside that group.

## Safety Boundary

Navigation is UI-only. It must not connect APIs, databases, brokers, live AI services, or deployment systems.
