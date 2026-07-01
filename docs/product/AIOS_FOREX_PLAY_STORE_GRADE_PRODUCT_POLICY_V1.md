# AIOS Forex Play Store-Grade Product Policy V1

## Status

Internal product policy. This document is not legal advice, not store-submission approval, not a public marketing claim, and not live-trading authority.

AIOS Forex is not Play Store ready until final release review is completed. AIOS Forex is not legally or commercially approved until owner legal/compliance review is completed. This policy defines product boundaries required before Vacation Mode control-plane implementation proceeds.

## Product Identity

AIOS Forex is the Trading Lab / Forex product vertical inside AIOS. AIOS is a governed, human-controlled, broker-capable trading system and execution platform framework. Forex features are stages inside that platform, including backtesting, paper simulation, supervised demo review, broker-readiness evidence, owner approval workflows, dashboard truth, risk controls, and governed broker execution paths.

## Product Scope

This policy covers how AIOS Forex must present itself before mobile packaging, public release, commercial sale, or store submission. It applies to product copy, app behavior, evidence displays, owner consent, privacy/data-safety disclosures, Android permissions, support paths, shutdown paths, and release-candidate review.

This policy is documentation only. It does not edit strategy code, Forex execution code, broker integrations, mobile app code, notifications, schedulers, daemons, webhooks, or production deployment systems.

## Release-Candidate Definition

`AIOS_FOREX_PLAY_STORE_GRADE_VACATION_MODE_RELEASE_CANDIDATE_V1` means a governed release-candidate target, not a completed release. A release candidate can be reviewed only after:

- product-policy documents are present.
- required user disclosures are drafted and owner-reviewed.
- Android permissions are known and mapped to features.
- privacy/data-safety handling is documented.
- Vacation Mode authority boundaries are implemented and validated.
- evidence and audit requirements are enforced.
- support, escalation, and shutdown paths are defined.
- owner legal/compliance review clears the release path.

## What AIOS Forex Is

- A governed Forex product vertical inside AIOS.
- A human-controlled automation and evidence framework.
- A product that may support paper simulation, supervised demo evidence, and governed broker-capable pathways when explicitly approved.
- A system that separates metadata-only readiness from live execution authority.
- A system that requires owner review before live broker action, repeated attempts, public claims, release, sale, or store submission.

## What AIOS Forex Is Not

- It is not a public release.
- It is not a legal or financial-services clearance.
- It is not an app-store approval.
- It is not a public sales package.
- It is not investment advice unless later owner/legal review explicitly authorizes an exact public statement.
- It is not ownerless trading automation.
- It is not live broker authority by default.
- It is not a credential store.
- It is not an account identifier storage system.
- It is not a raw broker payload archive.

## Forbidden Claims

The following phrases are policy examples of claims AIOS Forex must not make in product copy, screenshots, videos, onboarding, sales material, app text, notifications, reports, or public release notes unless a later owner/legal review creates an exact approved replacement statement:

- guaranteed profit
- guaranteed returns
- risk-free
- passive income guaranteed
- set and forget
- prints money
- fully autonomous live trading
- no loss possible
- legal compliant
- Play Store approved
- sell ready
- production deployed

## Play Store-Grade Standard

Play Store-grade means AIOS Forex should be able to survive store-style product scrutiny as an internal engineering target. It does not mean Play Store approval has happened.

Minimum standard:

- claims must be evidence-backed.
- financial risk must be visible before any user-facing release.
- user consent must be explicit for trade authority.
- live trading must stay behind owner-governed gates.
- credentials, account identifiers, broker receipts, raw broker payloads, and private data must be protected.
- unnecessary data collection must be avoided.
- Android permissions must be minimized and mapped to features.
- background execution must be disclosed and blocked unless separately approved.
- support, escalation, kill-switch, and shutdown paths must exist before release.

## No Live Authority By Default

AIOS Forex defaults to no live broker action. Metadata-only readiness, policy readiness, evidence readiness, paper simulation, and supervised demo review do not authorize broker execution, live routing, order placement, retry loops, or repeated trade attempts.

Any future live action must satisfy `RISK_POLICY.md` and exact owner approval. Validators, dashboards, reports, packets, and product docs are evidence only.

## Owner-Governed Automation Model

AIOS Forex automation must remain owner-governed:

- owner approval is required before any broker/live action.
- owner review is required before repeated trade attempts.
- one-action stop rules must be preserved for live-micro boundaries.
- alert acknowledgement must not become approval by implication.
- Vacation Mode must not escalate from observation into live action without explicit authority.
- kill-switch and shutdown paths must override automation.

## Financial-Risk Posture

AIOS Forex must disclose that Forex activity can lose money. It must not present outcome certainty, fixed return expectations, passive-income expectations, or advice claims without owner/legal approval.

Broker-result claims require broker receipts and sanitized evidence. Realized profit claims require reconciled PnL after spread, fees, slippage, and rejected/partial-fill handling.

## Privacy Posture

AIOS Forex must collect only the data required for approved features. It must avoid unnecessary personal data, unnecessary broker data, unnecessary device data, and unnecessary background collection.

Credential values, account identifiers, broker receipts, raw broker payloads, and private evidence must never appear in public docs, store copy, screenshots, support messages, telemetry, or repo files unless a later owner-approved redaction model explicitly permits sanitized examples.

## Security Posture

Security defaults:

- no credential persistence in repo files.
- no account identifier exposure.
- no raw broker payload exposure.
- no hidden external connector enablement.
- no background worker, scheduler, daemon, webhook, or notification sender unless separately approved.
- evidence must be sanitized and traceable.

## Release Blockers

Release is blocked until:

- this policy index is complete.
- financial-risk disclosure is owner-reviewed.
- privacy/data-safety model is owner-reviewed.
- Android permissions model is complete.
- store listing claims policy is approved for public copy.
- owner consent and trade authority policy is implemented in the control plane.
- legal/compliance owner review gate is passed.
- support/escalation and shutdown paths are defined.
- final release review confirms no unauthorized live authority.

## Sellability Blockers

Commercial sale is blocked until:

- owner legal/compliance review approves the sales path.
- financial-services review is completed.
- jurisdiction review is completed.
- broker terms review is completed.
- privacy policy and user agreement are approved.
- support/escalation and shutdown processes are operational.
- public claims are reviewed against evidence.

## Next Required Docs, Source, And Evidence

- Policy docs in this package must be reviewed as a set.
- Next source PR should implement `AIOS_FOREX_VACATION_MODE_CONTROL_PLANE_SKELETON_V1`.
- Vacation Mode must preserve metadata-only readiness until owner-governed trade authority is explicitly granted.
- Evidence and audit outputs must remain sanitized.
