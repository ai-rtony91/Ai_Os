<#
.SYNOPSIS
Evaluates AI_OS post-merge local-main sync state without mutating the repo.

.DESCRIPTION
Test-AiOsPostPushVerification.DRY_RUN.ps1 validates repo identity, branch
state, HEAD vs origin/main sync, working tree cleanliness, and optionally
confirms the PR is merged on GitHub. It classifies the result as
POST_MERGE_SYNCED, HUMAN_APPROVAL_REQUIRED, or BLOCKED.

This helper is DRY_RUN/report-only. It does not edit files, stage, commit,
push, switch branches, reset, clean files, or run automation scripts.

.PARAMETER ExpectedBranch
Expected branch for post-merge verification. Default is main.

.PARAMETER PrNumber
Optional GitHub PR number to verify merge state. When supplied, the script
queries gh pr view to confirm the PR was merged.

.PARAMETER Json
Emit JSON instead of the default Markdown report.

.EXAMPLE
.\automation\orchestration\post_push\Test-AiOsPostPushVerification.DRY_RUN.ps1

.EXAMPLE
.\automation\orchestration\post_push\Test-AiOsPostPushVerification.DRY_RUN.ps1 -PrNumber 241

.EXAMPLE
.\automation\orchestration\post_push\Test-AiOsPostPushVerification.DRY_RUN.ps1 -PrNumber 241 -Json
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string] $ExpectedBranch = "main",

    [Parameter(Mandatory = $false)]
    [ValidateRange(1, [int]::MaxValue)]
    [int] $PrNumber = 0,

    [Parameter(Mandatory = $false)]
    [switch] $Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptName = Split-Path -Leaf $PSCommandPath
$expectedRepoPath = "C:\Dev\Ai.Os"
$expectedRemoteUrl = "https://github.com/ai-rtony91/Ai_Os.git"

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
            -WhyItFailed "The post-merge verification gate needs '$CommandName' for state inspection." `
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
            -WhyItFailed "The post-merge verification gate could not collect required state." `
            -NextAction "Review the error, then rerun this helper after the issue is corrected." `
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

function Format-MarkdownReport {
    param([Parameter(Mandatory = $true)][pscustomobject] $Packet)

    $blockerText = if ($Packet.blockers.Count -gt 0) {
        ($Packet.blockers | ForEach-Object { "- $_" }) -join "`n"
    }
    else {
        "- none"
    }

    $prSection = ""
    if ($null -ne $Packet.pr_merge_state) {
        $prSection = @"

## PR Merge State
- PR: #$($Packet.pr_merge_state.pr_number)
- URL: $($Packet.pr_merge_state.url)
- State: $($Packet.pr_merge_state.state)
- Merge commit: $($Packet.pr_merge_state.merge_commit)
"@
    }

    return @"
# AI_OS Post-Merge Verification Gate

- Mode: DRY_RUN
- Gate state: $($Packet.gate_state)
- Safety: $($Packet.safety_classification)
- Generated: $($Packet.generated_at)

## Repo Identity
- Path: $($Packet.repo_identity.repo_path) [$($Packet.repo_identity.path_result)]
- Remote: $($Packet.repo_identity.remote_url) [$($Packet.repo_identity.remote_result)]

## Branch State
- Current: $($Packet.branch_state.current_branch)
- Expected: $($Packet.branch_state.expected_branch)
- Branch check: $($Packet.branch_state.branch_result)

## Sync State
- HEAD: $($Packet.sync_state.head_hash)
- origin/$($Packet.branch_state.expected_branch): $($Packet.sync_state.origin_main_hash)
- Sync: $($Packet.sync_state.sync_status)
- Latest commit: $($Packet.sync_state.latest_commit_message)
$prSection

## Git Status
- State: $($Packet.git_status.state)
- Dirty files: $($Packet.git_status.dirty_count)
- Untracked: $($Packet.git_status.untracked_count)
- Conflicts: $($Packet.git_status.conflict_count)

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

    $generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $blockers = @()

    # --- Repo identity ---
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

    # --- Branch state ---
    $branchResult = Invoke-NativeCommand -CommandName "git" -Arguments @("branch", "--show-current") -DisplayCommand "git branch --show-current"
    $branch = $branchResult.output.Trim()
    if ([string]::IsNullOrWhiteSpace($branch)) {
        $branch = "UNKNOWN"
        $blockers += "Could not determine current branch."
    }

    $branchCheck = if ($branch -eq $ExpectedBranch) { "PASS" } else { "BLOCKED" }
    if ($branchCheck -ne "PASS") {
        $blockers += "Branch mismatch: expected $ExpectedBranch, got $branch"
    }

    # --- HEAD and origin sync ---
    $headResult = Invoke-NativeCommand -CommandName "git" -Arguments @("rev-parse", "--short", "HEAD") -DisplayCommand "git rev-parse --short HEAD"
    $headFullResult = Invoke-NativeCommand -CommandName "git" -Arguments @("rev-parse", "HEAD") -DisplayCommand "git rev-parse HEAD"
    $messageResult = Invoke-NativeCommand -CommandName "git" -Arguments @("log", "-1", "--pretty=%s") -DisplayCommand "git log -1 --pretty=%s"

    $headHash = $headResult.output.Trim()
    $headFullHash = $headFullResult.output.Trim()
    $latestMessage = $messageResult.output.Trim()

    $originRef = "origin/$ExpectedBranch"
    $originResult = Invoke-NativeCommand -CommandName "git" -Arguments @("rev-parse", $originRef) -DisplayCommand "git rev-parse $originRef" -AllowFailure
    $originShortResult = Invoke-NativeCommand -CommandName "git" -Arguments @("rev-parse", "--short", $originRef) -DisplayCommand "git rev-parse --short $originRef" -AllowFailure

    $originAvailable = $originResult.exit_code -eq 0
    $originFullHash = if ($originAvailable) { $originResult.output.Trim() } else { "UNKNOWN" }
    $originHash = if ($originShortResult.exit_code -eq 0) { $originShortResult.output.Trim() } else { "UNKNOWN" }
    $headMatchesOrigin = $originAvailable -and ($headFullHash -eq $originFullHash)

    $syncStatus = if (-not $originAvailable) {
        "UNKNOWN"
    } elseif ($headMatchesOrigin) {
        "SYNCED"
    } else {
        "OUT_OF_SYNC"
    }

    if (-not $originAvailable) {
        $blockers += "$originRef ref is unavailable. Cannot verify sync state."
    } elseif (-not $headMatchesOrigin) {
        $blockers += "HEAD ($headHash) does not match $originRef ($originHash). Local main is not synced."
    }

    # --- Git status ---
    $statusResult = Invoke-NativeCommand -CommandName "git" -Arguments @("status", "--short") -DisplayCommand "git status --short"
    $statusLines = @($statusResult.lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $dirtyFiles = @($statusLines | Where-Object { -not $_.StartsWith("?? ") } | ForEach-Object {
        if ($_.Length -ge 4) { $_.Substring(3).Replace("\", "/") } else { $_ }
    })
    $untrackedFiles = @($statusLines | Where-Object { $_.StartsWith("?? ") } | ForEach-Object {
        if ($_.Length -ge 4) { $_.Substring(3).Replace("\", "/") } else { $_ }
    })
    $conflictLines = @($statusLines | Where-Object { $_ -match "^(UU|AA|DD|AU|UA|DU|UD) " })
    $gitState = if ($dirtyFiles.Count -eq 0 -and $conflictLines.Count -eq 0) { "clean" } else { "dirty" }

    if ($conflictLines.Count -gt 0) {
        $blockers += "Merge conflicts detected ($($conflictLines.Count) file(s))."
    }

    if ($dirtyFiles.Count -gt 0) {
        $blockers += "Working tree has $($dirtyFiles.Count) dirty file(s) after expected sync."
    }

    # --- Optional PR merge state ---
    $prMergeState = $null
    if ($PrNumber -gt 0) {
        Assert-CommandAvailable -CommandName "gh"

        $prViewResult = Invoke-NativeCommand `
            -CommandName "gh" `
            -Arguments @("pr", "view", "$PrNumber", "--json", "number,state,mergeCommit,url") `
            -DisplayCommand "gh pr view $PrNumber --json number,state,mergeCommit,url" `
            -AllowFailure

        if ($prViewResult.exit_code -ne 0) {
            $blockers += "Could not query PR #$PrNumber state: $($prViewResult.output)"
        } else {
            try {
                $pr = $prViewResult.output | ConvertFrom-Json

                $prState = Get-ObjectValue -InputObject $pr -Names @("state") -Default "UNKNOWN"
                $prUrl = Get-ObjectValue -InputObject $pr -Names @("url") -Default ""
                $mergeCommitObj = if ($null -ne $pr -and $pr.PSObject.Properties["mergeCommit"] -and $null -ne $pr.mergeCommit) {
                    $pr.mergeCommit
                } else {
                    $null
                }
                $mergeCommitOid = if ($null -ne $mergeCommitObj -and $mergeCommitObj.PSObject.Properties["oid"]) {
                    [string] $mergeCommitObj.oid
                } else {
                    "UNKNOWN"
                }

                $prMergeState = [pscustomobject] @{
                    pr_number    = $PrNumber
                    state        = $prState
                    url          = $prUrl
                    merge_commit = $mergeCommitOid
                }

                if ($prState -ne "MERGED") {
                    $blockers += "PR #$PrNumber is not merged: state=$prState"
                }
            }
            catch {
                $blockers += "PR #$PrNumber JSON parse failed: $($_.Exception.Message)"
            }
        }
    }

    # --- Classification ---
    $gateState = if ($blockers.Count -gt 0) { "BLOCKED" } else { "POST_MERGE_SYNCED" }
    $safetyClassification = if ($gateState -eq "BLOCKED") { "BLOCKED" } else { "SAFE_READ_ONLY" }

    $recommendedNextAction = if ($gateState -eq "POST_MERGE_SYNCED") {
        "Post-merge sync verified. Safe to proceed with next task or close PR lane."
    } else {
        "Resolve blockers before declaring post-merge sync complete."
    }

    $stopCondition = if ($gateState -eq "POST_MERGE_SYNCED") {
        "Verification complete. No mutation needed."
    } else {
        "Do not proceed until blockers are resolved and verification passes."
    }

    # --- Build packet ---
    $packet = [pscustomobject] @{
        schema                 = "AIOS_POST_MERGE_VERIFICATION_PACKET.v1"
        generated_at           = $generatedAt
        script                 = $scriptName
        mode                   = "DRY_RUN"
        gate_state             = $gateState
        safety_classification  = $safetyClassification
        repo_identity          = [pscustomobject] @{
            repo_path     = $repoPath
            path_result   = $repoPathResult
            remote_url    = $remoteUrl
            remote_result = $remoteResult
        }
        branch_state           = [pscustomobject] @{
            current_branch  = $branch
            expected_branch = $ExpectedBranch
            branch_result   = $branchCheck
        }
        sync_state             = [pscustomobject] @{
            head_hash             = $headHash
            head_full_hash        = $headFullHash
            origin_main_hash      = $originHash
            origin_main_full_hash = $originFullHash
            origin_main_available = $originAvailable
            head_matches_origin   = $headMatchesOrigin
            sync_status           = $syncStatus
            latest_commit_message = $latestMessage
        }
        git_status             = [pscustomobject] @{
            state           = $gitState
            dirty_count     = $dirtyFiles.Count
            untracked_count = $untrackedFiles.Count
            conflict_count  = $conflictLines.Count
            dirty_files     = @($dirtyFiles)
            untracked_files = @($untrackedFiles)
        }
        pr_merge_state         = $prMergeState
        blockers               = @($blockers)
        recommended_next_action = $recommendedNextAction
        stop_condition         = $stopCondition
        safety                 = [pscustomobject] @{
            files_edited      = 0
            files_staged      = 0
            commits_performed = 0
            pushes_performed  = 0
            branch_switches   = 0
            resets_performed   = 0
            files_deleted     = 0
            reports_written   = 0
        }
    }

    # --- Output ---
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
        -WhatFailed "Unhandled error in post-merge verification gate." `
        -WhyItFailed $_.Exception.Message `
        -NextAction "Review the error and rerun this helper after the issue is corrected." `
        -Reference "AGENTS.md -> AI_OS Failure Recovery Response Rule; docs/workflows/AI_OS_PR_LANE_RUNNER.md" `
        -SafeCommandOrPrompt "No command recommended."
    exit 1
}
