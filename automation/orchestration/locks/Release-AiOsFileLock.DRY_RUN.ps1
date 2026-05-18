param(
    [string]$WorkerId = "AIOS-WORKER-DRY-RUN",
    [string]$LockId = "",
    [string]$Path = "",
    [string]$Reason = "DRY_RUN release simulation",
    [string]$RegistryPath = (Join-Path $PSScriptRoot "FILE_LOCK_REGISTRY.example.json"),
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Read-AiOsJsonFile {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Registry file not found: $Path"
    }

    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function ConvertTo-AiOsPathKey {
    param([AllowNull()][string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return ""
    }

    $key = $Path.Replace("\", "/").Trim()
    while ($key.StartsWith("./")) {
        $key = $key.Substring(2)
    }
    return $key.TrimEnd("/")
}

function Test-AiOsPathOverlap {
    param(
        [string]$LeftPath,
        [string]$RightPath
    )

    $left = ConvertTo-AiOsPathKey -Path $LeftPath
    $right = ConvertTo-AiOsPathKey -Path $RightPath

    if ([string]::IsNullOrWhiteSpace($left) -or [string]::IsNullOrWhiteSpace($right)) {
        return $false
    }

    return ($left -eq $right -or $left.StartsWith("$right/") -or $right.StartsWith("$left/"))
}

$registry = Read-AiOsJsonFile -Path $RegistryPath
$locks = @($registry.locks)
$matches = @()
$normalizedPath = ConvertTo-AiOsPathKey -Path $Path

foreach ($lock in $locks) {
    $lockIdMatches = (-not [string]::IsNullOrWhiteSpace($LockId) -and $lock.lock_id -eq $LockId)
    $workerMatches = ($lock.worker_id -eq $WorkerId)
    $pathMatches = $false

    if (-not [string]::IsNullOrWhiteSpace($normalizedPath)) {
        foreach ($claimedPath in @($lock.claimed_paths)) {
            if (Test-AiOsPathOverlap -LeftPath $normalizedPath -RightPath $claimedPath) {
                $pathMatches = $true
            }
        }
    }

    if ($lockIdMatches -or ($workerMatches -and $pathMatches)) {
        $matches += $lock
    }
}

$releaseStatus = "SIMULATED_NOT_FOUND"
if ($matches.Count -eq 1) {
    if ($matches[0].status -eq "ACTIVE") {
        $releaseStatus = "SIMULATED_RELEASE_ALLOWED_AFTER_OPERATOR_APPROVAL"
    } else {
        $releaseStatus = "SIMULATED_NO_ACTIVE_LOCK_TO_RELEASE"
    }
} elseif ($matches.Count -gt 1) {
    $releaseStatus = "SIMULATED_REVIEW_REQUIRED_MULTIPLE_MATCHES"
}

$releasePreview = @()
foreach ($match in $matches) {
    $releasePreview += [pscustomobject]@{
        lock_id = $match.lock_id
        worker_id = $match.worker_id
        packet_id = $match.packet_id
        current_status = $match.status
        simulated_status = "RELEASED"
        simulated_released_at = (Get-Date).ToString("s")
        simulated_release_reason = $Reason
    }
}

$result = [pscustomobject]@{
    task = "Simulate AI_OS file lock release"
    mode = "DRY_RUN"
    registry_path = $RegistryPath
    release_status = $releaseStatus
    match_count = $matches.Count
    release_preview = $releasePreview
    safety = [pscustomobject]@{
        writes_performed = 0
        commits_performed = 0
        pushes_performed = 0
        broker_or_live_api_work = "NO"
    }
    next_safe_action = "Use an operator-approved APPLY workflow before changing any real lock record."
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AI_OS File Lock Release Simulation"
Write-Host "Mode: DRY_RUN"
Write-Host "Worker: $WorkerId"
Write-Host "LockId: $LockId"
Write-Host "Path: $normalizedPath"
Write-Host "Result: $releaseStatus"
Write-Host ""

if ($matches.Count -eq 0) {
    Write-Host "No matching lock was found."
} else {
    Write-Host "Matched locks:"
    foreach ($preview in $releasePreview) {
        Write-Host "  - $($preview.lock_id): $($preview.current_status) would become $($preview.simulated_status)"
    }
}

Write-Host ""
Write-Host "Validator note: no files were changed; this was simulation-only."
Write-Host "Next safe action: $($result.next_safe_action)"
