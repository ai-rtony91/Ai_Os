<#
.SYNOPSIS
Exports an AI_OS PR handoff packet to the console.

.DESCRIPTION
Export-AIOSPrHandoff.ps1 collects pull request state from GitHub CLI and
local Git state from read-only Git commands, then prints Markdown and/or JSON
handoff packets to the console. It performs zero repo mutations.

The helper is DRY_RUN/report-only. It does not stage, commit, push, merge,
switch branches, delete branches, clean files, or write reports to disk.

.PARAMETER PrNumber
Required GitHub pull request number to inspect.

.PARAMETER Format
Output format. Valid values are Markdown, JSON, or Both. Default is Both.

.PARAMETER Mode
Execution mode. Only DRY_RUN is supported. Default is DRY_RUN.

.EXAMPLE
.\automation\orchestration\Export-AIOSPrHandoff.ps1 -PrNumber 196 -Format Both -Mode DRY_RUN

.EXAMPLE
.\automation\orchestration\Export-AIOSPrHandoff.ps1 -PrNumber 196 -Format Markdown -Mode DRY_RUN

.EXAMPLE
.\automation\orchestration\Export-AIOSPrHandoff.ps1 -PrNumber 196 -Format JSON -Mode DRY_RUN
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateRange(1, [int]::MaxValue)]
    [int] $PrNumber,

    [Parameter(Mandatory = $false)]
    [ValidateSet("Markdown", "JSON", "Both")]
    [string] $Format = "Both",

    [Parameter(Mandatory = $false)]
    [ValidateSet("DRY_RUN")]
    [string] $Mode = "DRY_RUN"
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
    param(
        [Parameter(Mandatory = $true)]
        [string] $CommandName
    )

    $command = Get-Command $CommandName -ErrorAction SilentlyContinue
    if (-not $command) {
        Write-FailureRecovery `
            -WhatFailed "Required command '$CommandName' was not found." `
            -WhyItFailed "The PR handoff exporter depends on '$CommandName' to collect read-only state." `
            -NextAction "Install or authenticate the required tool, then rerun this DRY_RUN helper." `
            -Reference "AGENTS.md -> AI_OS Failure Recovery Response Rule; docs/workflows/AI_OS_PR_HANDOFF_REPORTER.md" `
            -SafeCommandOrPrompt "No command recommended."
        exit 1
    }
}

function Invoke-ReadOnlyCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string] $CommandName,

        [Parameter(Mandatory = $true)]
        [string[]] $Arguments,

        [Parameter(Mandatory = $true)]
        [string] $DisplayCommand
    )

    $output = & $CommandName @Arguments 2>&1
    $exitCode = $LASTEXITCODE

    if ($exitCode -ne 0) {
        $message = ($output | Out-String).Trim()
        Write-FailureRecovery `
            -WhatFailed "Command failed: $DisplayCommand`n$message" `
            -WhyItFailed "The helper could not collect the required read-only handoff state." `
            -NextAction "Review the command error, confirm the PR number and tool authentication, then rerun in DRY_RUN mode." `
            -Reference "docs/workflows/AI_OS_PR_HANDOFF_REPORTER.md; AGENTS.md -> AI_OS Failure Recovery Response Rule" `
            -SafeCommandOrPrompt "No command recommended."
        exit 1
    }

    return ($output | Out-String).Trim()
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
    if ($null -eq $StatusCheckRollup) {
        return $checks
    }

    foreach ($check in @($StatusCheckRollup)) {
        $checks += [pscustomobject] @{
            workflow = Get-ObjectValue -InputObject $check -Names @("workflowName", "workflow", "appName") -Default "UNKNOWN"
            name = Get-ObjectValue -InputObject $check -Names @("name", "context") -Default "UNKNOWN"
            status = Get-ObjectValue -InputObject $check -Names @("status", "state") -Default "UNKNOWN"
            conclusion = Get-ObjectValue -InputObject $check -Names @("conclusion") -Default "UNKNOWN"
        }
    }

    return $checks
}

function Format-MarkdownHandoff {
    param(
        [Parameter(Mandatory = $true)]
        [pscustomobject] $Packet
    )

    $checkLines = @()
    foreach ($check in @($Packet.checks)) {
        $checkLines += "- Workflow: $($check.workflow)"
        $checkLines += "  Check name: $($check.name)"
        $checkLines += "  Status: $($check.status)"
        $checkLines += "  Conclusion: $($check.conclusion)"
    }

    if ($checkLines.Count -eq 0) {
        $checkLines += "- Workflow: UNKNOWN"
        $checkLines += "  Check name: UNKNOWN"
        $checkLines += "  Status: UNKNOWN"
        $checkLines += "  Conclusion: UNKNOWN"
    }

    return @"
# AI_OS PR Handoff

## PR
- Number: $($Packet.pr.number)
- URL: $($Packet.pr.url)
- Title: $($Packet.pr.title)
- Base branch: $($Packet.pr.base_branch)
- Head branch: $($Packet.pr.head_branch)
- PR state: $($Packet.pr.state)
- Merge state: $($Packet.pr.merge_state)
- Mergeable: $($Packet.pr.mergeable)

## Checks
$($checkLines -join "`n")

## Merge And Cleanup
- Merge result: $($Packet.merge_and_cleanup.merge_result)
- Local branch cleanup: $($Packet.merge_and_cleanup.local_branch_cleanup)
- Remote branch cleanup: $($Packet.merge_and_cleanup.remote_branch_cleanup)
- Local current branch: $($Packet.merge_and_cleanup.local_current_branch)
- Local main sync: $($Packet.merge_and_cleanup.local_main_sync_status)
- Known untracked backlog: $($Packet.merge_and_cleanup.known_untracked_backlog_status)

## Next Safe Action
- $($Packet.next_safe_action)

## Timestamp
- $($Packet.timestamp)
"@
}

try {
    if ($Mode -ne "DRY_RUN") {
        Write-FailureRecovery `
            -WhatFailed "Unsupported mode: $Mode" `
            -WhyItFailed "This helper is report-only and supports DRY_RUN mode only." `
            -NextAction "Rerun with -Mode DRY_RUN." `
            -Reference "docs/workflows/AI_OS_PR_HANDOFF_REPORTER.md" `
            -SafeCommandOrPrompt ".\automation\orchestration\Export-AIOSPrHandoff.ps1 -PrNumber $PrNumber -Format $Format -Mode DRY_RUN"
        exit 1
    }

    Assert-CommandAvailable -CommandName "gh"
    Assert-CommandAvailable -CommandName "git"

    $prJson = Invoke-ReadOnlyCommand `
        -CommandName "gh" `
        -Arguments @("pr", "view", [string] $PrNumber, "--json", "number,title,state,mergeStateStatus,mergeable,statusCheckRollup,headRefName,baseRefName,url") `
        -DisplayCommand "gh pr view $PrNumber --json number,title,state,mergeStateStatus,mergeable,statusCheckRollup,headRefName,baseRefName,url"

    try {
        $pr = $prJson | ConvertFrom-Json
    }
    catch {
        Write-FailureRecovery `
            -WhatFailed "GitHub CLI returned JSON that could not be parsed for PR #$PrNumber." `
            -WhyItFailed $_.Exception.Message `
            -NextAction "Confirm GitHub CLI output for the PR, then rerun this helper." `
            -Reference "docs/workflows/AI_OS_PR_HANDOFF_REPORTER.md" `
            -SafeCommandOrPrompt "No command recommended."
        exit 1
    }

    $gitStatus = Invoke-ReadOnlyCommand `
        -CommandName "git" `
        -Arguments @("status", "--short", "--branch") `
        -DisplayCommand "git status --short --branch"

    $currentBranch = Invoke-ReadOnlyCommand `
        -CommandName "git" `
        -Arguments @("branch", "--show-current") `
        -DisplayCommand "git branch --show-current"

    $lastCommit = Invoke-ReadOnlyCommand `
        -CommandName "git" `
        -Arguments @("log", "-1", "--oneline") `
        -DisplayCommand "git log -1 --oneline"

    $statusLines = @($gitStatus -split "(`r`n|`n|`r)" | Where-Object { $_ -ne "" })
    $branchStatus = "UNKNOWN"
    if ($statusLines.Count -gt 0) {
        $branchStatus = $statusLines[0]
    }

    $hasUntracked = $false
    foreach ($line in $statusLines) {
        if ($line.StartsWith("??")) {
            $hasUntracked = $true
            break
        }
    }

    $knownBacklog = "none"
    if ($hasUntracked) {
        $knownBacklog = "exists; not enumerated; do not stage or treat as a new emergency"
    }

    $mergeResult = "UNKNOWN"
    if ($pr.state -eq "MERGED" -or $pr.state -eq "merged") {
        $mergeResult = "merged"
    }
    elseif ($pr.state -eq "OPEN" -or $pr.state -eq "open") {
        $mergeResult = "not merged"
    }
    elseif ($pr.state) {
        $mergeResult = [string] $pr.state
    }

    $packet = [pscustomobject] @{
        pr = [pscustomobject] @{
            number = $pr.number
            url = $pr.url
            title = $pr.title
            base_branch = $pr.baseRefName
            head_branch = $pr.headRefName
            state = $pr.state
            merge_state = $pr.mergeStateStatus
            mergeable = $pr.mergeable
        }
        checks = @(Convert-CheckRollup -StatusCheckRollup $pr.statusCheckRollup)
        merge_and_cleanup = [pscustomobject] @{
            merge_result = $mergeResult
            local_branch_cleanup = "UNKNOWN"
            remote_branch_cleanup = "UNKNOWN"
            local_current_branch = $currentBranch
            local_main_sync_status = "$branchStatus; latest local commit: $lastCommit"
            known_untracked_backlog_status = $knownBacklog
        }
        next_safe_action = "Use this structured handoff as context for the next assigned AI_OS lane."
        timestamp = (Get-Date).ToString("o")
    }

    $json = $packet | ConvertTo-Json -Depth 12
    $null = $json | ConvertFrom-Json

    if ($Format -eq "Markdown" -or $Format -eq "Both") {
        Write-Output (Format-MarkdownHandoff -Packet $packet)
    }

    if ($Format -eq "Both") {
        Write-Output ""
        Write-Output "---"
        Write-Output ""
    }

    if ($Format -eq "JSON" -or $Format -eq "Both") {
        Write-Output $json
    }
}
catch {
    Write-FailureRecovery `
        -WhatFailed "Unhandled error while exporting PR handoff for PR #$PrNumber." `
        -WhyItFailed $_.Exception.Message `
        -NextAction "Review the error, confirm required tools and PR number, then rerun in DRY_RUN mode." `
        -Reference "AGENTS.md -> AI_OS Failure Recovery Response Rule; docs/workflows/AI_OS_PR_HANDOFF_REPORTER.md" `
        -SafeCommandOrPrompt "No command recommended."
    exit 1
}
