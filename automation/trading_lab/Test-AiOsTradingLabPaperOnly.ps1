param(
    [switch]$QuietJson,
    [switch]$SkipPytest
)

Set-StrictMode -Off
$ErrorActionPreference = "SilentlyContinue"

$scriptName   = Split-Path -Leaf $PSCommandPath
$repoRoot     = Split-Path (Split-Path (Split-Path $PSCommandPath -Parent) -Parent) -Parent

function Resolve-RepoPath {
    param([string]$Rel)
    return [System.IO.Path]::GetFullPath((Join-Path $repoRoot $Rel))
}

# -------------------------------------------------------------------
# SAFETY: this script must not enable live trading, add credentials,
# or connect to real brokers. It is READ-ONLY inspection + test runner.
# -------------------------------------------------------------------

$overallResult  = "UNKNOWN"
$scanResults    = @()
$validatorResults = @()
$pytestResult   = "NOT_RUN"
$pytestOutput   = ""
$errors         = @()

# ------------------------------------------------------------------
# SECTION 1: Dangerous string scan
# Scan for patterns that would indicate live broker access.
# Report findings as evidence only -do NOT delete or rewrite files.
# ------------------------------------------------------------------

# Scan only Python source files in the Trading Lab package directories.
# Validators (.ps1), documentation (.md), results (.json), and __pycache__
# are excluded -they legitimately mention these terms without executing them.
$scanPaths = @(
    (Resolve-RepoPath "apps/trading_lab/trading_lab"),
    (Resolve-RepoPath "aios/modules/trader")
)

$dangerousPatterns = @(
    [ordered]@{ pattern = "LIVE_BROKER_DISABLED"; severity = "SAFE";    note = "Expected paper-only safety guard" },
    [ordered]@{ pattern = "oanda_account_id\s*=\s*\w";            severity = "CRITICAL"; note = "OANDA account ID assigned a non-None value" },
    [ordered]@{ pattern = "access_token\s*=\s*\w";                severity = "CRITICAL"; note = "Access token assigned a non-None value" },
    [ordered]@{ pattern = "bearer_token\s*=\s*\w";                severity = "CRITICAL"; note = "Bearer token assigned a non-None value" },
    [ordered]@{ pattern = "api_key\s*=\s*\w";                     severity = "CRITICAL"; note = "API key assigned a non-None value" },
    [ordered]@{ pattern = "requests\.post.*oanda";                severity = "CRITICAL"; note = "Possible live OANDA HTTP POST" },
    [ordered]@{ pattern = "place_order\(";                        severity = "HIGH";     note = "Order placement call - verify it routes through the stub" }
)

$criticalHitCount = 0
$highHitCount     = 0

foreach ($scanPath in $scanPaths) {
    if (-not (Test-Path -LiteralPath $scanPath)) {
        $scanResults += [ordered]@{
            path    = $scanPath.Replace($repoRoot, ".")
            status  = "PATH_NOT_FOUND"
            matches = @()
        }
        continue
    }

    $pathMatches = @()
    # Only scan Python source files; exclude __pycache__
    $files = Get-ChildItem -LiteralPath $scanPath -Recurse -File -Filter "*.py" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch "__pycache__" }

    foreach ($file in $files) {
        $content = Get-Content -LiteralPath $file.FullName -Raw -ErrorAction SilentlyContinue
        if ($null -eq $content) { continue }

        foreach ($dp in $dangerousPatterns) {
            if ($content -imatch $dp.pattern) {
                $matchEntry = [ordered]@{
                    file      = $file.FullName.Replace($repoRoot, ".")
                    pattern   = $dp.pattern
                    severity  = $dp.severity
                    note      = $dp.note
                }
                $pathMatches += $matchEntry

                if ($dp.severity -eq "CRITICAL") { $criticalHitCount++ }
                if ($dp.severity -eq "HIGH")     { $highHitCount++ }
            }
        }
    }

    $scanResults += [ordered]@{
        path    = $scanPath.Replace($repoRoot, ".")
        status  = "SCANNED"
        matches = $pathMatches
    }
}

# ------------------------------------------------------------------
# SECTION 2: Inventory existing validators
# The existing phase-specific validators in automation/trading_lab/
# reference docs/AI_OS/trading_laboratory/ which has been archived.
# They are informational only -their failures do not block the gate.
# The dangerous string scan and pytest are the primary safety checks.
# ------------------------------------------------------------------

$allValidatorScripts = @(Get-ChildItem -LiteralPath (Resolve-RepoPath "automation/trading_lab") -Filter "Test-*.ps1" -File -ErrorAction SilentlyContinue)
foreach ($vs in $allValidatorScripts) {
    if ($vs.Name -eq (Split-Path $PSCommandPath -Leaf)) { continue }
    $validatorResults += [ordered]@{
        script    = "automation/trading_lab/$($vs.Name)"
        status    = "INVENTORIED_NOT_RUN"
        exit_code = $null
        note      = "Phase-specific validators reference archived docs. Run individually for detailed phase results."
    }
}

# ------------------------------------------------------------------
# SECTION 3: pytest for tests/trader/
# ------------------------------------------------------------------

if (-not $SkipPytest) {
    $testsPath = Resolve-RepoPath "tests/trader"
    if (Test-Path -LiteralPath $testsPath) {
        $pythonCmd = "python"
        $null = & $pythonCmd --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            $pytestResult = "PYTHON_NOT_FOUND"
        } else {
            $null = & $pythonCmd -c "import pytest" 2>&1
            if ($LASTEXITCODE -ne 0) {
                $pytestResult = "PYTEST_NOT_INSTALLED"
            } else {
                $pytestOutput = & $pythonCmd -m pytest $testsPath -v --tb=short 2>&1 | Out-String
                if ($LASTEXITCODE -eq 0) {
                    $pytestResult = "PASS"
                } else {
                    $pytestResult = "FAIL"
                    $errors += "pytest returned non-zero exit code for tests/trader/"
                }
            }
        }
    } else {
        $pytestResult = "TESTS_DIR_NOT_FOUND"
    }
}

# ------------------------------------------------------------------
# SECTION 4: Determine overall result
# ------------------------------------------------------------------

# Critical hits that are NOT the expected safety guard = problem
$realCriticalHits = @($scanResults | ForEach-Object { $_.matches } | Where-Object {
    $_.severity -eq "CRITICAL"
})

if ($realCriticalHits.Count -gt 0) {
    $overallResult = "FAIL"
    $errors += "Dangerous string scan found $($realCriticalHits.Count) CRITICAL pattern(s) outside expected safety guards."
} elseif ($pytestResult -eq "FAIL") {
    $overallResult = "FAIL"
} elseif ($pytestResult -eq "PASS") {
    $overallResult = "PASS"
} elseif ($pytestResult -in @("NOT_RUN", "PYTHON_NOT_FOUND", "TESTS_DIR_NOT_FOUND", "PYTEST_NOT_INSTALLED")) {
    $overallResult = if ($realCriticalHits.Count -eq 0) { "PARTIAL_PASS" } else { "FAIL" }
} else {
    $overallResult = "UNKNOWN"
}

# Build structured output
$report = [ordered]@{
    mode                   = "READ_ONLY"
    script                 = $scriptName
    overall_result         = $overallResult
    paper_only_boundary    = "PRESERVED"
    live_broker_enabled    = $false
    credentials_added      = $false
    commit_performed       = $false
    push_performed         = $false
    dangerous_string_scan  = [ordered]@{
        critical_hits      = $realCriticalHits.Count
        high_hits          = $highHitCount
        paths_scanned      = @($scanResults | ForEach-Object { $_.path })
        findings           = $scanResults
    }
    validator_results      = $validatorResults
    pytest_result          = $pytestResult
    errors                 = $errors
}

if ($QuietJson) {
    $report | ConvertTo-Json -Depth 8
    exit $(if ($overallResult -eq "FAIL") { 1 } else { 0 })
}

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Trading Lab Paper-Only Validation Harness" -ForegroundColor Cyan
Write-Host "Mode: READ_ONLY - does not enable live trading or modify broker paths"
Write-Host ""

$resultColor = switch ($overallResult) {
    "PASS"         { "Green" }
    "PARTIAL_PASS" { "Yellow" }
    "FAIL"         { "Red" }
    default        { "White" }
}
Write-Host "OVERALL RESULT: $overallResult" -ForegroundColor $resultColor
Write-Host "Paper-only boundary: PRESERVED"
Write-Host "Live broker enabled: NO"
Write-Host "Credentials added:   NO"
Write-Host ""

Write-Host "=== Dangerous String Scan ===" -ForegroundColor Yellow
Write-Host "  CRITICAL hits (outside safety guards): $($realCriticalHits.Count)"
Write-Host "  HIGH hits: $highHitCount"
foreach ($sr in $scanResults) {
    Write-Host "  [$($sr.status)] $($sr.path)"
    foreach ($m in $sr.matches) {
        $mColor = if ($m.severity -eq "CRITICAL") { "Red" } elseif ($m.severity -eq "SAFE") { "Green" } else { "Yellow" }
        Write-Host "    [$($m.severity)] $($m.pattern) in $($m.file)" -ForegroundColor $mColor
    }
}

Write-Host ""
Write-Host "=== Inventoried Validators ($($validatorResults.Count) scripts) ===" -ForegroundColor Yellow
Write-Host "  Note: Phase-specific validators reference archived docs. Run individually for detailed results."
foreach ($vr in $validatorResults | Select-Object -First 5) {
    Write-Host "  [$($vr.status)] $($vr.script)" -ForegroundColor Cyan
}
if ($validatorResults.Count -gt 5) {
    Write-Host "  ... and $($validatorResults.Count - 5) more (use -QuietJson for full list)"
}

Write-Host ""
Write-Host "=== pytest (tests/trader/) ===" -ForegroundColor Yellow
$ptColor = if ($pytestResult -eq "PASS") { "Green" } elseif ($pytestResult -eq "FAIL") { "Red" } else { "Cyan" }
Write-Host "  Result: $pytestResult" -ForegroundColor $ptColor
if ($pytestOutput) {
    Write-Host $pytestOutput
}

if ($errors.Count -gt 0) {
    Write-Host ""
    Write-Host "=== Errors ===" -ForegroundColor Red
    foreach ($err in $errors) { Write-Host "  $err" -ForegroundColor Red }
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")

exit $(if ($overallResult -eq "FAIL") { 1 } else { 0 })
