[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$credentialDirectory = Join-Path -Path $env:LOCALAPPDATA -ChildPath "AIOS\Security"
$credentialPath = Join-Path -Path $credentialDirectory -ChildPath "bitwarden-master-password.dpapi"

$bwSession = $env:BW_SESSION
if ($null -ne $bwSession -and $bwSession.Trim().Length -gt 0) {
    Write-Output "AIOS_BITWARDEN_SESSION_READY=true"
    Write-Output "BW_SESSION_PRESENT=true"
    Write-Output ("LOCAL_CREDENTIAL_PRESENT={0}" -f (Test-Path -LiteralPath $credentialPath).ToString().ToLower())
    Write-Output "SAFE_NEXT_ACTION=ready"
    return
}

$localCredentialPresent = Test-Path -LiteralPath $credentialPath
if (-not $localCredentialPresent) {
    Write-Output "AIOS_BITWARDEN_SESSION_READY=false"
    Write-Output "BW_SESSION_PRESENT=false"
    Write-Output "LOCAL_CREDENTIAL_PRESENT=false"
    Write-Output "SAFE_NEXT_ACTION=run Register-AiosBitwardenLocalCredential.ps1 once"
    return
}

$sessionReady = $false
$bwSessionPresent = $false
$securePassword = $null
$bstr = [IntPtr]::Zero
$plainPassword = [string]::Empty

try {
    $securePassword = Get-Content -Path $credentialPath -Raw -ErrorAction Stop | ConvertTo-SecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
    try {
        $plainPassword = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
        $bstr = [IntPtr]::Zero
    }

    if (-not [string]::IsNullOrWhiteSpace($plainPassword)) {
        $env:BW_PASSWORD = $plainPassword
        try {
            $rawSession = (& bw unlock --passwordenv BW_PASSWORD --raw) 2>$null
            if (-not [string]::IsNullOrWhiteSpace([string]$rawSession)) {
                $env:BW_SESSION = [string]$rawSession.Trim()
                $bwSessionPresent = -not [string]::IsNullOrWhiteSpace($env:BW_SESSION)
                $sessionReady = $bwSessionPresent
            }
        } catch {
            $sessionReady = $false
            $bwSessionPresent = $false
        }
    }
} finally {
    $plainPassword = [string]::Empty
    if (Test-Path Env:BW_PASSWORD) {
        Remove-Item Env:BW_PASSWORD -ErrorAction SilentlyContinue
    }
}

if ($sessionReady) {
    Write-Output "AIOS_BITWARDEN_SESSION_READY=true"
} else {
    Write-Output "AIOS_BITWARDEN_SESSION_READY=false"
}

Write-Output ("BW_SESSION_PRESENT={0}" -f $bwSessionPresent.ToString().ToLower())
Write-Output ("LOCAL_CREDENTIAL_PRESENT={0}" -f $localCredentialPresent.ToString().ToLower())
if ($sessionReady) {
    Write-Output "SAFE_NEXT_ACTION=runtime session is ready"
} else {
    Write-Output "SAFE_NEXT_ACTION=verify local credential and rerun Register-AiosBitwardenLocalCredential.ps1 if needed"
}
