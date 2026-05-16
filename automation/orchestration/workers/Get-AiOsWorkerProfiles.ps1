param(
    [string]$ProfilesPath = "automation/orchestration/workers/AIOS_WORKER_PROFILES.json"
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Resolve-AiOsPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return Join-Path (Get-Location).Path $Path
}

$scriptName = Split-Path -Leaf $PSCommandPath
$profilesFullPath = Resolve-AiOsPath -Path $ProfilesPath
if (-not (Test-Path -LiteralPath $profilesFullPath -PathType Leaf)) {
    throw "Worker profiles file not found: $profilesFullPath"
}

$profiles = Get-Content -LiteralPath $profilesFullPath -Raw | ConvertFrom-Json
$workers = @($profiles.workers)

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Worker Profiles" -ForegroundColor Cyan
Write-Host "Mode: PREVIEW - print only"
Write-Host "Profiles: $profilesFullPath"
Write-Host "Worker count: $($workers.Count)"
Write-Host ""
Write-Host "Workers:" -ForegroundColor Yellow
foreach ($worker in $workers) {
    Write-Host "  worker_id: $($worker.worker_id)"
    Write-Host "  title: $($worker.display_title)"
    Write-Host "  type: $($worker.worker_type)"
    Write-Host "  path: $($worker.default_path)"
    Write-Host "  branch: $($worker.default_branch)"
    Write-Host ""
}

Write-Host "Overlapping restrictions:" -ForegroundColor Yellow
foreach ($worker in $workers) {
    $blockedOverlap = @($worker.cannot_overlap_with)
    if ($blockedOverlap.Count -gt 0) {
        Write-Host "  $($worker.worker_id): cannot overlap with $($blockedOverlap -join ', ')"
    }
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
