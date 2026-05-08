# AI_OS Tool Registry Dashboard Status Contract Draft

## Purpose

Define the local mock-data contract for rendering Tool Registry readiness in the dashboard.

## Fixture Path

`apps/dashboard/mock-data/tool-registry-status-fixture.example.json`

## Required Fields

- `tool_id`
- `label`
- `category`
- `desired_status`
- `detected_status`
- `installed`
- `command`
- `version`
- `path_hint`
- `needs_login`
- `needs_config`
- `blocked_reason`
- `last_checked`
- `notes`

## Display Rules

- The dashboard should show the label and detected status.
- Missing tools should show MISSING, not trigger install.
- Login-required tools should show NEEDS_LOGIN and remain manual.
- Internal repo modules should show INTERNAL_MODULE.
- Blocked actions should show BLOCKED with reason text.

## Safety Boundary

The dashboard reads local fixture data only. It must not run detection commands from the browser or connect directly to external services.
