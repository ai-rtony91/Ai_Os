# AI_OS Dashboard Blocked Data Sources Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.14 - Dashboard Status Implementation Readiness

## Purpose

Define data sources the dashboard must not read for status display.

## Blocked Sources

- Secrets, credentials, API keys, broker tokens, private keys, and recovery keys.
- Live broker APIs or broker account endpoints.
- Trading execution engines or order-routing interfaces.
- Windows registry, firewall, VPN, browser policy, BIOS, UEFI, or security settings.
- Unapproved external network sources.
- Personal operator infrastructure, worktree, dual Codex, POI, or Phase 13 files.
- Unreviewed temporary files outside approved report, checkpoint, health, progress, and dashboard planning paths.

## Rule

If a desired dashboard field requires a blocked source, the field must display UNKNOWN and the limitation must be documented.

