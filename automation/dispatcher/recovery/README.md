# Dispatcher Recovery

Recovery files help resume work after a reboot, crash, or closed Codex window.

Recovery state should show what was active, what was waiting, what failed, and the next safe action.

Required recovery fields:

- `active_packets`
- `active_locks`
- `pending_approvals`
- `failed_packets`
- `last_known_git_state`
- `next_safe_action`
- `updated_at`

Recovery rules:

- Check recovery before assigning new packets.
- Check active locks before APPLY.
- Check pending approvals before edits.
- Treat unknown worker state as `REVIEW_REQUIRED`.
- Do not auto-clean dirty files.
- Do not auto-stage files.
- Do not auto-commit or auto-push.

