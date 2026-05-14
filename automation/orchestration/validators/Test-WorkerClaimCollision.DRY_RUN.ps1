[CmdletBinding()]
param(
    [string]$ClaimRegistryPath = "automation/orchestration/claims/WORKER_CLAIM_REGISTRY_001.json"
)

$ErrorActionPreference = "Stop"

function Write-WarningLine {
    param([string]$Message)
    Write-Output ("REVIEW_REQUIRED: {0}" -f $Message)
}

if (-not (Test-Path -LiteralPath $ClaimRegistryPath)) {
    Write-WarningLine "Claim registry not found: $ClaimRegistryPath"
    return
}

try {
    $claimData = Get-Content -LiteralPath $ClaimRegistryPath -Raw | ConvertFrom-Json
}
catch {
    Write-WarningLine "Claim registry JSON could not be parsed."
    return
}

$claims = @()
if ($claimData.PSObject.Properties.Name -contains "claims") {
    $claims = @($claimData.claims)
}
else {
    $claims = @($claimData)
}

$warnings = New-Object System.Collections.Generic.List[string]
$pathOwners = @{}
$packetIds = New-Object System.Collections.Generic.HashSet[string]

foreach ($claim in $claims) {
    $workerId = [string]$claim.worker_id
    $packetId = [string]$claim.packet_id
    $status = [string]$claim.claim_status
    $paths = @($claim.assigned_paths)

    if ([string]::IsNullOrWhiteSpace($workerId)) {
        $warnings.Add("Claim has missing worker_id.") | Out-Null
    }
    if ([string]::IsNullOrWhiteSpace($packetId) -or $packetId -like "*PLACEHOLDER*") {
        $warnings.Add("Claim has invalid packet reference: $packetId") | Out-Null
    }
    elseif (-not $packetIds.Add($packetId)) {
        $warnings.Add("Duplicate packet claim detected: $packetId") | Out-Null
    }
    if ($status -eq "expired") {
        $warnings.Add("Expired claim requires review: $packetId") | Out-Null
    }

    foreach ($path in $paths) {
        $normalizedPath = ([string]$path).Trim().Replace("\", "/")
        if ([string]::IsNullOrWhiteSpace($normalizedPath)) { continue }

        foreach ($existingPath in @($pathOwners.Keys)) {
            $overlaps = $normalizedPath.StartsWith($existingPath) -or $existingPath.StartsWith($normalizedPath)
            if ($overlaps -and $pathOwners[$existingPath] -ne $workerId) {
                $warnings.Add("Overlapping worker assignment: $normalizedPath conflicts with $existingPath") | Out-Null
            }
        }

        if ($pathOwners.ContainsKey($normalizedPath) -and $pathOwners[$normalizedPath] -ne $workerId) {
            $warnings.Add("Duplicate path ownership: $normalizedPath") | Out-Null
        }
        else {
            $pathOwners[$normalizedPath] = $workerId
        }
    }
}

if ($warnings.Count -eq 0) {
    Write-Output "PASS: No worker claim collisions detected."
}
else {
    foreach ($warning in $warnings) {
        Write-WarningLine $warning
    }
}
