# AIOS Bitwarden Runtime Session Hardening V1

## Mission

The controlled micro-live runner must not expose live credentials in console output.
Owner runtime should not store the Bitwarden master password or `BW_SESSION` values in
repo files or reports.

## Required session handling

- Do not store the Bitwarden master password.
- Do not store BW_SESSION in repo.
- Do not store bw_session in repo.
- Run session helpers from the current PowerShell process using dot-sourcing:
  - `. .\scripts\security\Start-AiosBitwardenSession.ps1`
  - `. .\scripts\security\Clear-AiosBitwardenSession.ps1`
- `Start-AiosBitwardenSession.ps1` must:
  - call `bw status` first.
  - set `AIOS_BITWARDEN_SESSION_READY=true/false`.
  - set `BW_SESSION_PRESENT=true/false`.
  - avoid printing session keys, vault contents, or item values.
  - call `bw unlock --raw` only when the vault is locked.
  - never persist credentials in any repo file.
- `Clear-AiosBitwardenSession.ps1` must:
  - remove `Env:BW_SESSION`.
  - call `bw lock`.
  - print only safe confirmation lines.

## Runtime hardening notes

- The controlled micro-live runner must print redacted stdout only, matching the same
  sanitizer used for state/report output.
- Rotate any token that was pasted to console or chat immediately after the
  owner run.
- Do not use repository secrets for convenience.
- Persistent convenience is allowed only through owner-local session management
  helpers, never through repository-stored credentials.
