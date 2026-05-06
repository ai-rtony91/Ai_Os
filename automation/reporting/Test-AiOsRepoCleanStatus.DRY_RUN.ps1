[CmdletBinding()]
param(
    [string]$RepoRoot = 'C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN'
)

$ErrorActionPreference = 'Stop'
$Task = 'AI_OS repo clean-status check'
$Mode = 'DRY_RUN'
$ExpectedStatus = '## main...origin/main'
$FilesInspected = @()
$Errors = @()
$Unknowns = @()
$GitStatus = 'UNKNOWN'
$ResolvedRepoRoot = 'UNKNOWN'

try {
    $ResolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
    $FilesInspected += $ResolvedRepoRoot
    $GitStatusLines = @(& git -C $ResolvedRepoRoot status --short --branch 2>&1)
    if ($LASTEXITCODE -ne 0) {
        $Errors += "git status failed: $($GitStatusLines -join ' ')"
    }
    elseif ($GitStatusLines.Count -eq 0) {
        $Unknowns += 'git status returned no output.'
    }
    else {
        $GitStatus = ($GitStatusLines -join [Environment]::NewLine)
    }
}
catch {
    $Errors += $_.Exception.Message
}

$IsExpectedCleanStatus = ($GitStatus -eq $ExpectedStatus)

Write-Output "Task: $Task"
Write-Output "Mode: $Mode"
Write-Output "Repo root: $ResolvedRepoRoot"
Write-Output "Git status: $GitStatus"
Write-Output "Expected clean status: $ExpectedStatus"
Write-Output "Status equals expected: $IsExpectedCleanStatus"
Write-Output "Files inspected: $($FilesInspected -join '; ')"
Write-Output "Would create: NONE"
Write-Output "Would change: NONE"
Write-Output "Would delete: NONE"
Write-Output "Errors: $(if ($Errors.Count) { $Errors -join '; ' } else { 'NONE' })"
Write-Output "Unknowns: $(if ($Unknowns.Count) { $Unknowns -join '; ' } else { 'NONE' })"
Write-Output "Protected action involved: NO"
Write-Output "Approval required: NO for DRY_RUN read-only check; YES before any APPLY action"
Write-Output "Next safe action: Review this output and stop if git status is not exactly ## main...origin/main."
