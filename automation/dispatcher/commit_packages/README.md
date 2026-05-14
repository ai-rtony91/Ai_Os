# Dispatcher Commit Packages

Commit packages group approved files into a clean review unit.

The dispatcher does not auto-stage files. Commit packages only describe what may be staged after human review.

Required commit package fields:

- `commit_package_id`
- `packet_ids`
- `files_allowed_to_stage`
- `validation_result`
- `commit_message_draft`
- `repo_state`
- `approval_status`
- `next_safe_action`

Commit rules:

- A dirty repo blocks commit packaging until reviewed.
- Untracked `??` files are `REVIEW_REQUIRED`.
- Never use `git add .`.
- Stage exact approved files only.
- Commit requires human approval.
- Push requires human approval.

