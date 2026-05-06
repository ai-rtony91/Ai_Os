[CmdletBinding()]
param(
    [string]$RepoRoot = 'C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN'
)

$ErrorActionPreference = 'Stop'
$Task = 'AI_OS folder-purpose coverage check'
$Mode = 'DRY_RUN'
$FilesInspected = @()
$Errors = @()
$Unknowns = @()
$GitStatus = 'UNKNOWN'
$ResolvedRepoRoot = 'UNKNOWN'

$RelativePaths = @(
    'agent\README_FOLDER_PURPOSE.txt',
    'apps\README_FOLDER_PURPOSE.txt',
    'automation\README_FOLDER_PURPOSE.txt',
    'docs\README_FOLDER_PURPOSE.txt',
    'inputs\README_FOLDER_PURPOSE.txt',
    'internal\README_FOLDER_PURPOSE.txt',
    'Reports\README_FOLDER_PURPOSE.txt',
    'services\README_FOLDER_PURPOSE.txt'
)

try {
    $ResolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
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

$Results = foreach ($RelativePath in $RelativePaths) {
    $FullPath = Join-Path $ResolvedRepoRoot $RelativePath
    $FilesInspected += $RelativePath
    [pscustomobject]@{
        Path = $RelativePath
        Status = if (Test-Path -LiteralPath $FullPath -PathType Leaf) { 'PRESENT' } else { 'MISSING' }
    }
}

Write-Output "Task: $Task"
Write-Output "Mode: $Mode"
Write-Output "Repo root: $ResolvedRepoRoot"
Write-Output "Git status: $GitStatus"
Write-Output "Files inspected: $($FilesInspected -join '; ')"
Write-Output "Folder purpose coverage:"
foreach ($Result in $Results) {
    Write-Output "$($Result.Path): $($Result.Status)"
}
Write-Output "Would create: NONE"
Write-Output "Would change: NONE"
Write-Output "Would delete: NONE"
Write-Output "Errors: $(if ($Errors.Count) { $Errors -join '; ' } else { 'NONE' })"
Write-Output "Unknowns: $(if ($Unknowns.Count) { $Unknowns -join '; ' } else { 'NONE' })"
Write-Output "Protected action involved: NO"
Write-Output "Approval required: NO for DRY_RUN read-only check; YES before creating missing notes"
Write-Output "Next safe action: Review any MISSING result and use a separate create-only APPLY approval if a note should be created."
