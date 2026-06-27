# AIOS AEE Compound Spark Longrun Campaign V1

## Purpose

Increase implementation depth of AEE governance infrastructure by combining V1 validator, V3 stopgate, owner handoff, and CI governance checks into one compound execution track.

## Scope

- campaign state classification
- validation planning
- owner handoff block synthesis
- static CI governance guardrails
- campaign metrics and work estimation
- compound campaign CLI coordination
- fixture growth
- test suite expansion
- campaign docs and final checkpoint/report artifacts

## Why Spark is finishing faster

Single-packet composition means a campaign can complete early if all checks fit into established patterns. This can hide untested breadth. This document defines a harder completion bar so future packets expand work units rather than stop at first green.

## Why more implementation tracks are required

Longrun confidence requires orthogonal tracks running together:

- state transitions
- command classification
- owner handoff safety
- static CI posture
- evidence quality and checkpoint/report integrity

## Compound campaign architecture

```text
state classifier -> validator planner -> static guard -> metrics estimator
      -> owner handoff builder -> CLI coordinator
```

The CLI reads only explicit changed artifacts and produces a single campaign report.

## Module map

- `automation/governance/aios_aee_campaign_state_classifier_v1.py`
- `automation/governance/aios_aee_validator_execution_planner_v1.py`
- `automation/governance/aios_aee_owner_handoff_builder_v1.py`
- `automation/governance/aios_aee_static_ci_guard_v1.py`
- `automation/governance/aios_aee_campaign_metrics_v1.py`
- `scripts/governance/run_aios_aee_compound_campaign_v1.py`

## CLI usage

```text
python scripts/governance/run_aios_aee_compound_campaign_v1.py --branch lane/aios-aee-governance-validator-v1 --strict --dirty-file automation/governance/aios_aee_governance_validator_v1.py --dirty-file automation/governance/aios_aee_stopgate_inventory_v3.py --dirty-file Reports/core_delivery/AIOS_AEE_STOPGATE_CARRYOVER_CONTINUATION_V3_REPORT.md

python scripts/governance/run_aios_aee_compound_campaign_v1.py --write-report --strict --branch lane/aios-aee-governance-validator-v1 --dirty-file automation/governance/aios_aee_governance_validator_v1.py --dirty-file automation/governance/aios_aee_stopgate_inventory_v3.py --dirty-file Reports/core_delivery/AIOS_AEE_STOPGATE_CARRYOVER_CONTINUATION_V3_REPORT.md

python scripts/governance/run_aios_aee_compound_campaign_v1.py --strict --branch lane/aios-aee-governance-validator-v1 --dirty-file automation/governance/aios_aee_governance_validator_v1.py --simulate-1312 --simulate-targeted-tests-passed
```

## State classifier contract

`classify_campaign_state` and helper functions must classify:

- branch state
- dirty carryover state
- staged file state
- forbidden path state
- approved continuation state
- accidental review prompt interruption
- deferred validation
- owner handoff readiness

## Validation planner contract

`build_validation_plan` must produce executable local commands for:

- safe Python compile
- targeted pytest
- strict CLI
- report write
- git diff check
- status check
- owner deferred validation

## Owner handoff builder contract

- accepts explicit file list
- rejects broad staging commands
- emits Block 1 (publish/check)
- emits Block 2 (merge/sync)
- includes required PR title/body/commit text

## Static CI guard contract

Scanner must detect:

- sensitive assignment patterns
- broad git add
- placeholder command tokens
- protected action block mixing
- forbidden path references
- accidental branch-switch in wrong block
- report/checkpoint contradiction
- safety-boundary omissions

## Campaign metrics contract

Track created/modified files, tests, fixtures, modules, validations, 1312 events and estimate work units.
`classify_campaign_depth` must expose:

- MICRO_PACKET
- SHORT_PACKET
- MEDIUM_PACKET
- LONGRUN_PACKET
- COMPOUND_LONGRUN_PACKET

## 1312 handling

- read-only command with 1312: one retry path is allowed and classification becomes `SANDBOX_LIMITATION` or `DEFERRED_OWNER_VALIDATION` if strictly blocking local exit.
- strict CLI 1312 after passing targeted tests: `DEFERRED_OWNER_VALIDATION`.
- remaining-work blocked by repeated 1312: owner powershell handoff instruction.

## Prompt interruption handling

- prompts matching explain/search/review phrases are queued as `PROMPT_INTERRUPTION_REVIEW_QUEUE`
- explicit stop phrases are hard stop.

## Dirty carryover continuation handling

- approved lane continuation with approved carryover artifacts is treated as continuation statuses and not hard stop.
- main branch for this campaign remains forbidden: `WRONG_PACKET_FOR_CLEAN_MAIN`.

## Owner handoff policy

- no protected commands by Codex
- explicit file lists only
- handoff split into two blocks
- Block 1 includes `gh pr checks --watch`, Block 2 includes merge/sync only

## Safety statement

This artifact does not authorize broker/API access.  
This artifact does not authorize credential access.  
This artifact does not authorize trading execution.  
This artifact does not authorize money movement.  
This artifact does not authorize commit/push/merge without explicit Human Owner approval.
