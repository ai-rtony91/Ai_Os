# AI_OS Dashboard Panel Behavior Draft

## Purpose

This draft defines future panel behavior for AI_OS dashboard planning. It is documentation only.

## Panel Types

Future dashboard panels may include:

- system status
- protected-file status
- validator status
- telemetry preview
- report readiness
- mobile readiness
- app registry
- trading readiness
- broker/OANDA boundary status
- next safe action

## Behavior Rules

Panels should:

- display validated state before summary claims
- separate INFO, READY, REVIEW, WARN, BLOCKED, and FAIL states
- keep critical BLOCKED or FAIL states visible
- avoid hidden execution controls
- use fixture or approved read-only data only
- show UNKNOWN when data is unavailable

## Docking Rules

Future docking behavior may support fixed, docked, and focused-review panels. Docking must not hide critical warnings, protected-file status, or broker/trading blocked status.

## Mobile Behavior

On mobile, panels should:

- stack in priority order
- keep critical safety state near the top
- avoid overlapping the sidebar drawer
- fit text without truncating safety labels
- preserve clear next-safe-action wording

## Blocked Controls

Panel controls must not:

- execute scripts
- call APIs
- create files
- edit protected files
- write telemetry
- place broker orders
- access credentials
- activate strategies
- enable live trading

## Non-Approval Statement

This draft does not approve code changes, live dashboard controls, telemetry writers, persistence, API calls, broker code, credentials, or trading execution.
