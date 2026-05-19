[CmdletBinding()]
param(
    [string]$ConfigPath = "automation/orchestration/validators/VALIDATOR_CHAIN_CONFIG_001.json"
)

$ErrorActionPreference = "Stop"

function Add-ValidatorResult {
    param(
        [System.Collections.Generic.List[object]]$Results,
        [string]$ValidatorName,
        [string]$Result,
        [string]$Severity,
        [string]$Notes
    )

    $Results.Add([pscustomobject]@{
        validator_name = $ValidatorName
        result = $Result
        severity = $Severity
        notes = $Notes
    }) | Out-Null
}

function Get-RepoRoot {
    $root = & git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($root)) {
        throw "Unable to find git repository root."
    }
    return $root.Trim()
}

$repoRoot = Get-RepoRoot
Set-Location -LiteralPath $repoRoot

$resolvedConfigPath = Join-Path $repoRoot $ConfigPath
$results = [System.Collections.Generic.List[object]]::new()
$config = $null

Write-Output ("Repo root: {0}" -f $repoRoot)
Write-Output ("Validator config path: {0}" -f $resolvedConfigPath)

if (Test-Path -LiteralPath $resolvedConfigPath) {
    try {
        $config = Get-Content -LiteralPath $resolvedConfigPath -Raw | ConvertFrom-Json
        Add-ValidatorResult -Results $results -ValidatorName "config_load" -Result "PASS" -Severity "INFO" -Notes "Validator config loaded."
    }
    catch {
        Add-ValidatorResult -Results $results -ValidatorName "config_load" -Result "FAIL" -Severity "BLOCKER" -Notes "Validator config JSON could not parse."
    }
}
else {
    Add-ValidatorResult -Results $results -ValidatorName "config_load" -Result "FAIL" -Severity "BLOCKER" -Notes "Validator config file is missing."
}

$statusLines = @(& git status --short --branch)
if ($LASTEXITCODE -eq 0) {
    $changedLines = @($statusLines | Where-Object { $_ -notlike "##*" })
    if ($changedLines.Count -eq 0) {
        Add-ValidatorResult -Results $results -ValidatorName "git_clean_state" -Result "PASS" -Severity "INFO" -Notes "Working tree has no changed files."
    }
    else {
        Add-ValidatorResult -Results $results -ValidatorName "git_clean_state" -Result "WARN" -Severity "REVIEW_REQUIRED" -Notes ("Working tree has {0} changed or untracked entries." -f $changedLines.Count)
    }
}
else {
    Add-ValidatorResult -Results $results -ValidatorName "git_clean_state" -Result "FAIL" -Severity "BLOCKER" -Notes "git status failed."
}

$changedPaths = @(
    foreach ($line in $statusLines) {
        if ($line -like "##*" -or $line.Length -lt 4) { continue }
        $path = $line.Substring(3).Trim()
        if ($path -match " -> ") {
            $path = ($path -split " -> ")[-1].Trim()
        }
        $path -replace "\\", "/"
    }
)

$allowedPrefixes = @(
    "automation/orchestration/",
    "docs/concepts/",
    "docs/workflows/",
    "docs/architecture/",
    "docs/audits/"
)
$blockedPrefixes = @(
    "apps/",
    "services/",
    "core/",
    ".git/",
    ".codex_backups/",
    "package.json",
    "tsconfig.json",
    "Reports/security/",
    "automation/operator/",
    "automation/telemetry/",
    "Reports/telemetry/",
    "README.md",
    "RISK_POLICY.md",
    "SOURCE_LOG.md",
    "ERROR_LOG.md",
    "HALLUCINATION_LOG.md",
    "AAR.md",
    "DAILY_REPORT.md",
    "ARCHITECTURE.md",
    "DEPLOYMENT.md",
    "WHITEPAPER.md"
)

$outsideAllowed = @($changedPaths | Where-Object {
    $path = $_
    -not [bool]@($allowedPrefixes | Where-Object { $path -like "$_*" }).Count
})
if ($outsideAllowed.Count -eq 0) {
    Add-ValidatorResult -Results $results -ValidatorName "allowed_paths" -Result "PASS" -Severity "INFO" -Notes "Changed files are inside orchestration allowed paths."
}
else {
    Add-ValidatorResult -Results $results -ValidatorName "allowed_paths" -Result "WARN" -Severity "REVIEW_REQUIRED" -Notes ("Changed files outside current validator package: {0}" -f ($outsideAllowed -join ", "))
}

$blockedMatches = @($changedPaths | Where-Object {
    $path = $_
    [bool]@($blockedPrefixes | Where-Object { $path -eq $_ -or $path -like "$_*" }).Count
})
if ($blockedMatches.Count -eq 0) {
    Add-ValidatorResult -Results $results -ValidatorName "blocked_paths" -Result "PASS" -Severity "INFO" -Notes "No blocked changed paths detected."
}
else {
    Add-ValidatorResult -Results $results -ValidatorName "blocked_paths" -Result "FAIL" -Severity "BLOCKER" -Notes ("Blocked changed paths detected: {0}" -f ($blockedMatches -join ", "))
}

$jsonFiles = @($changedPaths | Where-Object { $_ -like "*.json" })
$jsonFailures = New-Object System.Collections.Generic.List[string]
foreach ($jsonFile in $jsonFiles) {
    $fullPath = Join-Path $repoRoot $jsonFile
    if (Test-Path -LiteralPath $fullPath) {
        try {
            Get-Content -LiteralPath $fullPath -Raw | ConvertFrom-Json | Out-Null
        }
        catch {
            $jsonFailures.Add($jsonFile) | Out-Null
        }
    }
}
if ($jsonFailures.Count -eq 0) {
    Add-ValidatorResult -Results $results -ValidatorName "json_integrity" -Result "PASS" -Severity "INFO" -Notes ("Parsed changed JSON files: {0}" -f $jsonFiles.Count)
}
else {
    Add-ValidatorResult -Results $results -ValidatorName "json_integrity" -Result "FAIL" -Severity "BLOCKER" -Notes ("Invalid JSON files: {0}" -f ($jsonFailures -join ", "))
}

$psFiles = @($changedPaths | Where-Object { $_ -like "*.ps1" })
$psFailures = New-Object System.Collections.Generic.List[string]
foreach ($psFile in $psFiles) {
    $fullPath = Join-Path $repoRoot $psFile
    if (Test-Path -LiteralPath $fullPath) {
        $tokens = $null
        $errors = $null
        [System.Management.Automation.Language.Parser]::ParseFile($fullPath, [ref]$tokens, [ref]$errors) | Out-Null
        if ($errors.Count -gt 0) {
            $psFailures.Add($psFile) | Out-Null
        }
    }
}
if ($psFailures.Count -eq 0) {
    Add-ValidatorResult -Results $results -ValidatorName "powershell_syntax" -Result "PASS" -Severity "INFO" -Notes ("Parsed changed PowerShell files: {0}" -f $psFiles.Count)
}
else {
    Add-ValidatorResult -Results $results -ValidatorName "powershell_syntax" -Result "FAIL" -Severity "BLOCKER" -Notes ("PowerShell syntax errors: {0}" -f ($psFailures -join ", "))
}

$requiredMarkdown = @(
    "automation/orchestration/validators/VALIDATOR_CHAIN_RUNBOOK_001.md",
    "docs/concepts/aios-dispatcher-orchestration-concepts.md"
)
$missingMarkdown = @($requiredMarkdown | Where-Object { -not (Test-Path -LiteralPath (Join-Path $repoRoot $_)) })
if ($missingMarkdown.Count -eq 0) {
    Add-ValidatorResult -Results $results -ValidatorName "markdown_exists" -Result "PASS" -Severity "INFO" -Notes "Required Markdown files exist."
}
else {
    Add-ValidatorResult -Results $results -ValidatorName "markdown_exists" -Result "WARN" -Severity "REVIEW_REQUIRED" -Notes ("Missing Markdown files: {0}" -f ($missingMarkdown -join ", "))
}

$sensitivePathMatches = @($changedPaths | Where-Object { $_ -match "(?i)(secret|credential|token|api[_-]?key|private[_-]?key|\.env)" })
if ($sensitivePathMatches.Count -eq 0) {
    Add-ValidatorResult -Results $results -ValidatorName "no_secrets" -Result "PASS" -Severity "INFO" -Notes "No sensitive filenames detected in changed paths."
}
else {
    Add-ValidatorResult -Results $results -ValidatorName "no_secrets" -Result "FAIL" -Severity "BLOCKER" -Notes ("Sensitive path names detected: {0}" -f ($sensitivePathMatches -join ", "))
}

$liveTradingPathMatches = @($changedPaths | Where-Object { $_ -match "(?i)(broker|oanda|live[_-]?trading|webhook|real[_-]?order)" })
if ($liveTradingPathMatches.Count -eq 0) {
    Add-ValidatorResult -Results $results -ValidatorName "no_live_trading_enablement" -Result "PASS" -Severity "INFO" -Notes "No live trading path names detected."
}
else {
    Add-ValidatorResult -Results $results -ValidatorName "no_live_trading_enablement" -Result "FAIL" -Severity "BLOCKER" -Notes ("Live trading related path names detected: {0}" -f ($liveTradingPathMatches -join ", "))
}

Add-ValidatorResult -Results $results -ValidatorName "approval_gate" -Result "WARN" -Severity "REVIEW_REQUIRED" -Notes "Human approval is required before APPLY, commit, or push."
Add-ValidatorResult -Results $results -ValidatorName "commit_package_review" -Result "WARN" -Severity "REVIEW_REQUIRED" -Notes "Exact-file commit package review is required before staging or commit."

if ($LASTEXITCODE -eq 0) {
    Add-ValidatorResult -Results $results -ValidatorName "final_git_status" -Result "PASS" -Severity "INFO" -Notes (($statusLines -join " | "))
}
else {
    Add-ValidatorResult -Results $results -ValidatorName "final_git_status" -Result "FAIL" -Severity "BLOCKER" -Notes "Final git status unavailable."
}

$failCount = @($results | Where-Object { $_.result -eq "FAIL" }).Count
$warnCount = @($results | Where-Object { $_.result -eq "WARN" }).Count
$overall = if ($failCount -gt 0) { "FAIL" } elseif ($warnCount -gt 0) { "WARN" } else { "PASS" }

Write-Output "Validator results:"
foreach ($result in $results) {
    Write-Output ("{0}: {1} [{2}] - {3}" -f $result.validator_name, $result.result, $result.severity, $result.notes)
}

[pscustomobject]@{
    chain_id = if ($null -ne $config) { $config.chain_id } else { "UNKNOWN" }
    mode = "DRY_RUN_READ_ONLY"
    overall_result = $overall
    pass_count = @($results | Where-Object { $_.result -eq "PASS" }).Count
    warn_count = $warnCount
    fail_count = $failCount
    modifies_files = $false
    commits = $false
    pushes = $false
    next_safe_action = if ($overall -eq "PASS") { "Validation passed. Human approval is still required before APPLY, commit, or push." } else { "Review WARN and FAIL results before APPLY, commit, or push." }
} | ConvertTo-Json -Depth 5

