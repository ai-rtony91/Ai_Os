# AI_OS App Telemetry Schema Draft

## Purpose

This draft defines future app telemetry concepts for AI_OS dashboard and local application health. It is documentation only and does not create runtime telemetry, API calls, storage, service-worker behavior, collectors, or writers.

## Scope

App telemetry may describe local app health, dashboard render state, validator visibility, and user-control surface readiness.

Allowed future examples:

- `event_id`
- `timestamp`
- `app_name`
- `app_version`
- `build_mode`
- `route_or_view`
- `panel_id`
- `panel_status`
- `render_status`
- `fixture_data_loaded`
- `validator_state`
- `warning_count`
- `blocked_count`
- `latency_ms`
- `accessibility_check_status`
- `offline_capability_status`
- `service_worker_status`

## Blocked Data

App telemetry must not include:

- secrets
- credentials
- tokens
- API keys
- broker tokens
- private keys
- recovery keys
- browser profile data
- private file contents
- uncontrolled screenshot data
- broker account identifiers
- live market data
- live order path data
- trade execution decisions

## Service Worker Boundary

`service_worker_status` may be a future read-only planning field. This draft does not approve service-worker registration, caching, fetch handlers, push notifications, background sync, offline persistence, or app-store publishing.

## Storage Boundary

Future app telemetry storage path, format, retention, redaction rules, and rollback plan are UNKNOWN until separately approved.

## Non-Approval Statement

This draft does not approve telemetry writing, app telemetry collection, persistence, browser storage, network analytics, API calls, broker integration, credential access, report writers, or dashboard production activation.
