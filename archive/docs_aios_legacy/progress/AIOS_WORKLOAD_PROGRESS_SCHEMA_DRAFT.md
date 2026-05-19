# AIOS Workload Progress Schema Draft

Status: Draft schema

## CSV Header

```csv
date,time,stage,task_id,task_name,planned_steps,completed_steps,percent_complete,status,blocked,blocker,next_action,checkpoint_file,commit_hash,git_status,notes
```

## Field Definitions

- date: local date in YYYY-MM-DD format.
- time: local time in HH:mm:ss format.
- stage: current AI_OS stage or module name.
- task_id: stable workload identifier.
- task_name: human-readable workload name.
- planned_steps: expected step count.
- completed_steps: verified completed step count.
- percent_complete: integer percentage or UNKNOWN.
- status: current workload status.
- blocked: YES or NO.
- blocker: blocker detail or blank when not blocked.
- next_action: exact next safe action.
- checkpoint_file: related checkpoint path or UNKNOWN.
- commit_hash: Git commit hash or UNKNOWN.
- git_status: summarized Git status.
- notes: short operator-facing notes.

## Validation Rules

- Header must match the required CSV header exactly.
- planned_steps and completed_steps must be numeric or UNKNOWN.
- percent_complete must be numeric from 0 to 100 or UNKNOWN.
- blocked must be YES or NO.
- next_action must not be blank.
