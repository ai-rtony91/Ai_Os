<#
.SYNOPSIS
Evaluates AI_OS PR creation readiness and optionally creates the pull request.

.DESCRIPTION
Open-AiOsPullRequest.DRY_RUN.ps1 validates repo identity, branch state, and
local changes before creating a GitHub pull request. In DRY_RUN mode it reports
what would happen without mutating anything.

This helper validates: repo path, remote URL, current branch is not base,
no merge conflicts, git diff --check passes, and optionally generates a PR
body from the commit log when none is supplied.

.PARAMETER Title
PR title. Required.

.PARAMETER Body
PR body text. When omitted, an auto-generated body is built from the commit
log between base and HEAD.

.PARAMETER BaseBranch
Target branch for the PR. Default is main.

.PARAMETER Json
Emit JSON instead of the default Markdown report.

.EXAMPLE
.\automation\orchestration\pr_gates\Open-AiOsPullRequest.DRY_RUN.ps1 -Title "Add feature X"

.EXAMPLE
.\automation\orchestration\pr_gates\Open-AiOsPullRequest.DRY_RUN.ps1 -Title "Add feature X" -Body "Custom body" -Json
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $Title,

    [Parameter(Mandatory = $false)]
    [string] $Body = "",

    [Parameter(Mandatory = $false)]
    [string] $BaseBranch = "main",

    [Parameter(Mandatory = $false)]
    [switch] $Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptName = Split-Path -Leaf $PSCommandPath
$mode = "DRY_RUN"

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
            -WhyItFailed "The PR creation gate needs '$CommandName' for state inspection." `
            -NextAction "Install or restore '$CommandName', then rerun this helper." `
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
            -WhyItFailed "The PR creation gate could not collect required state." `
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

try {
    Assert-CommandAvailable -CommandName "git"

    $timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $blockers = @()

    # --- Repo identity ---
    $repoTopLevelResult = Invoke-ReadOnlyCommand -CommandName "git" -Arguments @("rev-parse", "--show-toplevel") -DisplayCommand "git rev-parse --show-toplevel"
    $repoPath = $repoTopLevelResult.output.Trim().Replace("/", "\")
    $repoPathResult = if ($repoPath -ieq "C:\Dev\Ai.Os") { "PASS" } else { "BLOCKED" }
    if ($repoPathResult -ne "PASS") {
        $blockers += "Repo path mismatch: expected C:\Dev\Ai.Os, got $repoPath"
    }

    $remoteUrlResult = Invoke-ReadOnlyCommand -CommandName "git" -Arguments @("remote", "get-url", "origin") -DisplayCommand "git remote get-url origin" -AllowFailure
    $remoteUrl = if ($remoteUrlResult.exit_code -eq 0) { $remoteUrlResult.output.Trim() } else { "NOT_CONFIGURED" }
    $remoteResult = if ($remoteUrl -eq "https://github.com/ai-rtony91/Ai_Os.git") { "PASS" } else { "BLOCKED" }
    if ($remoteResult -ne "PASS") {
        $blockers += "Remote mismatch: expected https://github.com/ai-rtony91/Ai_Os.git, got $remoteUrl"
    }

    # --- Branch state ---
    $branchResult = Invoke-ReadOnlyCommand -CommandName "git" -Arguments @("branch", "--show-current") -DisplayCommand "git branch --show-current"
    $branch = $branchResult.output.Trim()
    if ([string]::IsNullOrWhiteSpace($branch)) {
        $branch = "UNKNOWN"
        $blockers += "Could not determine current branch."
    }

    if ($branch -eq $BaseBranch) {
        $blockers += "Current branch ($branch) is the same as base branch ($BaseBranch). Cannot create PR from base branch."
    }

    # --- Conflict check ---
    $statusResult = Invoke-ReadOnlyCommand -CommandName "git" -Arguments @("status", "--short", "--branch") -DisplayCommand "git status --short --branch"
    $statusLines = @($statusResult.lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $fileStatusLines = @($statusLines | Where-Object { -not $_.StartsWith("##") })
    $conflictLines = @($fileStatusLines | Where-Object { $_ -match "^(UU|AA|DD|AU|UA|DU|UD) " })
    if ($conflictLines.Count -gt 0) {
        $blockers += "Merge conflicts detected ($($conflictLines.Count) file(s))."
    }

    # --- diff --check ---
    $diffCheckResult = Invoke-ReadOnlyCommand -CommandName "git" -Arguments @("diff", "--check") -DisplayCommand "git diff --check" -AllowFailure
    $diffCheckPassed = $diffCheckResult.exit_code -eq 0
    if (-not $diffCheckPassed) {
        $blockers += "git diff --check failed: whitespace or conflict marker issues."
    }

    # --- Ahead/behind ---
    $branchStatus = if ($statusLines.Count -gt 0) { [string] $statusLines[0] } else { "UNKNOWN" }
    $aheadCount = 0
    $behindCount = 0
    if ($branchStatus -match 'ahead\s+(\d+)') { $aheadCount = [int]$Matches[1] }
    if ($branchStatus -match 'behind\s+(\d+)') { $behindCount = [int]$Matches[1] }

    if ($behindCount -gt 0) {
        $blockers += "Branch is behind upstream by $behindCount commit(s). Sync before creating PR."
    }

    # --- Commit log for auto body ---
    $commitLogResult = Invoke-ReadOnlyCommand -CommandName "git" -Arguments @("log", "--oneline", "$BaseBranch..HEAD") -DisplayCommand "git log --oneline $BaseBranch..HEAD" -AllowFailure
    $commitLines = @($commitLogResult.lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $commitCount = $commitLines.Count

    if ($commitCount -eq 0 -and $blockers.Count -eq 0) {
        $blockers += "No commits ahead of $BaseBranch. Nothing to create a PR for."
    }

    # --- Auto-generate body if not supplied ---
    $bodySource = "user_supplied"
    $resolvedBody = $Body
    if ([string]::IsNullOrWhiteSpace($resolvedBody)) {
        $bodySource = "auto_generated"
        $sb = [System.Text.StringBuilder]::new()
        $null = $sb.AppendLine("## Summary")
        $null = $sb.AppendLine("")
        foreach ($cl in ($commitLines | Select-Object -First 20)) {
            $null = $sb.AppendLine("- $cl")
        }
        if ($commitLines.Count -gt 20) {
            $null = $sb.AppendLine("- ... and $($commitLines.Count - 20) more commit(s)")
        }
        $null = $sb.AppendLine("")
        $null = $sb.AppendLine("---")
        $null = $sb.AppendLine("Generated by AI_OS PR creation gate ($scriptName)")
        $resolvedBody = $sb.ToString().TrimEnd()
    }

    # --- Safety classification ---
    $safetyClassification = "HUMAN_APPROVAL_REQUIRED"
    if ($blockers.Count -gt 0) {
        $safetyClassification = "BLOCKED"
    }

    $gateState = if ($blockers.Count -gt 0) { "BLOCKED" } else { "READY" }

    # --- PR creation blocked in DRY_RUN ---
    $prCreated = $false
    $prUrl = ""
    $prError = ""
    $prError = "PR creation skipped: this .DRY_RUN.ps1 helper is report-only."

    # --- Build packet ---
    $packet = [pscustomobject] @{
        schema                = "AIOS_PR_CREATE_GATE_PACKET.v2"
        generated_at          = $timestamp
        mode                  = $mode
        gate_state            = $gateState
        safety_classification = $safetyClassification
        repo_identity         = [pscustomobject] @{
            repo_path   = $repoPath
            path_result = $repoPathResult
            remote_url  = $remoteUrl
            remote_result = $remoteResult
        }
        branch_state          = [pscustomobject] @{
            current_branch = $branch
            base_branch    = $BaseBranch
            ahead_count    = $aheadCount
            behind_count   = $behindCount
            commit_count   = $commitCount
            diff_check     = if ($diffCheckPassed) { "PASS" } else { "FAIL" }
            conflicts      = $conflictLines.Count
        }
        pr_details            = [pscustomobject] @{
            title       = $Title
            body_source = $bodySource
            body_length = $resolvedBody.Length
            pr_created  = $prCreated
            pr_url      = $prUrl
        }
        blockers              = @($blockers)
        recommended_next_action = if ($gateState -eq "BLOCKED") {
            "Resolve blockers before creating PR."
        } elseif ($mode -eq "DRY_RUN") {
            "Use a separately approved APPLY helper to create the pull request."
        } else {
            "PR created. Monitor checks and request review."
        }
        safety                = [pscustomobject] @{
            files_edited       = 0
            files_staged       = 0
            commits_performed  = 0
            pushes_performed   = 0
            branch_switches    = 0
            prs_created        = if ($prCreated) { 1 } else { 0 }
        }
    }

    # --- Output ---
    if ($Json) {
        $jsonText = $packet | ConvertTo-Json -Depth 10
        $null = $jsonText | ConvertFrom-Json
        Write-Output $jsonText
    } else {
        $sb = [System.Text.StringBuilder]::new()
        $null = $sb.AppendLine("# AI_OS PR Creation Gate")
        $null = $sb.AppendLine("")
        $null = $sb.AppendLine("- Mode: $mode")
        $null = $sb.AppendLine("- Gate state: $gateState")
        $null = $sb.AppendLine("- Safety: $safetyClassification")
        $null = $sb.AppendLine("- Generated: $timestamp")
        $null = $sb.AppendLine("")
        $null = $sb.AppendLine("## Repo Identity")
        $null = $sb.AppendLine("- Path: $repoPath [$repoPathResult]")
        $null = $sb.AppendLine("- Remote: $remoteUrl [$remoteResult]")
        $null = $sb.AppendLine("")
        $null = $sb.AppendLine("## Branch State")
        $null = $sb.AppendLine("- Branch: $branch -> $BaseBranch")
        $null = $sb.AppendLine("- Ahead: $aheadCount / Behind: $behindCount")
        $null = $sb.AppendLine("- Commits: $commitCount")
        $null = $sb.AppendLine("- diff --check: $(if ($diffCheckPassed) { 'PASS' } else { 'FAIL' })")
        $null = $sb.AppendLine("- Conflicts: $($conflictLines.Count)")
        $null = $sb.AppendLine("")
        $null = $sb.AppendLine("## PR Details")
        $null = $sb.AppendLine("- Title: $Title")
        $null = $sb.AppendLine("- Body source: $bodySource ($($resolvedBody.Length) chars)")
        if ($prCreated) {
            $null = $sb.AppendLine("- PR created: YES")
            $null = $sb.AppendLine("- PR URL: $prUrl")
        } else {
            $null = $sb.AppendLine("- PR created: NO")
        }
        if ($blockers.Count -gt 0) {
            $null = $sb.AppendLine("")
            $null = $sb.AppendLine("## Blockers")
            foreach ($b in $blockers) {
                $null = $sb.AppendLine("- $b")
            }
        }
        $null = $sb.AppendLine("")
        $null = $sb.AppendLine("## Next Action")
        $null = $sb.AppendLine("- $($packet.recommended_next_action)")
        $null = $sb.AppendLine("")
        $null = $sb.AppendLine("---")
        $null = $sb.AppendLine("Commit performed: NO")
        $null = $sb.AppendLine("Push performed: NO")

        Write-Output $sb.ToString().TrimEnd()
    }
}
catch {
    Write-FailureRecovery `
        -WhatFailed "Unhandled error in PR creation gate." `
        -WhyItFailed $_.Exception.Message `
        -NextAction "Review the error and rerun this helper after the issue is corrected." `
        -Reference "AGENTS.md -> AI_OS Failure Recovery Response Rule; docs/workflows/AI_OS_PR_LANE_RUNNER.md" `
        -SafeCommandOrPrompt "No command recommended."
    exit 1
}
