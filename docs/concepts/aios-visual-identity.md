# AI_OS Visual Identity

Status: canonical visual identity summary extracted from dashboard planning docs and existing dashboard assets

## Purpose

This document preserves the AI_OS dashboard/site/interface visual direction before legacy dashboard planning material is archived.

It is not an implementation spec and does not approve app source changes. It defines the visual identity that future dashboard, site, and operator-interface work should preserve unless MAIN CONTROL explicitly changes direction.

## Core Direction

AI_OS should feel like a premium local-first operator control environment.

Preserved visual identity:

- deep space / midnight background,
- neon blue and violet glow,
- orbital energy lines,
- electric signal, tower, telemetry, connectivity, and network motifs,
- global/system-scale imagery,
- futuristic control-center / cockpit feel,
- clean card-based dashboard layout,
- strong visual hierarchy,
- high-contrast dark UI,
- blue/purple worker, status, validator, and telemetry indicators,
- premium but readable interface treatment,
- tagline tone similar to `Intelligent. Adaptive. Yours.`

## Existing Visual Anchors

Matching repo assets found:

- `apps/dashboard/assets/ai_osgalaxy.theme.jpg`
- `apps/dashboard/src/assets/hero.png`
- `apps/dashboard/assets/brand/README_AIOS_LOGO_USAGE.md`
- `apps/dashboard/assets/brand/aios-favicon-placeholder.svg`
- `apps/dashboard/assets/aios-icon.svg`

`apps/dashboard/assets/ai_osgalaxy.theme.jpg` is the strongest current visual anchor. It contains the midnight/deep-space background, neon blue/violet glow, signal tower, global/system imagery, orbital energy lines, and the tagline direction.

These assets should not be deleted, moved, down-ranked, or replaced without a separate visual review.

## Source Docs Preserved

The following legacy dashboard docs contain visual, theme, layout, or branding direction that should be treated as KEEP / EXTRACT before any archive action:

- `docs/AI_OS/dashboard/AIOS_DASHBOARD_THEME_SYSTEM_DRAFT.md`
- `docs/AI_OS/dashboard/AIOS_VISUAL_DASHBOARD_RENDER_PLAN_DRAFT.md`
- `docs/AI_OS/dashboard/AIOS_STATIC_DASHBOARD_PROTOTYPE_ARCHITECTURE_DRAFT.md`
- `docs/AI_OS/dashboard/AIOS_ALERT_HIERARCHY_AND_COLOR_SYSTEM_DRAFT.md`
- `docs/AI_OS/dashboard/AIOS_DASHBOARD_PANEL_LAYOUT_DRAFT.md`
- `docs/AI_OS/dashboard/AIOS_DASHBOARD_THEME_CONTROL_GUIDE_DRAFT.md`
- `docs/AI_OS/dashboard/AIOS_DASHBOARD_THEME_SELECTOR_GUIDE_DRAFT.md`
- `docs/AI_OS/dashboard/AIOS_DASHBOARD_THEME_SELECTOR_HANDOFF_PACKET.md`
- `docs/AI_OS/dashboard/AIOS_UI_PERFORMANCE_REQUIREMENTS_DRAFT.md`
- `docs/AI_OS/dashboard/AIOS_OPERATOR_COCKPIT_LAYOUT_SYSTEM_DRAFT.md`
- `docs/AI_OS/dashboard/AIOS_STATIC_DASHBOARD_MOCK_CONTRACT_DRAFT.md`
- `docs/AI_OS/dashboard/AIOS_STATIC_RENDERED_MOCK_BOUNDARY_DRAFT.md`
- `docs/AI_OS/dashboard/AIOS_RENDERING_STACK_EVALUATION_DRAFT.md`
- `docs/AI_OS/dashboard/AIOS_FRONTEND_RUNTIME_ARCHITECTURE_DRAFT.md`
- `docs/AI_OS/dashboard/sidebar/AIOS_LEFT_COLLAPSIBLE_SIDEBAR_REQUIREMENT_DRAFT.md`
- `docs/AI_OS/dashboard/sidebar/AIOS_LEFT_COLLAPSIBLE_SIDEBAR_REQUIREMENT_DRAFT_2026-05-07_153925.md`

If these files are archived later, the archive report should state that their visual direction is preserved here.

## Interface Principles

Future UI work should preserve:

- operator readability before decoration,
- compact but readable cards,
- stable panel placement,
- clear alert hierarchy,
- visible next safe action,
- low visual noise,
- local/offline-first behavior,
- strong status contrast,
- predictable responsive layouts,
- accessibility and keyboard usability.

Future visual work may use:

- glassmorphism for panel depth,
- restrained glow for status and readiness boundaries,
- restrained parallax for non-critical depth cues,
- modular widgets,
- detachable/floating panels after review,
- multi-monitor cockpit concepts after review.

## Safety Boundaries

Visual identity work must not:

- enable live trading,
- connect brokers,
- connect OANDA,
- fire webhooks,
- collect secrets,
- write telemetry,
- create hidden automation,
- imply unapproved APPLY behavior,
- make mock data look like trusted runtime truth.

Trading Lab panels must present the current approved execution stage honestly: paper/simulation when applicable, broker-readiness or governed demo stages only when separately approved, and no live execution claims without governance.

## Archive Rule

Do not archive, delete, or down-rank dashboard/site/interface docs, specs, assets, mockups, theme guides, layout notes, or branding material that define this visual identity unless:

1. the design intent is already preserved in this document or a later approved canonical visual identity doc,
2. active app assets are left untouched,
3. archive notes clearly state that the visual identity was preserved before move,
4. MAIN CONTROL has reviewed any ambiguous visual or brand material.

## Human Review Items

- Decide whether `apps/dashboard/assets/ai_osgalaxy.theme.jpg` remains the primary brand/hero visual.
- Decide whether the tagline `Intelligent. Adaptive. Yours.` is final or a strong placeholder.
- Decide whether to promote the neon blue/violet cockpit theme into app-level brand guidelines.
- Decide whether future dashboard UI should use the galaxy/global/tower imagery directly or only use it as brand inspiration.
- Review any future archive batch for visual identity files before moving them.
