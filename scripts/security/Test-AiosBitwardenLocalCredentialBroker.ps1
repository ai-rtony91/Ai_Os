[CmdletBinding()]
param(
    [switch] $ValidateUnlock
)

$ErrorActionPreference = "Stop"

$credentialDirectory = Join-Path -Path $env:LOCALAPPDATA -ChildPath "AIOS\Security"
$credentialPath = Join-Path -Path $credentialDirectory -ChildPath "bitwarden-master-password.dpapi"

$credentialPresent = Test-Path -LiteralPath $credentialPath
$validateAttempted = $false
$validateSuccess = $false
$bwSessionPresent = $false

if ($ValidateUnlock -and $credentialPresent) {
    $validateAttempted = $true
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
                    $bwSessionPresent = $true
                    $validateSuccess = $true
                }
            } catch {
                $validateSuccess = $false
            }
        }
    } finally {
        if (Test-Path Env:BW_PASSWORD) {
            Remove-Item Env:BW_PASSWORD -ErrorAction SilentlyContinue
        }
    }
}

Write-Output ("AIOS_BITWARDEN_LOCAL_CREDENTIAL_PRESENT={0}" -f $credentialPresent.ToString().ToLower())
Write-Output ("VALIDATE_UNLOCK_ATTEMPTED={0}" -f $validateAttempted.ToString().ToLower())
Write-Output ("VALIDATE_UNLOCK_SUCCESS={0}" -f $validateSuccess.ToString().ToLower())
Write-Output ("BW_SESSION_PRESENT={0}" -f $bwSessionPresent.ToString().ToLower())
