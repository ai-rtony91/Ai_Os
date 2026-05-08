# AI_OS Work Table AI Recommendation Rules Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.19 - Work Table AI Foundation

## Purpose

Define recommendation boundaries for Work Table AI.

## Allowed Recommendations

- recommend next card to review
- recommend sort by blocked status
- recommend filter by validation status
- recommend review of missing evidence
- recommend checking latest checkpoint
- recommend operator approval before action

## Blocked Recommendations

- execute APPLY
- commit or push
- deploy
- connect live AI API
- connect broker
- place trade
- connect database
- read secrets
- edit protected root governance files

## Recommendation Output

Every recommendation should include:

- recommended target
- reason
- confidence
- evidence source
- approval required flag
- blocked actions

