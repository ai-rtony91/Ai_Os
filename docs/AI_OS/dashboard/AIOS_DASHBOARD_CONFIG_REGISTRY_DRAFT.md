# AI_OS Dashboard Config Registry Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.17 - Dashboard Config + Data Adapter Foundation

## Purpose

Define the planning boundary for moving dashboard labels, cards, button definitions, layout order, data-source mappings, and future visual-depth settings into local configuration.

## Registry Targets

- `apps/dashboard/mock-data/dashboard-ui-registry.example.json`
- `apps/dashboard/mock-data/dashboard-data-sources.example.json`
- `apps/dashboard/mock-data/dashboard-layout-registry.example.json`

## Configurable Fields

- Button labels and actions
- Card labels, titles, descriptions, and order
- Enabled, disabled, blocked, and visible states
- Assistant and console message text
- Local fixture source mapping
- Layout section order
- Visual depth tier
- Parallax enabled or disabled
- Motion intensity
- Card elevation level
- Background layer behavior

## Visual Depth Planning

Visual depth tiers are future UI experience layers, not active effects by default:

- `2D_STATIC`: default local dashboard behavior
- `PARALLAX_LIGHT`: future low-motion parallax
- `3D_DEPTH`: future depth styling only after approval
- `4D_CONTEXTUAL_MOTION`: future contextual motion planning only
- `5D_IMMERSIVE_EXPERIENCE`: future immersive boundary only

The default must remain low-motion and mobile-safe. Heavy animation is blocked unless a future performance and accessibility review approves it.

## Safety Rules

- Config must not contain secrets.
- Config must not execute code.
- Config must not connect brokers.
- Config must not connect directly to a database from the browser.
- Config must not create live trading, deployment, or external API paths.

