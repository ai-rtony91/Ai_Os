# AIOS Forex Privacy Data Safety Model V1

## Status

Internal product policy. This document is not legal advice, not a privacy policy, not a store data-safety filing, and not release approval.

AIOS Forex is not Play Store ready until final release review. AIOS Forex is not legally or commercially approved until owner legal/compliance review.

## Purpose

This model defines the privacy and data-safety boundaries required before AIOS Forex Vacation Mode and mobile packaging work proceed.

## Data Classes

Allowed data classes must be minimized and documented before release:

- policy metadata.
- user-facing settings.
- local feature state.
- sanitized evidence summaries.
- sanitized broker-readiness status.
- app diagnostics that exclude private financial data.
- owner consent records that avoid credential values and account identifiers.

## Forbidden Data Classes

AIOS Forex must not collect, persist, print, display, transmit, or commit:

- credential values.
- authentication materials.
- account identifiers.
- private broker receipts.
- raw broker payloads.
- live execution payloads.
- private financial data not required for an approved feature.
- device data unrelated to the approved feature set.

## Credentials Policy

Credential values must remain outside repo files, screenshots, reports, telemetry, store assets, and support messages. Runtime-only handling requires separate owner approval and must not be introduced by this policy package.

## Account Identifier Policy

Account identifiers must be redacted from evidence, UI, reports, logs, and support flows. Where an identifier is necessary for owner review, the product must show a redacted or owner-approved alias.

## Broker Receipt Redaction Policy

Broker receipts may be used only as sanitized evidence. Receipt evidence must remove credentials, account identifiers, private broker data, raw broker payloads, and any unnecessary personal or financial data.

## Raw Broker Payload Policy

Raw broker payloads must not be stored in product docs, repo files, public assets, mobile screens, analytics, or support messages. If future debugging requires payload inspection, it must use a separate owner-approved private evidence path.

## Local Evidence Policy

Local evidence should be sanitized, minimal, and traceable. Evidence files must separate:

- what was approved.
- what ran.
- what was blocked.
- what was observed.
- what remains unknown.

Evidence must not become execution authority.

## Data Minimization

AIOS Forex must collect only what the approved feature needs. If a feature can function without a data class, that data class remains blocked.

## Consent And Disclosure Requirements

Before release, AIOS Forex must disclose:

- what data is used.
- why it is used.
- whether data remains local.
- whether any third-party service receives data.
- how owner consent is recorded.
- how shutdown and deletion requests are handled.

## No Sale Of Personal Or Sensitive Data

AIOS Forex must not sell personal or sensitive data. Any later analytics, SDK, payment, broker, or cloud service review must preserve this boundary unless owner legal/compliance review explicitly changes the release model.

## Secure Handling Requirements

Secure handling requires:

- redaction by default.
- least-data collection.
- no private data in repo fixtures.
- no sensitive values in logs.
- no hidden background collection.
- owner review for any third-party data path.

## Third-Party And SDK Review Placeholder

Placeholder status: BLOCKED_PENDING_OWNER_REVIEW.

Before release, every SDK, analytics tool, crash tool, broker connector, payment tool, notification provider, cloud service, or external data processor must be reviewed for data classes, consent, retention, deletion/export, and disclosure.

## Data Retention Placeholder

Placeholder status: BLOCKED_PENDING_OWNER_REVIEW.

Retention windows must be defined before release for local evidence, app state, owner consent records, diagnostics, support records, and sanitized broker-readiness evidence.

## Deletion And Export Placeholder

Placeholder status: BLOCKED_PENDING_OWNER_REVIEW.

Deletion and export flows must be defined before release. The model must distinguish local app data, local evidence, support records, third-party records, and owner-controlled private evidence.

## Owner Review Requirements

Owner review is required before public release, sale, store submission, new data collection, third-party SDK use, broker data handling, analytics, support-data capture, or background data collection.
