# AI_OS Dashboard and Interface Concepts

Status: canonical concept summary extracted from legacy `docs/AI_OS/dashboard`

## Purpose

This document captures useful dashboard/interface ideas from legacy `docs/AI_OS/dashboard`. It is a concept summary, not an implementation spec.

## Current Doctrine

The dashboard should help the operator understand current AI_OS state and next safe action.

It must not:

- trigger live trading,
- connect brokers,
- collect secrets,
- execute real webhooks,
- imply actions are approved when they are not,
- make fixture data look like trusted runtime truth.

## Dashboard Ideas Extracted

Useful ideas from the dashboard draft swarm:

- command center landing panel,
- validator-first status,
- next safe action card,
- protected-file warning placement,
- work packet and approval visibility,
- report and telemetry grouping,
- safety status card,
- assistant/help panel,
- work table / task view,
- compact operator cockpit,
- mobile-responsive status behavior,
- fixture-first data contracts.

## Terminal Dashboard Readability Direction

Terminal/operator displays should stay:

- concise,
- mode-first,
- clear about DRY_RUN vs APPLY,
- explicit about source paths,
- explicit about missing or stale data,
- clear about next safe action.

## Operator Panels

Potential panels:

- system status,
- clean-state status,
- packet queue,
- approval inbox,
- validator chain,
- commit package recommendation,
- worker status,
- safety and blocked actions,
- Trading Lab paper-only readiness,
- dashboard data freshness.

## Concept vs Implemented

Implemented or partially grounded:

- `apps/dashboard` exists as an active app surface.
- static/mock dashboard planning exists.
- orchestration display scripts exist for some terminal views.

Concept only:

- full operator cockpit,
- dynamic dashboard adapter layer,
- voice/tour guide,
- floating/docking panels,
- production telemetry dashboard,
- execution monitor.

## Human-Review Items

- Decide whether dashboard docs should become implementation specs or product concepts.
- Confirm which dashboard data sources are allowed.
- Ensure any Trading Lab panel says paper-only.
- Confirm app docs in `apps/dashboard` remain separate from legacy planning docs.
