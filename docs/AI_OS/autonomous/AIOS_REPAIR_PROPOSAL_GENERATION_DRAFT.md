# AIOS Repair Proposal Generation Draft

Stage: 11.3
Status: Draft planning doc

## Purpose

Define how AI_OS may generate repair proposals without applying them.

## Required Proposal Fields

- repair_id
- detected_issue
- evidence_path
- affected_files
- proposed_action
- protected_action_involved
- approval_required
- rollback_reference
- next_safe_action

## Evidence Rules

- Missing facts are UNKNOWN.
- Conflicting evidence is MISMATCH.
- Unverified claims are INVALID DATA.

## Boundary

Repair proposals are not repair execution.
