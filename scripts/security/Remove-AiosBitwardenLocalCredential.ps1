[CmdletBinding()]
param(
    [switch] $ClearSession
)

$ErrorActionPreference = "Stop"

$credentialDirectory = Join-Path -Path $env:LOCALAPPDATA -ChildPath "AIOS\Security"
$credentialPath = Join-Path -Path $credentialDirectory -ChildPath "bitwarden-master-password.dpapi"

$removed = $false

try {
    if (Test-Path -LiteralPath $credentialPath) {
        Remove-Item -LiteralPath $credentialPath -Force
    }

    $removed = -not (Test-Path -LiteralPath $credentialPath)
} catch {
    $removed = $false
}

if (Test-Path Env:BW_PASSWORD) {
    Remove-Item Env:BW_PASSWORD -ErrorAction SilentlyContinue
}

if ($ClearSession -and (Test-Path Env:BW_SESSION)) {
    Remove-Item Env:BW_SESSION -ErrorAction SilentlyContinue
}

Write-Output ("AIOS_BITWARDEN_LOCAL_CREDENTIAL_REMOVED={0}" -f $removed.ToString().ToLower())
Write-Output "BW_PASSWORD_PRESENT=false"
