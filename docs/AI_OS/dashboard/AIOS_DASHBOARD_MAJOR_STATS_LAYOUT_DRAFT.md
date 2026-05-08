# AI_OS Dashboard Major Stats Layout Draft

## Purpose

Define the major AI_OS stats that should be visible in the dashboard command-center view.

## Major Stats

- Current phase
- Current stage
- Phase progress %
- Stage progress %
- Latest commit
- Latest checkpoint
- Validator status
- Safety status
- Files created today
- KB / MB created today
- Next action
- AI Assistance status
- Work Table AI status

## Layout Plan

- Top summary strip: phase, stage, validator, safety, next action.
- Compact metrics grid: progress %, files/KB/MB, latest commit, latest checkpoint.
- Detail panel region: changes with selected nav item.

## Data Source Plan

Use local mock-data JSON first. Future API/database flow must be dashboard UI to API adapter to backend/database, never direct browser-to-database.
