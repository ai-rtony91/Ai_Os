# AI_OS Dashboard Command-Center Control Plane Draft

Status: Draft
Mode: Static command-center readiness model
Date: 2026-05-08

## Purpose

Define the dashboard command-center control plane and connect the current organization, operator actions, mock action safety, validation coverage, and theme-selector handoff into one readiness model.

## Current Control-Plane Inputs

Control-panel organization:

`docs/AI_OS/dashboard/AIOS_DASHBOARD_CONTROL_PANEL_ORGANIZATION_DRAFT.md`

Operator action map:

`docs/AI_OS/dashboard/AIOS_DASHBOARD_OPERATOR_ACTION_MAP_DRAFT.md`

Mock action safety registry:

`docs/AI_OS/dashboard/AIOS_DASHBOARD_MOCK_ACTION_SAFETY_REGISTRY_DRAFT.md`

Validation index:

`docs/AI_OS/dashboard/AIOS_DASHBOARD_VALIDATION_INDEX_DRAFT.md`

Theme selector handoff:

`docs/AI_OS/dashboard/AIOS_DASHBOARD_THEME_SELECTOR_HANDOFF_PACKET.md`

## Command-Center Readiness Model

The static dashboard is becoming a command-center control plane through staged readiness gates.

The current goal is not live automation. The current goal is a trustworthy local control surface that shows operator context, mock actions, safety boundaries, validation state, and future action categories.

## Maturity Levels

### Level 1: Static Preview

The dashboard renders local HTML, CSS, and JavaScript only.

Capabilities:

- Static navigation.
- Static cards.
- Local visual state.
- Mock assistant/console output.

### Level 2: Fixture-Backed Visibility

The dashboard reads local mock fixtures.

Capabilities:

- Status panels.
- Tool registry readiness.
- Work Table AI fixture insights.
- Safe/blocked fixture action display.

### Level 3: Mock Action Registry

The dashboard has documented action categories and safety rules.

Capabilities:

- Safe mock action definitions.
- Blocked action definitions.
- Approval-required future action definitions.
- Operator action map.

### Level 4: Approval-Gated Local Automation

Future state only.

Requirements:

- Separate DRY_RUN.
- Explicit approval.
- Validator coverage.
- Checkpoint report.
- Exact file scope.
- Stop condition.

### Level 5: Future Service Integration

Future state only.

Requirements:

- Separate governance.
- Auth boundary design.
- Secret handling policy.
- API boundary policy.
- Deployment policy.
- Observability plan.
- Human approval gates.

## Current Maturity

Current maturity:

`Level 2.5 — Fixture-backed static control surface with documented mock action categories`

The dashboard has moved beyond static preview because it now includes fixture-backed visibility, theme controls, Work Table AI display, tool registry display, and validation/reporting documentation.

It has not reached local automation because no dashboard control executes validators, writes reports, modifies files, calls APIs, or invokes live AI.

## Control-Plane Readiness Requirements

Before any command-center action becomes executable:

- It must appear in the operator action map.
- It must be classified in the mock action safety registry.
- It must have a validator.
- It must have a checkpoint report.
- It must be explicitly approved.
- It must preserve no-secrets/no-trading/no-deployment boundaries.

## Blocked Until Separately Approved

Blocked:

- API integration.
- Account integration.
- Secret storage.
- Deployment.
- Broker/trading execution.
- Live AI execution.
- React dashboard parity work.
- Background services.

## Next Safe Expansion

The next safe expansion is a final readiness report and push-readiness checkpoint for the command-center documentation/validator block.
