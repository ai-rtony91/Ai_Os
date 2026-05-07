# AI_OS Dashboard Theme System Draft

## Purpose

This draft defines the future dashboard theme system concepts for DRY_RUN review.

No production dashboard theme files are created in this stage.

## Primary Colors

Primary colors may use dark neutral backgrounds with high-contrast text and restrained accent colors.

Potential primary roles:

- base background
- panel background
- text primary
- text secondary
- active accent
- muted border

## Warning Colors

Warning colors should clearly distinguish PASS, WARN, FAIL, BLOCKED, and INFO states.

Warning colors must remain readable in dark mode and color-blind-aware contexts.

## Profit/Loss Colors

Profit/loss colors may be reserved for future read-only market visibility.

Profit/loss colors must not imply trade execution approval.

## Terminal/Cyber Aesthetics

Terminal/cyber aesthetics may inform typography, spacing, panel treatment, and status indicators.

The design should avoid unnecessary visual noise.

## Typography Concepts

Typography should favor legible operator scanning, compact headings, readable numeric values, and clear alert labels.

## Blur/Transparency Concepts

Blur/transparency concepts may support glassmorphism, but must preserve readability and low-GPU-impact goals.

## Animation Restraint Rules

Animation restraint rules:

- no distracting constant motion
- no animation required for comprehension
- no hidden critical state behind motion
- no performance-heavy effects for routine status panels

## Low-GPU-Impact Goals

The theme should prioritize low-GPU-impact goals, low latency, local/offline support, and predictable rendering.

## Approval Boundary

Dashboard production outputs require separate approval.
