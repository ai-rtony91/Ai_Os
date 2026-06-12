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
- premium Unreal Engine 5 planetary command-map client,
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

## Visual Identity Direction

Anthony's preferred AI_OS visual identity should be preserved before any dashboard legacy docs are archived.

Canonical visual identity reference: `docs/concepts/aios-visual-identity.md`

Preserved direction:

- deep space / midnight dark background,
- neon blue and violet glow accents,
- orbital energy, electric signal, tower, connectivity, telemetry, and network motifs,
- futuristic control-center / operator cockpit feel,
- global/system-scale imagery where it reinforces AI_OS as a control environment,
- premium but readable dark UI,
- clean card-based dashboard layout,
- strong visual hierarchy,
- high-contrast status and safety indicators,
- blue/purple worker, status, validator, and telemetry accents,
- tagline tone similar to `Intelligent. Adaptive. Yours.`

Implementation guardrails:

- preserve readability over visual effects,
- use glow, glass, and restrained parallax only when they clarify depth or status,
- avoid excessive motion or visual noise,
- keep critical FAIL, BLOCKED, WARN, REVIEW REQUIRED, and next-action states visible without hunting,
- keep dashboard visuals separate from live broker/trading activation,
- do not archive or down-rank branding, theme, layout, mockup, or visual-direction docs unless the design intent is preserved here or in a future canonical visual identity doc.

## Dual-Client Architecture Direction

AI_OS should evaluate Unreal Engine 5 as a premium 3D/4D planetary command-map client, not as an immediate replacement for the web dashboard.

Recommended client split:

1. Web dashboard: fast, accessible, browser-first, Cloudflare Access protected, and usable by end users and admins. The future web target is Next.js plus React Three Fiber for browser-native 3D where useful. The current `apps/dashboard` implementation remains the active dashboard surface until a separate redesign or migration is approved.
2. UE5 client: premium command center, immersive desktop app, kiosk operator mode, and possible future launcher. It should be evaluated as a high-fidelity command-map experience for operator situational awareness, not as default runtime authority.

UE5 visual and interaction requirements:

- cinematic Mars, Moon, Earth, Galaxy, and Black Hole navigation metaphors,
- high-fidelity lighting and material direction inspired by Nanite/Lumen-class Unreal workflows,
- planetary, orbital, galactic, and timeline overlays that preserve operator readability,
- controller-first navigation with gamepad-native movement, focus, select, back/cancel, zoom, orbit, pan, and snap-to-status controls,
- keyboard, mouse, and Xbox controller as first-class input models,
- desktop operator mode and kiosk/command-center mode,
- high-contrast safety, approval, blocked, stale, and `UNKNOWN` states visible over 3D scenery,
- reduced-motion and non-3D fallback through the web dashboard.

UE5 phase boundary:

- UE5 is a future evaluation lane.
- UE5 must not be assumed to replace the web dashboard immediately.
- A future APPLY packet must decide whether UE5 belongs in Phase 2 or Phase 3 after the web dashboard redesign.
- No UE5 project, launcher, packaging workflow, asset pipeline, or runtime integration is approved by this concept note alone.

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

UE5 state access boundary:

- UE5 must read AI_OS state through approved backend APIs only.
- UE5 must not read repo files, telemetry ledgers, approval inboxes, worker queues, scheduler state, local environment files, or generated runtime files directly from disk.
- UE5 must not store secrets, broker keys, Azure tokens, Cloudflare tokens, repo credentials, Git credentials, API keys, private keys, recovery keys, or persistent privileged sessions.
- UE5 must treat runtime, scheduler, queue, broker, and live-trading controls as display-only or approval-request previews unless a separate approved workflow and approval gate authorizes a specific action.
- Live broker execution and live trading remain blocked.

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
- Decide whether the web dashboard redesign targets Next.js plus React Three Fiber while the current Vite/React dashboard remains the active bridge.
- Decide whether UE5 evaluation belongs in Phase 2 or Phase 3 after the web dashboard redesign.
- Decide the exact approved backend API contract before any UE5 client reads AI_OS state.
- Review legacy dashboard docs for archive after this extraction.
