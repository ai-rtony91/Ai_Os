# AIOS Bitwarden Local Credential Broker V1

## Purpose

Stop repeated Bitwarden master-password prompts by storing a Windows owner-local encrypted credential blob outside the repo and unlocking the session helper non-interactively.

## Storage

- `Register-AiosBitwardenLocalCredential.ps1` saves the Bitwarden master password to:
  `$env:LOCALAPPDATA\AIOS\Security\bitwarden-master-password.dpapi`
- The file is encrypted with Windows DPAPI in current-user scope via
  `ConvertFrom-SecureString` and written as stable single-line ASCII content using
  `System.IO.File.WriteAllText`.
- The file stays outside repo at `%LOCALAPPDATA%`.
- If the stored blob becomes malformed, remove and re-register it with
  `Register-AiosBitwardenLocalCredential.ps1` before running start helper again.

## Risk

This is owner-local convenience, not zero-trust storage.
Any process running as the same Windows user can potentially decrypt the blob.
Treat `AIOS` runtime access as local-user privileged, not globally trusted.

## Runtime flow

1. Register once:
   `. .\scripts\security\Register-AiosBitwardenLocalCredential.ps1`
2. Start runtime:
   `. .\scripts\security\Start-AiosBitwardenSession.ps1`
3. Clear runtime session:
   `. .\scripts\security\Clear-AiosBitwardenSession.ps1`
4. Remove stored local credential:
   `. .\scripts\security\Remove-AiosBitwardenLocalCredential.ps1`

## Safe behavior rules

- Never paste or screenshot:
  - Bitwarden master password
  - `BW_PASSWORD`
  - `BW_SESSION`
  - vault JSON
  - token
  - account ID
- Do not store secrets in:
  - repo files
  - `.env`
  - plain text files
- Do not use `--passwordfile`.
- Do not store API tokens in repo.
- Credential registration is explicit and owner-run only.

## Implementation notes

- Start helper uses local DPAPI blob when `Env:BW_SESSION` is missing.
- Start helper trims whitespace and BOM (`[char]0xFEFF`) from DPAPI text before
  decryption, and exits with safe status if decryption fails.
- Start helper calls only `bw unlock --passwordenv BW_PASSWORD --raw`.
- Start helper clears `BW_PASSWORD` immediately and only leaves `BW_SESSION` in the current shell session.
- `Clear-AiosBitwardenSession.ps1` clears both environment variables and calls `bw lock`.
- Local credential file removal is handled only by `Remove-AiosBitwardenLocalCredential.ps1`.
- If decryption fails, start helper must return:
  - `AIOS_BITWARDEN_SESSION_READY=false`
  - `BW_SESSION_PRESENT=false`
  - `LOCAL_CREDENTIAL_PRESENT=true`
  - `SAFE_NEXT_ACTION=re-register local credential`
- The helper must never crash on malformed DPAPI blobs (fail-closed behavior).
