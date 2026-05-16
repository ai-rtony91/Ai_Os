param(
    [Parameter(Mandatory = $true)][string]$Title,
    [Parameter(Mandatory = $true)][string]$Body,
    [string]$BaseBranch = "main",
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "COPY START — Open-AiOsPullRequest.DRY_RUN.ps1"
Write-Host "AI_OS PR Create Gate" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"

$branch = git branch --show-current
$status = @(git status --short)

Write-Host "Branch: $branch"
Write-Host "Base: $BaseBranch"

if ($branch -eq $BaseBranch) {
    throw "Blocked: do not create PR from base branch."
}

if ($status | Where-Object { $_ -match "server.py" }) {
    throw "Blocked: server.py is uncommitted and must not be included."
}

git diff --check
if ($LASTEXITCODE -ne 0) {
    throw "Blocked: git diff --check failed."
}

if ($Apply) {
    gh pr create --base $BaseBranch --head $branch --title $Title --body $Body
    Write-Host "PR create attempted: YES"
} else {
    Write-Host "PR create attempted: NO"
    Write-Host "Would run: gh pr create --base $BaseBranch --head $branch --title `"$Title`" --body `"$Body`""
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END — Open-AiOsPullRequest.DRY_RUN.ps1"
