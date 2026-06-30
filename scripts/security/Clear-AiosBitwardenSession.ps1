[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

if (Test-Path Env:BW_PASSWORD) {
    Remove-Item Env:BW_PASSWORD -ErrorAction SilentlyContinue
}
if (Test-Path Env:BW_SESSION) {
    Remove-Item Env:BW_SESSION -ErrorAction SilentlyContinue
}

try {
    & bw lock 2>$null | Out-Null
} catch {
    # No-op: keep status output constrained.
}

Write-Output "AIOS_BITWARDEN_SESSION_READY=false"
Write-Output "BW_SESSION_PRESENT=false"
Write-Output "BW_PASSWORD_PRESENT=false"
