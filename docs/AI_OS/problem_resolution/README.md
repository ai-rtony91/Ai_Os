# AI_OS Problem Resolution Workflow

This folder explains how AI_OS should detect a problem, classify it, find the likely owner, and propose a safe repair path.

This does not perform repair by itself. It feeds the change-control process in `docs/AI_OS/change_control/`.

Example problem: the dock player is confusing. The icon may show the wrong state, spacing may be cramped on mobile, or the player may be placed in the wrong area.

Basic flow:

1. Describe the problem.
2. Classify the problem type.
3. Find likely ownership.
4. List likely affected files.
5. List blocked files.
6. Pick the validator or check.
7. Decide repair type.
8. Check whether the package is isolated.
9. Write a rollback note.
10. Route to the right agent or role.
11. Send the scoped repair proposal to change control.

Default result is DRY_RUN. APPLY requires separate approval.
