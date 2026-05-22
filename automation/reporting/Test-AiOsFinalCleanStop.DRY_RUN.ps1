[CmdletBinding()]
param(
    [string]$RepoRoot = 'C:\Dev\Ai.Os'
)

$ErrorActionPreference = 'Stop'
$Task = 'AI_OS final clean-stop readiness check'
$Mode = 'DRY_RUN'
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

$StatusLines = @()
if ($GitStatus -ne 'UNKNOWN') {
    $StatusLines = @($GitStatus -split "(`r`n|`n|`r)" | Where-Object { $_ -ne '' })
}

$HasOnlyBranchLine = ($StatusLines.Count -eq 1 -and $StatusLines[0] -like '## *')
$Pass = ($Errors.Count -eq 0 -and $Unknowns.Count -eq 0 -and $HasOnlyBranchLine)

Write-Output "Task: $Task"
Write-Output "Mode: $Mode"
Write-Output "Repo root: $ResolvedRepoRoot"
Write-Output "Git status: $GitStatus"
Write-Output "Clean stop result: $(if ($Pass) { 'PASS' } else { 'FAIL' })"
Write-Output "Files inspected: $($FilesInspected -join '; ')"
Write-Output "Would create: NONE"
Write-Output "Would change: NONE"
Write-Output "Would delete: NONE"
Write-Output "Errors: $(if ($Errors.Count) { $Errors -join '; ' } else { 'NONE' })"
Write-Output "Unknowns: $(if ($Unknowns.Count) { $Unknowns -join '; ' } else { 'NONE' })"
Write-Output "Protected action involved: NO"
Write-Output "Approval required: NO for DRY_RUN read-only check; YES before any APPLY action"
Write-Output "Next safe action: If result is FAIL, inspect git status manually before stopping work."
