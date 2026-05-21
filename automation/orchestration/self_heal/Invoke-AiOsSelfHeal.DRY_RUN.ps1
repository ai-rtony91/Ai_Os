param(
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "COPY START - Invoke-AiOsSelfHeal.DRY_RUN.ps1"
Write-Host "AI_OS Self-Healing Runtime" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN"

$branch = git branch --show-current
$status = @(git status --short)

Write-Host ""
Write-Host "CHECKS"
Write-Host "branch: $branch"
Write-Host "changes: $($status.Count)"

$actions = @()
$requestedFolderMutations = @()

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
        $requestedFolderMutations += [pscustomobject]@{
            folder = $folder
            reason = "Required self-heal folder is missing."
            skipped_remediation_path = "folder creation command for the missing self-heal path"
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
if ($requestedFolderMutations.Count -gt 0) {
    foreach ($mutation in $requestedFolderMutations) {
        Write-Host "Requested mutation: create self-heal folder"
        Write-Host "Folder path: $($mutation.folder)"
        Write-Host "Why: $($mutation.reason)"
        Write-Host "Skipped remediation path: $($mutation.skipped_remediation_path)"
        Write-Host "Mutation skipped: YES"
        Write-Host "Folder created: NO"
    }
}
else {
    Write-Host "Requested mutation: create self-heal folder"
    Write-Host "Why: no required self-heal folder is missing."
    Write-Host "Skipped remediation path: none"
    Write-Host "Mutation skipped: YES - no missing self-heal folders were detected."
    Write-Host "Folder created: NO"
}

Write-Host "Runtime modified: NO"
Write-Host "Files changed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "Next safe action: Request a separately approved APPLY repair if missing folders should be created."
Write-Host "COPY END - Invoke-AiOsSelfHeal.DRY_RUN.ps1"
