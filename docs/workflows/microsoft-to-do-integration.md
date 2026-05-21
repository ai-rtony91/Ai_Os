# Microsoft To Do Phase 1 Integration Plan

## Purpose

This plan defines the Phase 1 Microsoft To Do integration foundation for AI_OS.

Phase 1 is documentation-first. It establishes how AI_OS can produce task recommendations in a human-readable format before any live Microsoft Graph integration exists.

The goal is to support AI_OS task output, human review, and later controlled export to Microsoft To Do without granting AI_OS autonomous execution authority.

## Scope

Phase 1 includes:

- A documented AI_OS task output model.
- Human approval boundaries for task creation and task routing.
- A future Microsoft To Do account-linking approach.
- A future Microsoft Graph permission model.
- A Markdown-only first task batch.
- A placement recommendation for any later integration code.

Phase 1 does not include live API calls, OAuth setup, token storage, background sync, or task creation inside Microsoft To Do.

## Non-Goals

Phase 1 does not allow AI_OS to:

- Create Microsoft To Do tasks automatically.
- Modify, complete, delete, or reorder Microsoft To Do tasks.
- Execute repo changes based on task recommendations.
- Close issues, merge pull requests, commit code, push branches, or approve work.
- Store Microsoft credentials, tokens, secrets, or OAuth client IDs.
- Act as the final authority for task priority or execution.

## Phase 1 Behavior

AI_OS may generate task recommendations as local documentation or structured draft output.

Each task recommendation should include:

- Clear title.
- Category.
- Priority.
- Reason.
- Source.
- Approval requirement.
- Estimated effort.
- Status.
- Target list.
- Notes.

Recommended statuses for Phase 1 are:

- `draft`
- `review_needed`
- `approved_for_export`
- `blocked`
- `manual_only`

The safe default is `review_needed`.

## Human Approval Boundary

Human approval is required before any task leaves AI_OS and enters Microsoft To Do.

Human approval is also required before any AI_OS-generated task leads to:

- File edits.
- Script execution.
- Runtime automation.
- Credential handling.
- Git operations beyond status or diff inspection.
- Dashboard, trading, broker, webhook, or live-order work.

Microsoft To Do is a task tracking surface only. It is not approval authority and must not be treated as permission to execute repo work.

## Required Microsoft Graph Permissions

Future Microsoft Graph integration should request the smallest practical delegated permissions.

Candidate permissions for a later reviewed implementation:

- `Tasks.ReadWrite` for creating and updating To Do tasks after approval.
- `offline_access` only if persistent background sync is explicitly approved.
- `User.Read` only if required by the chosen account-linking flow.

Phase 1 grants no permissions and creates no app registration.

Any future permission request must be reviewed for:

- Least privilege.
- Token storage location.
- Expiration and revocation behavior.
- Whether background access is truly needed.
- Separation between draft task export and task execution.

## Account-Linking Approach

Future account linking should use an explicit user-initiated OAuth flow.

Recommended constraints:

- Link one human Microsoft account at a time.
- Store tokens only in an approved secret store, never in repo files.
- Display the target account before exporting tasks.
- Require a human confirmation step before writing to Microsoft To Do.
- Provide a local dry-run preview of every task that would be exported.
- Support unlinking and token revocation.

Until that flow exists, all task batches remain local documentation only.

## Data Flow

Phase 1 data flow:

1. AI_OS inspects approved repo context.
2. AI_OS generates task recommendations in local docs.
3. Human reviews the task batch.
4. Human decides which tasks are approved, deferred, changed, or rejected.
5. No Microsoft To Do write occurs.

Future approved data flow:

1. AI_OS generates a task batch.
2. Human reviews a dry-run export preview.
3. Human approves selected tasks for export.
4. Integration adapter sends approved task fields to Microsoft Graph.
5. Adapter records returned external task IDs in an approved local ledger.
6. AI_OS continues to treat Microsoft To Do as a tracking surface, not execution authority.

## Integration Placement Recommendation

The least invasive future architecture is an external adapter or tools integration, not core runtime code.

Options evaluated:

| Option | Recommendation | Reason |
|---|---|---|
| Core integration | Defer | Too invasive for Phase 1 and risks turning task tracking into system authority. |
| Tools integration | Candidate | Fits a human-triggered export workflow if the repo later standardizes a tools layer. |
| External adapter | Preferred | Keeps Microsoft Graph boundaries separate from orchestration, runtime, dashboard, and trading systems. |
| Scripts utility | Candidate for dry-run preview only | Useful for local validation, but should not become an ungoverned automation path. |
| Worker plugin | Defer | Worker routing should not gain task-write capability until approval and audit models are stronger. |

Recommended future home, pending approval:

- `automation/integrations/microsoft-todo/` for governed dry-run/export scripts, or
- `tools/integrations/microsoft-todo/` if a top-level tools pattern is explicitly approved later.

No integration code should be added until the adapter boundary, token storage model, and validation chain are approved.

## Safety Risks

Primary risks:

- Treating a task recommendation as permission to execute.
- Accidentally storing OAuth secrets in the repo.
- Over-permissioning Microsoft Graph access.
- Creating duplicate task authority across AI_OS docs, Microsoft To Do, GitHub issues, and runtime queues.
- Allowing Microsoft To Do completion status to imply repo completion.
- Letting AI_OS create or close work without human review.

Risk controls:

- Keep Phase 1 local and documentation-only.
- Require human approval before export.
- Keep Microsoft To Do as a tracking surface only.
- Do not store credentials or tokens in repo files.
- Keep repo execution under AI_OS DRY_RUN/APPLY rules.

## Future Phases

Phase 2 candidate:

- Define JSON schema for task batch export.
- Create a dry-run Microsoft To Do export preview.
- Validate required fields and target list mapping.

Phase 3 candidate:

- Add human-approved OAuth setup.
- Add token storage using an approved secret store.
- Add explicit one-shot export after dry-run approval.

Phase 4 candidate:

- Record exported task IDs in an approved ledger.
- Support read-only reconciliation between local task records and Microsoft To Do.

Phase 5 candidate:

- Add controlled sync rules, if still needed.
- Keep execution authority separate from task tracking.

## Open Questions

- Should AI_OS use one Microsoft To Do list or multiple lists by task category?
- Should exported task IDs be recorded in a local ledger, a JSON file, or an existing telemetry system?
- Should task export be allowed only from approved Markdown batches, or from structured JSON too?
- Which approved secret store should hold future OAuth tokens?
- Should GitHub issues and Microsoft To Do tasks be correlated later, or kept separate?
- What validation must pass before a task is eligible for export?
