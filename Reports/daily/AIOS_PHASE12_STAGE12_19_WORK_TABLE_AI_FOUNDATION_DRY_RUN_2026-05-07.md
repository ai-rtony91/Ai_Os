# AI_OS Phase 12 Stage 12.19 Work Table AI Foundation DRY_RUN

Date: 2026-05-07
Mode: DRY_RUN
Classification: AI_OS project work only
Phase: Phase 12 - Productization + System-Wide Integration
Stage: Stage 12.19 - Work Table AI Foundation
Current commit inspected: b8b784c

## Task

Create a DRY_RUN plan for adding Work Table AI as a separate intelligence layer for the dashboard work table. This stage prepares task, card, and row intelligence, scoring, status interpretation, sorting/filtering recommendations, and mock AI outputs without connecting to live AI APIs.

This DRY_RUN creates only this report and the matching checkpoint. It does not edit dashboard HTML, CSS, or JavaScript.

## Mismatch

The prompt says AI Assistance Core should already be saved before this starts. Terminal evidence shows Stage 12.18 AI Assistance files are present as untracked files. This is marked as MISMATCH and left untouched.

## Important Separation

This stage is Work Table AI only.

Work Table AI scope:

- work table row and card intelligence
- task/card status interpretation
- task scoring
- priority recommendation
- sorting/filtering recommendation logic
- mock Work Table AI outputs
- human approval before action

AI Assistance excluded scope:

- project helper behavior
- command explainer behavior
- checkpoint summarizer behavior
- operator assistant behavior
- general next-action guide behavior
- safety reminder panel behavior

AI Assistance Core is a separate system and is not mixed into this stage.

## Files Inspected

- apps/dashboard/AIOS_STATIC_PREVIEW.html
- apps/dashboard/css/aios-static-preview.css
- apps/dashboard/js/aios-static-preview.js
- apps/dashboard/mock-data/
- docs/AI_OS/dashboard/
- docs/AI_OS/llm/
- docs/AI_OS/agents/
- docs/AI_OS/progress/
- Reports/progress/
- Reports/checkpoints/
- Reports/health/

## Existing Work Table Observed

The current work table has six hardcoded cards:

- Project Brief
- Prompt Stack
- Build Instructions
- Tool Output
- Approval Gate
- Validation Queue

The JavaScript has corresponding static message entries for:

- `project-brief`
- `prompt-stack`
- `build-instructions`
- `tool-output`
- `approval-gate`
- `validation-queue`

No Work Table AI scoring, sorting, filtering, or recommendation behavior exists yet.

## Step 1 - Work Table AI Role Boundary

Plan:

- Create `docs/AI_OS/llm/AIOS_WORK_TABLE_AI_ROLE_BOUNDARY_DRAFT.md`.
- Define Work Table AI as a planning/intelligence layer for work table cards and rows.
- Block autonomous execution, APPLY, commit, push, deployment, broker access, database access, live AI API access, and live trading.
- Keep AI Assistance separate.

## Step 2 - Work Table Row / Card Intelligence Model

Plan:

- Create `docs/AI_OS/llm/AIOS_WORK_TABLE_AI_INPUT_OUTPUT_CONTRACT_DRAFT.md`.
- Define inputs:
  - work card id
  - label
  - title
  - description
  - current status
  - blockers
  - checkpoint evidence
  - progress evidence
  - validator evidence
- Define outputs:
  - interpreted status
  - confidence
  - score
  - priority tier
  - recommended next review target
  - explanation

## Step 3 - Mock Scoring / Recommendation Contract

Plan:

- Create `docs/AI_OS/llm/AIOS_WORK_TABLE_AI_SCORING_RULES_DRAFT.md`.
- Create `docs/AI_OS/llm/AIOS_WORK_TABLE_AI_RECOMMENDATION_RULES_DRAFT.md`.
- Create `apps/dashboard/mock-data/work-table-ai-fixture.example.json`.
- Create `apps/dashboard/mock-data/work-table-ai-actions.example.json`.
- Use mock scoring only.
- Do not connect OpenAI, Azure OpenAI, Claude, or any live AI API.
- Do not imply AI-generated recommendations are approved actions.

## Step 4 - Work Table AI Dashboard Panel Plan

Plan:

- Create `docs/AI_OS/dashboard/AIOS_WORK_TABLE_AI_PANEL_CONTRACT_DRAFT.md`.
- Create `docs/AI_OS/dashboard/AIOS_WORK_TABLE_AI_MOCK_DATA_DRAFT.md`.
- Plan a future panel that may show:
  - score
  - priority tier
  - recommendation text
  - reason
  - blocked action warning
  - human approval required flag
- Do not edit dashboard code during this DRY_RUN.

## Step 5 - Future AI Adapter Boundary

Plan:

- Create `docs/AI_OS/llm/AIOS_WORK_TABLE_AI_FUTURE_API_ADAPTER_BOUNDARY_DRAFT.md`.
- Future live AI adapter requires separate DRY_RUN and APPLY approval.
- Future adapter must keep API keys and secrets outside browser code.
- Future adapter must return suggestions only, never execute actions.
- Future adapter must not connect brokers, real databases, external APIs, deployments, or trading paths without separate approval.

## Separation Document

Plan:

- Create `docs/AI_OS/agents/AIOS_AI_ASSISTANCE_AND_WORK_TABLE_AI_BOUNDARY_DRAFT.md`.
- Document AI Assistance and Work Table AI as separate systems.
- Prevent Stage 12.19 from adding general operator assistant behavior.

## Files To Create On APPLY

- docs/AI_OS/llm/AIOS_WORK_TABLE_AI_ROLE_BOUNDARY_DRAFT.md
- docs/AI_OS/llm/AIOS_WORK_TABLE_AI_INPUT_OUTPUT_CONTRACT_DRAFT.md
- docs/AI_OS/llm/AIOS_WORK_TABLE_AI_SCORING_RULES_DRAFT.md
- docs/AI_OS/llm/AIOS_WORK_TABLE_AI_RECOMMENDATION_RULES_DRAFT.md
- docs/AI_OS/llm/AIOS_WORK_TABLE_AI_FUTURE_API_ADAPTER_BOUNDARY_DRAFT.md
- docs/AI_OS/dashboard/AIOS_WORK_TABLE_AI_PANEL_CONTRACT_DRAFT.md
- docs/AI_OS/dashboard/AIOS_WORK_TABLE_AI_MOCK_DATA_DRAFT.md
- apps/dashboard/mock-data/work-table-ai-fixture.example.json
- apps/dashboard/mock-data/work-table-ai-actions.example.json
- docs/AI_OS/agents/AIOS_AI_ASSISTANCE_AND_WORK_TABLE_AI_BOUNDARY_DRAFT.md

## Files Skipped Already Existed

No expected APPLY target files existed during inspection.

## Mock Data Plan

`work-table-ai-fixture.example.json` should include:

- mode: `LOCAL_MOCK_ONLY`
- work table cards
- interpreted status
- score
- priority tier
- confidence
- recommendation
- reason
- approval required flag
- source references

`work-table-ai-actions.example.json` should include mock action labels only:

- interpret_card_status
- score_work_card
- recommend_next_review
- explain_priority
- suggest_sort_filter
- flag_blocked_card

These actions must not execute.

## Future API Adapter Plan

Future API adapter is out of scope for this DRY_RUN. A later adapter must:

- require separate DRY_RUN and APPLY approval
- avoid browser-stored API keys
- avoid direct dashboard-to-provider calls unless separately approved
- avoid broker, trading, database, deployment, and destructive actions
- return scoring and recommendation suggestions only
- require human approval before any operator action

## Progress Ledger Proposal

Reports/progress exists. This DRY_RUN proposes the following row but does not append it:

```csv
date,time,stage,task_id,task_name,planned_steps,completed_steps,percent_complete,status,blocked,blocker,next_action,checkpoint_file,commit_hash,git_status,notes
2026-05-07,UNKNOWN,Phase 12 Stage 12.19,AIOS-P12-S12-19-DRYRUN,Work Table AI Foundation,5,1,20,DRY_RUN_COMPLETE_PENDING_APPLY,NO,,Approve APPLY for Phase 12 Stage 12.19 Work Table AI Foundation,Reports/checkpoints/CHECKPOINT_2026-05-07_PHASE12_STAGE12_19_WORK_TABLE_AI_FOUNDATION_DRY_RUN.md,b8b784c,main has untracked Stage 12.18 APPLY files,MISMATCH documented; no ledger append performed
```

## Protected Files Not Touched

- README.md
- AGENTS.md
- RISK_POLICY.md
- SOURCE_LOG.md
- ERROR_LOG.md
- HALLUCINATION_LOG.md
- AAR.md
- DAILY_REPORT.md
- WHITEPAPER.md
- docs/White_Paper.md

## Safety Blocks Confirmed

- No overwrite performed.
- No delete performed.
- No move performed.
- No rename performed.
- No secrets added.
- No API keys added.
- No OpenAI, Azure OpenAI, Claude, or live AI API connection made.
- No broker connection made.
- No real database connection made.
- No external APIs used.
- No live trading code created.
- No trades placed.
- No protected root governance files modified.
- No deployment performed.
- No dashboard HTML, CSS, or JavaScript edited.
- No dual Codex, POI, worktree, or Phase 13 files created.
- No AI Assistance scope mixed into this stage.

## Errors

None observed during DRY_RUN inspection.

## Unknowns

- Future Work Table AI provider is UNKNOWN and intentionally not selected in this stage.
- Future secure API adapter shape is UNKNOWN until a later DRY_RUN.
- Final dashboard implementation behavior is UNKNOWN because dashboard code was intentionally not edited.

## DRY_RUN Result

DRY_RUN_COMPLETE_PENDING_APPLY_WITH_MISMATCH_NOTED.

Only the DRY_RUN report and checkpoint were created. All Work Table AI APPLY files remain planned only.

## Next Safe Action

Approve APPLY mode for AI_OS Phase 12 Stage 12.19 Work Table AI Foundation using this DRY_RUN report.

