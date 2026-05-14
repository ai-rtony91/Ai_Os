[CmdletBinding()]
param(
    [string]$LockRegistryPath = "automation/orchestration/locks/FILE_LOCK_REGISTRY_001.json"
)

$ErrorActionPreference = "Stop"

function Write-WarningLine {
    param([string]$Message)
    Write-Output ("REVIEW_REQUIRED: {0}" -f $Message)
}

if (-not (Test-Path -LiteralPath $LockRegistryPath)) {
    Write-WarningLine "Lock registry not found: $LockRegistryPath"
    return
}

try {
    $lockData = Get-Content -LiteralPath $LockRegistryPath -Raw | ConvertFrom-Json
}
catch {
    Write-WarningLine "Lock registry JSON could not be parsed."
    return
}

$locks = @()
if ($lockData.PSObject.Properties.Name -contains "locks") {
    $locks = @($lockData.locks)
}
else {
    $locks = @($lockData)
}

$warnings = New-Object System.Collections.Generic.List[string]
$lockIds = New-Object System.Collections.Generic.HashSet[string]

foreach ($lock in $locks) {
    $lockId = [string]$lock.lock_id
    $workerId = [string]$lock.worker_id
    $lockedPaths = @($lock.locked_paths)

    if ([string]::IsNullOrWhiteSpace($lockId) -or $lockId -like "*PLACEHOLDER*") {
        $warnings.Add("Lock has malformed lock_id: $lockId") | Out-Null
    }
    elseif (-not $lockIds.Add($lockId)) {
        $warnings.Add("Duplicate lock_id detected: $lockId") | Out-Null
    }

    if ([string]::IsNullOrWhiteSpace($workerId) -or $workerId -like "*PLACEHOLDER*") {
        $warnings.Add("Lock has missing worker_id.") | Out-Null
    }

    if ($lockedPaths.Count -eq 0) {
        $warnings.Add("Lock has empty locked_paths array: $lockId") | Out-Null
    }
}

if ($warnings.Count -eq 0) {
    Write-Output "PASS: Lock registry integrity checks passed."
}
else {
    foreach ($warning in $warnings) {
        Write-WarningLine $warning
    }
}
