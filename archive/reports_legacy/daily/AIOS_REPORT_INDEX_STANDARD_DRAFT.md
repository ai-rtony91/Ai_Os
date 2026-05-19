# AIOS Report Index Standard Draft

Status: Draft planning doc
Stage: 12.3

## Purpose

Define rules for indexing AI_OS daily reports.

## Required Index Fields

- report_path
- report_date
- workload
- mode
- related_checkpoint
- apply_status
- known_gaps
- next_action

## Rules

- Do not modify source reports.
- Mark missing related checkpoints as UNKNOWN.
- Mark conflicting report evidence as MISMATCH.
