param(
    [Parameter(Mandatory = $true)][string]$Title,
    [string]$Body = "",
    [Parameter(Mandatory = $true)][string]$CommitMessage,
    [string]$BaseBranch = "main",
    [string[]]$IncludePaths = @(),
    [switch]$CreatePR,
    [switch]$MergePR,
    [switch]$Apply,
    [switch]$Preview,
    [switch]$AllowMain
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Write-AiOsSection {
    param([Parameter(Mandatory = $true)][string]$Title)

    Write-Host ""
    Write-Host "== $Title ==" -ForegroundColor Yellow
}

function Invoke-GitText {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $output = @(git @Arguments 2>&1)
    $exitCode = $LASTEXITCODE
    return [pscustomobject]@{
        Output = $output
        ExitCode = $exitCode
    }
}

function Get-ChangedPathFromPorcelainLine {
    param([Parameter(Mandatory = $true)][string]$Line)

    if ($Line.Length -lt 4) {
        return ""
    }

    $path = $Line.Substring(3)
    if ($path -match " -> ") {
        $parts = $path -split " -> "
        return $parts[$parts.Count - 1]
    }

    return $path
}

if ($Preview -and $Apply) {
    throw "Use either -Preview or -Apply, not both."
}

$scriptName = Split-Path -Leaf $PSCommandPath
$isApply = [bool]$Apply
$currentPath = (Get-Location).Path
$branchResult = Invoke-GitText -Arguments @("branch", "--show-current")
if ($branchResult.ExitCode -ne 0) {
    throw "Unable to read current branch: $($branchResult.Output -join ' ')"
}

$currentBranch = (($branchResult.Output | Select-Object -First 1) -as [string]).Trim()
if ([string]::IsNullOrWhiteSpace($currentBranch)) {
    throw "Current branch is empty or detached. Stop before save automation."
}

if ($currentBranch -eq $BaseBranch -and -not $AllowMain) {
    throw "Refusing to run on $BaseBranch without -AllowMain."
}

if ($currentBranch -eq "main" -and -not $AllowMain) {
    throw "Refusing to run on main without -AllowMain."
}

$statusResult = Invoke-GitText -Arguments @("status", "--short", "--branch")
$porcelainResult = Invoke-GitText -Arguments @("status", "--porcelain")
$changedPaths = @($porcelainResult.Output | ForEach-Object { Get-ChangedPathFromPorcelainLine -Line ([string]$_) } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$pathsToStage = if ($IncludePaths.Count -gt 0) { @($IncludePaths) } else { @($changedPaths) }
$bodyText = if ([string]::IsNullOrWhiteSpace($Body)) { "Automated AI_OS save package from Submit-AiOsWork.ps1." } else { $Body }

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS GitHub Save Automation" -ForegroundColor Cyan
Write-Host "Mode: $(if ($isApply) { 'APPLY' } else { 'PREVIEW - no git state changes' })"
Write-Host "Safety: no commit unless -Apply. No push unless -Apply. No PR unless -Apply -CreatePR. No merge unless -Apply -MergePR."

Write-AiOsSection -Title "Current Location"
Write-Host "Path: $currentPath"
Write-Host "Branch: $currentBranch"
Write-Host "BaseBranch: $BaseBranch"

Write-AiOsSection -Title "Git Status"
$statusResult.Output | ForEach-Object { Write-Host $_ }

Write-AiOsSection -Title "Package Scope"
if ($pathsToStage.Count -eq 0) {
    Write-Host "No changed paths detected."
} else {
    if ($IncludePaths.Count -gt 0) {
        Write-Host "IncludePaths provided. Staging only listed paths:"
    } else {
        Write-Host "IncludePaths not provided. Staging currently changed paths:"
    }
    $pathsToStage | ForEach-Object { Write-Host "  $_" }
}

Write-AiOsSection -Title "WHERE TO RUN NEXT"
Write-Host ("Visible tab/window: SAVE " + [char]0x00b7 + " git")
Write-Host "Path: $currentPath"
Write-Host "Preview:"
Write-Host "  powershell -ExecutionPolicy Bypass -File automation\orchestration\git\Submit-AiOsWork.ps1 -Preview -Title `"$Title`" -CommitMessage `"$CommitMessage`""
Write-Host "Apply:"
Write-Host "  powershell -ExecutionPolicy Bypass -File automation\orchestration\git\Submit-AiOsWork.ps1 -Apply -CreatePR -Title `"$Title`" -CommitMessage `"$CommitMessage`""

if (-not $isApply) {
    Write-Host ""
    Write-Host "Preview complete. Staged: NO"
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    Write-Host "PR created: NO"
    Write-Host "Merge performed: NO"
    Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
    exit 0
}

if ($pathsToStage.Count -gt 0) {
    Write-AiOsSection -Title "Stage"
    git add -- $pathsToStage
    if ($LASTEXITCODE -ne 0) {
        throw "git add failed."
    }
    Write-Host "Staged selected paths."
} else {
    Write-Host "No paths staged."
}

$stagedResult = Invoke-GitText -Arguments @("diff", "--cached", "--name-only")
$stagedPaths = @($stagedResult.Output | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })

if ($stagedPaths.Count -gt 0) {
    Write-AiOsSection -Title "Commit"
    git commit -m $CommitMessage
    if ($LASTEXITCODE -ne 0) {
        throw "git commit failed."
    }
    Write-Host "Commit performed: YES"
} else {
    Write-Host "No staged changes. Commit performed: NO"
}

Write-AiOsSection -Title "Push"
git push -u origin $currentBranch
if ($LASTEXITCODE -ne 0) {
    throw "git push failed."
}
Write-Host "Push performed: YES"

if ($CreatePR -or $MergePR) {
    $ghCommand = Get-Command gh -ErrorAction SilentlyContinue
    if ($null -eq $ghCommand) {
        throw "gh CLI not found. Push completed, but PR automation cannot continue."
    }

    Write-AiOsSection -Title "Pull Request"
    $existingPr = @(gh pr view --json url -q ".url" 2>$null)
    if ($LASTEXITCODE -eq 0 -and $existingPr.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace([string]$existingPr[0])) {
        Write-Host "Existing PR: $($existingPr[0])"
    } elseif ($CreatePR) {
        gh pr create --base $BaseBranch --head $currentBranch --title $Title --body $bodyText
        if ($LASTEXITCODE -ne 0) {
            throw "gh pr create failed."
        }
    } else {
        Write-Host "No existing PR found. CreatePR not requested."
    }
}

if ($MergePR) {
    Write-AiOsSection -Title "Merge"
    gh pr merge --merge
    if ($LASTEXITCODE -ne 0) {
        throw "gh pr merge failed."
    }
    Write-Host "Merge performed: YES"
} else {
    Write-Host "Merge performed: NO"
}

Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
