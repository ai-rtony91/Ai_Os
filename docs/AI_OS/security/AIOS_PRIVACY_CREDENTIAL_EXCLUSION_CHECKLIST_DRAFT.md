# AI_OS Privacy Credential Exclusion Checklist Draft

## Purpose

This draft defines privacy and credential exclusion checks for future telemetry/reporting persistence planning.

No protected root files are edited by this draft. Human approval is required before adopting this checklist for APPLY behavior. This draft creates no live automation, no active telemetry writer, no active report writer, no persistence enabled, and no trading automation.

## Must Block

- Passwords.
- Tokens.
- API keys.
- SSH keys.
- OAuth secrets.
- Browser profile paths.
- Credential stores.
- Broker account identifiers.
- Live account data.
- Private user data.
- Screenshots containing private data.
- Live market execution data.

## Fail-Closed Rule

Any suspected credential, private data, broker data, or live market execution data must fail closed. The result should be BLOCKED until human approval and verified evidence clarify the path forward.

## Mismatch Rule

Report mismatch, do not hide it. If observed evidence conflicts with prior notes or instructions, mark it REVIEW, BLOCKED, or INVALID DATA as appropriate.

## Boundary

This checklist does not approve persistence, report writing, telemetry writing, protected root file edits, live automation, or trading automation.
