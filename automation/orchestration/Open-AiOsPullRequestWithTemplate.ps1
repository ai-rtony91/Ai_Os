[CmdletBinding()]
param(
    [string]$Title = "",
    [string]$Purpose = "AI_OS orchestration update."
)

$ErrorActionPreference = "Stop"

$branch = git branch --show-current

if ($branch -eq "main") {
    throw "Do not open a PR from main. Switch to a feature branch first."
}

if ([string]::IsNullOrWhiteSpace($Title)) {
    $Title = ($branch -replace "-", " ")
    $Title = (Get-Culture).TextInfo.ToTitleCase($Title)
}

$changedFiles = @(git diff --name-only main...HEAD)

$changedFileText = if ($changedFiles.Count -eq 0) {
    "- none detected yet"
}
else {
    ($changedFiles | ForEach-Object { "- $_" }) -join "`n"
}

$body = @"
$Title

Purpose:
$Purpose

Changed files:
$changedFileText

Safety:
- orchestration workflow protected
- validator chain expected before merge
- blocked paths must remain untouched
- no runtime/app/service changes unless explicitly approved

Branch:
$branch
"@

$bodyPath = "automation/orchestration/PR_BODY_LAST_GENERATED.md"
$body | Out-File -FilePath $bodyPath -Encoding utf8
$body | Set-Clipboard

Write-Host "PR body copied to clipboard."
Write-Host "PR body saved to: $bodyPath"
Write-Host "Paste it into the GitHub PR description box with CTRL+V."
Write-Host ""
Write-Host "Opening PR page:"
Write-Host "https://github.com/ai-rtony91/Ai_Os/pull/new/$branch"

Start-Process "https://github.com/ai-rtony91/Ai_Os/pull/new/$branch"