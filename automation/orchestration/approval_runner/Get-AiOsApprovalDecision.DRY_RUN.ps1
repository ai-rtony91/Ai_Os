[CmdletBinding()]
param(
    [string]$ValidationEvidencePath = "",
    [string]$WorkerReportPath = "",
    [string]$ApprovalReason = "",
    [string]$WorkerLanePath = "",
    [switch]$Json
)

$ErrorActionPreference = "Stop"

function Get-AiOsRepoRoot {
    $root = & git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($root)) {
        throw "Unable to find git repository root."
    }

    return $root.Trim()
}

function Add-AiOsRisk {
    param(
        [System.Collections.Generic.List[object]]$Risks,
        [ValidateSet("INFO", "WARN", "BLOCKED")][string]$Level,
        [string]$CheckId,
        [string]$Message,
        [string[]]$Evidence = @(),
        [string]$NextSafeAction = "Review this risk before approving APPLY."
    )

    $Risks.Add([pscustomobject]@{
        level = $Level
        check_id = $CheckId
        message = $Message
        evidence = @($Evidence)
        next_safe_action = $NextSafeAction
    }) | Out-Null
}

function Get-AiOsGitStatusLines {
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $lines = @(git status --short 2>$null)
    $ErrorActionPreference = $previousErrorActionPreference
    return $lines
}

function Convert-AiOsStatusLineToPath {
    param([string]$Line)

    if ([string]::IsNullOrWhiteSpace($Line) -or $Line.Length -lt 4) {
        return ""
    }

    $path = $Line.Substring(3).Trim()
    if ($path -match " -> ") {
        $path = ($path -split " -> ")[-1].Trim()
    }

    return ($path -replace "\\", "/")
}

function Test-AiOsReadableEvidence {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return $false
    }

    return Test-Path -LiteralPath $Path
}

function Test-AiOsPathPrefix {
    param(
        [string]$Path,
        [string]$Prefix
    )

    if ([string]::IsNullOrWhiteSpace($Path) -or [string]::IsNullOrWhiteSpace($Prefix)) {
        return $false
    }

    $normalizedPath = ($Path -replace "\\", "/").Trim("/")
    $normalizedPrefix = ($Prefix -replace "\\", "/").Trim("/")
    return ($normalizedPath -eq $normalizedPrefix -or $normalizedPath.StartsWith($normalizedPrefix + "/"))
}

$repoRoot = Get-AiOsRepoRoot
Set-Location -LiteralPath $repoRoot

$generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$risks = [System.Collections.Generic.List[object]]::new()
$statusLines = Get-AiOsGitStatusLines
$changedFiles = @($statusLines | ForEach-Object { Convert-AiOsStatusLineToPath -Line $_ } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$stagedFiles = @(git diff --cached --name-only 2>$null | ForEach-Object { $_ -replace "\\", "/" })
$ErrorActionPreference = $previousErrorActionPreference
$untrackedFiles = @($statusLines | Where-Object { $_ -like "??*" } | ForEach-Object { Convert-AiOsStatusLineToPath -Line $_ })

if ($changedFiles.Count -eq 0) {
    Add-AiOsRisk -Risks $risks -Level "INFO" -CheckId "git_status_cleanliness" -Message "Working tree is clean." -NextSafeAction "Continue approval review."
}
else {
    Add-AiOsRisk -Risks $risks -Level "WARN" -CheckId "git_status_cleanliness" -Message "Working tree has changed or untracked files." -Evidence $changedFiles -NextSafeAction "Review exact changed files before approving APPLY."
}

if ($stagedFiles.Count -gt 0) {
    Add-AiOsRisk -Risks $risks -Level "BLOCKED" -CheckId "staged_files" -Message "Staged files exist during approval review." -Evidence $stagedFiles -NextSafeAction "Unstage or review exact staged files before approval."
}
else {
    Add-AiOsRisk -Risks $risks -Level "INFO" -CheckId "staged_files" -Message "No staged files detected." -NextSafeAction "Continue approval review."
}

if ($untrackedFiles.Count -gt 0) {
    Add-AiOsRisk -Risks $risks -Level "WARN" -CheckId "untracked_files" -Message "Untracked files exist." -Evidence $untrackedFiles -NextSafeAction "Confirm each untracked file belongs to the approved packet before APPLY."
}
else {
    Add-AiOsRisk -Risks $risks -Level "INFO" -CheckId "untracked_files" -Message "No untracked files detected." -NextSafeAction "Continue approval review."
}

$protectedPatterns = @(
    "^README\.md$",
    "^RISK_POLICY\.md$",
    "^SOURCE_LOG\.md$",
    "^ERROR_LOG\.md$",
    "^HALLUCINATION_LOG\.md$",
    "^AAR\.md$",
    "^DAILY_REPORT\.md$",
    "^ARCHITECTURE\.md$",
    "^DEPLOYMENT\.md$",
    "^WHITEPAPER\.md$",
    "^\.codex_backups/",
    "^apps/dashboard/assets/"
)
$protectedHits = @($changedFiles | Where-Object {
    $path = $_
    @($protectedPatterns | Where-Object { $path -match $_ }).Count -gt 0
})

if ($protectedHits.Count -gt 0) {
    Add-AiOsRisk -Risks $risks -Level "BLOCKED" -CheckId "protected_path_risk" -Message "Protected path changes are present." -Evidence $protectedHits -NextSafeAction "Stop and request explicit protected-path approval."
}
else {
    Add-AiOsRisk -Risks $risks -Level "INFO" -CheckId "protected_path_risk" -Message "No protected path changes detected." -NextSafeAction "Continue approval review."
}

$liveHits = @($changedFiles | Where-Object { $_ -match "(?i)(broker|oanda|live[_-]?trading|api[_-]?key|secret|credential|webhook|real[_-]?order|\.env)" })
if ($liveHits.Count -gt 0) {
    Add-AiOsRisk -Risks $risks -Level "BLOCKED" -CheckId "broker_live_api_risk" -Message "Broker/live/API/secret-related paths are changed." -Evidence $liveHits -NextSafeAction "Stop. Do not approve APPLY until safety review is complete."
}
else {
    Add-AiOsRisk -Risks $risks -Level "INFO" -CheckId "broker_live_api_risk" -Message "No broker/live/API path changes detected." -NextSafeAction "Continue approval review."
}

if (Test-AiOsReadableEvidence -Path $ValidationEvidencePath) {
    Add-AiOsRisk -Risks $risks -Level "INFO" -CheckId "validation_evidence" -Message "Validation evidence path exists." -Evidence @($ValidationEvidencePath) -NextSafeAction "Review validation result before APPLY."
}
else {
    Add-AiOsRisk -Risks $risks -Level "WARN" -CheckId "validation_evidence" -Message "Validation evidence path is missing or was not supplied." -Evidence @($ValidationEvidencePath) -NextSafeAction "Run required validators and provide evidence before approval."
}

if (Test-AiOsReadableEvidence -Path $WorkerReportPath) {
    Add-AiOsRisk -Risks $risks -Level "INFO" -CheckId "worker_report" -Message "Worker report path exists." -Evidence @($WorkerReportPath) -NextSafeAction "Review worker report before approval."
}
else {
    Add-AiOsRisk -Risks $risks -Level "WARN" -CheckId "worker_report" -Message "Worker report path is missing or was not supplied." -Evidence @($WorkerReportPath) -NextSafeAction "Ask the worker for a report before approval."
}

if ([string]::IsNullOrWhiteSpace($ApprovalReason)) {
    Add-AiOsRisk -Risks $risks -Level "WARN" -CheckId "approval_reason" -Message "Approval reason is missing." -NextSafeAction "Write a plain-language approval reason before APPLY."
}
else {
    Add-AiOsRisk -Risks $risks -Level "INFO" -CheckId "approval_reason" -Message "Approval reason was supplied." -Evidence @($ApprovalReason) -NextSafeAction "Confirm the reason matches the packet scope."
}

if (-not [string]::IsNullOrWhiteSpace($WorkerLanePath)) {
    $laneChanged = @($changedFiles | Where-Object { Test-AiOsPathPrefix -Path $_ -Prefix $WorkerLanePath })
    if ($laneChanged.Count -gt 0) {
        Add-AiOsRisk -Risks $risks -Level "WARN" -CheckId "dirty_worker_lane" -Message "Worker lane has changed files." -Evidence $laneChanged -NextSafeAction "Review worker lane changes before approval."
    }
    else {
        Add-AiOsRisk -Risks $risks -Level "INFO" -CheckId "dirty_worker_lane" -Message "No dirty files detected in the supplied worker lane." -Evidence @($WorkerLanePath) -NextSafeAction "Continue approval review."
    }
}
else {
    Add-AiOsRisk -Risks $risks -Level "WARN" -CheckId "dirty_worker_lane" -Message "Worker lane path was not supplied, so lane cleanliness could not be checked." -NextSafeAction "Supply -WorkerLanePath for lane-specific review."
}

$blockedCount = @($risks | Where-Object { $_.level -eq "BLOCKED" }).Count
$warnCount = @($risks | Where-Object { $_.level -eq "WARN" }).Count
$infoCount = @($risks | Where-Object { $_.level -eq "INFO" }).Count

$decision = if ($blockedCount -gt 0) {
    "BLOCKED"
}
elseif ($warnCount -gt 0) {
    "REVIEW"
}
else {
    "SAFE"
}

$decisionLabel = switch ($decision) {
    "SAFE" { "SAFE TO APPLY" }
    "REVIEW" { "NEEDS REVIEW" }
    default { "BLOCKED" }
}

$nextSafeAction = switch ($decision) {
    "SAFE" { "Operator may consider APPLY only if the packet scope and approval reason are correct. No commit or push is approved by this checker." }
    "REVIEW" { "Resolve review warnings or explicitly accept them before approving APPLY. No commit or push is approved." }
    default { "Do not APPLY. Resolve blocked risks before approval, commit, or push." }
}

$report = [pscustomobject]@{
    schema = "AIOS_APPROVAL_DECISION_REPORT.v1"
    mode = "DRY_RUN"
    generated_at = $generatedAt
    repo_root = $repoRoot
    decision = $decision
    decision_label = $decisionLabel
    info_count = $infoCount
    warn_count = $warnCount
    blocked_count = $blockedCount
    changed_files = @($changedFiles)
    staged_files = @($stagedFiles)
    untracked_files = @($untrackedFiles)
    validation_evidence_path = $ValidationEvidencePath
    worker_report_path = $WorkerReportPath
    worker_lane_path = $WorkerLanePath
    approval_reason_supplied = -not [string]::IsNullOrWhiteSpace($ApprovalReason)
    risks = @($risks)
    files_changed_by_runner = @()
    commit_performed = $false
    push_performed = $false
    next_safe_action = $nextSafeAction
}

if (-not $Json) {
    Write-Host "AI_OS Approval Inbox Runner"
    Write-Host "Mode: DRY_RUN"
    Write-Host "Decision: $decisionLabel"
    Write-Host "Info: $infoCount  Warnings: $warnCount  Blocked: $blockedCount"
    Write-Host ""
    Write-Host "Risk list:"
    foreach ($risk in $risks) {
        Write-Host ("- {0}: {1} - {2}" -f $risk.level, $risk.check_id, $risk.message)
    }
    Write-Host ""
    Write-Host "Next safe action: $nextSafeAction"
    Write-Host ""
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    Write-Host ""
}

$report | ConvertTo-Json -Depth 12

if ($decision -eq "BLOCKED") {
    exit 1
}

exit 0
