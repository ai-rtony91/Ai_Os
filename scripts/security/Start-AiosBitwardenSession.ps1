$bwSession = $env:BW_SESSION
if ($null -ne $bwSession -and $bwSession.Trim().Length -gt 0) {
    Write-Output "AIOS_BITWARDEN_SESSION_READY=true"
    Write-Output "BW_SESSION_PRESENT=true"
    return
}

$rawSession = ""
try {
    $rawSession = bw unlock --raw
} catch {
    $rawSession = ""
}

if ($null -eq $rawSession -or [string]::IsNullOrWhiteSpace([string]$rawSession)) {
    Write-Output "AIOS_BITWARDEN_SESSION_READY=false"
    Write-Output "BW_SESSION_PRESENT=false"
    return
}

$candidateSession = [string]$rawSession
$env:BW_SESSION = $candidateSession.Trim()
if ([string]::IsNullOrWhiteSpace($env:BW_SESSION)) {
    Write-Output "AIOS_BITWARDEN_SESSION_READY=false"
    Write-Output "BW_SESSION_PRESENT=false"
} else {
    Write-Output "AIOS_BITWARDEN_SESSION_READY=true"
    Write-Output "BW_SESSION_PRESENT=true"
}
