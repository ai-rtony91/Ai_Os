# Initial Microsoft To Do Task Batch

## Purpose

This is the first AI_OS Microsoft To Do task batch in Markdown only.

No tasks have been created in Microsoft To Do. These entries are local planning material for human review.

## Task Batch

| Title | Category | Priority | Reason | Approval Required | Estimated Effort | Target List | Status |
|---|---|---|---|---:|---|---|---|
| Draft Microsoft To Do Phase 1 integration plan | documentation | high | Establish the safe Phase 1 boundary before any integration code exists. | true | small | AI_OS - Documentation | review_needed |
| Create AI_OS - Command Inbox list | human_approval | medium | Prepare a future human-facing inbox for approved AI_OS task output. | true | tiny | AI_OS - Human Review | draft |
| Create AI_OS - Automation Candidates list | human_approval | medium | Prepare a future list for automation candidates that still require review. | true | tiny | AI_OS - Human Review | draft |
| Create AI_OS task schema | documentation | high | Define the task fields needed before export or automation can be considered. | true | small | AI_OS - Documentation | review_needed |
| Document task approval rules | governance | high | Prevent task recommendations from becoming execution authority. | true | small | AI_OS - Documentation | review_needed |
| Identify which AI_OS tasks can be automated now | automation_candidate | medium | Separate safe DRY_RUN candidates from work that requires stronger controls. | true | medium | AI_OS - Automation Candidates | draft |
| Identify which AI_OS actions must remain human-approved | governance | high | Preserve human authority over risky actions and external writes. | true | medium | AI_OS - Human Review | review_needed |
| Review current repo structure before adding integration code | repo_review | high | Confirm canonical placement before introducing Microsoft Graph code. | true | medium | AI_OS - Command Inbox | review_needed |
| Decide whether Microsoft Graph integration belongs in core or tools | human_approval | high | Integration placement affects runtime boundaries, token handling, and audit scope. | true | small | AI_OS - Human Review | manual_only |
| Create progress report for current AI_OS stage | documentation | medium | Capture current posture and next steps for continuity. | true | small | AI_OS - Documentation | review_needed |

## Batch Rules

- This batch is not a Microsoft To Do export.
- All entries require human review before export.
- No entry authorizes repo mutation.
- No entry authorizes Microsoft Graph calls.
- No credentials, tokens, OAuth clients, or task IDs are included.
- `Target List` is a routing suggestion only.
