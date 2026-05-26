param(
    [string]$ValidatorConfigPath,
    [string]$ValidatorRecommendationPath,
    [string]$ValidatorRunReportPath,
    [string[]]$CandidateFile = @(),
    [switch]$Json
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")

if ([string]::IsNullOrWhiteSpace($ValidatorConfigPath)) {
    $ValidatorConfigPath = Join-Path $repoRoot.Path "automation\orchestration\validators\VALIDATOR_CHAIN_CONFIG_001.json"
}
if ([string]::IsNullOrWhiteSpace($ValidatorRecommendationPath)) {
    $ValidatorRecommendationPath = Join-Path $repoRoot.Path "automation\orchestration\validators\VALIDATOR_RECOMMENDATION.example.json"
}
if ([string]::IsNullOrWhiteSpace($ValidatorRunReportPath)) {
    $ValidatorRunReportPath = Join-Path $repoRoot.Path "automation\orchestration\validator_chain_runner\VALIDATOR_CHAIN_RUN_REPORT.example.json"
}

function ConvertTo-RelativePath {
    param([string]$Path)

    $resolved = Resolve-Path -LiteralPath $Path -ErrorAction SilentlyContinue
    if (-not $resolved) {
        return ($Path -replace "\\", "/")
    }

    $rootPath = $repoRoot.Path.TrimEnd("\")
    $resolvedPath = $resolved.Path
    if ($resolvedPath.StartsWith($rootPath, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $resolvedPath.Substring($rootPath.Length).TrimStart("\") -replace "\\", "/"
    }

    return ($resolvedPath -replace "\\", "/")
}

function Read-JsonSafe {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            parse_error = $_.Exception.Message
            path = ConvertTo-RelativePath -Path $Path
        }
    }
}

function Normalize-PathText {
    param([string]$Path)
    return (($Path -replace "\\", "/").Trim().Trim("/"))
}

function Add-WeightedFinding {
    param(
        [System.Collections.Generic.List[object]]$Findings,
        [string]$Source,
        [string]$Severity,
        [int]$Weight,
        [string]$Reason
    )

    $Findings.Add([pscustomobject]@{
        source = $Source
        severity = $Severity
        weight = $Weight
        reason = $Reason
    }) | Out-Null
}

$config = Read-JsonSafe -Path $ValidatorConfigPath
$recommendation = Read-JsonSafe -Path $ValidatorRecommendationPath
$runReport = Read-JsonSafe -Path $ValidatorRunReportPath

$requiredValidators = @()
if ($config -and $config.validators) {
    $requiredValidators = @($config.validators | Where-Object { $_.required -eq $true } | ForEach-Object { [string]$_.name })
}

$reportedValidators = @()
if ($runReport -and $runReport.validators_run) {
    $reportedValidators = @($runReport.validators_run | ForEach-Object {
        if ($_.validator_id) { [string]$_.validator_id } elseif ($_.validator_name) { [string]$_.validator_name } elseif ($_.name) { [string]$_.name }
    } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
}

$requiredMissing = @()
if ($requiredValidators.Count -gt 0 -and $reportedValidators.Count -gt 0) {
    $requiredMissing = @($requiredValidators | Where-Object { $reportedValidators -notcontains $_ })
}
elseif ($requiredValidators.Count -gt 0 -and $null -eq $runReport) {
    $requiredMissing = @("validator_run_report_missing")
}

$blockedFindings = New-Object System.Collections.Generic.List[string]
$reviewFindings = New-Object System.Collections.Generic.List[string]
$weightedFindings = New-Object System.Collections.Generic.List[object]
$failedValidators = New-Object System.Collections.Generic.List[string]

if ($null -eq $config) {
    $blockedFindings.Add("Validator chain config is missing.") | Out-Null
    Add-WeightedFinding -Findings $weightedFindings -Source "validator_config" -Severity "BLOCKED" -Weight 100 -Reason "Missing required validator chain config."
}
elseif ($config.parse_error) {
    $blockedFindings.Add("Validator chain config could not parse.") | Out-Null
    Add-WeightedFinding -Findings $weightedFindings -Source "validator_config" -Severity "BLOCKED" -Weight 100 -Reason $config.parse_error
}

if ($null -eq $runReport) {
    $reviewFindings.Add("Validator run report is missing; confidence cannot prove a current validator pass.") | Out-Null
    Add-WeightedFinding -Findings $weightedFindings -Source "validator_run_report" -Severity "REVIEW_REQUIRED" -Weight 20 -Reason "Missing validator run report."
}
elseif ($runReport.parse_error) {
    $blockedFindings.Add("Validator run report could not parse.") | Out-Null
    Add-WeightedFinding -Findings $weightedFindings -Source "validator_run_report" -Severity "BLOCKED" -Weight 100 -Reason $runReport.parse_error
}

foreach ($missing in $requiredMissing) {
    $blockedFindings.Add("Missing required validator: $missing") | Out-Null
    Add-WeightedFinding -Findings $weightedFindings -Source $missing -Severity "BLOCKED" -Weight 100 -Reason "Missing required validator."
}

if ($runReport -and $runReport.failed_validators) {
    foreach ($validator in @($runReport.failed_validators)) {
        if (-not [string]::IsNullOrWhiteSpace([string]$validator)) {
            $failedValidators.Add([string]$validator) | Out-Null
            $blockedFindings.Add("Failed validator: $validator") | Out-Null
            Add-WeightedFinding -Findings $weightedFindings -Source ([string]$validator) -Severity "BLOCKED" -Weight 100 -Reason "Validator is listed as failed."
        }
    }
}

if ($runReport -and $runReport.validators_run) {
    foreach ($validator in @($runReport.validators_run)) {
        $name = if ($validator.validator_id) { [string]$validator.validator_id } elseif ($validator.validator_name) { [string]$validator.validator_name } elseif ($validator.name) { [string]$validator.name } else { "unknown_validator" }
        $result = if ($validator.result) { ([string]$validator.result).ToUpperInvariant() } else { "UNKNOWN" }
        if ($result -in @("FAIL", "FAILED", "BLOCKED")) {
            $failedValidators.Add($name) | Out-Null
            $blockedFindings.Add("Blocked validator result: $name") | Out-Null
            Add-WeightedFinding -Findings $weightedFindings -Source $name -Severity "BLOCKED" -Weight 100 -Reason "Validator result is $result."
        }
        elseif ($result -in @("WARN", "WARNING", "REVIEW", "REVIEW_REQUIRED", "UNKNOWN")) {
            $reviewFindings.Add("Review-required validator result: $name") | Out-Null
            Add-WeightedFinding -Findings $weightedFindings -Source $name -Severity "REVIEW_REQUIRED" -Weight 15 -Reason "Validator result is $result."
        }
    }
}

if ($recommendation -and $recommendation.blocked_findings) {
    foreach ($finding in @($recommendation.blocked_findings)) {
        $reason = if ($finding.reason) { [string]$finding.reason } else { ($finding | ConvertTo-Json -Compress -Depth 5) }
        $blockedFindings.Add("Validator recommendation blocked finding: $reason") | Out-Null
        Add-WeightedFinding -Findings $weightedFindings -Source "validator_recommendation" -Severity "BLOCKED" -Weight 100 -Reason $reason
    }
}

if ($recommendation -and $recommendation.review_findings) {
    foreach ($finding in @($recommendation.review_findings)) {
        $reason = if ($finding.reason) { [string]$finding.reason } else { ($finding | ConvertTo-Json -Compress -Depth 5) }
        $reviewFindings.Add("Validator recommendation review finding: $reason") | Out-Null
        Add-WeightedFinding -Findings $weightedFindings -Source "validator_recommendation" -Severity "REVIEW_REQUIRED" -Weight 15 -Reason $reason
    }
}

$blockedPathPattern = "(?i)(broker|oanda|live[_-]?trading|api[_-]?key|secret|credential|webhook|real[_-]?order|order[_-]?execution)"
$protectedPathPrefixes = @(
    "AGENTS.md",
    "README.md",
    "docs/governance/",
    "docs/security/",
    "automation/orchestration/policy/",
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

foreach ($file in @($CandidateFile | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })) {
    $normalized = Normalize-PathText -Path $file
    if ($normalized -match $blockedPathPattern) {
        $blockedFindings.Add("Blocked live/broker/secret path pattern: $normalized") | Out-Null
        Add-WeightedFinding -Findings $weightedFindings -Source $normalized -Severity "BLOCKED" -Weight 100 -Reason "Blocked path pattern."
    }
    foreach ($prefix in $protectedPathPrefixes) {
        if ($normalized -eq $prefix.TrimEnd("/") -or $normalized.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            $blockedFindings.Add("Protected path touched: $normalized") | Out-Null
            Add-WeightedFinding -Findings $weightedFindings -Source $normalized -Severity "BLOCKED" -Weight 100 -Reason "Protected path requires human authority."
            break
        }
    }
}

$score = 100
if ($blockedFindings.Count -gt 0) {
    $score = 0
}
else {
    foreach ($finding in $weightedFindings) {
        $score -= [int]$finding.weight
    }
    if ($score -lt 0) {
        $score = 0
    }
}

$band = "HIGH"
if ($score -lt 90) { $band = "MEDIUM" }
if ($score -lt 70) { $band = "LOW" }
if ($score -lt 40 -or $blockedFindings.Count -gt 0) { $band = "BLOCKED" }

$overallResult = "PASS"
if ($reviewFindings.Count -gt 0 -or $band -in @("MEDIUM", "LOW")) {
    $overallResult = "REVIEW_REQUIRED"
}
if ($blockedFindings.Count -gt 0 -or $band -eq "BLOCKED") {
    $overallResult = "BLOCKED"
}
if ($null -eq $config -and $null -eq $recommendation -and $null -eq $runReport) {
    $overallResult = "UNKNOWN"
}

$safeAutoAllowedEligible = (
    $overallResult -eq "PASS" -and
    $score -ge 90 -and
    $blockedFindings.Count -eq 0 -and
    $reviewFindings.Count -eq 0
)

$failedValidatorItems = @()
foreach ($item in $failedValidators) {
    $text = [string]$item
    if (-not [string]::IsNullOrWhiteSpace($text) -and $failedValidatorItems -notcontains $text) {
        $failedValidatorItems += $text
    }
}
$blockedFindingItems = @()
foreach ($item in $blockedFindings) {
    $blockedFindingItems += [string]$item
}
$reviewFindingItems = @()
foreach ($item in $reviewFindings) {
    $reviewFindingItems += [string]$item
}
$weightedFindingItems = @()
foreach ($item in $weightedFindings) {
    $weightedFindingItems += $item
}

$result = [pscustomobject]@{
    schema = "AIOS_VALIDATOR_CONFIDENCE.v1"
    schema_version = "1.0"
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    mode = "DRY_RUN"
    overall_result = $overallResult
    confidence_score = $score
    confidence_band = $band
    required_validators_missing = @($requiredMissing)
    failed_validators = $failedValidatorItems
    blocked_findings = $blockedFindingItems
    review_findings = $reviewFindingItems
    weighted_findings = $weightedFindingItems
    source_reports = @(
        ConvertTo-RelativePath -Path $ValidatorConfigPath
        ConvertTo-RelativePath -Path $ValidatorRecommendationPath
        ConvertTo-RelativePath -Path $ValidatorRunReportPath
    )
    safe_auto_allowed_eligible = $safeAutoAllowedEligible
    stop_conditions = @(
        "missing required validator",
        "blocked validator result",
        "failed validator",
        "protected path touched",
        "lock conflict",
        "missing required approval",
        "unknown file classification",
        "runtime stale or missing evidence",
        "dirty tree outside approved candidate files"
    )
    authority_boundary = [pscustomobject]@{
        read_only = $true
        execution_enabled = $false
        approval_authority = "ANTHONY_ONLY"
        blocked_capabilities = @(
            "apply changes",
            "stage files",
            "commit changes",
            "push changes",
            "merge pull requests",
            "mutate approvals",
            "move packets",
            "write runtime state",
            "launch workers",
            "start loops"
        )
    }
}

if ($Json) {
    $result | ConvertTo-Json -Depth 12
    exit 0
}

Write-Host "AI_OS Validator Confidence"
Write-Host "Mode: DRY_RUN"
Write-Host "Overall result: $($result.overall_result)"
Write-Host "Confidence: $($result.confidence_band) $($result.confidence_score)"
Write-Host "Blocked findings: $($result.blocked_findings.Count)"
Write-Host "Review findings: $($result.review_findings.Count)"
Write-Host "SAFE_AUTO_ALLOWED eligible: $($result.safe_auto_allowed_eligible)"
Write-Host "Validator confidence helper is read-only."
