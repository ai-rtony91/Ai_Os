# Safe Repair Flow

Use this flow before fixing any problem.

1. State the issue in one sentence.
2. Classify the issue.
3. Identify the likely owner.
4. Identify likely affected files.
5. Identify blocked files.
6. Decide repair type.
7. Check change-control rules.
8. Pick validator checks.
9. Write rollback note.
10. Write a scoped APPLY prompt.
11. Wait for approval.

Dock player example:

- Issue: dock player icon state is confusing.
- Category: UI-only or logic-only.
- Owner: UI Agent.
- Route: UI readability role for wording/spacing; UI Agent for behavior; Validator Gap Agent if there is no check.
- Allowed files: exact dashboard files only after approval.
- Blocked files: Trading Lab, product docs, secrets, broker files, OANDA files, protected root files, `.codex_backups/`.
- Validator: dashboard boundary check, state consistency check, mobile readability check.
- Commit package: dashboard dock player fix only.

If the repair touches unrelated files, stop and split the package.
