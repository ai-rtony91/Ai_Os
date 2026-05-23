<#
.SYNOPSIS
Evaluates AI_OS commit and push gate readiness without mutating the repo.

.DESCRIPTION
Test-AiOsCommitPushGate.DRY_RUN.ps1 reads local Git state and classifies the
current repo state as SAFE_TO_COMMIT, SAFE_TO_PUSH, HUMAN_APPROVAL_REQUIRED,
or BLOCKED.

This helper is DRY_RUN/report-only. It does not edit files, stage files, commit,
push, switch branches, reset, clean files, run automation scripts, or enumerate
the known untracked backlog.

.PARAMETER Mode
Execution mode. Only DRY_RUN is supported. Default is DRY_RUN.

.PARAMETER ApprovedPath
Optional approved path boundary list. When supplied, staged files must be inside
one of these paths before commit readiness can be considered safe.

.PARAMETER Json
Emit JSON instead of the default compact Markdown report.

.EXAMPLE
.\automation\orchestration\commit_packages\Test-AiOsCommitPushGate.DRY_RUN.ps1

.EXAMPLE
.\automation\orchestration\commit_packages\Test-AiOsCommitPushGate.DRY_RUN.ps1 -ApprovedPath AGENTS.md

.EXAMPLE
.\automation\orchestration\commit_packages\Test-AiOsCommitPushGate.DRY_RUN.ps1 -ApprovedPath AGENTS.md,docs/workflows -Json
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("DRY_RUN")]
    [string] $Mode = "DRY_RUN",

    [Parameter(Mandatory = $false)]
    [string[]] $ApprovedPath = @(),

    [Parameter(Mandatory = $false)]
    [switch] $Json
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
            -WhyItFailed "The commit/push gate evaluator needs '$CommandName' for read-only state inspection." `
            -NextAction "Install or restore '$CommandName', then rerun this DRY_RUN helper." `
            -Reference "AGENTS.md -> AI_OS Failure Recovery Response Rule; docs/workflows/AI_OS_COMMIT_PUSH_GATE.md" `
            -SafeCommandOrPrompt "No command recommended."
        exit 1
    }
}

function Invoke-ReadOnlyCommand {
    param(
        [Parameter(Mandatory = $true)][string] $CommandName,
        [Parameter(Mandatory = $true)][string[]] $Arguments,
        [Parameter(Mandatory = $true)][string] $DisplayCommand,
        [Parameter(Mandatory = $false)][switch] $AllowFailure
    )

    $output = & $CommandName @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $text = ($output | Out-String).Trim()

    if ($exitCode -ne 0 -and -not $AllowFailure) {
        Write-FailureRecovery `
            -WhatFailed "Command failed: $DisplayCommand`n$text" `
            -WhyItFailed "The gate evaluator could not collect required read-only Git state." `
            -NextAction "Review the Git error, then rerun this DRY_RUN helper after the local repo issue is corrected." `
            -Reference "docs/workflows/AI_OS_COMMIT_PUSH_GATE.md; AGENTS.md -> AI_OS Failure Recovery Response Rule" `
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

function Convert-ToNormalizedPath {
    param([Parameter(Mandatory = $true)][string] $Path)

    return (($Path -replace "\\", "/").Trim().Trim("/"))
}

function Test-PathInsideBoundary {
    param(
        [Parameter(Mandatory = $true)][string] $Path,
        [Parameter(Mandatory = $true)][string[]] $Boundary
    )

    if ($Boundary.Count -eq 0) {
        return $false
    }

    $normalizedPath = Convert-ToNormalizedPath -Path $Path
    foreach ($item in $Boundary) {
        if ([string]::IsNullOrWhiteSpace($item)) {
            continue
        }

        $normalizedBoundary = Convert-ToNormalizedPath -Path $item
        if ($normalizedPath -eq $normalizedBoundary -or $normalizedPath.StartsWith($normalizedBoundary + "/")) {
            return $true
        }
    }

    return $false
}

function Format-MarkdownReport {
    param([Parameter(Mandatory = $true)][pscustomobject] $Packet)

    $approvedBoundaryText = if ($Packet.approved_paths.Count -gt 0) {
        ($Packet.approved_paths -join ", ")
    }
    else {
        "not supplied"
    }

    $stagedText = if ($Packet.staged_files.Count -gt 0) {
        ($Packet.staged_files -join ", ")
    }
    else {
        "none"
    }

    $unstagedText = if ($Packet.unstaged_tracked_files.Count -gt 0) {
        ($Packet.unstaged_tracked_files -join ", ")
    }
    else {
        "none"
    }

    $outsideText = if ($Packet.staged_files_outside_approved_paths.Count -gt 0) {
        ($Packet.staged_files_outside_approved_paths -join ", ")
    }
    else {
        "none"
    }

    return @"
# AI_OS Commit/Push Gate DRY_RUN Packet

- Gate state: $($Packet.gate_state)
- Approval class: $($Packet.approval_class)
- Current branch: $($Packet.current_branch)
- Branch kind: $($Packet.branch_kind)
- Branch status: $($Packet.branch_status)
- Approved paths: $approvedBoundaryText
- Staged files: $stagedText
- Unstaged tracked files: $unstagedText
- Untracked backlog: $($Packet.untracked_backlog)
- Staged files outside approved paths: $outsideText
- Recommended next action: $($Packet.recommended_next_action)
- Stop condition: $($Packet.stop_condition)
- Mutation status: none
"@
}

try {
    if ($Mode -ne "DRY_RUN") {
        Write-FailureRecovery `
            -WhatFailed "Unsupported mode: $Mode" `
            -WhyItFailed "This helper is report-only and supports DRY_RUN mode only." `
            -NextAction "Rerun with -Mode DRY_RUN." `
            -Reference "docs/workflows/AI_OS_COMMIT_PUSH_GATE.md" `
            -SafeCommandOrPrompt ".\automation\orchestration\commit_packages\Test-AiOsCommitPushGate.DRY_RUN.ps1 -Mode DRY_RUN"
        exit 1
    }

    Assert-CommandAvailable -CommandName "git"

    $generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $branchResult = Invoke-ReadOnlyCommand -CommandName "git" -Arguments @("branch", "--show-current") -DisplayCommand "git branch --show-current"
    $statusResult = Invoke-ReadOnlyCommand -CommandName "git" -Arguments @("status", "--short", "--branch") -DisplayCommand "git status --short --branch"
    $stagedResult = Invoke-ReadOnlyCommand -CommandName "git" -Arguments @("diff", "--cached", "--name-only") -DisplayCommand "git diff --cached --name-only"
    $unstagedResult = Invoke-ReadOnlyCommand -CommandName "git" -Arguments @("diff", "--name-only") -DisplayCommand "git diff --name-only"
    $latestCommitResult = Invoke-ReadOnlyCommand -CommandName "git" -Arguments @("log", "-1", "--oneline") -DisplayCommand "git log -1 --oneline" -AllowFailure

    $branch = $branchResult.output.Trim()
    if ([string]::IsNullOrWhiteSpace($branch)) {
        $branch = "UNKNOWN"
    }

    $statusLines = @($statusResult.lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $branchStatus = if ($statusLines.Count -gt 0) { [string] $statusLines[0] } else { "UNKNOWN" }
    $fileStatusLines = @($statusLines | Where-Object { -not $_.StartsWith("##") })
    $untrackedLines = @($fileStatusLines | Where-Object { $_.StartsWith("??") })
    $conflictLines = @($fileStatusLines | Where-Object { $_ -match "^(UU|AA|DD|AU|UA|DU|UD) " })

    $stagedFiles = @($stagedResult.lines |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        ForEach-Object { Convert-ToNormalizedPath -Path $_ })

    $unstagedTrackedFiles = @($unstagedResult.lines |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        ForEach-Object { Convert-ToNormalizedPath -Path $_ })

    $normalizedApprovedPaths = @($ApprovedPath |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        ForEach-Object { Convert-ToNormalizedPath -Path $_ })

    $stagedOutsideApproved = @()
    if ($normalizedApprovedPaths.Count -gt 0) {
        $stagedOutsideApproved = @($stagedFiles | Where-Object {
            -not (Test-PathInsideBoundary -Path $_ -Boundary $normalizedApprovedPaths)
        })
    }

    $isMain = $branch -eq "main"
    $isLaneBranch = $branch -like "lane/*"
    $branchKind = if ($isMain) {
        "main"
    }
    elseif ($isLaneBranch) {
        "lane"
    }
    elseif ($branch -eq "UNKNOWN") {
        "unknown"
    }
    else {
        "other"
    }

    $hasStaged = $stagedFiles.Count -gt 0
    $hasUnstagedTracked = $unstagedTrackedFiles.Count -gt 0
    $hasUntracked = $untrackedLines.Count -gt 0
    $untrackedBacklog = if ($hasUntracked) {
        "exists; not enumerated; do not stage or treat as a new emergency"
    }
    else {
        "none"
    }

    $ahead = $branchStatus -match "\[.*ahead\s+\d+"
    $behind = $branchStatus -match "\[.*behind\s+\d+"
    $diverged = $ahead -and $behind

    $gateState = "HUMAN_APPROVAL_REQUIRED"
    $approvalClass = "HUMAN_APPROVAL_REQUIRED"
    $recommended = "Review the packet and request explicit operator approval for the next mutation step."
    $stopCondition = "Stop before staging, committing, or pushing until the operator approves the exact next action."
    $reason = "State requires human review before mutation."

    if ($conflictLines.Count -gt 0) {
        $gateState = "BLOCKED"
        $approvalClass = "BLOCKED"
        $recommended = "No command recommended."
        $stopCondition = "Merge conflicts or unmerged files are present."
        $reason = "Merge conflicts block commit and push gates."
    }
    elseif ($branch -eq "UNKNOWN") {
        $gateState = "BLOCKED"
        $approvalClass = "BLOCKED"
        $recommended = "No command recommended."
        $stopCondition = "Current branch could not be read."
        $reason = "Branch identity is required before commit or push classification."
    }
    elseif ($diverged -or $behind) {
        $gateState = "BLOCKED"
        $approvalClass = "BLOCKED"
        $recommended = "No command recommended."
        $stopCondition = "Branch is behind or diverged from upstream."
        $reason = "Push or commit classification is blocked until branch divergence is reviewed."
    }
    elseif ($normalizedApprovedPaths.Count -gt 0 -and $stagedOutsideApproved.Count -gt 0) {
        $gateState = "BLOCKED"
        $approvalClass = "BLOCKED"
        $recommended = "No command recommended."
        $stopCondition = "Cached diff includes files outside the approved boundary."
        $reason = "Staged files outside ApprovedPath cannot pass the commit gate."
    }
    elseif ($hasStaged -and $normalizedApprovedPaths.Count -eq 0) {
        $gateState = "HUMAN_APPROVAL_REQUIRED"
        $approvalClass = "HUMAN_APPROVAL_REQUIRED"
        $recommended = "Rerun with -ApprovedPath for the exact approved file or folder boundary before committing."
        $stopCondition = "ApprovedPath is missing while staged files exist."
        $reason = "The evaluator cannot prove staged files are inside the approved boundary."
    }
    elseif ($hasStaged -and $hasUnstagedTracked) {
        $gateState = "HUMAN_APPROVAL_REQUIRED"
        $approvalClass = "HUMAN_APPROVAL_REQUIRED"
        $recommended = "Review unstaged tracked changes before committing the cached diff."
        $stopCondition = "Unstaged tracked changes remain outside the cached diff."
        $reason = "The cached diff may be valid, but nearby unstaged tracked work requires human review."
    }
    elseif ($hasStaged -and $normalizedApprovedPaths.Count -gt 0 -and $stagedOutsideApproved.Count -eq 0) {
        $gateState = "SAFE_TO_COMMIT"
        $approvalClass = "HUMAN_APPROVAL_REQUIRED"
        $recommended = "If commit authorization, validation result, and commit message are present, run git diff --cached and commit only the staged approved files."
        $stopCondition = "This DRY_RUN helper does not stage or commit; operator authorization is still required for mutation."
        $reason = "Cached diff contains only files inside ApprovedPath and no conflict or upstream blocker was detected."
    }
    elseif (-not $hasStaged -and -not $hasUnstagedTracked -and $ahead -and -not $isMain) {
        $gateState = "SAFE_TO_PUSH"
        $approvalClass = "HUMAN_APPROVAL_REQUIRED"
        $recommended = "If push is separately authorized, push only the current named lane branch to its approved remote target."
        $stopCondition = "This DRY_RUN helper does not push; operator authorization is still required."
        $reason = "Branch appears ahead with no staged or unstaged tracked changes."
    }
    elseif (-not $hasStaged -and -not $hasUnstagedTracked -and $ahead -and $isMain) {
        $gateState = "HUMAN_APPROVAL_REQUIRED"
        $approvalClass = "HUMAN_APPROVAL_REQUIRED"
        $recommended = "Protected main work should use PR lane flow; do not direct-push main unless explicitly authorized by the operator."
        $stopCondition = "Direct main push is not the standard protected-main path."
        $reason = "Main is ahead, but protected-main rules require additional human decision."
    }
    elseif (-not $hasStaged -and ($hasUnstagedTracked -or $hasUntracked)) {
        $gateState = "HUMAN_APPROVAL_REQUIRED"
        $approvalClass = "HUMAN_APPROVAL_REQUIRED"
        $recommended = "Review exact intended files and run a scoped commit gate with ApprovedPath before staging."
        $stopCondition = "Local changes or known untracked backlog exist, but no cached diff is ready."
        $reason = "Mutation requires exact-file approval and selective staging."
    }
    elseif (-not $hasStaged -and -not $hasUnstagedTracked -and -not $ahead) {
        $gateState = "HUMAN_APPROVAL_REQUIRED"
        $approvalClass = "HUMAN_APPROVAL_REQUIRED"
        $recommended = "No commit or push action is currently ready from local Git state."
        $stopCondition = "There are no staged files and no local ahead marker."
        $reason = "No commit or push candidate was detected."
    }

    $packet = [pscustomobject] @{
        schema = "AIOS_COMMIT_PUSH_GATE_DRY_RUN_PACKET.v1"
        generated_at = $generatedAt
        mode = "DRY_RUN"
        gate_state = $gateState
        approval_class = $approvalClass
        reason = $reason
        current_branch = $branch
        branch_kind = $branchKind
        branch_status = $branchStatus
        latest_commit = $latestCommitResult.output
        approved_paths = @($normalizedApprovedPaths)
        staged_files = @($stagedFiles)
        unstaged_tracked_files = @($unstagedTrackedFiles)
        untracked_backlog = $untrackedBacklog
        staged_files_outside_approved_paths = @($stagedOutsideApproved)
        evidence = [pscustomobject] @{
            staged_file_count = $stagedFiles.Count
            unstaged_tracked_file_count = $unstagedTrackedFiles.Count
            untracked_backlog_exists = $hasUntracked
            conflict_status_exists = $conflictLines.Count -gt 0
            branch_ahead = $ahead
            branch_behind = $behind
            branch_diverged = $diverged
        }
        recommended_next_action = $recommended
        stop_condition = $stopCondition
        safety = [pscustomobject] @{
            files_edited = 0
            files_staged = 0
            commits_performed = 0
            pushes_performed = 0
            branch_switches = 0
            resets_performed = 0
            files_deleted = 0
            scripts_run = 0
            reports_written = 0
        }
    }

    if ($Json) {
        $jsonText = $packet | ConvertTo-Json -Depth 10
        $null = $jsonText | ConvertFrom-Json
        Write-Output $jsonText
    }
    else {
        Write-Output (Format-MarkdownReport -Packet $packet)
    }
}
catch {
    Write-FailureRecovery `
        -WhatFailed "Unhandled error while building the commit/push gate DRY_RUN packet." `
        -WhyItFailed $_.Exception.Message `
        -NextAction "Review the error and rerun this helper only after the local Git state issue is corrected." `
        -Reference "AGENTS.md -> AI_OS Failure Recovery Response Rule; docs/workflows/AI_OS_COMMIT_PUSH_GATE.md" `
        -SafeCommandOrPrompt "No command recommended."
    exit 1
}
