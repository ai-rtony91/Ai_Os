<#
.SYNOPSIS
Evaluates AI_OS PR merge readiness and optionally performs the approved merge.

.DESCRIPTION
Merge-AiOsPullRequest.DRY_RUN.ps1 validates repo identity, local Git state,
approval evidence, and GitHub PR readiness before a merge. DRY_RUN mode reports
what would happen without mutation. APPLY mode runs the merge only when all gate
checks pass and the approval file explicitly approves the target PR.

This helper does not commit, push, switch branches, reset, clean files, edit
reports, or bypass GitHub branch protection.

.PARAMETER PrNumber
GitHub pull request number to inspect or merge.

.PARAMETER ApprovalPath
Path to an approval JSON file. Defaults to
automation/orchestration/approvals/APPROVE_PR_<PrNumber>.json.

.PARAMETER Json
Emit JSON instead of the default Markdown report.

.EXAMPLE
.\automation\orchestration\pr_gates\Merge-AiOsPullRequest.DRY_RUN.ps1 -PrNumber 240

#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateRange(1, [int]::MaxValue)]
    [int] $PrNumber,

    [Parameter(Mandatory = $false)]
    [string] $ApprovalPath = "",

    [Parameter(Mandatory = $false)]
    [switch] $Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptName = Split-Path -Leaf $PSCommandPath
$mode = "DRY_RUN"
$expectedRepoPath = "C:\Dev\Ai.Os"
$expectedRemoteUrl = "https://github.com/ai-rtony91/Ai_Os.git"
$baseBranch = "main"

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
            -WhyItFailed "The PR merge gate needs '$CommandName' for state inspection and merge readiness checks." `
            -NextAction "Install or restore '$CommandName', then rerun this helper." `
            -Reference "AGENTS.md -> AI_OS Failure Recovery Response Rule; docs/workflows/AI_OS_PR_LANE_RUNNER.md" `
            -SafeCommandOrPrompt "No command recommended."
        exit 1
    }
}

function Invoke-NativeCommand {
    param(
        [Parameter(Mandatory = $true)][string] $CommandName,
        [Parameter(Mandatory = $true)][string[]] $Arguments,
        [Parameter(Mandatory = $true)][string] $DisplayCommand,
        [Parameter(Mandatory = $false)][switch] $AllowFailure
    )

    $ErrorActionPreference = "Continue"
    $output = & $CommandName @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = "Stop"

    $stdoutItems = @($output | Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] })
    $stderrItems = @($output | Where-Object { $_ -is [System.Management.Automation.ErrorRecord] })
    $text = ($stdoutItems | Out-String).Trim()
    $stderrText = ($stderrItems | ForEach-Object { $_.Exception.Message } | Out-String).Trim()

    if ($exitCode -ne 0 -and -not $AllowFailure) {
        $failDetail = if ($stderrText) { "$text`n$stderrText" } else { $text }
        Write-FailureRecovery `
            -WhatFailed "Command failed: $DisplayCommand`n$failDetail" `
            -WhyItFailed "The merge gate could not collect required state." `
            -NextAction "Review the command error, then rerun this helper after the issue is corrected." `
            -Reference "docs/workflows/AI_OS_PR_LANE_RUNNER.md; AGENTS.md -> AI_OS Failure Recovery Response Rule" `
            -SafeCommandOrPrompt "No command recommended."
        exit 1
    }

    if ($stderrText) {
        Write-Warning "[$DisplayCommand] $stderrText"
    }

    return [pscustomobject] @{
        exit_code = $exitCode
        output = $text
        lines = @($stdoutItems | ForEach-Object { [string] $_ })
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

function Get-CheckSummary {
    param([Parameter(Mandatory = $true)][object[]] $Checks)

    if ($Checks.Count -eq 0) {
        return "missing"
    }

    $failed = @($Checks | Where-Object {
        $_.status -eq "completed" -and $_.conclusion -notin @("success", "neutral", "skipped")
    })
    if ($failed.Count -gt 0) {
        return "failed"
    }

    $pending = @($Checks | Where-Object { $_.status -ne "completed" })
    if ($pending.Count -gt 0) {
        return "pending"
    }

    $passed = @($Checks | Where-Object {
        $_.status -eq "completed" -and $_.conclusion -in @("success", "neutral", "skipped")
    })
    if ($passed.Count -eq $Checks.Count) {
        return "success"
    }

    return "unknown"
}

function Read-ApprovalFile {
    param([Parameter(Mandatory = $true)][string] $Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject] @{
            exists = $false
            valid = $false
            approved = $false
            pr_number = $null
            reason = "Approval file missing: $Path"
        }
    }

    try {
        $approval = Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    }
    catch {
        return [pscustomobject] @{
            exists = $true
            valid = $false
            approved = $false
            pr_number = $null
            reason = "Approval file JSON parse failed: $($_.Exception.Message)"
        }
    }

    $approvedValue = $false
    $approvedProperty = $approval.PSObject.Properties["approved"]
    if ($null -ne $approvedProperty) {
        $approvedValue = [bool] $approvedProperty.Value
    }

    $approvalPrNumber = $null
    $prProperty = $approval.PSObject.Properties["pr_number"]
    if ($null -ne $prProperty -and $null -ne $prProperty.Value) {
        $approvalPrNumber = [int] $prProperty.Value
    }

    return [pscustomobject] @{
        exists = $true
        valid = $true
        approved = $approvedValue
        pr_number = $approvalPrNumber
        reason = "Approval file parsed."
    }
}

function Format-MarkdownReport {
    param([Parameter(Mandatory = $true)][pscustomobject] $Packet)

    $blockerText = if ($Packet.blockers.Count -gt 0) {
        ($Packet.blockers | ForEach-Object { "- $_" }) -join "`n"
    }
    else {
        "- none"
    }

    $checkText = if ($Packet.pr_state.checks.Count -gt 0) {
        ($Packet.pr_state.checks | ForEach-Object {
            "- $($_.name): status=$($_.status), conclusion=$($_.conclusion), workflow=$($_.workflow)"
        }) -join "`n"
    }
    else {
        "- none reported"
    }

    return @"
# AI_OS PR Merge Gate

- Mode: $($Packet.mode)
- Gate state: $($Packet.gate_state)
- Safety: $($Packet.safety_classification)
- Generated: $($Packet.generated_at)
- Merge attempted: $($Packet.merge.merge_attempted)

## Repo Identity
- Path: $($Packet.repo_identity.repo_path) [$($Packet.repo_identity.path_result)]
- Branch: $($Packet.repo_identity.current_branch) [$($Packet.repo_identity.branch_result)]
- Remote: $($Packet.repo_identity.remote_url) [$($Packet.repo_identity.remote_result)]
- Local status: $($Packet.repo_identity.local_status)

## Approval
- Path: $($Packet.approval.path)
- Exists: $($Packet.approval.exists)
- Approved: $($Packet.approval.approved)
- PR number: $($Packet.approval.pr_number)

## PR State
- PR: #$($Packet.pr_number)
- URL: $($Packet.pr_state.url)
- State: $($Packet.pr_state.state)
- Base: $($Packet.pr_state.base_ref)
- Head: $($Packet.pr_state.head_ref)
- Draft: $($Packet.pr_state.is_draft)
- Merge state: $($Packet.pr_state.merge_state_status)
- Review decision: $($Packet.pr_state.review_decision)
- Checks: $($Packet.pr_state.check_summary)

## Checks
$checkText

## Blockers
$blockerText

## Next Action
- $($Packet.recommended_next_action)
- Stop: $($Packet.stop_condition)

---
Commit performed: NO
Push performed: NO
"@
}

try {
    Assert-CommandAvailable -CommandName "git"
    Assert-CommandAvailable -CommandName "gh"

    if ([string]::IsNullOrWhiteSpace($ApprovalPath)) {
        $ApprovalPath = "automation/orchestration/approvals/APPROVE_PR_$PrNumber.json"
    }

    $generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $blockers = @()

    $repoTopLevelResult = Invoke-NativeCommand -CommandName "git" -Arguments @("rev-parse", "--show-toplevel") -DisplayCommand "git rev-parse --show-toplevel"
    $repoPath = $repoTopLevelResult.output.Trim().Replace("/", "\")
    $repoPathResult = if ($repoPath -ieq $expectedRepoPath) { "PASS" } else { "BLOCKED" }
    if ($repoPathResult -ne "PASS") {
        $blockers += "Repo path mismatch: expected $expectedRepoPath, got $repoPath"
    }

    $remoteUrlResult = Invoke-NativeCommand -CommandName "git" -Arguments @("remote", "get-url", "origin") -DisplayCommand "git remote get-url origin" -AllowFailure
    $remoteUrl = if ($remoteUrlResult.exit_code -eq 0) { $remoteUrlResult.output.Trim() } else { "NOT_CONFIGURED" }
    $remoteResult = if ($remoteUrl -eq $expectedRemoteUrl) { "PASS" } else { "BLOCKED" }
    if ($remoteResult -ne "PASS") {
        $blockers += "Remote mismatch: expected $expectedRemoteUrl, got $remoteUrl"
    }

    $branchResult = Invoke-NativeCommand -CommandName "git" -Arguments @("branch", "--show-current") -DisplayCommand "git branch --show-current"
    $branch = $branchResult.output.Trim()
    if ([string]::IsNullOrWhiteSpace($branch)) {
        $branch = "UNKNOWN"
        $blockers += "Could not determine current branch."
    }

    $branchResultText = if ($branch -eq $baseBranch) { "PASS" } else { "BLOCKED" }
    if ($branchResultText -ne "PASS") {
        $blockers += "Merge gate must run from $baseBranch, got $branch"
    }

    $statusResult = Invoke-NativeCommand -CommandName "git" -Arguments @("status", "--short", "--branch") -DisplayCommand "git status --short --branch"
    $statusLines = @($statusResult.lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $branchStatus = if ($statusLines.Count -gt 0) { [string] $statusLines[0] } else { "UNKNOWN" }
    $fileStatusLines = @($statusLines | Where-Object { -not $_.StartsWith("##") })
    $conflictLines = @($fileStatusLines | Where-Object { $_ -match "^(UU|AA|DD|AU|UA|DU|UD) " })
    if ($fileStatusLines.Count -gt 0) {
        $blockers += "Local working tree is not clean ($($fileStatusLines.Count) file status line(s))."
    }
    if ($conflictLines.Count -gt 0) {
        $blockers += "Merge conflicts detected ($($conflictLines.Count) file(s))."
    }
    if ($branchStatus -match "ahead\s+\d+" -or $branchStatus -match "behind\s+\d+") {
        $blockers += "Local branch is not cleanly synced with upstream: $branchStatus"
    }

    $approval = Read-ApprovalFile -Path $ApprovalPath
    if (-not $approval.exists) {
        $blockers += $approval.reason
    }
    elseif (-not $approval.valid) {
        $blockers += $approval.reason
    }
    elseif (-not $approval.approved) {
        $blockers += "Approval file does not say approved=true."
    }
    elseif ($approval.pr_number -ne $PrNumber) {
        $blockers += "Approval file PR number mismatch: expected $PrNumber, got $($approval.pr_number)"
    }

    $prViewResult = Invoke-NativeCommand `
        -CommandName "gh" `
        -Arguments @("pr", "view", "$PrNumber", "--json", "number,title,state,baseRefName,headRefName,mergeStateStatus,isDraft,reviewDecision,statusCheckRollup,url") `
        -DisplayCommand "gh pr view $PrNumber --json number,title,state,baseRefName,headRefName,mergeStateStatus,isDraft,reviewDecision,statusCheckRollup,url" `
        -AllowFailure

    $pr = $null
    $checks = @()
    $checkSummary = "unknown"
    if ($prViewResult.exit_code -ne 0) {
        $blockers += "GitHub PR state unavailable: $($prViewResult.output)"
    }
    else {
        try {
            $pr = $prViewResult.output | ConvertFrom-Json
            $rollup = if ($pr.PSObject.Properties["statusCheckRollup"]) { $pr.statusCheckRollup } else { @() }
            $checks = @(Convert-CheckRollup -StatusCheckRollup $rollup)
            $checkSummary = Get-CheckSummary -Checks $checks
        }
        catch {
            $blockers += "GitHub PR JSON parse failed: $($_.Exception.Message)"
        }
    }

    $prState = if ($null -ne $pr) { Get-ObjectValue -InputObject $pr -Names @("state") -Default "UNKNOWN" } else { "UNKNOWN" }
    $baseRef = if ($null -ne $pr) { Get-ObjectValue -InputObject $pr -Names @("baseRefName") -Default "UNKNOWN" } else { "UNKNOWN" }
    $headRef = if ($null -ne $pr) { Get-ObjectValue -InputObject $pr -Names @("headRefName") -Default "UNKNOWN" } else { "UNKNOWN" }
    $mergeState = if ($null -ne $pr) { Get-ObjectValue -InputObject $pr -Names @("mergeStateStatus") -Default "UNKNOWN" } else { "UNKNOWN" }
    $reviewDecision = if ($null -ne $pr) { Get-ObjectValue -InputObject $pr -Names @("reviewDecision") -Default "UNKNOWN" } else { "UNKNOWN" }
    $prUrl = if ($null -ne $pr) { Get-ObjectValue -InputObject $pr -Names @("url") -Default "" } else { "" }
    $isDraft = if ($null -ne $pr -and $pr.PSObject.Properties["isDraft"]) { [bool] $pr.isDraft } else { $false }

    if ($null -ne $pr) {
        if ($prState -ne "OPEN") {
            $blockers += "PR is not open: $prState"
        }
        if ($baseRef -ne $baseBranch) {
            $blockers += "PR base branch mismatch: expected $baseBranch, got $baseRef"
        }
        if ($isDraft) {
            $blockers += "PR is still draft."
        }
        if ($mergeState -in @("BLOCKED", "DIRTY", "UNKNOWN", "UNSTABLE")) {
            $blockers += "PR merge state is not ready: $mergeState"
        }
        if ($checkSummary -ne "success") {
            $blockers += "PR checks are not passing: $checkSummary"
        }
    }

    $gateState = if ($blockers.Count -gt 0) { "BLOCKED" } else { "READY_FOR_MERGE" }
    $safetyClassification = if ($gateState -eq "BLOCKED") { "BLOCKED" } else { "HUMAN_APPROVAL_REQUIRED" }
    $recommendedNextAction = if ($gateState -eq "BLOCKED") {
        "Resolve blockers before merge."
    }
    else {
        "Use a separately approved APPLY helper only after operator confirms merge approval remains current."
    }
    $stopCondition = if ($gateState -eq "BLOCKED") {
        "Stop before merge until blockers are resolved."
    }
    else {
        "Stop before mutation; DRY_RUN only."
    }

    $mergeAttempted = "NO"
    $mergeExitCode = $null
    $mergeOutput = ""
    $mergeOutput = "Merge skipped: this .DRY_RUN.ps1 helper is report-only."

    $packet = [pscustomobject] @{
        schema = "AIOS_PR_MERGE_GATE_PACKET.v1"
        generated_at = $generatedAt
        script = $scriptName
        mode = $mode
        pr_number = $PrNumber
        gate_state = $gateState
        safety_classification = $safetyClassification
        repo_identity = [pscustomobject] @{
            repo_path = $repoPath
            path_result = $repoPathResult
            remote_url = $remoteUrl
            remote_result = $remoteResult
            current_branch = $branch
            branch_result = $branchResultText
            local_status = $branchStatus
            local_change_count = $fileStatusLines.Count
            conflict_count = $conflictLines.Count
        }
        approval = [pscustomobject] @{
            path = $ApprovalPath
            exists = $approval.exists
            valid = $approval.valid
            approved = $approval.approved
            pr_number = $approval.pr_number
            reason = $approval.reason
        }
        pr_state = [pscustomobject] @{
            url = $prUrl
            state = $prState
            base_ref = $baseRef
            head_ref = $headRef
            is_draft = $isDraft
            merge_state_status = $mergeState
            review_decision = $reviewDecision
            check_summary = $checkSummary
            checks = @($checks)
        }
        blockers = @($blockers)
        merge = [pscustomobject] @{
            merge_attempted = $mergeAttempted
            merge_command = "Separate APPLY merge helper required."
            merge_exit_code = $mergeExitCode
            merge_output = $mergeOutput
        }
        recommended_next_action = $recommendedNextAction
        stop_condition = $stopCondition
        safety = [pscustomobject] @{
            files_edited = 0
            files_staged = 0
            commits_performed = 0
            pushes_performed = 0
            branch_switches = 0
            resets_performed = 0
            files_deleted = 0
            reports_written = 0
            merges_performed = if ($mergeAttempted -eq "YES" -and $mergeExitCode -eq 0) { 1 } else { 0 }
        }
    }

    if ($Json) {
        $jsonText = $packet | ConvertTo-Json -Depth 10
        $null = $jsonText | ConvertFrom-Json
        Write-Output $jsonText
    }
    else {
        Write-Output (Format-MarkdownReport -Packet $packet).TrimEnd()
    }
}
catch {
    Write-FailureRecovery `
        -WhatFailed "Unhandled error in PR merge gate." `
        -WhyItFailed $_.Exception.Message `
        -NextAction "Review the error and rerun this helper only after the local Git or GitHub state issue is corrected." `
        -Reference "AGENTS.md -> AI_OS Failure Recovery Response Rule; docs/workflows/AI_OS_PR_LANE_RUNNER.md" `
        -SafeCommandOrPrompt "No command recommended."
    exit 1
}
