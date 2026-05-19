# AI_OS Dashboard Editable Layout Rules Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.17 - Dashboard Config + Data Adapter Foundation

## Purpose

Define rules for making the existing dashboard easier to edit without creating a separate redesign folder or hardcoding every future label and layout decision.

## Editable Through Config

- Section order
- Card order
- Card visibility
- Button labels
- Button enabled or blocked state
- Card labels, titles, and descriptions
- Data-source mapping
- Visual depth tier
- Card elevation level
- Motion intensity

## Not Editable Through Config

- Secrets
- Broker connections
- Live trading behavior
- Direct browser database connections
- Deployment behavior
- Destructive file operations
- Arbitrary JavaScript execution

## Visual Depth Rules

- `2D_STATIC` is the default tier.
- Parallax must default to disabled.
- Reduced-motion fallback must disable nonessential movement.
- Mobile layouts must use conservative visual depth.
- Performance-heavy animation is blocked by default.
- Future immersive UI work needs separate DRY_RUN and APPLY approval.

## Existing Structure Rule

Future implementation should reuse the existing dashboard structure and CSS conventions unless a separate approved dashboard refactor explicitly changes them.

