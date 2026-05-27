param(
    [ValidateSet("commit", "push", "merge")]
    [string]$Action = "commit",
    [string[]]$CandidateFile = @(),
    [ValidateSet("PASS", "REVIEW", "FAIL", "BLOCKED", "UNKNOWN")]
    [string]$ValidatorResult = "UNKNOWN",
    [ValidateSet("HIGH", "MEDIUM", "LOW", "BLOCKED", "UNKNOWN")]
    [string]$RuntimeConfidence = "UNKNOWN",
    [string]$RuntimeBundlePath = "",
    [int]$MinimumConfidenceScore = 90,
    [ValidateSet("PASS", "PENDING", "FAIL", "MISSING", "UNKNOWN")]
    [string]$PrChecksStatus = "UNKNOWN",
    [switch]$Json
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Get-GitStatusLines {
    $output = & git status --short --branch 2>&1
    return @($output | ForEach-Object { [string]$_ })
}

function Convert-StatusLineToPath {
    param([string]$Line)

    if ([string]::IsNullOrWhiteSpace($Line) -or $Line.Length -lt 4 -or $Line.StartsWith("##")) {
        return ""
    }

    $path = $Line.Substring(3).Trim()
    if ($path -match " -> ") {
        $path = ($path -split " -> ")[-1].Trim()
    }

    return ($path -replace "\\", "/")
}

function Normalize-PathText {
    param([string]$Path)
    return (($Path -replace "\\", "/").Trim().Trim("/"))
}

function Read-JsonSafe {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path) -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            parse_error = $_.Exception.Message
            path = $Path
        }
    }
}

function Test-PathPrefix {
    param(
        [string]$Path,
        [string]$Prefix
    )

    $normalizedPath = Normalize-PathText -Path $Path
    $normalizedPrefix = Normalize-PathText -Path $Prefix
    return ($normalizedPath -eq $normalizedPrefix -or $normalizedPath.StartsWith($normalizedPrefix + "/"))
}

function Test-AnyPathPrefix {
    param(
        [string]$Path,
        [string[]]$Prefixes
    )

    foreach ($prefix in $Prefixes) {
        if (Test-PathPrefix -Path $Path -Prefix $prefix) {
            return $true
        }
    }

    return $false
}

$safeAutoAllowedClasses = @(
    "docs_only_updates_inside_approved_non_protected_paths",
    "generated_reports",
    "validator_evidence_files",
    "telemetry_ledgers",
    "approved_packet_completion_records",
    "non_protected_workflow_notes"
)

$humanRequiredClasses = @(
    "protected_files",
    "AGENTS.md",
    "README.md",
    "security_docs",
    "governance_doctrine_changes",
    "package_install_dependency_changes",
    "dashboard_code",
    "trading_logic",
    "live_trading_broker_api_keys_orders_credentials_webhooks",
    "merge_conflicts",
    "failed_validators",
    "unknown_files",
    "broad_untracked_backlog",
    "direct_push_to_main"
)

$validatorRequirements = @(
    "git diff --check PASS",
    "changed PowerShell parse PASS",
    "changed JSON parse PASS",
    "allowed paths PASS",
    "blocked paths PASS",
    "no secrets PASS",
    "no live trading or broker enablement PASS",
    "commit package exact-file review PASS",
    "runtime bundle confidence HIGH",
    "runtime bundle path supplied",
    "runtime bundle generated from trusted non-example evidence",
    "PR checks PASS before merge",
    "auto-git decision SAFE_AUTO_ALLOWED"
)

$stopConditions = @(
    "validator result is not PASS",
    "runtime confidence is not HIGH",
    "runtime bundle path is missing",
    "runtime bundle evidence is missing, stale, mock, example, or unverifiable",
    "PR checks are required and not PASS",
    "merge conflict or unmerged file is present",
    "protected path is present",
    "unknown or broad untracked backlog is present",
    "candidate file list is empty",
    "candidate file is outside SAFE_AUTO_ALLOWED classes",
    "direct push to main is requested",
    "live trading, broker, API key, order, credential, webhook, or secret path is present"
)

$safePathPrefixes = @(
    "Reports/",
    "automation/orchestration/reports/",
    "automation/orchestration/validators/VALIDATOR_CHAIN_RUNBOOK_001.md",
    "automation/orchestration/work_packets/complete/",
    "work_packets/examples/",
    "work_packets/state/"
)

$protectedPathPrefixes = @(
    "AGENTS.md",
    "README.md",
    "docs/governance/",
    "docs/security/",
    "automation/orchestration/policy/",
    "automation/orchestration/validators/",
    "automation/orchestration/validator_chain_runner/",
    "schemas/aios/orchestration/",
    "apps/",
    "services/",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "secrets/",
    "credentials/",
    ".env"
)

$blockedPathPattern = "(?i)(broker|oanda|live[_-]?trading|api[_-]?key|secret|credential|webhook|real[_-]?order|order[_-]?execution)"

$runtimeBundle = Read-JsonSafe -Path $RuntimeBundlePath
$runtimeBundleConfidenceScore = $null
$validatorConfidenceScore = $null
$requiredBundleSectionsPresent = $false
$bundleStopConditions = @()
$runtimeEvidenceTrusted = $false

if ([string]::IsNullOrWhiteSpace($RuntimeBundlePath)) {
    $RuntimeConfidence = "BLOCKED"
    $ValidatorResult = "BLOCKED"
    $bundleStopConditions += "runtime bundle path missing"
}
elseif ($runtimeBundle) {
    if ($runtimeBundle.parse_error) {
        $RuntimeConfidence = "BLOCKED"
        $bundleStopConditions += "runtime bundle parse failure"
    }
    else {
        if ($runtimeBundle.confidence_state -and $runtimeBundle.confidence_state.overall_confidence) {
            $RuntimeConfidence = [string]$runtimeBundle.confidence_state.overall_confidence
        }
        if ($runtimeBundle.confidence_state -and $null -ne $runtimeBundle.confidence_state.confidence_score) {
            $runtimeBundleConfidenceScore = [int]$runtimeBundle.confidence_state.confidence_score
        }
        if ($runtimeBundle.validator_confidence) {
            if ($runtimeBundle.validator_confidence.overall_result) {
                $ValidatorResult = if ($runtimeBundle.validator_confidence.overall_result -eq "REVIEW_REQUIRED") { "REVIEW" } else { [string]$runtimeBundle.validator_confidence.overall_result }
            }
            if ($null -ne $runtimeBundle.validator_confidence.confidence_score) {
                $validatorConfidenceScore = [int]$runtimeBundle.validator_confidence.confidence_score
            }
        }
        if ($runtimeBundle.auto_git_eligibility -and $runtimeBundle.auto_git_eligibility.stop_conditions) {
            $bundleStopConditions += @($runtimeBundle.auto_git_eligibility.stop_conditions | ForEach-Object { [string]$_ })
        }
        $requiredBundleSectionsPresent = [bool](
            $runtimeBundle.packet_state -and
            $runtimeBundle.worker_state -and
            $runtimeBundle.lock_state -and
            $runtimeBundle.validator_state -and
            $runtimeBundle.approval_state -and
            $runtimeBundle.git_state -and
            $runtimeBundle.confidence_state -and
            $runtimeBundle.validator_confidence
        )
        $runtimeEvidenceTrusted = [bool](
            $runtimeBundle.required_evidence_present -and
            $runtimeBundle.required_evidence_present.validator_confidence -eq $true -and
            $runtimeBundle.bundle_integrity -and
            $runtimeBundle.bundle_integrity.status -eq "PASS" -and
            $runtimeBundle.auto_git_eligibility -and
            $runtimeBundle.auto_git_eligibility.safe_auto_allowed -eq $true
        )
    }
}
else {
    $RuntimeConfidence = "BLOCKED"
    $ValidatorResult = "BLOCKED"
    $bundleStopConditions += "runtime bundle missing or unreadable"
}

$gitStatus = Get-GitStatusLines
$statusPaths = @($gitStatus | ForEach-Object { Convert-StatusLineToPath -Line $_ } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$untrackedPaths = @($gitStatus | Where-Object { $_ -like "??*" } | ForEach-Object { Convert-StatusLineToPath -Line $_ } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$conflictLines = @($gitStatus | Where-Object { $_ -match "^(UU|AA|DD|AU|UA|DU|UD) " })

$candidateFiles = @($CandidateFile | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { Normalize-PathText -Path $_ } | Select-Object -Unique)

$reviewFindings = New-Object System.Collections.Generic.List[string]
$blockedFindings = New-Object System.Collections.Generic.List[string]

if ($candidateFiles.Count -eq 0) {
    $blockedFindings.Add("No candidate files were supplied; auto-git will not infer candidates from git status.") | Out-Null
}

if ([string]::IsNullOrWhiteSpace($RuntimeBundlePath)) {
    $blockedFindings.Add("Runtime bundle path is required for SAFE_AUTO_ALLOWED eligibility.") | Out-Null
}
elseif ($null -eq $runtimeBundle) {
    $blockedFindings.Add("Runtime bundle evidence is missing or unreadable.") | Out-Null
}
elseif (-not $runtimeEvidenceTrusted) {
    $blockedFindings.Add("Runtime bundle does not prove trusted SAFE_AUTO_ALLOWED evidence.") | Out-Null
}

if ($ValidatorResult -ne "PASS") {
    $blockedFindings.Add("Validator result is $ValidatorResult, not PASS.") | Out-Null
}

if ($RuntimeConfidence -ne "HIGH") {
    $blockedFindings.Add("Runtime confidence is $RuntimeConfidence, not HIGH.") | Out-Null
}

if ($null -ne $runtimeBundleConfidenceScore -and $runtimeBundleConfidenceScore -lt $MinimumConfidenceScore) {
    $blockedFindings.Add("Runtime bundle confidence score is $runtimeBundleConfidenceScore, below $MinimumConfidenceScore.") | Out-Null
}

if ($null -ne $validatorConfidenceScore -and $validatorConfidenceScore -lt $MinimumConfidenceScore) {
    $blockedFindings.Add("Validator confidence score is $validatorConfidenceScore, below $MinimumConfidenceScore.") | Out-Null
}

if ($runtimeBundle -and -not $requiredBundleSectionsPresent) {
    $blockedFindings.Add("Runtime bundle is missing required decision sections.") | Out-Null
}

if ($runtimeBundle -and $runtimeBundle.blocking_signals) {
    foreach ($signal in @($runtimeBundle.blocking_signals)) {
        $blockedFindings.Add("Runtime bundle blocking signal: $signal") | Out-Null
    }
}

if ($runtimeBundle -and $runtimeBundle.human_required_signals) {
    foreach ($signal in @($runtimeBundle.human_required_signals)) {
        $reviewFindings.Add("Runtime bundle human-required signal: $signal") | Out-Null
    }
}

if ($Action -eq "merge" -and $PrChecksStatus -ne "PASS") {
    $blockedFindings.Add("PR checks status is $PrChecksStatus, not PASS.") | Out-Null
}

if ($Action -eq "push") {
    $blockedFindings.Add("Auto push remains disabled in this foundation pack.") | Out-Null
}

if ($Action -eq "merge") {
    $blockedFindings.Add("Auto merge remains disabled in this foundation pack.") | Out-Null
}

if ($conflictLines.Count -gt 0) {
    $blockedFindings.Add("Merge conflict or unmerged file status is present.") | Out-Null
}

$unknownUntracked = @($untrackedPaths | Where-Object { $_ -ne ".codex_worktrees/" -and -not ($candidateFiles -contains (Normalize-PathText -Path $_)) })
if ($unknownUntracked.Count -gt 0) {
    $blockedFindings.Add("Unknown untracked backlog exists outside candidate files: $($unknownUntracked -join ', ')") | Out-Null
}

foreach ($file in $candidateFiles) {
    if ($file -match $blockedPathPattern) {
        $blockedFindings.Add("Blocked live/broker/secret path pattern: $file") | Out-Null
        continue
    }

    if (Test-AnyPathPrefix -Path $file -Prefixes $protectedPathPrefixes) {
        $blockedFindings.Add("Human-required protected path: $file") | Out-Null
        continue
    }

    if (-not (Test-AnyPathPrefix -Path $file -Prefixes $safePathPrefixes)) {
        $reviewFindings.Add("Candidate is not in SAFE_AUTO_ALLOWED path classes: $file") | Out-Null
    }
}

$decision = "SAFE_AUTO_ALLOWED"
if ($reviewFindings.Count -gt 0) {
    $decision = "HUMAN_REQUIRED"
}
if ($blockedFindings.Count -gt 0) {
    $decision = "BLOCKED"
}

$autoGitAllowed = ($decision -eq "SAFE_AUTO_ALLOWED" -and $Action -eq "commit")
$nextSafeAction = if ($autoGitAllowed) {
    "Future auto commit could be allowed after a separate execution APPLY helper is approved. This helper cannot execute it."
}
elseif ($decision -eq "HUMAN_REQUIRED") {
    "Request human review before any commit, push, or merge."
}
else {
    "Stop. Resolve blocked findings before any commit, push, or merge."
}

$result = [pscustomobject]@{
    schema = "AIOS_AUTO_GIT_POLICY_DECISION.v1"
    schema_version = "1.0"
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    mode = "DRY_RUN"
    requested_action = $Action
    decision = $decision
    auto_git_allowed = $autoGitAllowed
    candidate_files = $candidateFiles
    safe_auto_allowed_classes = $safeAutoAllowedClasses
    human_required_classes = $humanRequiredClasses
    validator_requirements = $validatorRequirements
    stop_conditions = $stopConditions
    evidence = [pscustomobject]@{
        git_status = $gitStatus
        validator_result = $ValidatorResult
        runtime_confidence = $RuntimeConfidence
        runtime_bundle_path = if ([string]::IsNullOrWhiteSpace($RuntimeBundlePath)) { $null } else { $RuntimeBundlePath }
        runtime_bundle_confidence_score = $runtimeBundleConfidenceScore
        validator_confidence_score = $validatorConfidenceScore
        minimum_confidence_score = $MinimumConfidenceScore
        required_bundle_sections_present = $requiredBundleSectionsPresent
        bundle_stop_conditions = @($bundleStopConditions | Select-Object -Unique)
        pr_checks_status = $PrChecksStatus
        review_findings = @($reviewFindings)
        blocked_findings = @($blockedFindings)
    }
    next_safe_action = $nextSafeAction
    authority_boundary = [pscustomobject]@{
        execution_enabled = $false
        approval_authority = "ANTHONY_ONLY"
        blocked_capabilities = @(
            "git add",
            "commit operation",
            "push operation",
            "pull request creation",
            "pull request merge",
            "direct push to main",
            "validator bypass",
            "protected path mutation",
            "live trading",
            "broker execution",
            "secret handling"
        )
    }
}

if ($Json) {
    $result | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "[VALIDATOR RESULT]"
Write-Host "AI_OS Auto-Git Decision"
Write-Host "Mode: DRY_RUN"
Write-Host "Action: $($result.requested_action)"
Write-Host "Decision: $($result.decision)"
Write-Host "auto_git_allowed: $($result.auto_git_allowed)"
Write-Host "Candidate files: $($result.candidate_files.Count)"
Write-Host "Review findings: $($result.evidence.review_findings.Count)"
Write-Host "Blocked findings: $($result.evidence.blocked_findings.Count)"
Write-Host ""
Write-Host "[CREW RECOMMENDATION]"
Write-Host "Next safe action: $($result.next_safe_action)"
Write-Host "[VALIDATOR RESULT]"
Write-Host "Auto-git execution enabled: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
