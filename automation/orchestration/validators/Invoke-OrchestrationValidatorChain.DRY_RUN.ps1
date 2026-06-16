[CmdletBinding()]
param(
    [string]$ConfigPath = "automation/orchestration/validators/VALIDATOR_CHAIN_CONFIG_001.json",
    [string[]]$ChangedPath = @(),
    [string[]]$AllowedPath = @(),
    [string[]]$ForbiddenPath = @()
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

function ConvertTo-AiOsRelativePath {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return ""
    }

    $normalized = $Path.Trim().Trim([char]34).Trim([char]39) -replace "\\", "/"
    while ($normalized.StartsWith("./")) {
        $normalized = $normalized.Substring(2)
    }
    while ($normalized.StartsWith("/")) {
        $normalized = $normalized.Substring(1)
    }
    return $normalized
}

function ConvertTo-AiOsPathList {
    param([string[]]$Paths)

    $normalized = New-Object System.Collections.Generic.List[string]
    foreach ($path in @($Paths)) {
        $clean = ConvertTo-AiOsRelativePath -Path $path
        if (-not [string]::IsNullOrWhiteSpace($clean)) {
            $normalized.Add($clean.TrimEnd("/")) | Out-Null
        }
    }
    return @($normalized | Sort-Object -Unique)
}

function Test-AiOsPathUnder {
    param(
        [string]$Path,
        [string]$Scope
    )

    $normalizedPath = (ConvertTo-AiOsRelativePath -Path $Path).TrimEnd("/")
    $normalizedScope = (ConvertTo-AiOsRelativePath -Path $Scope).TrimEnd("/")
    if ([string]::IsNullOrWhiteSpace($normalizedPath) -or [string]::IsNullOrWhiteSpace($normalizedScope)) {
        return $false
    }

    return ($normalizedPath -eq $normalizedScope -or $normalizedPath -like "$normalizedScope/*")
}

function Test-AiOsPathInScope {
    param(
        [string]$Path,
        [string[]]$Scopes
    )

    foreach ($scope in @($Scopes)) {
        if (Test-AiOsPathUnder -Path $Path -Scope $scope) {
            return $true
        }
    }
    return $false
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

$statusChangedPaths = @(
    foreach ($line in $statusLines) {
        if ($line -like "##*" -or $line.Length -lt 4) { continue }
        $path = $line.Substring(3).Trim()
        if ($path -match " -> ") {
            $path = ($path -split " -> ")[-1].Trim()
        }
        ConvertTo-AiOsRelativePath -Path $path
    }
)
$explicitChangedPaths = ConvertTo-AiOsPathList -Paths $ChangedPath
$changedPaths = if ($explicitChangedPaths.Count -gt 0) { $explicitChangedPaths } else { $statusChangedPaths }
$packetAllowedPaths = ConvertTo-AiOsPathList -Paths $AllowedPath
$packetForbiddenPaths = ConvertTo-AiOsPathList -Paths $ForbiddenPath
$packetScopeProvided = ($packetAllowedPaths.Count -gt 0 -or $packetForbiddenPaths.Count -gt 0)
$unsafePacketAllowedScopes = @($packetAllowedPaths | Where-Object {
    $_ -in @("apps", "apps/trading_lab", "apps/trading_lab/trading_lab")
})

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
$hardBlockedPrefixes = @(
    ".git/",
    ".codex_backups/",
    "apps/dashboard/",
    "services/",
    "core/",
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

if ($packetScopeProvided) {
    if ($unsafePacketAllowedScopes.Count -eq 0) {
        Add-ValidatorResult -Results $results -ValidatorName "packet_scope" -Result "PASS" -Severity "INFO" -Notes "Packet-aware path scope is exact enough for validator review."
    }
    else {
        Add-ValidatorResult -Results $results -ValidatorName "packet_scope" -Result "FAIL" -Severity "BLOCKER" -Notes ("Broad packet allowed paths are blocked: {0}" -f ($unsafePacketAllowedScopes -join ", "))
    }
}

$outsideAllowed = @($changedPaths | Where-Object {
    $path = $_
    -not (Test-AiOsPathInScope -Path $path -Scopes $allowedPrefixes) -and
        -not (Test-AiOsPathInScope -Path $path -Scopes $packetAllowedPaths)
})
if ($outsideAllowed.Count -eq 0) {
    $allowedNotes = if ($packetAllowedPaths.Count -gt 0) {
        "Changed files are inside validator defaults or packet-approved exact paths."
    }
    else {
        "Changed files are inside orchestration allowed paths."
    }
    Add-ValidatorResult -Results $results -ValidatorName "allowed_paths" -Result "PASS" -Severity "INFO" -Notes $allowedNotes
}
else {
    $allowedResult = if ($packetScopeProvided) { "FAIL" } else { "WARN" }
    $allowedSeverity = if ($packetScopeProvided) { "BLOCKER" } else { "REVIEW_REQUIRED" }
    $allowedMessage = if ($packetScopeProvided) { "Changed files outside packet-approved exact paths" } else { "Changed files outside current validator package" }
    Add-ValidatorResult -Results $results -ValidatorName "allowed_paths" -Result $allowedResult -Severity $allowedSeverity -Notes ("{0}: {1}" -f $allowedMessage, ($outsideAllowed -join ", "))
}

$blockedMatches = @($changedPaths | Where-Object {
    $path = $_
    $blockedByPacketForbidden = Test-AiOsPathInScope -Path $path -Scopes $packetForbiddenPaths
    $blockedByHardPrefix = Test-AiOsPathInScope -Path $path -Scopes $hardBlockedPrefixes
    $blockedByDefaultPrefix = Test-AiOsPathInScope -Path $path -Scopes $blockedPrefixes
    $allowedByPacketScope = Test-AiOsPathInScope -Path $path -Scopes $packetAllowedPaths

    $blockedByPacketForbidden -or
        ($packetScopeProvided -and ($blockedByHardPrefix -or ((-not $allowedByPacketScope) -and $blockedByDefaultPrefix))) -or
        ((-not $packetScopeProvided) -and $blockedByDefaultPrefix)
})
if ($blockedMatches.Count -eq 0) {
    $blockedNotes = if ($packetScopeProvided) {
        "No blocked changed paths detected inside packet-aware exact path scope."
    }
    else {
        "No blocked changed paths detected."
    }
    Add-ValidatorResult -Results $results -ValidatorName "blocked_paths" -Result "PASS" -Severity "INFO" -Notes $blockedNotes
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
    orchestration_result_contract = [pscustomobject]@{
        status = $overall
        severity = if ($overall -eq "FAIL") { "BLOCKED" } elseif ($overall -eq "WARN") { "REVIEW" } else { "INFO" }
        packet_id = "VALIDATOR_CHAIN"
        worker_identity = "UNKNOWN"
        validator_results = @($results | ForEach-Object {
            [pscustomobject]@{
                validator_id = [string]$_.validator_name
                status = [string]$_.result
                severity = [string]$_.severity
                evidence = [string]$_.notes
                next_safe_action = "Review validator result before APPLY, commit, or push."
            }
        })
        approval_required = $true
        blocked_reason = if ($failCount -gt 0) { "One or more validator results failed." } else { "none" }
        escalation_reason = if ($overall -eq "PASS") { "Human approval is still required before protected actions." } else { "Validator chain returned WARN or FAIL." }
        commit_candidate = $false
        next_safe_action = if ($overall -eq "PASS") { "Validation passed. Human approval is still required before APPLY, commit, or push." } else { "Review WARN and FAIL results before APPLY, commit, or push." }
        stop_condition = "REPORT_ONLY_NO_APPLY_NO_COMMIT_NO_PUSH"
        runtime_notes = @(
            "DRY_RUN_READ_ONLY",
            "No APPLY, commit, or push was performed."
        )
        evidence = [pscustomobject]@{
            pass_count = @($results | Where-Object { $_.result -eq "PASS" }).Count
            warn_count = $warnCount
            fail_count = $failCount
            changed_path_count = $changedPaths.Count
        }
        generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    }
} | ConvertTo-Json -Depth 5

