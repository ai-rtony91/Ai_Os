# Fix Verification Checklist

Use this after APPLY and before commit.

- Problem category was named.
- Owner or agent was named.
- Allowed files were followed.
- Blocked files were not touched.
- Repair type stayed isolated.
- Validator checks passed.
- No secrets were touched.
- No connector/API activation happened.
- No broker, OANDA, live trading, real webhook, or real order path was added.
- Rollback note exists.
- Commit package contains only related files.
- `git add .` was not used.

Dock player checks:

- Icon state matches playback state.
- Button labels are clear.
- Mobile layout remains readable.
- Panel spacing does not overlap.
- No unrelated dashboard panels changed.
- No Trading Lab files changed.
