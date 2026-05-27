param(
    [int]$Pr = 0,
    [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function ConvertTo-AiOsJson {
    param([object]$Value)
    return ($Value | ConvertTo-Json -Depth 12)
}

function Write-AiOsResult {
    param([object]$Result)

    if ($Json) {
        Write-Output (ConvertTo-AiOsJson -Value $Result)
        return
    }

    Write-Host "AI_OS PR Finisher Preview" -ForegroundColor Cyan
    Write-Host ("PR: {0}" -f $Result.pr_number)
    Write-Host ("State: {0}" -f $Result.pr_state)
    Write-Host ("Head branch: {0}" -f $Result.head_branch)
    Write-Host ("Base branch: {0}" -f $Result.base_branch)
    Write-Host ("Checks: {0}" -f $Result.checks_state)
    Write-Host ("Merge preview: {0}" -f $Result.merge_preview.status)
    Write-Host ("Local sync preview: {0}" -f $Result.local_sync_preview.status)
    Write-Host ("Branch delete preview: {0}" -f $Result.local_branch_delete_preview.status)
    Write-Host ("Next safe action: {0}" -f $Result.next_safe_action)
}

function New-AiOsPreviewPacket {
    param(
        [int]$PrNumber,
        [string]$PrState = "UNKNOWN",
        [string]$HeadBranch = "",
        [string]$BaseBranch = "",
        [string]$ChecksState = "NOT_RUN",
        [object]$MergePreview,
        [object]$LocalSyncPreview,
        [object]$LocalBranchDeletePreview,
        [string[]]$StopConditions,
        [string]$NextSafeAction,
        [object[]]$Evidence = @()
    )

    return [ordered]@{
        schema                      = "AIOS_PR_FINISHER_PREVIEW.v1"
        mode                        = "DRY_RUN"
        execution_enabled           = $false
        pr_number                   = $PrNumber
        pr_state                    = $PrState
        head_branch                 = $HeadBranch
        base_branch                 = $BaseBranch
        checks_state                = $ChecksState
        merge_preview               = $MergePreview
        local_sync_preview          = $LocalSyncPreview
        local_branch_delete_preview = $LocalBranchDeletePreview
        blocked_actions             = @(
            "gh pr merge execution",
            "merge execution",
            "branch deletion execution",
            "git reset execution",
            "git pull execution",
            "git push execution",
            "git checkout execution",
            "git switch execution",
            "--admin",
            "--force",
            "--delete-branch",
            "secrets",
            "broker/OANDA/live trading/webhook scope"
        )
        stop_conditions             = $StopConditions
        evidence                    = $Evidence
        next_safe_action            = $NextSafeAction
    }
}

function New-AiOsBlockedPreview {
    param(
        [int]$PrNumber,
        [string]$Reason,
        [object[]]$Evidence = @()
    )

    return New-AiOsPreviewPacket `
        -PrNumber $PrNumber `
        -PrState "BLOCKED" `
        -ChecksState "NOT_RUN" `
        -MergePreview ([ordered]@{
            status  = "BLOCKED"
            reason  = $Reason
            command = ""
        }) `
        -LocalSyncPreview ([ordered]@{
            status   = "BLOCKED"
            reason   = $Reason
            commands = @()
        }) `
        -LocalBranchDeletePreview ([ordered]@{
            status        = "BLOCKED"
            reason        = $Reason
            target_branch = ""
            command       = ""
        }) `
        -StopConditions @($Reason, "DRY_RUN preview only; no repository mutation executed.") `
        -NextSafeAction "Provide a valid, non-draft PR targeting main with passing checks." `
        -Evidence $Evidence
}

function Invoke-AiOsReadOnlyCommand {
    param(
        [string]$FilePath,
        [string[]]$ArgumentList
    )

    $output = & $FilePath @ArgumentList 2>&1
    $exitCode = $LASTEXITCODE

    return [ordered]@{
        command   = (($FilePath, $ArgumentList) -join " ")
        exit_code = $exitCode
        output    = @($output)
    }
}

function Get-AiOsChecksState {
    param([object[]]$StatusCheckRollup)

    if (-not $StatusCheckRollup -or $StatusCheckRollup.Count -eq 0) {
        return "UNKNOWN"
    }

    $pending = $false
    $failed = $false

    foreach ($check in $StatusCheckRollup) {
        $status = ""
        $conclusion = ""

        if ($null -ne $check.status) {
            $status = [string]$check.status
        }
        if ($null -ne $check.conclusion) {
            $conclusion = [string]$check.conclusion
        }

        if ($status -and $status -ne "COMPLETED") {
            $pending = $true
        }

        if ($conclusion -and @("SUCCESS", "NEUTRAL", "SKIPPED") -notcontains $conclusion) {
            $failed = $true
        }
    }

    if ($failed) {
        return "FAILED"
    }
    if ($pending) {
        return "PENDING"
    }

    return "SUCCESS"
}

function Test-AiOsLocalBranch {
    param([string]$BranchName)

    if ([string]::IsNullOrWhiteSpace($BranchName)) {
        return $false
    }

    $branchOutput = & git branch --list $BranchName 2>$null
    return (@($branchOutput).Count -gt 0)
}

if ($Pr -le 0) {
    $result = New-AiOsBlockedPreview -PrNumber $Pr -Reason "PR number must be a positive integer."
    Write-AiOsResult -Result $result
    exit 0
}

$ghEvidence = Invoke-AiOsReadOnlyCommand -FilePath "gh" -ArgumentList @(
    "pr",
    "view",
    [string]$Pr,
    "--json",
    "number,state,headRefName,baseRefName,mergeStateStatus,isDraft,statusCheckRollup,url"
)

if ($ghEvidence.exit_code -ne 0) {
    $result = New-AiOsBlockedPreview `
        -PrNumber $Pr `
        -Reason "Unable to read PR metadata with gh pr view." `
        -Evidence @($ghEvidence)
    Write-AiOsResult -Result $result
    exit 0
}

try {
    $prInfo = (($ghEvidence.output -join "`n") | ConvertFrom-Json)
}
catch {
    $result = New-AiOsBlockedPreview `
        -PrNumber $Pr `
        -Reason "Unable to parse gh pr view JSON output." `
        -Evidence @($ghEvidence)
    Write-AiOsResult -Result $result
    exit 0
}

$prState = [string]$prInfo.state
$headBranch = [string]$prInfo.headRefName
$baseBranch = [string]$prInfo.baseRefName
$checksState = Get-AiOsChecksState -StatusCheckRollup @($prInfo.statusCheckRollup)
$isDraft = [bool]$prInfo.isDraft
$currentBranch = (& git branch --show-current 2>$null)
$localBranchExists = Test-AiOsLocalBranch -BranchName $headBranch

$stopConditions = @("DRY_RUN preview only; no repository mutation executed.")
$nextSafeAction = "Review preview output before any separate approval-gated PR finish action."

if ($baseBranch -ne "main") {
    $stopConditions += "PR base branch is not main."
}

if ($isDraft) {
    $stopConditions += "Draft PRs cannot be finished."
}

if ($checksState -ne "SUCCESS" -and $prState -ne "MERGED") {
    $stopConditions += "Checks must be successful before merge preview."
}

$mergePreview = [ordered]@{
    status  = "BLOCKED"
    reason  = "PR does not meet merge preview requirements."
    command = ""
}

if ($prState -eq "MERGED") {
    $mergePreview = [ordered]@{
        status  = "SKIPPED_ALREADY_MERGED"
        reason  = "PR is already merged; only local sync and cleanup preview remain."
        command = ""
    }
}
elseif ($baseBranch -eq "main" -and -not $isDraft -and $checksState -eq "SUCCESS") {
    $mergePreview = [ordered]@{
        status  = "READY_FOR_APPROVAL"
        reason  = "Checks are successful. This is a preview only; merge still requires explicit human approval."
        command = ("gh pr merge {0} --squash" -f $Pr)
    }
}
elseif ($checksState -eq "PENDING") {
    $mergePreview = [ordered]@{
        status  = "WAITING_FOR_CHECKS"
        reason  = "Checks are still pending."
        command = ("gh pr checks {0} --watch" -f $Pr)
    }
}
elseif ($checksState -eq "FAILED") {
    $mergePreview = [ordered]@{
        status  = "BLOCKED_FAILED_CHECKS"
        reason  = "Checks failed."
        command = ""
    }
}

$localSyncStatus = "AFTER_MERGE_ONLY"
if ($prState -eq "MERGED") {
    $localSyncStatus = "READY_FOR_APPROVAL"
}

$localSyncPreview = [ordered]@{
    status   = $localSyncStatus
    reason   = "Local sync preview only. No git switch, pull, reset, or fetch is executed by this helper."
    commands = @(
        "git switch main",
        "git pull",
        "git status --short --branch"
    )
}

$deleteStatus = "AFTER_MERGE_ONLY"
$deleteReason = "Branch cleanup should only happen after merge and local sync approval."
$deleteCommand = ""

if ([string]::IsNullOrWhiteSpace($headBranch)) {
    $deleteStatus = "BLOCKED"
    $deleteReason = "PR head branch is missing."
}
elseif ($headBranch -eq "main") {
    $deleteStatus = "BLOCKED"
    $deleteReason = "Refusing to target main for local branch deletion."
}
elseif ($currentBranch -eq $headBranch) {
    $deleteStatus = "BLOCKED_CURRENT_BRANCH"
    $deleteReason = "Refusing to preview deletion of the currently checked out branch."
}
elseif (-not $localBranchExists) {
    $deleteStatus = "ALREADY_CLEAN"
    $deleteReason = "Matching local branch is not present."
}
elseif ($prState -eq "MERGED") {
    $deleteStatus = "READY_FOR_APPROVAL"
    $deleteReason = "Matching local branch exists and PR is merged. Deletion still requires explicit approval."
    $deleteCommand = ("git branch -d {0}" -f $headBranch)
}

$localBranchDeletePreview = [ordered]@{
    status        = $deleteStatus
    reason        = $deleteReason
    target_branch = $headBranch
    command       = $deleteCommand
}

$result = New-AiOsPreviewPacket `
    -PrNumber $Pr `
    -PrState $prState `
    -HeadBranch $headBranch `
    -BaseBranch $baseBranch `
    -ChecksState $checksState `
    -MergePreview $mergePreview `
    -LocalSyncPreview $localSyncPreview `
    -LocalBranchDeletePreview $localBranchDeletePreview `
    -StopConditions $stopConditions `
    -NextSafeAction $nextSafeAction `
    -Evidence @([ordered]@{
        pr_url              = [string]$prInfo.url
        merge_state_status  = [string]$prInfo.mergeStateStatus
        current_branch      = [string]$currentBranch
        local_branch_exists = [bool]$localBranchExists
    })

Write-AiOsResult -Result $result
