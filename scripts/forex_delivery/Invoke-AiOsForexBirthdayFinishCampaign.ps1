[CmdletBinding()]
param(
    [ValidateSet("DRY_RUN", "APPLY")]
    [string]$Mode = "DRY_RUN",

    [string]$TargetDate = "2026-07-06"
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$BoardPath = "Reports/forex_delivery/AIOS_FOREX_BIRTHDAY_FINISH_BOARD_V1.json"
$ReportPath = "Reports/forex_delivery/AIOS_FOREX_BIRTHDAY_FINISH_CAMPAIGN_V1_REPORT.md"
$BoardFullPath = Join-Path $RepoRoot $BoardPath
$ReportFullPath = Join-Path $RepoRoot $ReportPath

$FinalOwnerSentence = "AIOS Forex repo build work remaining is 0; boundary work remaining is owner-protected 3, external-evidence 1, broker/live 1750, safety-blocked 25, deferred/stale 74; exact human session count is not stored unless a session ledger exists."

$SafetyRules = @(
    "No Git mutation.",
    "No network.",
    "No broker/API.",
    "No credentials.",
    "No account access.",
    "No trading.",
    "No scheduler/daemon/webhook/production/autonomy activation."
)

$ForbiddenActions = @(
    "git add",
    "git commit",
    "git push",
    "PR creation",
    "merge",
    "branch creation",
    "reset",
    "stash",
    "clean",
    "broad delete",
    "broker/API access",
    "credentials",
    "account access",
    "demo trade",
    "live trade",
    "order placement",
    "order closure",
    "money movement",
    "scheduler activation",
    "daemon activation",
    "webhook activation",
    "production activation",
    "autonomous trading",
    "claiming profitable trading readiness",
    "claiming autonomous trading readiness"
)

$SourceEvidence = @(
    "AGENTS.md",
    "README.md",
    "WHITEPAPER.md",
    "RISK_POLICY.md",
    "Reports/forex_delivery/AIOS_FOREX_FINAL_KNOWN_COUNTS_CAMPAIGN_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_FINAL_BOUNDARY_CLOSURE_CAMPAIGN_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_OWNER_BOUNDARY_ACTION_QUEUE_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_FINISH_SESSION_LEDGER_TEMPLATE_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_BOUNDARY_CLOSURE_FINAL_HANDOFF_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_ALL_LANES_GOALS_MANIFEST_V1.json"
)

$ExpectedCounts = [ordered]@{
    raw_goal_count = 1998
    repo_actionable_forex_lanes = 0
    repo_actionable_open_count = 0
    owner_protected_count = 3
    external_evidence_required_count = 1
    broker_live_boundary_count = 1750
    safety_blocked_count = 25
    deferred_or_stale_count = 74
}

function Get-RepoRelativeText {
    param(
        [Parameter(Mandatory)]
        [string]$RelativePath
    )

    $fullPath = Join-Path $RepoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        throw "Required source evidence is missing: $RelativePath"
    }

    return Get-Content -Raw -LiteralPath $fullPath
}

function Get-RequiredIntegerCount {
    param(
        [Parameter(Mandatory)]
        [string]$Text,

        [Parameter(Mandatory)]
        [string]$Key,

        [Parameter(Mandatory)]
        [int]$Expected
    )

    $pattern = "(?m)^\s*-\s*$([regex]::Escape($Key)):\s*(\d+)\s*$"
    $match = [regex]::Match($Text, $pattern)
    if (-not $match.Success) {
        throw "Required count was not found in source evidence: $Key"
    }

    $actual = [int]$match.Groups[1].Value
    if ($actual -ne $Expected) {
        throw "Count mismatch for $Key. Expected $Expected, observed $actual."
    }

    return $actual
}

function Get-RequiredStatus {
    param(
        [Parameter(Mandatory)]
        [string]$Text,

        [Parameter(Mandatory)]
        [string]$Key,

        [Parameter(Mandatory)]
        [string]$Expected
    )

    $pattern = "(?m)^\s*-\s*$([regex]::Escape($Key)):\s*([A-Z_]+)\s*$"
    $match = [regex]::Match($Text, $pattern)
    if (-not $match.Success) {
        throw "Required status was not found in source evidence: $Key"
    }

    $actual = $match.Groups[1].Value
    if ($actual -ne $Expected) {
        throw "Status mismatch for $Key. Expected $Expected, observed $actual."
    }

    return $actual
}

function Test-LedgerHasCompletedEntries {
    param(
        [Parameter(Mandatory)]
        [string]$LedgerText
    )

    $rows = $LedgerText -split "`r?`n" | Where-Object {
        $_ -match "^\|" -and
        $_ -notmatch "session_id" -and
        $_ -notmatch "---" -and
        $_.Trim() -ne ""
    }

    return @($rows).Count -gt 0
}

if ($TargetDate -notmatch "^\d{4}-\d{2}-\d{2}$") {
    throw "TargetDate must use yyyy-MM-dd format."
}

$evidenceText = [ordered]@{}
foreach ($relativePath in $SourceEvidence) {
    $evidenceText[$relativePath] = Get-RepoRelativeText -RelativePath $relativePath
}

$knownCountsText = $evidenceText["Reports/forex_delivery/AIOS_FOREX_FINAL_KNOWN_COUNTS_CAMPAIGN_V1_REPORT.md"]
$ledgerText = $evidenceText["Reports/forex_delivery/AIOS_FOREX_FINISH_SESSION_LEDGER_TEMPLATE_V1.md"]

$verifiedCounts = [ordered]@{}
foreach ($entry in $ExpectedCounts.GetEnumerator()) {
    $verifiedCounts[$entry.Key] = Get-RequiredIntegerCount -Text $knownCountsText -Key $entry.Key -Expected $entry.Value
}

$finalOperatingStatus = Get-RequiredStatus -Text $knownCountsText -Key "final_operating_status" -Expected "DEFERRED_OWNER_VALIDATION"
$ledgerHasCompletedEntries = Test-LedgerHasCompletedEntries -LedgerText $ledgerText

Push-Location $RepoRoot
try {
    $gitStatusLines = @(& git status --short --branch)
    $currentBranch = (& git branch --show-current).Trim()
    $remoteLines = @(& git remote -v)
}
finally {
    Pop-Location
}

$gitStatusLine = ""
if ($gitStatusLines.Count -gt 0) {
    $gitStatusLine = $gitStatusLines[0]
}

$gitClean = ($gitStatusLines.Count -eq 1 -and $gitStatusLine -like "## *")
$gitSyncedToOriginMain = ($gitStatusLine -eq "## main...origin/main")
$requiredFinalReports = @(
    "Reports/forex_delivery/AIOS_FOREX_FINAL_KNOWN_COUNTS_CAMPAIGN_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_FINAL_BOUNDARY_CLOSURE_CAMPAIGN_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_BOUNDARY_CLOSURE_FINAL_HANDOFF_V1_REPORT.md"
)
$requiredFinalReportsPresent = $true
foreach ($relativePath in $requiredFinalReports) {
    if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot $relativePath) -PathType Leaf)) {
        $requiredFinalReportsPresent = $false
    }
}

$finalBoundaryCampaign = "MISSING_EVIDENCE"
if ($requiredFinalReportsPresent) {
    $finalBoundaryCampaign = "COMPLETE"
}

$reportPublication = "INCOMPLETE"
if ($requiredFinalReportsPresent -and $currentBranch -eq "main" -and $gitClean -and $gitSyncedToOriginMain) {
    $reportPublication = "COMPLETE"
}

$exactHumanSessionCount = "LEDGER_REQUIRED"
if ($ledgerHasCompletedEntries) {
    $exactHumanSessionCount = "COMPLETE"
}

$terminalClassifications = [ordered]@{
    repo_actionable_lanes = "COMPLETE"
    final_boundary_campaign = $finalBoundaryCampaign
    report_publication = $reportPublication
    owner_protected_boundary = "OWNER_BOUNDARY"
    external_evidence_boundary = "OWNER_BOUNDARY"
    broker_live_boundary = "BROKER_BOUNDARY"
    safety_blocked_boundary = "SAFETY_BOUNDARY"
    deferred_stale_boundary = "DEFERRED_TRIAGE"
    exact_human_session_count = $exactHumanSessionCount
}

$boundaryCounts = [ordered]@{
    owner_protected_count = $verifiedCounts["owner_protected_count"]
    external_evidence_required_count = $verifiedCounts["external_evidence_required_count"]
    broker_live_boundary_count = $verifiedCounts["broker_live_boundary_count"]
    safety_blocked_count = $verifiedCounts["safety_blocked_count"]
    deferred_or_stale_count = $verifiedCounts["deferred_or_stale_count"]
}

$nextLawfulActions = @(
    [ordered]@{
        step = 1
        action = "Owner-protected boundary decision"
        classification = "OWNER_BOUNDARY"
        allowed_scope = "Owner review only"
    },
    [ordered]@{
        step = 2
        action = "External-evidence review"
        classification = "OWNER_BOUNDARY"
        allowed_scope = "Collect and review sanitized external evidence only"
    },
    [ordered]@{
        step = 3
        action = "Broker/live boundary review"
        classification = "BROKER_BOUNDARY"
        allowed_scope = "Permission readiness review only; no broker/API or account access"
    },
    [ordered]@{
        step = 4
        action = "Safety-blocker review"
        classification = "SAFETY_BOUNDARY"
        allowed_scope = "Review blockers without bypassing or weakening safety gates"
    },
    [ordered]@{
        step = 5
        action = "Deferred/stale triage"
        classification = "DEFERRED_TRIAGE"
        allowed_scope = "Classify items as keep, close, supersede, or later with source proof"
    },
    [ordered]@{
        step = 6
        action = "Final owner decision brief"
        classification = "OWNER_BOUNDARY"
        allowed_scope = "Owner decision only after boundary evidence is reviewed"
    }
)

$completionTruth = [ordered]@{
    repo_build_work_remaining = 0
    repo_actionable_forex_lanes = $verifiedCounts["repo_actionable_forex_lanes"]
    repo_actionable_open_count = $verifiedCounts["repo_actionable_open_count"]
    boundary_work_remaining = $boundaryCounts
    final_operating_status = $finalOperatingStatus
    remaining_progression_requires_human_owner_decision = $true
    exact_human_session_count_status = $exactHumanSessionCount
    blocked_from_complete_until_gates_satisfied = @(
        "owner_protected_boundary",
        "external_evidence_boundary",
        "broker_live_boundary",
        "safety_blocked_boundary",
        "deferred_stale_boundary"
    )
    broker_or_live_completion_claim_allowed = $false
    autonomy_completion_claim_allowed = $false
}

$board = [ordered]@{
    generated_at = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
    target_date = $TargetDate
    repo = [ordered]@{
        name = "ai-rtony91/Ai_Os"
        worktree = $RepoRoot
        remote = @($remoteLines)
    }
    branch = $currentBranch
    git_status = [ordered]@{
        observed_before_output_write = $true
        raw = @($gitStatusLines)
        clean = $gitClean
        synced_to_origin_main = $gitSyncedToOriginMain
    }
    raw_goal_count = $verifiedCounts["raw_goal_count"]
    repo_actionable_open_count = $verifiedCounts["repo_actionable_open_count"]
    terminal_classifications = $terminalClassifications
    boundary_counts = $boundaryCounts
    final_owner_sentence = $FinalOwnerSentence
    next_lawful_actions = $nextLawfulActions
    forbidden_actions = $ForbiddenActions
    completion_truth = $completionTruth
}

$sourceEvidenceMarkdown = ($SourceEvidence | ForEach-Object { "- $_" }) -join "`n"
$verifiedCountsMarkdown = ($verifiedCounts.GetEnumerator() | ForEach-Object { "- $($_.Key): $($_.Value)" }) -join "`n"
$terminalClassificationsMarkdown = ($terminalClassifications.GetEnumerator() | ForEach-Object { "- $($_.Key): $($_.Value)" }) -join "`n"
$boundaryQueueMarkdown = @(
    "- Owner-protected boundary: $($boundaryCounts["owner_protected_count"]) items; owner review only."
    "- External-evidence boundary: $($boundaryCounts["external_evidence_required_count"]) item; sanitized evidence review only."
    "- Broker/live boundary: $($boundaryCounts["broker_live_boundary_count"]) items; broker/live permission readiness review only."
    "- Safety-blocked boundary: $($boundaryCounts["safety_blocked_count"]) items; safety blocker review only."
    "- Deferred/stale boundary: $($boundaryCounts["deferred_or_stale_count"]) items; triage into keep, close, supersede, or later with source proof."
) -join "`n"
$nextLawfulActionsMarkdown = ($nextLawfulActions | ForEach-Object { "$($_.step). $($_.action): $($_.allowed_scope)" }) -join "`n"
$forbiddenActionsMarkdown = ($ForbiddenActions | ForEach-Object { "- $_" }) -join "`n"
$safetyRulesMarkdown = ($SafetyRules | ForEach-Object { "- $_" }) -join "`n"

$report = @"
# AIOS Forex Birthday Finish Campaign V1 Report

## Target Date

$TargetDate

Generated at: $($board.generated_at)

## Source Evidence

$sourceEvidenceMarkdown

## Verified Counts

$verifiedCountsMarkdown
- final_operating_status: $finalOperatingStatus

## Terminal Classifications

$terminalClassificationsMarkdown

Report publication is classified from the starting repo state: branch `main`, clean working tree, synced to `origin/main`, and required final campaign reports present.

## Completion Truth

- repo build work remaining: 0
- repo_actionable_forex_lanes: $($verifiedCounts["repo_actionable_forex_lanes"])
- repo_actionable_open_count: $($verifiedCounts["repo_actionable_open_count"])
- remaining progression requires human owner decision: true
- exact human session count status: $exactHumanSessionCount
- broker/live completion claim allowed: false
- autonomy completion claim allowed: false

## Boundary Queue

$boundaryQueueMarkdown

## Next Lawful Actions

$nextLawfulActionsMarkdown

## Forbidden Actions

$forbiddenActionsMarkdown

Safety rules:

$safetyRulesMarkdown

## Final Owner Sentence

$FinalOwnerSentence
"@

if ($Mode -eq "DRY_RUN") {
    Write-Host "AIOS Forex Birthday Finish Campaign DRY_RUN"
    Write-Host "DRY_RUN writes nothing."
    Write-Host "Target date: $TargetDate"
    Write-Host "Repo-actionable open count: $($verifiedCounts["repo_actionable_open_count"])"
    Write-Host "Final operating status: $finalOperatingStatus"
    Write-Host "Next lawful terminal step: owner-protected boundary decision."
    Write-Host $FinalOwnerSentence
    return
}

$reportsDirectory = Split-Path -Parent $BoardFullPath
if (-not (Test-Path -LiteralPath $reportsDirectory -PathType Container)) {
    throw "Reports directory is missing: $reportsDirectory"
}

$boardJson = $board | ConvertTo-Json -Depth 12
Set-Content -LiteralPath $BoardFullPath -Value $boardJson -Encoding utf8
Set-Content -LiteralPath $ReportFullPath -Value $report -Encoding utf8

Write-Host "AIOS Forex Birthday Finish Campaign APPLY"
Write-Host "Wrote: $BoardPath"
Write-Host "Wrote: $ReportPath"
Write-Host "Target date: $TargetDate"
Write-Host $FinalOwnerSentence
