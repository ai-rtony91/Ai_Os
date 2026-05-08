# AI_OS Tool Registry Status Model Draft

## Purpose

Define a read-only status model for dashboard Tool Registry buttons.

## Tool Buttons

- ChatGPT
- Codex
- Claude
- GitHub
- PowerShell
- Web/Research
- Files/OneDrive
- Reports
- Telemetry

## Status Values

- READY
- INSTALLED
- MISSING
- NEEDS_LOGIN
- NEEDS_CONFIG
- BLOCKED
- INTERNAL_MODULE
- NOT_APPLICABLE
- UNKNOWN

## Status Rules

- READY means the tool can be used within the approved local boundary.
- INSTALLED means the tool appears present but readiness may still require login or config.
- MISSING means the expected executable, app path, or folder was not found.
- NEEDS_LOGIN means manual operator sign-in is required.
- NEEDS_CONFIG means local configuration is incomplete.
- BLOCKED means the action is intentionally disabled by AI_OS safety policy.
- INTERNAL_MODULE means the item is part of the repo/dashboard and not external software.
- NOT_APPLICABLE means install detection does not apply.
- UNKNOWN means evidence is insufficient.

## Safety Boundary

This model is for detection and reporting only. It must not install software, store credentials, connect accounts, or call external APIs.
