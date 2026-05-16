param(
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "COPY START - Invoke-AiOsSelfHeal.DRY_RUN.ps1"
Write-Host "AI_OS Self-Healing Runtime" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"

$branch = git branch --show-current
$status = @(git status --short)

Write-Host ""
Write-Host "CHECKS"
Write-Host "branch: $branch"
Write-Host "changes: $($status.Count)"

$actions = @()

if ($branch -ne "main") {
    $actions += "Return to main branch."
}

$requiredFolders = @(
    "automation/orchestration/work_packets/active",
    "automation/orchestration/work_packets/blocked",
    "automation/orchestration/work_packets/complete",
    "automation/orchestration/approvals",
    "automation/orchestration/memory"
)

foreach ($folder in $requiredFolders) {
    if (-not (Test-Path $folder)) {
        $actions += "Create missing folder: $folder"

        if ($Apply) {
            New-Item -ItemType Directory -Force -Path $folder | Out-Null
        }
    }
}

if ($status.Count -gt 0) {
    $actions += "Working tree has changes. Do not auto-fix; human review needed."
}

if ($actions.Count -eq 0) {
    $actions += "No safe fixes needed."
}

Write-Host ""
Write-Host "SELF-HEAL RESULT"
foreach ($action in $actions) {
    Write-Host "- $action"
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Invoke-AiOsSelfHeal.DRY_RUN.ps1"
