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
- Owners should be prompted for their Bitwarden master password at most once per PowerShell session.
- After `BW_SESSION` is set in-session, repeated controlled runner invocations in that shell should reuse it and should not reprompt for the master password.
- Clear the session at the end of the shell session or when done with live operations using:
  - `. .\scripts\security\Clear-AiosBitwardenSession.ps1`
- `Start-AiosBitwardenSession.ps1` must:
  - trust an existing `Env:BW_SESSION` when non-empty and skip `bw unlock`.
  - set `AIOS_BITWARDEN_SESSION_READY=true/false`.
  - set `BW_SESSION_PRESENT=true/false`.
  - avoid printing session keys, vault contents, or item values.
  - call `bw unlock --raw` only when `Env:BW_SESSION` is missing or empty.
  - never persist credentials in any repo file.
- Start helper behavior in-session:
  - dot-source only: `. .\scripts\security\Start-AiosBitwardenSession.ps1`.
  - owner is prompted for a Bitwarden unlock at most once per PowerShell session.
  - once `BW_SESSION` is set, repeated runner calls in the same shell reuse it.
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
