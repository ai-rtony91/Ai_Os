# AI_OS Work Table AI Scoring Rules Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.19 - Work Table AI Foundation

## Purpose

Define draft scoring rules for local mock Work Table AI planning.

## Score Range

Scores should use a 0 to 100 range.

## Draft Inputs

- evidence completeness
- checkpoint availability
- validator status
- blocked status
- next action clarity
- phase/stage relevance
- operator approval requirement

## Draft Interpretation

- 0-19: insufficient evidence
- 20-39: blocked or unclear
- 40-59: needs review
- 60-79: ready for operator review
- 80-100: strong candidate for next review

## Safety Rule

A high score is not approval. A high score only means the item may deserve review. APPLY, commit, push, deploy, trading, broker access, and database access remain blocked without human approval.

