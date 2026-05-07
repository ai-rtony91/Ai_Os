# AI_OS User Telemetry Schema Draft

## Purpose

This draft defines future user telemetry concepts for AI_OS. It is documentation only and does not create a telemetry writer, collector, persistence layer, API call, service-worker registration, localStorage usage, or background process.

## Scope

User telemetry may describe operator interaction patterns needed to improve safety, usability, onboarding, and workflow clarity.

Allowed future examples:

- `event_id`
- `timestamp`
- `session_id`
- `operator_mode`
- `screen_or_panel_name`
- `action_type`
- `approval_prompt_shown`
- `approval_decision_label`
- `help_panel_opened`
- `navigation_target`
- `error_state_visible`
- `manual_note_present`

## Blocked Data

User telemetry must not include:

- passwords
- tokens
- API keys
- broker tokens
- private keys
- recovery keys
- browser profile data
- credential store paths
- private user material
- uncontrolled screen contents
- broker account identifiers
- live market execution data
- order details
- live order path data
- trade execution decisions

## Privacy Boundary

Future user telemetry must be opt-in or explicitly approved before persistence. Any field that could identify a private person, account, credential, or sensitive workflow must fail closed until reviewed.

## Retention Boundary

Retention duration, storage path, export format, deletion process, and review process are UNKNOWN until a later approved compliance batch.

## Non-Approval Statement

This draft does not approve telemetry collection, telemetry writing, local persistence, remote analytics, app-store analytics, browser storage, service-worker registration, broker integration, credential access, or live trading.
