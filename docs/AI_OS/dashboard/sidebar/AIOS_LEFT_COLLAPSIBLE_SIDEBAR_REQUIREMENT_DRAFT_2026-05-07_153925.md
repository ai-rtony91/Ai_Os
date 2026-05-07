# AI_OS Left Collapsible Sidebar Requirement Draft

## Purpose

The left collapsible sidebar is the future primary navigation surface for AI_OS dashboard work. It should organize operator views without becoming an execution surface.

## Desktop Behavior

On desktop, the sidebar should support an expanded state with readable labels and a collapsed state with compact icons/tooltips. Critical BLOCKED, FAIL, and next-safe-action states must remain visible somewhere in the cockpit when the sidebar is collapsed.

## Mobile Behavior

On mobile, the sidebar should behave as a drawer. The drawer must not cover critical alerts without a clear close action, and the operator should be able to dismiss it with a visible button and keyboard Escape behavior in any future implementation.

## Collapsed State

Collapsed state should preserve:

- active section indicator
- icon or compact label
- blocked broker/OANDA status visibility
- accessible tooltip or label concept
- no hidden automation action

## Expanded State

Expanded state should show:

- section labels
- grouped panels
- disabled future-only broker/OANDA entries
- admin/safety entries
- clear read-only state labels

## Button / Toggle Requirement

A future toggle should expose expanded/collapsed state to assistive technology and should not trigger scripts, file writes, API calls, telemetry persistence, broker execution, or hidden automation.

## Accessibility Notes

Future implementation should plan for focus order, `aria-expanded`, visible focus rings, keyboard control, screen-reader labels, and non-color-only state text.

## Human-Control Boundary

The sidebar is a human-control navigation aid only. It must not include live execution controls, broker execution buttons, hidden automation actions, telemetry persistence approval, API triggers, or credential access.

## Existing Static Preview Relationship

Existing static preview sidebar behavior can be treated as reference evidence for layout and interaction concepts only. It does not approve production UI, persistence, service-worker registration, API calls, or execution controls.

## Future React Dashboard Parity

Future React parity work should document matching sections, states, accessibility behavior, and blocked controls before code changes are approved.
