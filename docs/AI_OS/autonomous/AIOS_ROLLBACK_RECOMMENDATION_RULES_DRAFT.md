# AIOS Rollback Recommendation Rules Draft

Stage: 11.3
Status: Draft planning doc

## Purpose

Define how AI_OS may recommend rollback options without performing them.

## Required Rollback Recommendation Fields

- checkpoint_file
- candidate_commit_hash
- affected_scope
- reason
- evidence
- risk_notes
- human_approval_required
- exact verification instruction

## Boundary

Rollback recommendations must not run `git reset`, delete files, move files, or alter the working tree.
