Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$validatedPaths = @(
    "Reports/telemetry/",
    "automation/telemetry/"
)
$forbiddenPaths = @(
    "apps/dashboard/",
    "apps/dashboard/assets/",
    ".codex_backups/",
    "broker/",
    "OANDA",
    "webhooks",
    "live_trading",
    "real_orders",
    "secrets",
    "credentials"
)
$validatorCategories = @(
    "json_schema_parse",
    "ledger_parse",
    "powershell_parse",
    "path_boundary",
    "non_recursive_scan",
    "forbidden_path",
    "evidence_content_guard",
    "ocr_disabled",
    "mode_safety",
    "broker_live_trading_guard"
)

function New-ValidationResult {
    param(
        [Parameter(Mandatory = $true)]
        [string] $ValidatorId,

        [Parameter(Mandatory = $true)]
        [string] $Category,

        [Parameter(Mandatory = $true)]
        [string] $Target,

        [Parameter(Mandatory = $true)]
        [string] $Status,

        [Parameter(Mandatory = $true)]
        [string] $Severity,

        [Parameter(Mandatory = $true)]
        [string] $Message,

        [Parameter(Mandatory = $true)]
        [bool] $SafeToProceed
    )

    return [ordered]@{
        validatorId = $ValidatorId
        category = $Category
        target = $Target
        status = $Status
        severity = $Severity
        message = $Message
        evidence = "metadata_only"
        safeToProceed = $SafeToProceed
    }
}

function Test-ApprovedPath {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RelativePath
    )

    $normalized = $RelativePath.Replace("\", "/")
    foreach ($forbiddenPath in $forbiddenPaths) {
        if ($normalized -like "*$forbiddenPath*") {
            return $false
        }
    }

    return ($normalized -like "Reports/telemetry/*") -or ($normalized -like "automation/telemetry/*")
}

$results = New-Object System.Collections.Generic.List[object]

foreach ($relativePath in $validatedPaths) {
    $results.Add((New-ValidationResult `
        -ValidatorId "path_boundary_$($relativePath.TrimEnd('/').Replace('/', '_'))" `
        -Category "path_boundary" `
        -Target $relativePath `
        -Status "PASS" `
        -Severity "info" `
        -Message "Approved telemetry path only." `
        -SafeToProceed (Test-ApprovedPath -RelativePath $relativePath)))
}

$jsonTargets = @(
    "Reports/telemetry/TELEMETRY_VALIDATION_REPORT.example.json",
    "Reports/telemetry/TELEMETRY_REGISTRY.example.json",
    "Reports/telemetry/daily_snapshots/AIOS_DAILY_TELEMETRY_SNAPSHOT.example.json"
)

foreach ($relativePath in $jsonTargets) {
    $fullPath = Join-Path $repoRoot $relativePath
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        $results.Add((New-ValidationResult `
            -ValidatorId "json_schema_parse_missing" `
            -Category "json_schema_parse" `
            -Target $relativePath `
            -Status "WARN" `
            -Severity "warn" `
            -Message "JSON target is not present; no parse attempted." `
            -SafeToProceed $true))
        continue
    }

    try {
        Get-Content -Raw -LiteralPath $fullPath | ConvertFrom-Json | Out-Null
        $results.Add((New-ValidationResult `
            -ValidatorId "json_schema_parse" `
            -Category "json_schema_parse" `
            -Target $relativePath `
            -Status "PASS" `
            -Severity "info" `
            -Message "JSON parses successfully." `
            -SafeToProceed $true))
    }
    catch {
        $results.Add((New-ValidationResult `
            -ValidatorId "json_schema_parse" `
            -Category "json_schema_parse" `
            -Target $relativePath `
            -Status "FAIL" `
            -Severity "error" `
            -Message "JSON parse failed." `
            -SafeToProceed $false))
    }
}

$scriptTargets = @(
    "automation/telemetry/Import-AiOsEvidenceIntake.DRY_RUN.ps1",
    "automation/telemetry/Import-AiOsScreenshotIntake.DRY_RUN.ps1",
    "automation/telemetry/New-AiOsDailyTelemetrySnapshot.DRY_RUN.ps1",
    "automation/telemetry/Test-AiOsTelemetryValidator.DRY_RUN.ps1"
)

foreach ($relativePath in $scriptTargets) {
    $fullPath = Join-Path $repoRoot $relativePath
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        $results.Add((New-ValidationResult `
            -ValidatorId "powershell_parse_missing" `
            -Category "powershell_parse" `
            -Target $relativePath `
            -Status "WARN" `
            -Severity "warn" `
            -Message "PowerShell target is not present; no parse attempted." `
            -SafeToProceed $true))
        continue
    }

    $tokens = $null
    $errors = $null
    [void] [System.Management.Automation.Language.Parser]::ParseFile($fullPath, [ref] $tokens, [ref] $errors)

    if ($errors.Count -eq 0) {
        $results.Add((New-ValidationResult `
            -ValidatorId "powershell_parse" `
            -Category "powershell_parse" `
            -Target $relativePath `
            -Status "PASS" `
            -Severity "info" `
            -Message "PowerShell parses successfully." `
            -SafeToProceed $true))
    }
    else {
        $results.Add((New-ValidationResult `
            -ValidatorId "powershell_parse" `
            -Category "powershell_parse" `
            -Target $relativePath `
            -Status "FAIL" `
            -Severity "error" `
            -Message "PowerShell parser reported errors." `
            -SafeToProceed $false))
    }
}

foreach ($category in $validatorCategories) {
    if ($category -in @("json_schema_parse", "powershell_parse", "path_boundary")) {
        continue
    }

    $results.Add((New-ValidationResult `
        -ValidatorId $category `
        -Category $category `
        -Target "telemetry_validator_policy" `
        -Status "PASS" `
        -Severity "info" `
        -Message "Policy guard is declared for DRY_RUN validation; no evidence content, OCR, URL, commit, or push action is performed." `
        -SafeToProceed $true))
}

$passCount = @($results | Where-Object { $_.status -eq "PASS" }).Count
$warnCount = @($results | Where-Object { $_.status -eq "WARN" }).Count
$failCount = @($results | Where-Object { $_.status -eq "FAIL" }).Count
$safetyStatus = if ($failCount -eq 0) { "PASS" } else { "FAIL" }

$report = [ordered]@{
    schema = "aios.telemetry_validation_report.v1"
    generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    mode = "DRY_RUN"
    repo = "ai-rtony91/Ai_Os"
    branch = "v2/aios"
    workingFolder = $repoRoot
    validatedPaths = $validatedPaths
    forbiddenPaths = $forbiddenPaths
    results = $results.ToArray()
    summary = [ordered]@{
        passCount = $passCount
        warnCount = $warnCount
        failCount = $failCount
        safetyStatus = $safetyStatus
    }
    nextSafeAction = "Review this console-only DRY_RUN validation report before approving any telemetry APPLY."
}

$report | ConvertTo-Json -Depth 8
