<#
.SYNOPSIS
Builds a read-only AI_OS PR lane readiness packet.

.DESCRIPTION
Invoke-AiOsPrLaneRunner.DRY_RUN.ps1 reads local Git state and, when
available, GitHub PR state for the current lane branch. It classifies where
the operator is in the AI_OS PR lane and prints the next safe action as text.

This helper is DRY_RUN/report-only. It does not stage, commit, push, create
pull requests, merge pull requests, switch branches, reset, delete branches,
clean files, write reports, or enumerate known untracked backlog.

.PARAMETER Mode
Execution mode. Only DRY_RUN is supported. Default is DRY_RUN.

.PARAMETER Json
Also emit the readiness packet as JSON after the Markdown report.

.EXAMPLE
.\automation\orchestration\pr_gates\Invoke-AiOsPrLaneRunner.DRY_RUN.ps1

.EXAMPLE
.\automation\orchestration\pr_gates\Invoke-AiOsPrLaneRunner.DRY_RUN.ps1 -Json
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("DRY_RUN")]
    [string] $Mode = "DRY_RUN",

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
            -WhyItFailed "The PR lane runner planner needs '$CommandName' for read-only local state inspection." `
            -NextAction "Install or restore '$CommandName', then rerun this DRY_RUN helper." `
            -Reference "AGENTS.md -> AI_OS Failure Recovery Response Rule; docs/workflows/AI_OS_PR_LANE_RUNNER.md" `
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
            -WhyItFailed "The planner could not collect required read-only PR lane state." `
            -NextAction "Review the command error, then rerun this DRY_RUN helper after the local Git issue is corrected." `
            -Reference "docs/workflows/AI_OS_PR_LANE_RUNNER.md; AGENTS.md -> AI_OS Failure Recovery Response Rule" `
            -SafeCommandOrPrompt "No command recommended."
        exit 1
    }

    return [pscustomobject] @{
        exit_code = $exitCode
        output = $text
        lines = @($output | ForEach-Object { [string] $_ })
    }
}

function Get-ObjectValue {
    param(
        [Parameter(Mandatory = $false)]
        [AllowNull()]
        [object] $InputObject,

        [Parameter(Mandatory = $true)]
        [string[]] $Names,

        [Parameter(Mandatory = $false)]
        [string] $Default = ""
    )

    if ($null -eq $InputObject) {
        return $Default
    }

    foreach ($name in $Names) {
        $property = $InputObject.PSObject.Properties[$name]
        if ($null -ne $property -and $null -ne $property.Value) {
            return [string] $property.Value
        }
    }

    return $Default
}

function Convert-CheckRollup {
    param(
        [Parameter(Mandatory = $false)]
        [AllowNull()]
        [object] $StatusCheckRollup
    )

    $checks = @()
    foreach ($check in @($StatusCheckRollup)) {
        if ($null -eq $check) {
            continue
        }

        $checks += [pscustomobject] @{
            workflow = Get-ObjectValue -InputObject $check -Names @("workflowName", "workflow", "appName") -Default "UNKNOWN"
            name = Get-ObjectValue -InputObject $check -Names @("name", "context") -Default "UNKNOWN"
            status = Get-ObjectValue -InputObject $check -Names @("status", "state") -Default "UNKNOWN"
            conclusion = Get-ObjectValue -InputObject $check -Names @("conclusion") -Default "UNKNOWN"
        }
    }

    return $checks
}

function Get-ValidateSummary {
    param([object[]] $Checks)

    if ($Checks.Count -eq 0) {
        return "UNKNOWN"
    }

    $validateChecks = @($Checks | Where-Object {
        $_.name -match "(?i)validate" -or $_.workflow -match "(?i)validate|CI"
    })

    if ($validateChecks.Count -eq 0) {
        return "UNKNOWN"
    }

    $failed = @($validateChecks | Where-Object {
        $_.status -eq "completed" -and $_.conclusion -notin @("success", "neutral", "skipped")
    })
    if ($failed.Count -gt 0) {
        return "failed"
    }

    $pending = @($validateChecks | Where-Object { $_.status -ne "completed" })
    if ($pending.Count -gt 0) {
        return "pending"
    }

    $passed = @($validateChecks | Where-Object {
        $_.status -eq "completed" -and $_.conclusion -eq "success"
    })
    if ($passed.Count -gt 0) {
        return "success"
    }

    return "UNKNOWN"
}

function Get-CurrentBranchPr {
    param([Parameter(Mandatory = $true)][string] $Branch)

    $gh = Get-Command gh -ErrorAction SilentlyContinue
    if ($null -eq $gh) {
        return [pscustomobject] @{
            available = $false
            detected = $false
            reason = "GitHub CLI unavailable"
            pr = $null
            checks = @()
            validate = "UNKNOWN"
        }
    }

    $result = Invoke-ReadOnlyCommand `
        -CommandName "gh" `
        -Arguments @("pr", "list", "--head", $Branch, "--base", "main", "--state", "all", "--json", "number,title,state,mergeStateStatus,mergeable,statusCheckRollup,headRefName,baseRefName,url", "--limit", "1") `
        -DisplayCommand "gh pr list --head $Branch --base main --state all --json number,title,state,mergeStateStatus,mergeable,statusCheckRollup,headRefName,baseRefName,url --limit 1" `
        -AllowFailure

    if ($result.exit_code -ne 0) {
        return [pscustomobject] @{
            available = $false
            detected = $false
            reason = "GitHub PR state unavailable: $($result.output)"
            pr = $null
            checks = @()
            validate = "UNKNOWN"
        }
    }

    try {
        $items = @($result.output | ConvertFrom-Json)
    }
    catch {
        return [pscustomobject] @{
            available = $false
            detected = $false
            reason = "GitHub PR JSON parse failed: $($_.Exception.Message)"
            pr = $null
            checks = @()
            validate = "UNKNOWN"
        }
    }

    if ($items.Count -eq 0) {
        return [pscustomobject] @{
            available = $true
            detected = $false
            reason = "No PR found for current branch"
            pr = $null
            checks = @()
            validate = "UNKNOWN"
        }
    }

    $pr = $items[0]
    $checks = @(Convert-CheckRollup -StatusCheckRollup $pr.statusCheckRollup)
    return [pscustomobject] @{
        available = $true
        detected = $true
        reason = "PR found"
        pr = $pr
        checks = $checks
        validate = Get-ValidateSummary -Checks $checks
    }
}

function Format-PrSummary {
    param([object] $PrInfo)

    if (-not $PrInfo.available) {
        return "unavailable - $($PrInfo.reason)"
    }

    if (-not $PrInfo.detected) {
        return "none"
    }

    return "#$($PrInfo.pr.number) $($PrInfo.pr.state) $($PrInfo.pr.url)"
}

function New-Packet {
    param(
        [string] $CurrentBranch,
        [string] $LocalStatus,
        [string] $LatestCommit,
        [string] $KnownUntrackedBacklog,
        [string] $PrDetected,
        [string] $CiValidate,
        [string] $LaneState,
        [string] $ApprovalClass,
        [string] $RecommendedNextCommand,
        [string] $StopCondition,
        [object] $PrInfo,
        [bool] $HasStaged,
        [bool] $HasUnstagedTracked,
        [bool] $HasUntracked
    )

    return [pscustomobject] @{
        current_branch = $CurrentBranch
        local_status = $LocalStatus
        latest_commit = $LatestCommit
        known_untracked_backlog = $KnownUntrackedBacklog
        pr_detected = $PrDetected
        ci_validate = $CiValidate
        lane_state = $LaneState
        approval_class = $ApprovalClass
        recommended_next_command = $RecommendedNextCommand
        stop_condition = $StopCondition
        evidence = [pscustomobject] @{
            staged_files_present = $HasStaged
            unstaged_tracked_changes_present = $HasUnstagedTracked
            untracked_files_present = $HasUntracked
            github_pr_state_available = $PrInfo.available
            github_pr_detected = $PrInfo.detected
            github_pr_reason = $PrInfo.reason
        }
        safety = [pscustomobject] @{
            mode = "DRY_RUN"
            files_staged = 0
            commits_performed = 0
            pushes_performed = 0
            prs_created = 0
            merges_performed = 0
            branch_switches = 0
            resets_performed = 0
            files_deleted = 0
            reports_written = 0
        }
    }
}

function Format-MarkdownPacket {
    param([Parameter(Mandatory = $true)][pscustomobject] $Packet)

    return @"
# AI_OS PR Lane Runner DRY_RUN Packet

- Current branch: $($Packet.current_branch)
- Local status: $($Packet.local_status)
- Latest commit: $($Packet.latest_commit)
- Known untracked backlog: $($Packet.known_untracked_backlog)
- PR detected: $($Packet.pr_detected)
- CI/validate: $($Packet.ci_validate)
- Lane state: $($Packet.lane_state)
- Approval class: $($Packet.approval_class)
- Recommended next command: $($Packet.recommended_next_command)
- Stop condition: $($Packet.stop_condition)
"@
}

try {
    if ($Mode -ne "DRY_RUN") {
        Write-FailureRecovery `
            -WhatFailed "Unsupported mode: $Mode" `
            -WhyItFailed "This helper is report-only and supports DRY_RUN mode only." `
            -NextAction "Rerun with -Mode DRY_RUN." `
            -Reference "docs/workflows/AI_OS_PR_LANE_RUNNER.md" `
            -SafeCommandOrPrompt ".\automation\orchestration\pr_gates\Invoke-AiOsPrLaneRunner.DRY_RUN.ps1 -Mode DRY_RUN"
        exit 1
    }

    Assert-CommandAvailable -CommandName "git"

    $branchResult = Invoke-ReadOnlyCommand -CommandName "git" -Arguments @("branch", "--show-current") -DisplayCommand "git branch --show-current"
    $statusResult = Invoke-ReadOnlyCommand -CommandName "git" -Arguments @("status", "--short", "--branch") -DisplayCommand "git status --short --branch"
    $latestCommitResult = Invoke-ReadOnlyCommand -CommandName "git" -Arguments @("log", "-1", "--oneline") -DisplayCommand "git log -1 --oneline"
    $stagedResult = Invoke-ReadOnlyCommand -CommandName "git" -Arguments @("diff", "--cached", "--name-only") -DisplayCommand "git diff --cached --name-only"
    $unstagedTrackedResult = Invoke-ReadOnlyCommand -CommandName "git" -Arguments @("diff", "--name-only") -DisplayCommand "git diff --name-only"

    $branch = $branchResult.output.Trim()
    if ([string]::IsNullOrWhiteSpace($branch)) {
        $branch = "UNKNOWN"
    }

    $statusLines = @($statusResult.lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $branchStatus = if ($statusLines.Count -gt 0) { $statusLines[0] } else { "UNKNOWN" }
    $trackedStatusLines = @($statusLines | Where-Object { -not $_.StartsWith("##") -and -not $_.StartsWith("??") })
    $untrackedStatusLines = @($statusLines | Where-Object { $_.StartsWith("??") })

    $stagedFiles = @($stagedResult.lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $unstagedTrackedFiles = @($unstagedTrackedResult.lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

    $hasStaged = $stagedFiles.Count -gt 0
    $hasUnstagedTracked = $unstagedTrackedFiles.Count -gt 0
    $hasUntracked = $untrackedStatusLines.Count -gt 0
    $hasTrackedStatus = $trackedStatusLines.Count -gt 0
    $hasAnyLocalChange = $hasStaged -or $hasUnstagedTracked -or $hasUntracked -or $hasTrackedStatus
    $knownBacklog = if ($hasUntracked) { "exists; not enumerated; do not stage or treat as a new emergency" } else { "none" }

    $conflictLines = @($trackedStatusLines | Where-Object {
        $_ -match "^(UU|AA|DD|AU|UA|DU|UD) "
    })

    $isMain = $branch -eq "main"
    $isLaneBranch = $branch -like "lane/*"
    $prInfo = if (-not $isMain -and $branch -ne "UNKNOWN") {
        Get-CurrentBranchPr -Branch $branch
    } else {
        [pscustomobject] @{
            available = $false
            detected = $false
            reason = "PR lookup skipped on main or unknown branch"
            pr = $null
            checks = @()
            validate = "UNKNOWN"
        }
    }

    $laneState = "BLOCKED"
    $approvalClass = "BLOCKED"
    $recommended = "No command recommended."
    $stopCondition = "Stop until the blocking condition is resolved."

    if ($conflictLines.Count -gt 0) {
        $laneState = "BLOCKED"
        $approvalClass = "BLOCKED"
        $recommended = "No command recommended."
        $stopCondition = "Merge conflict markers or unmerged Git status are present."
    }
    elseif ($branch -eq "UNKNOWN") {
        $laneState = "BLOCKED"
        $approvalClass = "BLOCKED"
        $recommended = "No command recommended."
        $stopCondition = "Current branch could not be read."
    }
    elseif ($isMain) {
        $laneState = "READY_FOR_BRANCH"
        $approvalClass = "HUMAN_APPROVAL_REQUIRED"
        $recommended = "git switch -c lane/<short-purpose>"
        $stopCondition = "Create a lane branch only after the operator names the lane purpose."
    }
    elseif (-not $isLaneBranch) {
        $laneState = "HUMAN_APPROVAL_REQUIRED"
        $approvalClass = "HUMAN_APPROVAL_REQUIRED"
        $recommended = "No command recommended."
        $stopCondition = "Current branch is not main and does not match lane/<short-purpose>; operator should confirm branch intent."
    }
    elseif ($hasStaged -or $hasUnstagedTracked -or $hasUntracked -or $hasTrackedStatus) {
        $laneState = "READY_FOR_COMMIT_GATE"
        $approvalClass = "HUMAN_APPROVAL_REQUIRED"
        $recommended = "Run the AI_OS Commit/Push Gate review for exact approved files; do not stage broad backlog."
        $stopCondition = "Stop before staging or committing until exact files and commit message are approved."
    }
    elseif (-not $prInfo.detected) {
        $laneState = "READY_FOR_PUSH_LANE_BRANCH"
        $approvalClass = "HUMAN_APPROVAL_REQUIRED"
        $recommended = "git push -u origin $branch"
        $stopCondition = "Push only after push is explicitly authorized for this lane branch."
    }
    elseif ($prInfo.detected -and $prInfo.pr.state -eq "OPEN" -and $prInfo.validate -eq "UNKNOWN") {
        $laneState = "READY_FOR_CHECK_WATCH"
        $approvalClass = "AUTO_PROCEED_READ_ONLY"
        $recommended = "gh pr checks $($prInfo.pr.number) --watch"
        $stopCondition = "Watch checks only; do not merge while checks are pending, failing, or missing."
    }
    elseif ($prInfo.detected -and $prInfo.pr.state -eq "OPEN" -and $prInfo.validate -eq "pending") {
        $laneState = "READY_FOR_CHECK_WATCH"
        $approvalClass = "AUTO_PROCEED_READ_ONLY"
        $recommended = "gh pr checks $($prInfo.pr.number) --watch"
        $stopCondition = "Continue read-only check watching until validate completes."
    }
    elseif ($prInfo.detected -and $prInfo.pr.state -eq "OPEN" -and $prInfo.validate -eq "failed") {
        $laneState = "BLOCKED"
        $approvalClass = "BLOCKED"
        $recommended = "No command recommended."
        $stopCondition = "Validate failed; do not merge."
    }
    elseif ($prInfo.detected -and $prInfo.pr.state -eq "OPEN" -and $prInfo.validate -eq "success") {
        $laneState = "READY_FOR_MERGE_APPROVAL"
        $approvalClass = "HUMAN_APPROVAL_REQUIRED"
        $recommended = "gh pr merge $($prInfo.pr.number) --squash --delete-branch"
        $stopCondition = "Merge requires explicit operator approval."
    }
    elseif ($prInfo.detected -and $prInfo.pr.state -eq "MERGED") {
        $laneState = "READY_FOR_LOCAL_MAIN_SYNC"
        $approvalClass = "HUMAN_APPROVAL_REQUIRED"
        $recommended = "git fetch origin; git switch main; git reset --hard origin/main"
        $stopCondition = "Local main sync requires explicit operator approval because it includes branch switch and reset."
    }
    else {
        $laneState = "HUMAN_APPROVAL_REQUIRED"
        $approvalClass = "HUMAN_APPROVAL_REQUIRED"
        $recommended = "No command recommended."
        $stopCondition = "PR lane state is unclear; operator should inspect the branch and PR state."
    }

    $localStatus = "$branchStatus; staged=$($stagedFiles.Count); unstaged_tracked=$($unstagedTrackedFiles.Count); untracked=$($untrackedStatusLines.Count)"
    $packet = New-Packet `
        -CurrentBranch $branch `
        -LocalStatus $localStatus `
        -LatestCommit $latestCommitResult.output `
        -KnownUntrackedBacklog $knownBacklog `
        -PrDetected (Format-PrSummary -PrInfo $prInfo) `
        -CiValidate $prInfo.validate `
        -LaneState $laneState `
        -ApprovalClass $approvalClass `
        -RecommendedNextCommand $recommended `
        -StopCondition $stopCondition `
        -PrInfo $prInfo `
        -HasStaged $hasStaged `
        -HasUnstagedTracked $hasUnstagedTracked `
        -HasUntracked $hasUntracked

    Write-Output (Format-MarkdownPacket -Packet $packet)

    if ($Json) {
        Write-Output ""
        Write-Output "---"
        Write-Output ""
        $packet | ConvertTo-Json -Depth 10
    }
}
catch {
    Write-FailureRecovery `
        -WhatFailed "Unhandled error while building the PR lane runner DRY_RUN packet." `
        -WhyItFailed $_.Exception.Message `
        -NextAction "Review the error and rerun this helper only after the local Git or GitHub state issue is corrected." `
        -Reference "AGENTS.md -> AI_OS Failure Recovery Response Rule; docs/workflows/AI_OS_PR_LANE_RUNNER.md" `
        -SafeCommandOrPrompt "No command recommended."
    exit 1
}
