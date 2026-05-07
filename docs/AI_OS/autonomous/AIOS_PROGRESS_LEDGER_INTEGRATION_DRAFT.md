# AIOS Progress Ledger Integration Draft

Stage: 11.4
Status: Draft planning doc

## Purpose

Define how autonomous loops report status through the AI_OS Progress Ledger.

## Required Fields

- stage
- task_id
- task_name
- planned_steps
- completed_steps
- percent_complete
- status
- blocked
- blocker
- next_action
- checkpoint_file
- commit_hash
- git_status

## Boundary

Progress rows are reporting artifacts and do not authorize APPLY.
