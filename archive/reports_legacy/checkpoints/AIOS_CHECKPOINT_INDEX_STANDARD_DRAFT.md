# AIOS Checkpoint Index Standard Draft

Status: Draft planning doc
Stage: 12.3

## Purpose

Define rules for indexing AI_OS checkpoints.

## Required Index Fields

- checkpoint_path
- checkpoint_date
- workload
- mode
- related_report
- commit_hash
- next_action

## Rules

- Do not modify source checkpoints.
- Mark missing related reports as UNKNOWN.
- Mark conflicting checkpoint evidence as MISMATCH.
