[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$status = [ordered]@{
    AIOS_BITWARDEN_SESSION_READY = $false
    BW_SESSION_PRESENT           = $false
}

try {
    $statusRaw = & bw status 2>&1
    if ($LASTEXITCODE -ne 0) { throw "bw status failed" }

    $statusObject = $statusRaw | ConvertFrom-Json -ErrorAction Stop
    if ($statusObject.status -eq "unlocked") {
        if ($env:BW_SESSION) {
            $status.BW_SESSION_PRESENT = $true
            $status.AIOS_BITWARDEN_SESSION_READY = $true
        }
    } elseif ($statusObject.status -eq "locked") {
        $unlockedSession = (& bw unlock --raw 2>&1 | Out-String).Trim()
        if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($unlockedSession)) {
            $env:BW_SESSION = $unlockedSession
            $status.BW_SESSION_PRESENT = $true
            $status.AIOS_BITWARDEN_SESSION_READY = $true
        }
    }
} catch {
    # Intentionally keep output constrained to safe status lines only.
}

Write-Output ("AIOS_BITWARDEN_SESSION_READY={0}" -f ($status.AIOS_BITWARDEN_SESSION_READY.ToString().ToLowerInvariant()))
Write-Output ("BW_SESSION_PRESENT={0}" -f ($status.BW_SESSION_PRESENT.ToString().ToLowerInvariant()))
