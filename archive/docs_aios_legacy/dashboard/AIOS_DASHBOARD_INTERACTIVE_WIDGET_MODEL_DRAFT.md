# AI_OS Dashboard Interactive Widget Model Draft

## Purpose

Plan how dashboard buttons, cards, and chips become interactive widgets without creating separate pages.

## Interaction Rules

- Major nav buttons switch the active panel.
- Work Table cards open contextual detail widgets or update the active panel.
- Registry chips should update a detail panel with tool/app status.
- Optional modals are allowed only for drill-down details.
- Widgets should use local mock-data first.
- Transitions should be lightweight CSS opacity/transform changes.

## Widget Types

- Summary stat cards
- Detail cards
- Expandable rows
- Local mock-data status widgets
- Read-only explanation panels
- Approval-required flags

## Blocked Interactions

- External API calls
- Database calls
- Broker connections
- Live AI API calls
- Secret capture
- Deployment actions
