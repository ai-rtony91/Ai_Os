param(
    [Parameter(Mandatory = $true)][string]$PacketId,
    [Parameter(Mandatory = $true)][string]$Branch,
    [string]$CommitHash = "",
    [string[]]$FilesChanged = @(),
    [string]$TestsRun = "",
    [string[]]$TestsBlocked = @(),
    [string[]]$ValidationResults = @(),
    [string[]]$SafetyFlags = @(),
    [string]$CodexReportPath = "",
    [string]$CodexReportText = "",
    [switch]$OutputJson,
    [switch]$AsPromptBlock
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Read-JsonSafe {
    param([string]$Text, [string]$Source)
    if ([string]::IsNullOrWhiteSpace($Text)) {
        return [pscustomobject]@{
            _aios_parse_error = "JSON payload was empty."
            _aios_source = $Source
        }
    }

    try {
        return $Text | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        return [pscustomobject]@{
            _aios_parse_error = $_.Exception.Message
            _aios_source = $Source
        }
    }
}

function Get-CodexPayload {
    param([string]$Path, [string]$Text)

    $reportText = ""
    if (-not [string]::IsNullOrWhiteSpace($Text)) {
        $reportText = $Text
    }
    elseif (-not [string]::IsNullOrWhiteSpace($Path)) {
        if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
            throw "CodexReportPath not found: $Path"
        }
        $reportText = Get-Content -LiteralPath $Path -Raw
    }

    if ([string]::IsNullOrWhiteSpace($reportText)) {
        return [pscustomobject]@{
            source = "inline-parameters-only"
            parsed = [pscustomobject]@{}
        }
    }

    $payload = Read-JsonSafe -Text $reportText -Source "Codex report"
    return [pscustomobject]@{
        source = "json"
        parsed = $payload
    }
}

function To-StringArray {
    param($Value)
    if ($null -eq $Value) { return @() }
    if ($Value -is [string]) { return @([string]$Value) }
    if ($Value -is [System.Collections.IEnumerable]) { return @($Value) }
    return @([string]$Value)
}

$gitRootRaw = $null
try {
    $gitRootRaw = git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($gitRootRaw)) {
        $gitRootRaw = ""
    }
}
catch {
    $gitRootRaw = ""
}

if ([string]::IsNullOrWhiteSpace($gitRootRaw)) {
    $gitRootRaw = (Get-Location).Path
}
$repoRoot = $gitRootRaw.Trim()

$gitStatusRaw = @(git -C $repoRoot status --short --untracked-files=all 2>$null)
$dirtyCount = $gitStatusRaw.Count
$workingTreeClean = ($dirtyCount -eq 0)

$report = Get-CodexPayload -Path $CodexReportPath -Text $CodexReportText
$payload = $report.parsed

if ($payload -and -not (Get-Member -InputObject $payload -Name "_aios_parse_error" -MemberType NoteProperty)) {
    if ([string]::IsNullOrWhiteSpace($CommitHash) -and (Get-Member -InputObject $payload -Name "commit_hash" -MemberType NoteProperty)) {
        $CommitHash = [string]$payload.commit_hash
    }
    if ((Get-Member -InputObject $payload -Name "files_changed" -MemberType NoteProperty)) {
        $FilesChanged = @(To-StringArray -Value $payload.files_changed)
    }
    if ([string]::IsNullOrWhiteSpace($TestsRun) -and (Get-Member -InputObject $payload -Name "tests_run" -MemberType NoteProperty)) {
        $TestsRun = [string]$payload.tests_run
    }
    if ((Get-Member -InputObject $payload -Name "tests_blocked" -MemberType NoteProperty)) {
        $TestsBlocked = @(To-StringArray -Value $payload.tests_blocked)
    }
    if ((Get-Member -InputObject $payload -Name "validation_results" -MemberType NoteProperty)) {
        $ValidationResults = @(To-StringArray -Value $payload.validation_results)
    }
    if ((Get-Member -InputObject $payload -Name "safety_flags" -MemberType NoteProperty)) {
        $SafetyFlags = @(To-StringArray -Value $payload.safety_flags)
    }
}

$reportSummary = [ordered]@{
    packet_id = $PacketId
    branch = $Branch
    commit_hash = $CommitHash
    files_changed = @($FilesChanged)
    tests_run = $TestsRun
    tests_blocked = @($TestsBlocked)
    validation_results = @($ValidationResults)
    safety_flags = @($SafetyFlags)
    working_tree_clean = $workingTreeClean
    dirty_or_untracked_count = $dirtyCount
    requested_next_action = "Review result, then if safe generate a reviewed PowerShell execution request."
}

$safetyClaims = @(
    "No broker/OANDA/webhook/order/secrets changes."
    "No runtime, worker, scheduler, daemon, queue, approval inbox, telemetry, dashboard, backup, or Cloudflare mutation."
    "Command must be reviewed by ChatGPT and pasted by Anthony only."
)

$validationClaims = @(
    "Repository state validated: clean check performed."
    "Branch/state validation is required before running remote commands."
)

$requestedChatGptReview = "Please review this packet handoff payload for safe execution, repo state, and path scope. ChatGPT must review this report and confirm the next approved action before any execution."

$requestedPowerShellOutput = @"
# CHATGPT REVIEW REQUEST FOR POWERHELL
# packet_id: $PacketId
# branch: $Branch
# commit_hash: $CommitHash
# files_changed: $($reportSummary.files_changed -join ', ')
#
# PowerShell block only after confirming safety and repo state:
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/pr_lifecycle/Invoke-AiOsReviewedPrLifecycle.DRY_RUN.ps1 -AnthonyReviewed -Title `"`" -Body `"`" -HeadBranch `"$Branch`" -WatchChecks -AnthonyApprovedMerge
"@

$requestedPowerShellOutput = $requestedPowerShellOutput.Trim()

$output = [ordered]@{
    schema = "AIOS_CODEX_REPORT_CHATGPT_REVIEW_REQUEST.v1"
    mode = "DRY_RUN_READ_ONLY"
    packet_id = $PacketId
    branch = $Branch
    report_summary = $reportSummary
    safety_claims = @($safetyClaims)
    validation_claims = @($validationClaims)
    requested_chatgpt_review = $requestedChatGptReview
    requested_powerShell_output = $requestedPowerShellOutput
    must_not_execute_without_anthony = $true
    can_continue_without_anthony = $false
    writes_files = $false
    next_blocked_if_not_reviewed = "Stop until a human-approved ChatGPT-reviewed block is pasted by Anthony."
}

if ($AsPromptBlock) {
    $payloadText = $output | ConvertTo-Json -Depth 20
    Write-Output "```powershell"
    Write-Output "Codex report handoff JSON:"
    Write-Output $payloadText
    Write-Output "```
"
    Write-Output "ChatGPT must review this report and return a PowerShell block only after checking safety and repo state."
    exit 0
}

if ($OutputJson) {
    $output | ConvertTo-Json -Depth 20
    exit 0
}

Write-Output ($output | ConvertTo-Json -Depth 20)
