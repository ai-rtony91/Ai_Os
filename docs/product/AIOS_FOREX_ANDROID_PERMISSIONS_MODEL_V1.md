# AIOS Forex Android Permissions Model V1

## Status

Internal product policy. This document is not a manifest, not a store submission, not legal advice, and not release approval.

AIOS Forex is not Play Store ready until final release review. AIOS Forex is not legally or commercially approved until owner legal/compliance review.

## Purpose

This model defines the intended Android permission posture before AIOS Forex mobile packaging. Permission decisions must be feature-led, minimal, disclosed, and owner-reviewed.

## Intended Android Permission Inventory

Initial expected permission classes:

- Network access for approved app communication, policy updates, evidence sync, or broker-readiness status only when a future implementation approves the exact endpoint and disclosure.
- Notifications only for owner-visible alerts after owner approval and platform permission handling.
- Foreground execution only when needed for an owner-visible active workflow.

This model does not authorize implementation. Unknown permissions are release blockers.

## Permissions Explicitly Not Needed

The following permission categories are blocked by default:

- location.
- contacts.
- SMS.
- call logs.
- microphone.
- camera.
- broad storage.
- calendar.
- nearby devices.
- Bluetooth.
- background activity that is not owner-visible and feature-required.

## Location Default

Location is blocked by default. It may not be added unless owner/legal review later approves the exact feature, disclosure, data handling, and release rationale.

## Contacts Boundary

Contacts are blocked. AIOS Forex does not need contact access for governed Forex policy, evidence, consent, or Vacation Mode control.

## SMS And Call Logs Boundary

SMS and call logs are blocked. AIOS Forex must not request or imply a need for these permissions.

## Microphone And Camera Boundary

Microphone and camera are blocked unless a future owner-approved feature proves necessity, disclosure, and data handling. Screenshots, video evidence, and support capture must not quietly enable these permissions.

## Storage Minimization

Storage access must be minimized. Prefer app-private storage for local settings and sanitized evidence. Broad file access is blocked unless a later owner review approves the exact use.

## Notification Permission Model

Notifications may be used only for owner-facing alerts that do not expose private financial data, credentials, account identifiers, broker receipts, raw broker payloads, or live execution payloads.

Notification copy must avoid public lock-screen leakage. Notifications must not become approval, trade authority, or repeat-attempt authority.

## Network Permission Model

Network use must be disclosed and feature-bound. Network access must not enable hidden broker calls, hidden analytics, uncontrolled background data collection, or live action without owner authority.

## Background Execution Restrictions

Background execution is blocked unless later owner review approves:

- exact user benefit.
- foreground disclosure.
- stop/shutdown behavior.
- data-safety handling.
- no hidden broker/live action.
- no hidden notification sending.
- no hidden scheduler, daemon, or webhook path.

## Foreground Owner-Control Requirement

Trade-relevant actions must remain owner-visible. Any control-plane action that changes authority state must be foregrounded, auditable, and stoppable.

## Permission-To-Feature Mapping

| Permission class | Intended feature | Status |
| --- | --- | --- |
| Network | Approved app communication or sanitized evidence path | BLOCKED_UNTIL_SOURCE_PR |
| Notifications | Owner-visible alerts | BLOCKED_UNTIL_OWNER_REVIEW |
| Foreground service | Owner-visible active workflow | BLOCKED_UNTIL_SOURCE_PR |
| Location | None | BLOCKED |
| Contacts | None | BLOCKED |
| SMS / call logs | None | BLOCKED |
| Microphone / camera | None | BLOCKED |
| Broad storage | None | BLOCKED |

## Release Blocker

If permissions are unknown, unmapped, overbroad, or undisclosed, AIOS Forex is blocked from mobile release review.
