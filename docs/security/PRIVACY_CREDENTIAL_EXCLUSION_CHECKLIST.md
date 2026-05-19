# AI_OS Privacy Credential Exclusion Checklist

Status: canonical security checklist
Source: `docs/AI_OS/security/AIOS_PRIVACY_CREDENTIAL_EXCLUSION_CHECKLIST_DRAFT.md`

## Purpose

This checklist defines privacy and credential exclusions for future telemetry, reporting, dashboard, and persistence planning. It does not approve persistence, report writing, telemetry writing, protected root edits, live automation, or trading automation.

## Must Block

- Passwords.
- Tokens.
- API keys.
- SSH keys.
- OAuth secrets.
- Private keys.
- Recovery keys.
- Browser profile paths.
- Credential stores.
- Broker account identifiers.
- Live account data.
- Private user data.
- Screenshots containing private data.
- Live market execution data.
- Order details or live order path data.

## Fail-Closed Rule

Any suspected credential, private data, broker data, or live market execution data must fail closed. The result should be `BLOCKED` until human approval and verified evidence clarify the path forward.

## Mismatch Rule

Report mismatch; do not hide it. If observed evidence conflicts with prior notes or instructions, mark it `REVIEW`, `BLOCKED`, or `INVALID DATA` as appropriate.

