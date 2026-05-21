# AI_OS Task Approval Rules

## Purpose

This document defines how AI_OS may generate task recommendations and where human approval is required before action.

Task recommendations are planning material. They are not execution authority.

## What AI_OS May Generate Automatically

AI_OS may generate:

- Draft task titles.
- Task categories.
- Suggested priorities.
- Reasons and source notes.
- Estimated effort labels.
- Review-needed task batches.
- Local Markdown or structured draft output.
- Recommendations for next safe steps.

Automatically generated tasks must remain in `draft` or `review_needed` status until a human approves the next action.

## What AI_OS May Never Execute Without Approval

AI_OS may never execute these actions without explicit human approval:

- Commit, push, merge, rebase, reset, or delete Git history.
- Close issues or pull requests.
- Approve pull requests.
- Run live deployment or production automation.
- Modify secrets, credentials, tokens, OAuth clients, broker keys, or recovery keys.
- Execute broker, OANDA, webhook, live-trading, or real-order actions.
- Create, update, complete, or delete Microsoft To Do tasks.
- Move, rename, delete, or overwrite files outside an approved scope.
- Modify protected root authority files unless explicitly scoped.
- Treat generated task output as permission to mutate the repo.

## What Requires Explicit Human Approval

Explicit human approval is required before:

- Exporting a task to Microsoft To Do.
- Changing a task from `review_needed` to `approved_for_export`.
- Creating integration code.
- Adding OAuth configuration.
- Storing tokens in any location.
- Running APPLY work.
- Editing runtime, orchestration, dashboard, trading, or security systems.
- Creating new canonical documentation when an existing file may own the topic.
- Promoting a task recommendation into a work packet, GitHub issue, or execution lane.

## What Can Be Sent To Microsoft To Do As Draft Or Review-Needed

After a future approved export path exists, the following may be eligible for Microsoft To Do as draft or review-needed items:

- Documentation tasks.
- Repo review tasks.
- Governance review tasks.
- Human decision tasks.
- Automation candidate reviews.
- Safe validation reminders.
- Planning tasks that do not imply execution.

Every exported task must preserve its approval requirement and must not become executable solely because it appears in Microsoft To Do.

## What Should Remain Manual For Now

The following should remain manual until stronger governance and validation exist:

- Microsoft account linking.
- OAuth app registration.
- Token creation, storage, rotation, and revocation.
- Live Microsoft Graph writes.
- Task completion sync from Microsoft To Do back into AI_OS.
- Repo mutation based on external task state.
- GitHub issue or pull request automation from task state.
- Worker assignment based on Microsoft To Do status.

## Escalation Rules

Escalate to the human operator when:

- A task touches secrets, tokens, identity, or permissions.
- A task touches broker, OANDA, trading, webhook, or live-order systems.
- A task requires branch, commit, push, merge, or PR decisions.
- A task may duplicate existing canonical authority.
- A task requires changing runtime, orchestration, dashboard, or protected governance systems.
- A task source conflicts with `AGENTS.md`, `README.md`, or active governance docs.
- A task cannot be verified from allowed files.

## Stop Conditions

Stop immediately when:

- The task asks AI_OS to act without human approval.
- The task asks for credentials, tokens, secrets, or OAuth client secrets.
- The task asks AI_OS to create Microsoft To Do items before export approval exists.
- The task asks AI_OS to treat Microsoft To Do as execution authority.
- The task conflicts with protected trading or runtime boundaries.
- The approved scope is unclear or overlaps with another worker lane.
- The current branch or working folder does not match the task instructions.

## Microsoft To Do Boundary

Microsoft To Do is allowed only as a future human-facing task review and tracking surface.

It is not:

- Repo authority.
- Approval authority.
- Runtime authority.
- Worker authority.
- Evidence authority.
- A substitute for AI_OS validation.

AI_OS must continue to follow DRY_RUN/APPLY, validation, and selective commit rules regardless of Microsoft To Do task status.
