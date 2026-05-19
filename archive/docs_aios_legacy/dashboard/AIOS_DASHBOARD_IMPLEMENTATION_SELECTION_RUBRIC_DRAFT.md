# AI_OS Dashboard Implementation Selection Rubric Draft

## Purpose

This draft defines a DRY_RUN-only rubric for choosing a future AI_OS dashboard implementation stack. It does not select a production stack and does not create dashboard production outputs.

Dashboard production outputs require separate approval.

## Candidate Stacks

Future evaluation may compare:

- React
- Electron
- Tauri
- HTML/CSS/JavaScript

These candidates remain conceptual until a separate implementation stage is approved.

## Evaluation Criteria

Each candidate should be scored against:

- startup speed
- GPU efficiency
- low latency rendering
- offline support
- memory usage
- modular widgets
- multi-monitor support
- maintainability
- deployment complexity
- debugging simplicity
- security boundaries
- local-first behavior
- future extensibility

## React Considerations

React may support modular widgets, reusable operator cockpit components, and maintainable state-driven panels. It still requires a runtime decision for desktop packaging or browser-hosted operation.

## Electron Considerations

Electron may offer mature desktop packaging, broad web compatibility, and straightforward debugging. It must be evaluated carefully for memory usage, startup speed, and GPU efficiency.

## Tauri Considerations

Tauri may support lower memory usage, smaller deployment footprint, and local-first desktop behavior. It must be evaluated for maintainability, debugging simplicity, and Windows operator support.

## HTML/CSS/JavaScript Considerations

Plain HTML/CSS/JavaScript may support a simple offline prototype with minimal deployment complexity. It must be evaluated for modular widget scaling, future extensibility, and multi-monitor workflows.

## Security Boundary Requirements

Any future implementation must remain read-only dashboard first. It must not access credentials, route broker orders, fire webhooks, write reports, persist telemetry, create startup automation, run hidden background services, or activate live trading.

## Selection Rule

The selected stack must be chosen later based on performance, maintainability, local/offline support, visual quality, security, and operator usability. Rubric review does not approve APPLY implementation.

## Future Stage 42

Future Stage 42 may define a DRY_RUN prototype package plan or static render mock boundary. Production dashboard output remains blocked until separate approval.
