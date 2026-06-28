# AIOS Forex Remaining Closure Longrun Campaign V1

## Purpose
Provide deterministic local infrastructure for closing remaining Forex evidence work without broker/API or trading.

## Scope
- Build a local missing-evidence inventory.
- Generate owner-facing evidence collection pack.
- Validate evidence quality without execution or network access.
- Select review-ready candidates from local summaries.
- Project final bundle readiness and blocker classes.

## local-only boundary
- Local repository content only.
- No broker credentials.
- No API calls.
- No protected trading actions.

## evidence gap closure architecture
1. Build catalog from local reports and known families.
2. Convert missing evidence into owner-requestable packet.
3. Validate collected evidence files.
4. Score candidates and choose route.
5. Project final closure state.

## module map
- `automation/forex_engine/forex_missing_evidence_catalog_v1.py`
- `automation/forex_engine/forex_owner_evidence_pack_builder_v1.py`
- `automation/forex_engine/forex_evidence_quality_validator_v1.py`
- `automation/forex_engine/forex_review_ready_candidate_selector_v1.py`
- `automation/forex_engine/forex_final_bundle_readiness_projector_v1.py`

## owner evidence pack flow
- Catalog classes missing items.
- Owner pack enumerates missing families and expected outputs.
- Redaction rules prevent sensitive content.

## evidence quality validation flow
- Scan required sections.
- Detect sensitive assignment patterns.
- Detect suspicious broker/API command text.
- Emit PASS/REPAIR/REJECT statuses.

## candidate selector flow
- Score candidates deterministically.
- Explain each route.
- Never approve execution.

## final bundle projection flow
- Merge catalog + validator + selector.
- Output final readiness route and action lists.

## broker/API/credential/trading boundaries
- Do not read credentials.
- Do not run broker API clients.
- Do not place demo or live trades.
- Do not move funds.
- Do not activate production.

## safety statement
- This artifact does not authorize broker/API access.
- This artifact does not authorize credential access.
- This artifact does not authorize demo/live trading.
- This artifact does not authorize money movement.
- This artifact does not authorize production activation.
- This artifact does not authorize commit/push/merge without explicit Human Owner approval.

## owner handoff policy
- Owner packets are sanitized and redaction-aware.
- Human Owner decides evidence readiness and final promotion.
- Any protected action remains outside this lane.
