# AIOS Bitwarden Runtime Session Hardening V1

## Mission

The controlled micro-live runner must not expose live credentials in console output.
Owner runtime should not store the Bitwarden master password or `BW_SESSION` values in
repo files or reports.

## Required session handling

- Do not store the Bitwarden master password.
- Do not store BW_SESSION in repo.
- Do not store `bw_session` in repo.
- Run session helpers from the current PowerShell process using dot-sourcing:
  - `. .\scripts\security\Start-AiosBitwardenSession.ps1`
  - `. .\scripts\security\Clear-AiosBitwardenSession.ps1`
- Owners should be prompted for their Bitwarden master password at most once per PowerShell session.
- `Start-AiosBitwardenSession.ps1` uses the explicit local DPAPI broker:
  - trust an existing `Env:BW_SESSION` when non-empty and skip unlock.
  - otherwise use local credential storage at
    `$env:LOCALAPPDATA\AIOS\Security\bitwarden-master-password.dpapi`.
  - call `bw unlock --passwordenv BW_PASSWORD --raw` only.
  - never call `bw unlock --raw`.
  - never prompt for a master password.
- After `BW_SESSION` is set in-session, repeated controlled runner invocations in that shell should reuse it and should not reprompt for the master password.
- Clear the session at the end of the shell session or when done with live operations using:
  - `. .\scripts\security\Clear-AiosBitwardenSession.ps1`
- `Clear-AiosBitwardenSession.ps1` must:
  - remove `Env:BW_SESSION`.
  - remove `Env:BW_PASSWORD`.
  - call `bw lock`.
  - print only safe confirmation lines.
- `Start-AiosBitwardenSession.ps1` must:
  - set `AIOS_BITWARDEN_SESSION_READY=true/false`.
  - set `BW_SESSION_PRESENT=true/false`.
  - set `LOCAL_CREDENTIAL_PRESENT=true/false`.
  - set `SAFE_NEXT_ACTION=<safe text>`.
  - avoid printing session keys, vault contents, or item values.
  - use local DPAPI broker when local credential is registered.
  - never persist credentials in any repo file.
- Registration is explicit owner action in
  `scripts/security/Register-AiosBitwardenLocalCredential.ps1`.

## Runtime hardening notes

- the controlled micro-live runner must print redacted stdout only, matching the same
  sanitizer used for state/report output.
- Rotate any token that was pasted to console or chat immediately after the
  owner run.
- Do not use repository secrets for convenience.
- Persistent convenience is allowed only through owner-local session management
  helpers, never through repository-stored credentials.
- Do not use `--passwordfile`.

## Local broker reference

- See: `docs/security/AIOS_BITWARDEN_LOCAL_CREDENTIAL_BROKER_V1.md`
