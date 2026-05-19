# AI_OS Dashboard and Interface Concepts

Status: canonical concept summary extracted from legacy `docs/AI_OS/dashboard`

## Purpose

This document captures useful dashboard and operator-interface ideas from legacy `docs/AI_OS/dashboard`. It is a concept summary, not an implementation spec, and it does not claim that planned dashboard behavior is implemented.

## Current Doctrine

The dashboard should help MAIN CONTROL understand current AI_OS state, trust level, blocked actions, and next safe action.

It must not:

- trigger live trading,
- connect brokers,
- collect secrets,
- execute real webhooks,
- imply actions are approved when they are not,
- make fixture data look like trusted runtime truth.

## Current Implemented vs Concept-Only

Implemented or partially grounded:

- `apps/dashboard` exists as an active app surface.
- static/mock dashboard planning exists.
- local fixture concepts exist.
- orchestration display scripts exist for terminal/operator status.
- canonical summaries now exist outside the legacy `docs/AI_OS/dashboard` swarm.

Concept-only until separately approved:

- full operator cockpit,
- dashboard command-center control plane,
- dashboard-driven actions,
- dynamic adapter layer,
- AI assistant panel connected to live AI,
- floating/docking panels,
- production telemetry dashboard,
- execution monitor,
- external account, API, or broker visibility.

## UI and Operator Surface Principles

The dashboard should be a local-first operator surface, not a marketing page and not an autonomous control plane.

Principles:

- show the highest-risk state first: FAIL, BLOCKED, WARN, REVIEW REQUIRED, READY, INFO,
- keep next safe action visible,
- keep DRY_RUN/APPLY mode visible,
- show missing data as `UNKNOWN`,
- show corrupted or conflicting data as `INVALID DATA`,
- show stale data explicitly,
- keep protected-file and blocked-action warnings near the top,
- keep Trading Lab language paper-only,
- keep controls read-only until a separate approved APPLY pass creates executable behavior,
- prefer compact, repeatable panels over decorative dashboard clutter.

## Panel Taxonomy

Preserved panel ideas from the dashboard draft swarm:

Core operator panels:

- command center landing panel,
- validator-first status,
- next safe action card,
- protected-file warning placement,
- work packet and approval visibility,
- safety status card,
- clean-state status,
- source/data freshness.

Work and orchestration panels:

- packet queue,
- approval inbox,
- validator chain,
- commit package recommendation,
- worker status,
- work table / task view,
- worker activity and lane visibility.

Telemetry and reporting panels:

- report and telemetry grouping,
- lifetime telemetry fixture panel,
- progress and checkpoint status,
- validator history,
- work intelligence display.

Assistance and guidance panels:

- assistant/help panel,
- contextual warnings,
- blocked-action explanations,
- operator onboarding/tour concepts,
- beginner-readable panel help.

Interface system ideas:

- compact operator cockpit,
- command-center layout,
- left navigation rail / collapsible sidebar,
- mobile-responsive status behavior,
- theme system and alert color hierarchy,
- fixture-first data contracts,
- static preview and publishing-readiness boundary.

## Data Source Boundary

The dashboard should start with local, read-only sources and fixtures. Legacy drafts proposed report/checkpoint/health/progress sources, but PR #180 moved legacy reports into archive. Any future implementation must refresh allowed source paths before wiring dashboard adapters.

Allowed direction:

- local fixtures,
- canonical audit and roadmap summaries,
- orchestration status outputs after validation,
- explicit approved JSON contracts.

Blocked direction:

- secrets, credentials, API keys, broker tokens, private keys, or recovery keys,
- live broker APIs or account endpoints,
- trading execution engines or order-routing interfaces,
- unapproved external network sources,
- Windows registry, firewall, VPN, browser policy, BIOS, UEFI, or security settings,
- temporary files outside approved paths.

If a desired panel requires a blocked or missing source, it should display `UNKNOWN` and explain the limitation.

## Terminal Dashboard Readability Direction

Terminal/operator displays should stay:

- concise,
- mode-first,
- clear about DRY_RUN vs APPLY,
- explicit about source paths,
- explicit about missing or stale data,
- clear about next safe action.

## Static Preview Direction

The safe dashboard path remains:

1. Static preview.
2. Fixture-backed visibility.
3. Mock action registry.
4. Approval-gated local automation, future only.
5. Service integration, future only.

The current safe maturity is best treated as fixture-backed/static concept work unless a separate implementation review proves more.

## Mobile and Accessibility Direction

Preserved mobile/accessibility ideas:

- single-column status stack on narrow screens,
- safety, validator failure, blocked state, and next action above lower-priority metrics,
- no horizontal scrolling for status content,
- high-contrast status labels,
- keyboard navigation expectation,
- visible stop conditions,
- plain warning language.

## Human-Review Items

- Decide whether dashboard docs should become implementation specs or product concepts.
- Confirm which dashboard data sources are allowed.
- Ensure any Trading Lab panel says paper-only.
- Confirm app docs in `apps/dashboard` remain separate from legacy planning docs.
- Decide whether to create a compact dashboard data-contract spec before archiving `docs/AI_OS/dashboard`.
- Decide whether AI assistant and command-center action concepts remain mock-only or become future approved workflows.
- Review legacy dashboard docs for archive after this extraction.
