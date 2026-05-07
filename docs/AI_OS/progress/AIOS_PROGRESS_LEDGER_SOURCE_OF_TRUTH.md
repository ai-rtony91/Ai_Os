# AIOS Progress Ledger Source Of Truth

Status: Draft source-of-truth planning document
Mode: Documentation only

## Purpose

The AI_OS Progress Ledger defines how Codex workloads report stage progress, countdown status, blockers, checkpoints, and commit state.

## Required Workload Fields

- current stage
- task ID
- task name
- planned step count
- completed step count
- percent complete
- status
- blocked flag
- blocker
- next action
- checkpoint file
- commit hash
- git status
- notes

## Progress Rules

- Percent complete is calculated from completed steps divided by planned steps.
- If planned steps is zero or UNKNOWN, percent complete must be UNKNOWN.
- Blocked workloads must identify a blocker and next safe action.
- Every workload row must point to a checkpoint file when a checkpoint exists.
- Commit hash may be UNKNOWN before commit.

## Safety Boundary

The progress ledger is reporting-only. It must not create broker connections, place trades, add secrets, or modify protected root governance files.
