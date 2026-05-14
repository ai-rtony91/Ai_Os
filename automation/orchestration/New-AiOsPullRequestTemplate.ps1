[CmdletBinding()]
param(
    [string]$Title = "AI_OS automated update",

    [string]$Purpose = "Automated orchestration improvement.",

    [string]$BranchName = ""
)

if ([string]::IsNullOrWhiteSpace($BranchName)) {
    $BranchName = git branch --show-current
}

$template = @"
# $Title

## Purpose
$Purpose

## Safety
- validator chain enforced
- blocked paths enforced
- dry-run workflow validated
- no runtime/service modification

## Automated Checks
- commit package preview
- validator chain
- git clean state
- blocked path detection
- syntax validation

## Branch
$BranchName
"@

Write-Host ""
Write-Host "AI_OS Pull Request Template"
Write-Host ""
Write-Host $template

$templatePath = "automation/orchestration/PULL_REQUEST_TEMPLATE.md"

$template | Out-File -FilePath $templatePath -Encoding utf8

Write-Host ""
Write-Host "Saved:"
Write-Host $templatePath