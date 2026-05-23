<#
.SYNOPSIS
Summarizes known AI_OS repo state without turning known backlog into an alarm.

.DESCRIPTION
Get-AiOsKnownStateFilter.DRY_RUN.ps1 reads Git status and AI_OS repo memory,
then emits a compact known-state packet. It is intended to reduce repeated
operator concern about the same known untracked backlog while still showing
branch sync state, tracked changes, staged files, and whether backlog exists.

This helper is DRY_RUN/report-only. It does not edit files, write reports,
stage, commit, push, clean files, or touch known untracked backlog.

.PARAMETER Mode
Execution mode. Only DRY_RUN is supported. Default is DRY_RUN.

.PARAMETER Json
Emit the known-state packet as JSON instead of Markdown.

.PARAMETER ShowBacklogSample
Show a small sample of untracked status lines. Defaults to false. This still
does not enumerate the full known untracked backlog.

.EXAMPLE
.\automation\orchestration\control_summary\Get-AiOsKnownStateFilter.DRY_RUN.ps1

.EXAMPLE
.\automation\orchestration\control_summary\Get-AiOsKnownStateFilter.DRY_RUN.ps1 -Json

.EXAMPLE
.\automation\orchestration\control_summary\Get-AiOsKnownStateFilter.DRY_RUN.ps1 -ShowBacklogSample
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("DRY_RUN")]
    [string] $Mode = "DRY_RUN",

    [Parameter(Mandatory = $false)]
    [switch] $Json,

    [Parameter(Mandatory = $false)]
    [switch] $ShowBacklogSample
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-FailureRecovery {
    param(
        [Parameter(Mandatory = $true)]
        [string] $WhatFailed,

        [Parameter(Mandatory = $true)]
        [string] $WhyItFailed,

        [Parameter(Mandatory = $true)]
        [string] $NextAction,

        [Parameter(Mandatory = $true)]
        [string] $Reference,

        [Parameter(Mandatory = $false)]
        [string] $SafeCommandOrPrompt = "No command recommended."
    )

    Write-Output "WHAT FAILED:"
    Write-Output $WhatFailed
    Write-Output ""
    Write-Output "WHY IT FAILED:"
    Write-Output $WhyItFailed
    Write-Output ""
    Write-Output "WHAT NEEDS TO HAPPEN NEXT:"
    Write-Output $NextAction
    Write-Output ""
    Write-Output "WHERE TO REFERENCE:"
    Write-Output $Reference
    Write-Output ""
    Write-Output "SAFE NEXT COMMAND OR PROMPT:"
    Write-Output $SafeCommandOrPrompt
}

function Assert-CommandAvailable {
    param([Parameter(Mandatory = $true)][string] $CommandName)

    $command = Get-Command $CommandName -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        Write-FailureRecovery `
            -WhatFailed "Required command '$CommandName' was not found." `
            -WhyItFailed "The known-state filter needs '$CommandName' for read-only state inspection." `
            -NextAction "Install or restore '$CommandName', then rerun this DRY_RUN helper." `
            -Reference "AGENTS.md -> AI_OS Failure Recovery Response Rule; docs/governance/AI_OS_REPO_MEMORY.md" `
            -SafeCommandOrPrompt "No command recommended."
        exit 1
    }
}

function Invoke-ReadOnlyCommand {
    param(
        [Parameter(Mandatory = $true)][string] $CommandName,
        [Parameter(Mandatory = $true)][string[]] $Arguments,
        [Parameter(Mandatory = $true)][string] $DisplayCommand
    )

    $output = & $CommandName @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $text = ($output | Out-String).Trim()

    if ($exitCode -ne 0) {
        Write-FailureRecovery `
            -WhatFailed "Command failed: $DisplayCommand`n$text" `
            -WhyItFailed "The known-state filter could not collect required read-only Git state." `
            -NextAction "Review the Git error, then rerun this DRY_RUN helper after the local repo issue is corrected." `
            -Reference "docs/governance/AI_OS_REPO_MEMORY.md; AGENTS.md -> AI_OS Failure Recovery Response Rule" `
            -SafeCommandOrPrompt "No command recommended."
        exit 1
    }

    return [pscustomobject] @{
        exit_code = $exitCode
        output = $text
        lines = @($output | ForEach-Object { [string] $_ })
    }
}

function Convert-StatusLineToPath {
    param([Parameter(Mandatory = $true)][string] $Line)

    if ([string]::IsNullOrWhiteSpace($Line) -or $Line.Length -lt 4 -or $Line.StartsWith("##")) {
        return ""
    }

    $path = $Line.Substring(3).Trim()
    if ($path -match " -> ") {
        $path = ($path -split " -> ")[-1].Trim()
    }

    return ($path -replace "\\", "/")
}

function Get-BranchSyncState {
    param([Parameter(Mandatory = $true)][string] $BranchLine)

    $ahead = $BranchLine -match "ahead\s+\d+"
    $behind = $BranchLine -match "behind\s+\d+"

    if ($ahead -and $behind) {
        return "diverged"
    }

    if ($ahead) {
        return "ahead"
    }

    if ($behind) {
        return "behind"
    }

    if ($BranchLine -match "\.\.\.") {
        return "synced_or_no_ahead_behind_marker"
    }

    return "unknown"
}

function Get-MemoryExcerpt {
    param(
        [Parameter(Mandatory = $true)]
        [string] $MemoryText,

        [Parameter(Mandatory = $true)]
        [string] $Heading
    )

    $escapedHeading = [regex]::Escape($Heading)
    $match = [regex]::Match($MemoryText, "(?ms)^## $escapedHeading\s*(.*?)(?=^## |\z)")
    if (-not $match.Success) {
        return "UNKNOWN"
    }

    return $match.Groups[1].Value.Trim()
}

function Format-MarkdownPacket {
    param([Parameter(Mandatory = $true)][pscustomobject] $Packet)

    $sampleText = if ($Packet.backlog_sample.Count -gt 0) {
        ($Packet.backlog_sample -join "; ")
    }
    else {
        "not shown"
    }

    return @"
# AI_OS Known State Filter DRY_RUN Packet

- Branch line: $($Packet.branch_line)
- Branch sync state: $($Packet.branch_sync_state)
- Tracked files modified: $($Packet.tracked_files_modified)
- Staged files exist: $($Packet.staged_files_exist)
- Untracked backlog: $($Packet.untracked_backlog)
- Backlog sample: $sampleText
- Repo memory last updated: $($Packet.repo_memory.last_updated)
- Repo memory push state: $($Packet.repo_memory.last_known_push_state)
- Known-state interpretation: $($Packet.known_state_interpretation)
- Recommended next action: $($Packet.recommended_next_action)
- Mutation status: none
"@
}

try {
    if ($Mode -ne "DRY_RUN") {
        Write-FailureRecovery `
            -WhatFailed "Unsupported mode: $Mode" `
            -WhyItFailed "This helper is report-only and supports DRY_RUN mode only." `
            -NextAction "Rerun with -Mode DRY_RUN." `
            -Reference "docs/governance/AI_OS_REPO_MEMORY.md" `
            -SafeCommandOrPrompt ".\automation\orchestration\control_summary\Get-AiOsKnownStateFilter.DRY_RUN.ps1 -Mode DRY_RUN"
        exit 1
    }

    Assert-CommandAvailable -CommandName "git"

    $memoryPath = "docs/governance/AI_OS_REPO_MEMORY.md"
    if (-not (Test-Path -LiteralPath $memoryPath -PathType Leaf)) {
        Write-FailureRecovery `
            -WhatFailed "Missing repo memory file: $memoryPath" `
            -WhyItFailed "The known-state filter uses AI_OS repo memory as the starting context for known dirty and backlog state." `
            -NextAction "Restore or create the repo memory file through a scoped governance lane before using this helper." `
            -Reference "AGENTS.md -> Redundant State Revalidation Loop Prevention Rule; docs/governance/AI_OS_REPO_MEMORY.md" `
            -SafeCommandOrPrompt "No command recommended."
        exit 1
    }

    $generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $memoryText = Get-Content -Raw -LiteralPath $memoryPath
    $statusResult = Invoke-ReadOnlyCommand -CommandName "git" -Arguments @("status", "--short", "--branch") -DisplayCommand "git status --short --branch"
    $stagedResult = Invoke-ReadOnlyCommand -CommandName "git" -Arguments @("diff", "--cached", "--name-only") -DisplayCommand "git diff --cached --name-only"

    $statusLines = @($statusResult.lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $branchLine = if ($statusLines.Count -gt 0 -and $statusLines[0].StartsWith("##")) {
        [string] $statusLines[0]
    }
    else {
        "UNKNOWN"
    }

    $fileLines = @($statusLines | Where-Object { -not $_.StartsWith("##") })
    $untrackedLines = @($fileLines | Where-Object { $_.StartsWith("??") })
    $trackedLines = @($fileLines | Where-Object { -not $_.StartsWith("??") })
    $stagedFiles = @($stagedResult.lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

    $trackedPaths = @($trackedLines |
        ForEach-Object { Convert-StatusLineToPath -Line $_ } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

    $showSample = [bool] $ShowBacklogSample
    $sample = if ($showSample) {
        @($untrackedLines | Select-Object -First 5)
    }
    else {
        @()
    }

    $branchSyncState = Get-BranchSyncState -BranchLine $branchLine
    $hasTrackedModified = $trackedPaths.Count -gt 0
    $hasStaged = $stagedFiles.Count -gt 0
    $hasUntracked = $untrackedLines.Count -gt 0
    $untrackedBacklog = if ($hasUntracked) {
        "exists; known local backlog; not enumerated"
    }
    else {
        "none"
    }

    $memoryLastUpdated = Get-MemoryExcerpt -MemoryText $memoryText -Heading "Last Updated"
    $memoryPushState = Get-MemoryExcerpt -MemoryText $memoryText -Heading "Last Known Push State"
    $memoryDirtyState = Get-MemoryExcerpt -MemoryText $memoryText -Heading "Current Local Dirty State"
    $memoryNextQueue = Get-MemoryExcerpt -MemoryText $memoryText -Heading "Next Safe Queue"

    $interpretation = if ($hasUntracked -and -not $hasTrackedModified -and -not $hasStaged) {
        "Known untracked backlog exists, but no tracked or staged changes were detected by this filter."
    }
    elseif ($hasUntracked) {
        "Known untracked backlog exists alongside tracked or staged changes; review lane scope before any commit."
    }
    elseif ($hasTrackedModified -or $hasStaged) {
        "Tracked or staged changes exist without untracked backlog."
    }
    else {
        "No local file changes were detected by this filter."
    }

    $recommended = switch ($branchSyncState) {
        "diverged" { "Stop and review branch divergence before commit, push, pull, rebase, or merge." }
        "behind" { "Do not pull, rebase, merge, commit, or push until the operator reviews behind state." }
        "ahead" { "Use the commit/push gate before any push; do not treat known backlog as a new emergency." }
        default {
            if ($hasTrackedModified -or $hasStaged) {
                "Use the scoped commit/push gate for exact approved files; keep known backlog unstaged."
            }
            elseif ($hasUntracked) {
                "Continue from repo memory and next queue; report untracked files as known local backlog."
            }
            else {
                "Continue with the next assigned AI_OS lane."
            }
        }
    }

    $packet = [pscustomobject] @{
        schema = "AIOS_KNOWN_STATE_FILTER_PACKET.v1"
        generated_at = $generatedAt
        mode = "DRY_RUN"
        branch_line = $branchLine
        branch_sync_state = $branchSyncState
        tracked_files_modified = $hasTrackedModified
        tracked_file_count = $trackedPaths.Count
        staged_files_exist = $hasStaged
        staged_file_count = $stagedFiles.Count
        untracked_backlog = $untrackedBacklog
        untracked_backlog_exists = $hasUntracked
        untracked_backlog_count = $untrackedLines.Count
        backlog_sample = @($sample)
        repo_memory = [pscustomobject] @{
            path = $memoryPath
            last_updated = $memoryLastUpdated
            last_known_push_state = $memoryPushState
            current_local_dirty_state = $memoryDirtyState
            next_safe_queue = $memoryNextQueue
        }
        known_state_interpretation = $interpretation
        recommended_next_action = $recommended
        safety = [pscustomobject] @{
            files_edited = 0
            reports_written = 0
            files_staged = 0
            commits_performed = 0
            pushes_performed = 0
            cleans_performed = 0
            backlog_touched = $false
            backlog_enumerated = $showSample
        }
    }

    if ($Json) {
        $jsonText = $packet | ConvertTo-Json -Depth 10
        $null = $jsonText | ConvertFrom-Json
        Write-Output $jsonText
    }
    else {
        Write-Output (Format-MarkdownPacket -Packet $packet)
    }
}
catch {
    Write-FailureRecovery `
        -WhatFailed "Unhandled error while building the known-state DRY_RUN packet." `
        -WhyItFailed $_.Exception.Message `
        -NextAction "Review the error and rerun this helper only after the local Git state or repo memory issue is corrected." `
        -Reference "AGENTS.md -> AI_OS Failure Recovery Response Rule; docs/governance/AI_OS_REPO_MEMORY.md" `
        -SafeCommandOrPrompt "No command recommended."
    exit 1
}
