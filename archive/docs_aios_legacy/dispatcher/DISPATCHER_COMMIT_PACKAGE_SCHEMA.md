# Dispatcher Commit Package Schema

A commit package describes the exact files that may be staged after validation and human review.

Commit packages do not stage files by themselves.

Required fields:

| Field | Purpose |
| --- | --- |
| `commit_package_id` | Unique package name. |
| `packet_ids` | Packets included in the package. |
| `files_allowed_to_stage` | Exact files approved for staging. |
| `validation_result` | Validator result for the package. |
| `commit_message_draft` | Draft commit message. |
| `repo_state` | Clean, dirty, or review-required state. |
| `approval_status` | Human review state. |
| `next_safe_action` | Next safe operator action. |

Commit rules:

- Dirty repo state blocks commit packaging.
- Untracked `??` files are `REVIEW_REQUIRED`.
- Never use `git add .`.
- Stage exact approved files only.
- Commit requires human approval.
- Push requires human approval.

