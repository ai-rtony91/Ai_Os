param(
    [Parameter(Mandatory = $true)][string]$BranchName
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "COPY START - Start-AiOsPhaseBranch.ps1"
Write-Host "AI_OS New Phase Starter" -ForegroundColor Cyan
Write-Host "branch_name: $BranchName"

$current = git branch --show-current

if ($current -ne "main") {
    Write-Host "Switching to main..."
    git checkout main
}

Write-Host "Pulling latest main..."
git pull

Write-Host "Creating phase branch..."
git checkout -b $BranchName

Write-Host ""
Write-Host "Phase branch ready:"
git status --short --branch

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Start-AiOsPhaseBranch.ps1"
