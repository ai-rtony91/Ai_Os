param(
    [Parameter(Mandatory = $true)][string]$Title,
    [Parameter(Mandatory = $true)][string]$Body,
    [Parameter(Mandatory = $true)][string]$CommitMessage,
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$branch = git branch --show-current

Write-Host "COPY START - Complete-AiOsPhasePr.DRY_RUN.ps1"
Write-Host "AI_OS Phase PR Finisher" -ForegroundColor Cyan
Write-Host "branch: $branch"
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"

if ($branch -eq "main") {
    throw "Refusing to finish PR from main. Create a phase branch first."
}

Write-Host ""
Write-Host "STEP 1 - status"
git status --short --branch

Write-Host ""
Write-Host "STEP 2 - add all safe changes"
Write-Host "Would run: $pathsToAdd = @("automation", "docs", ".github")
foreach ($p in $pathsToAdd) {
    if (Test-Path $p) {
        git add $p
    } else {
        Write-Host "Skip missing path: $p"
    }
}"

if ($Apply) {
    $pathsToAdd = @("automation", "docs", ".github")
foreach ($p in $pathsToAdd) {
    if (Test-Path $p) {
        git add $p
    } else {
        Write-Host "Skip missing path: $p"
    }
}
}

Write-Host ""
Write-Host "STEP 3 - commit"
Write-Host "Would commit: $CommitMessage"

if ($Apply) {
    $hasChanges = @(git status --short).Count -gt 0
    if ($hasChanges) {
        git commit -m $CommitMessage
    } else {
        Write-Host "No changes to commit."
    }
}

Write-Host ""
Write-Host "STEP 4 - push branch"
if ($Apply) {
    git push -u origin $branch
} else {
    Write-Host "Would push: $branch"
}

Write-Host ""
Write-Host "STEP 5 - create PR"
if ($Apply) {
    gh pr create --title $Title --body $Body
} else {
    Write-Host "Would create PR:"
    Write-Host "title: $Title"
    Write-Host "body: $Body"
}

Write-Host ""
Write-Host "Commit performed: $(if ($Apply) { 'MAYBE' } else { 'NO' })"
Write-Host "Push performed: $(if ($Apply) { 'YES' } else { 'NO' })"
Write-Host "COPY END - Complete-AiOsPhasePr.DRY_RUN.ps1"

