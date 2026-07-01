[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$credentialDirectory = Join-Path -Path $env:LOCALAPPDATA -ChildPath "AIOS\Security"
$credentialPath = Join-Path -Path $credentialDirectory -ChildPath "bitwarden-master-password.dpapi"

$bwSession = $env:BW_SESSION
if (-not [string]::IsNullOrWhiteSpace($bwSession)) {
    Write-Output "AIOS_BITWARDEN_SESSION_READY=true"
    Write-Output "BW_SESSION_PRESENT=true"
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
$encryptedCredential = [string]::Empty

try {
    $encryptedCredential = Get-Content -LiteralPath $credentialPath -Raw -ErrorAction Stop
    if ($null -eq $encryptedCredential) {
        $encryptedCredential = [string]::Empty
    }
    $encryptedCredential = ([string]$encryptedCredential).Trim()
    $encryptedCredential = $encryptedCredential.Trim([char]0xFEFF)

    if ([string]::IsNullOrWhiteSpace($encryptedCredential)) {
        Write-Output "AIOS_BITWARDEN_SESSION_READY=false"
        Write-Output "BW_SESSION_PRESENT=false"
        Write-Output "LOCAL_CREDENTIAL_PRESENT=true"
        Write-Output "SAFE_NEXT_ACTION=re-register local credential"
        return
    }

    try {
        $securePassword = ConvertTo-SecureString -String $encryptedCredential -ErrorAction Stop
    } catch {
        Write-Output "AIOS_BITWARDEN_SESSION_READY=false"
        Write-Output "BW_SESSION_PRESENT=false"
        Write-Output "LOCAL_CREDENTIAL_PRESENT=true"
        Write-Output "SAFE_NEXT_ACTION=re-register local credential"
        return
    }

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
    Write-Output "BW_SESSION_PRESENT=true"
    return
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
