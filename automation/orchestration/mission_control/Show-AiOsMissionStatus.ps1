param(
    [switch]$Detailed
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$exportScript = Join-Path $scriptRoot "Export-AiOsMissionState.ps1"
$border = "=" * 100

function Write-Section {
    param(
        [Parameter(Mandatory = $true)][string]$Title,
        [string]$Color = "Cyan"
    )

    Write-Host ""
    Write-Host "== $Title ==" -ForegroundColor $Color
}

function Get-RiskColor {
    param([Parameter(Mandatory = $true)][string]$Risk)

    switch ($Risk) {
        "SAFE" { "Green" }
        "WATCH" { "Yellow" }
        "WARNING" { "Yellow" }
        "BLOCKED" { "Red" }
        default { "Gray" }
    }
}

function Get-LaneColor {
    param([Parameter(Mandatory = $true)][string]$Lane)

    switch ($Lane) {
        "COMMAND DECK" { "Magenta" }
        "BUILD ENGINE" { "Green" }
        "VALIDATION DECK" { "Cyan" }
        default { "Gray" }
    }
}

if (-not (Test-Path -LiteralPath $exportScript -PathType Leaf)) {
    throw "Mission state exporter not found: $exportScript"
}

$state = (& $exportScript | ConvertFrom-Json)
$riskColor = Get-RiskColor -Risk $state.risk
$laneColor = Get-LaneColor -Lane $state.recommended_lane

$Host.UI.RawUI.WindowTitle = "AI_OS MISSION CONTROL"

Write-Host $border -ForegroundColor Cyan
Write-Host "AI_OS MISSION CONTROL" -ForegroundColor Cyan
Write-Host "$(if ($Detailed) { 'Detailed mode.' } else { 'Simple mode.' }) Unified read-only operations status." -ForegroundColor Gray
Write-Host $border -ForegroundColor Cyan
Write-Host ""

Write-Host "Risk: $($state.risk)" -ForegroundColor $riskColor
Write-Host "Recommended lane: $($state.recommended_lane)" -ForegroundColor $laneColor
Write-Host "Exact next safe action: $($state.next_safe_action)" -ForegroundColor Yellow
Write-Host "Reason: $($state.reason)" -ForegroundColor Gray
Write-Host "Repo: $(if ($state.repo_state.clean) { 'CLEAN' } else { 'DIRTY' }) on $($state.repo_state.branch)" -ForegroundColor $(if ($state.repo_state.clean) { "Green" } else { "Yellow" })
Write-Host "GitHub: $(if ($state.github_state.gh_available) { 'AVAILABLE' } else { 'LOCAL-ONLY FALLBACK' })" -ForegroundColor $(if ($state.github_state.gh_available) { "Green" } else { "Yellow" })

if (-not $Detailed) {
    Write-Host ""
    Write-Host "Run with -Detailed for validation, stale, queue, recovery, routing, and blocked-state details." -ForegroundColor Gray
    return
}

Write-Section -Title "Repo State"
Write-Host "Repo root: $($state.repo_state.repo_root)" -ForegroundColor Gray
Write-Host "Branch: $($state.repo_state.branch)" -ForegroundColor Cyan
Write-Host "Changed files: $($state.repo_state.changed_files)" -ForegroundColor Gray
Write-Host "Untracked files: $($state.repo_state.untracked_files)" -ForegroundColor Gray
Write-Host "Latest commit: $($state.repo_state.latest_commit)" -ForegroundColor Gray
if ($state.repo_state.status_lines.Count -eq 0) {
    Write-Host "No changed or untracked files." -ForegroundColor Gray
} else {
    foreach ($line in @($state.repo_state.status_lines)) {
        Write-Host "  $line" -ForegroundColor Gray
    }
}

Write-Section -Title "GitHub State"
Write-Host "gh available: $($state.github_state.gh_available)" -ForegroundColor Gray
Write-Host "Open issues: $($state.github_state.open_issues)" -ForegroundColor Gray
Write-Host "Open PRs: $($state.github_state.open_prs)" -ForegroundColor Gray
Write-Host "Current branch PRs: $($state.github_state.current_branch_prs)" -ForegroundColor Gray
if ($state.github_state.local_only_fallback) {
    Write-Host "Reason: $($state.github_state.unavailable_reason)" -ForegroundColor Yellow
}

Write-Section -Title "Validation State"
Write-Host "git diff needed: $($state.validation_state.git_diff_needed)" -ForegroundColor Gray
Write-Host "JSON validation needed: $($state.validation_state.json_validation_needed)" -ForegroundColor Gray
Write-Host "PowerShell validation needed: $($state.validation_state.powershell_validation_needed)" -ForegroundColor Gray
Write-Host "Repo clean check needed: $($state.validation_state.repo_clean_check_needed)" -ForegroundColor Gray

Write-Section -Title "Routing State"
Write-Host "Command Deck needed: $($state.routing_state.command_deck_needed)" -ForegroundColor Magenta
Write-Host "Build Engine needed: $($state.routing_state.build_engine_needed)" -ForegroundColor Green
Write-Host "Validation Deck needed: $($state.routing_state.validation_deck_needed)" -ForegroundColor Cyan

Write-Section -Title "Queue And Recovery Awareness"
Write-Host "Visible queue files: $($state.queue_awareness.visible_queue_files.Count)" -ForegroundColor Gray
Write-Host "Visible recovery files: $($state.recovery_awareness.visible_recovery_files.Count)" -ForegroundColor Gray

Write-Section -Title "Stale And Approval State"
Write-Host "Stale branch review needed: $($state.stale_state.stale_branch_review_needed)" -ForegroundColor Gray
Write-Host "Issue without PR review needed: $($state.stale_state.issue_without_pr_review_needed)" -ForegroundColor Gray
Write-Host "PR without merge review needed: $($state.stale_state.pr_without_merge_review_needed)" -ForegroundColor Gray
Write-Host "Approval needed: $($state.approval_state.approval_needed)" -ForegroundColor Gray
Write-Host "Validation needed: $($state.approval_state.validation_needed)" -ForegroundColor Gray
Write-Host "Merge needed: $($state.approval_state.merge_needed)" -ForegroundColor Gray

Write-Section -Title "Blocked State" -Color Red
Write-Host "Blocked: $($state.blocked_state.blocked)" -ForegroundColor $(if ($state.blocked_state.blocked) { "Red" } else { "Green" })
if ($state.blocked_state.blocked_files.Count -gt 0) {
    foreach ($file in @($state.blocked_state.blocked_files)) {
        Write-Host "  $file" -ForegroundColor Red
    }
}

Write-Section -Title "Telemetry Readiness"
Write-Host "Telemetry ready: $($state.telemetry_ready)" -ForegroundColor Green
Write-Host "Dashboard ready: $($state.dashboard_ready)" -ForegroundColor Green
