# AI_OS Mobile Dashboard Readiness Draft

## Purpose

This draft defines mobile dashboard readiness requirements. It is documentation only and does not create live UI, service-worker registration, persistence, storage behavior, API calls, app publishing, or dashboard code changes.

## Readiness Checklist

- narrow-screen layout reviewed
- mobile drawer behavior planned
- critical safety state visible
- next safe action visible
- readable status labels
- no horizontal scrolling for core panels
- touch target sizing planned
- accessibility labels planned
- fixture-only preview boundary documented

## Responsive Behavior

Mobile views should stack panels by safety priority, keep BLOCKED and FAIL state near the top, and avoid overlapping drawer, alert, and status regions.

## PWA Boundary

PWA readiness is a planning topic only. This draft does not approve service-worker registration, offline cache, push notifications, background sync, localStorage, sessionStorage, IndexedDB, or production publishing.

## App-Store Boundary

App-store readiness requires future legal/compliance placeholders, privacy disclosures, terms, telemetry disclosures, support contact, and trading disclaimer review. No app submission is approved.

## Safe Preview Mode

Safe preview mode should use fixture-only or approved read-only data. It must not access broker data, credentials, private user data, live market data, or live execution state.

## Mobile Authentication Future Placeholder

Authentication requirements are UNKNOWN. No login, account creation, credential storage, OAuth, passkey, or token behavior is approved.

## Telemetry Consent Future Placeholder

Telemetry consent requirements are UNKNOWN and must be handled in legal/compliance planning before any collection or storage.

## Offline / Cache Restriction

Offline and cache behavior remain blocked until explicitly approved.

## Service-Worker Non-Approval Statement

This draft does not approve service-worker registration or any service-worker behavior.

## Production Publishing Non-Approval

This draft does not approve production publishing, PWA activation, app-store submission, analytics, billing, broker code, or trading execution.
