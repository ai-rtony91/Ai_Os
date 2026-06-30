[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

try {
    & bw lock 2>&1 | Out-Null
} catch {
    # Intentionally keep output constrained to safe status lines only.
}

if (Test-Path Env:BW_SESSION) {
    Remove-Item Env:BW_SESSION -ErrorAction SilentlyContinue
}

Write-Output "AIOS_BITWARDEN_SESSION_READY=false"
Write-Output "BW_SESSION_PRESENT=false"
