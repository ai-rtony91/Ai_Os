# APPROVAL REQUIRED — Enable SOS Notifier Channel

```
APPROVAL-ID: AIOS-APV-SOS-NOTIFIER-20260531
STATUS: WAITING
RISK: YELLOW (requires a credential — ultimate blocker)
REQUESTED-BY: Claude (overwatch)
RELATED: relay/handoffs/CODEX_CLOSE_AUTONOMY_LOOP.md (ISSUE 3)
```

## What this unblocks
`services/python_supervisor/notifier.py` ships with a safe default `file` channel
(writes to `relay/reports/SOS_OUTBOX/`). To actually reach Anthony overnight (email/push),
it needs ONE real credential. Until approved, the email/push channel stays DISABLED.

## What is being requested
Provide ONE notification credential, supplied via environment variable (never hardcoded,
never committed):

- **Email option:** `AIOS_SMTP_HOST`, `AIOS_SMTP_PORT`, `AIOS_SMTP_USER`, `AIOS_SMTP_PASS`,
  `AIOS_SMTP_TO` (Anthony's address).
- **Push option (simpler):** `AIOS_PUSH_TOKEN` (e.g. Pushover/ntfy token) + `AIOS_PUSH_TARGET`.

## Why it is gated
A credential/secret is an ultimate blocker per relay doctrine. Claude/Codex must never
hold, write, or commit a secret. Anthony sets the env var on the machine himself.

## Decision
- [ ] APPROVE — Anthony will set the chosen env vars locally, then notifier email/push enables.
- [ ] REJECT — keep `file`-channel SOS only (Anthony checks `relay/reports/SOS_OUTBOX/` manually).

## On approval
Move this file to `relay/approvals/approved/`. No code change needed beyond setting the env var;
notifier.py reads the var names at runtime.
