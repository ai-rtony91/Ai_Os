# AIOS Bootstrap Rollback Recommendation Draft

Status: Draft planning doc
Stage: 12.7

## Purpose

Plan rollback recommendation rules for bootstrap-generated work.

## Recommendation Fields

- checkpoint_file
- commit_hash
- affected_paths
- risk
- verification_command
- recovery_instruction

## Boundary

Recommendations must not run rollback commands.
