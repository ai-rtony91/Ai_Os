# AI_OS Task Schema

## Purpose

This document defines the Phase 1 AI_OS task recommendation schema.

The schema is for local task output and human review. It does not authorize execution, Microsoft To Do writes, repo mutation, commits, pushes, issue closure, or pull request merges.

## Schema Fields

| Field | Required | Type | Description |
|---|---:|---|---|
| `title` | yes | string | Short human-readable task name. |
| `category` | yes | string | Work class, such as documentation, governance, repo_review, automation_candidate, human_approval, telemetry, or safety. |
| `priority` | yes | string | Suggested priority: low, medium, high, or urgent. |
| `reason` | yes | string | Why the task exists and what problem it addresses. |
| `source` | yes | string | Where the recommendation came from, such as user_prompt, repo_audit, workflow_gap, telemetry, or human_request. |
| `approval_required` | yes | boolean | Whether a human must approve before execution or export. |
| `estimated_effort` | yes | string | Rough effort label: tiny, small, medium, large, or unknown. |
| `status` | yes | string | Current state: draft, review_needed, approved_for_export, blocked, manual_only, exported, or complete. |
| `created_by` | yes | string | Creator identity, such as Codex, ChatGPT, human, or AI_OS. |
| `created_at` | yes | string | ISO 8601 timestamp or date. |
| `target_list` | yes | string | Intended Microsoft To Do list name or local-only holding list. |
| `external_task_id` | no | string or null | Microsoft To Do task ID after export. Must be null before export. |
| `notes` | no | string | Additional context, constraints, or approval notes. |

## Field Rules

- `approval_required` should default to `true`.
- `external_task_id` must remain `null` until a human-approved Microsoft To Do export exists.
- `status` must not be used as execution approval.
- `target_list` is a routing suggestion only until a human approves export.
- `priority` is advisory and must not override safety rules.
- `source` must not treat generated evidence, task lists, or Microsoft To Do as authority.

## Recommended Categories

- `documentation`
- `governance`
- `repo_review`
- `automation_candidate`
- `human_approval`
- `telemetry`
- `safety`
- `integration_design`

## Recommended Target Lists

- `AI_OS - Command Inbox`
- `AI_OS - Automation Candidates`
- `AI_OS - Human Review`
- `AI_OS - Documentation`
- `local_only`

## Example: Documentation Task

```json
{
  "title": "Draft Microsoft To Do Phase 1 integration plan",
  "category": "documentation",
  "priority": "high",
  "reason": "AI_OS needs a documented boundary before any Microsoft To Do integration code is considered.",
  "source": "user_prompt",
  "approval_required": true,
  "estimated_effort": "small",
  "status": "review_needed",
  "created_by": "Codex",
  "created_at": "2026-05-20",
  "target_list": "AI_OS - Documentation",
  "external_task_id": null,
  "notes": "Phase 1 only. No Microsoft Graph calls."
}
```

## Example: Repo Review Task

```json
{
  "title": "Review current repo structure before adding integration code",
  "category": "repo_review",
  "priority": "high",
  "reason": "AI_OS requires existing canonical ownership before introducing a new integration path.",
  "source": "workflow_gap",
  "approval_required": true,
  "estimated_effort": "medium",
  "status": "review_needed",
  "created_by": "AI_OS",
  "created_at": "2026-05-20",
  "target_list": "AI_OS - Command Inbox",
  "external_task_id": null,
  "notes": "Review only. No file moves, runtime edits, or integration code."
}
```

## Example: Automation Candidate Task

```json
{
  "title": "Identify which AI_OS tasks can be automated now",
  "category": "automation_candidate",
  "priority": "medium",
  "reason": "Automation candidates need classification before any scripts or worker flows are added.",
  "source": "human_request",
  "approval_required": true,
  "estimated_effort": "medium",
  "status": "draft",
  "created_by": "Codex",
  "created_at": "2026-05-20",
  "target_list": "AI_OS - Automation Candidates",
  "external_task_id": null,
  "notes": "Candidates must stay DRY_RUN until explicitly approved."
}
```

## Example: Human Approval Task

```json
{
  "title": "Decide whether Microsoft Graph integration belongs in core or tools",
  "category": "human_approval",
  "priority": "high",
  "reason": "Integration placement affects authority boundaries, token handling, and future automation risk.",
  "source": "integration_design",
  "approval_required": true,
  "estimated_effort": "small",
  "status": "manual_only",
  "created_by": "AI_OS",
  "created_at": "2026-05-20",
  "target_list": "AI_OS - Human Review",
  "external_task_id": null,
  "notes": "Human decision required before implementation."
}
```
