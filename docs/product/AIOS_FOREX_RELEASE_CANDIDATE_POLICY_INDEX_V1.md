# AIOS Forex Release Candidate Policy Index V1

## Status

Internal product policy index. This document is not legal advice, not store-submission approval, not release approval, and not live-trading authority.

AIOS Forex is not Play Store ready until final release review. AIOS Forex is not legally or commercially approved until owner legal/compliance review.

## Purpose

This index ties the Play Store-grade policy documentation layer together before Vacation Mode control-plane implementation proceeds.

## Policy Document Index

| Document | Role | Status |
| --- | --- | --- |
| `AIOS_FOREX_PLAY_STORE_GRADE_PRODUCT_POLICY_V1.md` | Product identity, scope, blockers, and release target policy | CREATED_FOR_REVIEW |
| `AIOS_FOREX_FINANCIAL_RISK_DISCLOSURE_POLICY_V1.md` | Financial-risk disclosure and evidence claim boundaries | CREATED_FOR_REVIEW |
| `AIOS_FOREX_PRIVACY_DATA_SAFETY_MODEL_V1.md` | Data classes, redaction, minimization, and review placeholders | CREATED_FOR_REVIEW |
| `AIOS_FOREX_ANDROID_PERMISSIONS_MODEL_V1.md` | Android permission posture and feature mapping | CREATED_FOR_REVIEW |
| `AIOS_FOREX_STORE_LISTING_CLAIMS_POLICY_V1.md` | Store listing claim boundaries and review gates | CREATED_FOR_REVIEW |
| `AIOS_FOREX_OWNER_CONSENT_AND_TRADE_AUTHORITY_POLICY_V1.md` | Owner consent, trade authority, and Vacation Mode boundary | CREATED_FOR_REVIEW |
| `AIOS_FOREX_LEGAL_COMPLIANCE_OWNER_REVIEW_GATE_V1.md` | Owner/legal review gates before release or sale | CREATED_FOR_REVIEW |

## Current Readiness Status

Policy layer readiness: CREATED_FOR_REVIEW.

This status means the required documentation layer exists for owner and legal/compliance review. It does not mean AIOS Forex is Play Store ready, legally/commercially approved, sale-cleared, production released, or live-trading authorized.

## Open Blockers

- Final release review.
- Owner legal/compliance review.
- Financial-services review.
- Jurisdiction review.
- Broker terms review.
- Privacy/data-safety review.
- Android permission implementation review.
- Store listing copy review.
- User agreement.
- Privacy policy.
- Support/escalation and shutdown process.
- Vacation Mode control-plane source implementation.
- Evidence and audit validation.

## Relation To Vacation Mode

Vacation Mode must use this policy layer as a boundary. Vacation Mode may later coordinate owner-visible readiness, alert review, metadata-only states, and governed stop points. It must not become hidden live authority or ownerless trading automation.

## Relation To Play Store-Grade Product Target

The target `AIOS_FOREX_PLAY_STORE_GRADE_VACATION_MODE_RELEASE_CANDIDATE_V1` remains a release-candidate target. This index supplies policy prerequisites only.

## Next Source PR Required

Recommended next PR:

`AIOS_FOREX_VACATION_MODE_CONTROL_PLANE_SKELETON_V1`

Required next source focus:

- metadata-only state model.
- owner consent state model.
- Vacation Mode authority boundary.
- stop/shutdown controls.
- evidence-after-action interface.
- no broker/API calls.
- no credential access.
- no account identifier exposure.
- no scheduler, daemon, webhook, notification sender, or background execution without separate approval.
