# AI_OS Dashboard Button Card Registry Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.17 - Dashboard Config + Data Adapter Foundation

## Purpose

Define a registry model for dashboard buttons, cards, chips, actions, and display text.

## Registry Item Fields

- id
- type
- label
- title
- description
- action
- tab
- order
- enabled
- blocked
- status
- metric
- data_source_id
- visual_depth_tier
- card_elevation_level

## Button Types

- sidebar_button
- status_chip
- registry_chip
- action_button

## Card Types

- work_card
- app_card
- status_card
- metric_card
- safety_card
- next_action_card

## Action Rules

- Actions must map to known local preview behavior.
- Unknown actions must be ignored or displayed as UNKNOWN.
- Registry actions must not execute arbitrary code.
- Registry actions must not call external APIs.
- Registry actions must not connect brokers, databases, or deployment services.

## Visual Depth Rules

Cards may carry visual-depth hints for future UI work, but the default is static:

- visual_depth_tier: `2D_STATIC`
- parallax_enabled: false
- motion_intensity: low
- card_elevation_level: 1

Higher visual depth tiers require later approval and must respect reduced-motion and mobile performance constraints.

