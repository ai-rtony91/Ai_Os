# AI_OS Lock Rules

- One packet per worker.
- One owner per file group.
- No conflicting edits without explicit operator approval.
- No auto-merge to `main`.
- No blind `git add .`.
- No `git add -A`.
- No staging without exact-file review.
- No deleting, moving, or renaming files without explicit approval.
- No startup tasks or scheduled tasks.
- No broker, OANDA, API key, webhook, or live trading work.
- Unclear ownership is `REVIEW_REQUIRED`.
