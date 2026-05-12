$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $repoRoot

Write-Host "AI_OS Trading Lab Windows Codex #4 Control Tower"
Write-Host "Mode: DRY_RUN"
Write-Host "Paper Only: YES"
Write-Host "Live Trading: BLOCKED"
Write-Host ""

$failures = New-Object System.Collections.Generic.List[string]

Write-Host "Git status:"
git status --short --branch
Write-Host ""

Write-Host "Trading Lab phase folders:"
Get-ChildItem -LiteralPath "docs\AI_OS\trading_laboratory" -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like "phase_*" } |
    Sort-Object Name |
    ForEach-Object { Write-Host "- $($_.Name)" }
Write-Host ""

Write-Host "Trading Lab DRY_RUN validators:"
$currentScript = $PSCommandPath
$allDryRunScripts = Get-ChildItem -LiteralPath "automation\trading_lab" -Filter "*.DRY_RUN.ps1" -File -ErrorAction SilentlyContinue | Sort-Object Name
foreach ($script in $allDryRunScripts) {
    Write-Host "- $($script.Name)"
}
Write-Host ""

$validators = $allDryRunScripts |
    Where-Object { $_.FullName -ne $currentScript } |
    Where-Object { $_.Name -like "Test-*.DRY_RUN.ps1" } |
    Sort-Object Name

$phase143Folder = "docs\AI_OS\trading_laboratory\phase_14_3"
$phase143Doc = Join-Path $phase143Folder "PHASE_14_3_PAPER_SIGNAL_DECISION_ENGINE.md"
$phase143Json = Join-Path $phase143Folder "PHASE_14_3_DECISION_RESULT_001.json"
$phase143Validator = "automation\trading_lab\Test-AiOsTradingLabPhase143DecisionEngine.DRY_RUN.ps1"

$phase143Exists = Test-Path -LiteralPath $phase143Folder
$phase143DocExists = Test-Path -LiteralPath $phase143Doc
$phase143JsonExists = Test-Path -LiteralPath $phase143Json
$phase143ValidatorExists = Test-Path -LiteralPath $phase143Validator

if ($phase143Exists -and $phase143DocExists -and $phase143JsonExists -and $phase143ValidatorExists) {
    $phase143Status = "PRESENT_NOT_VALIDATED"
} elseif ((@($phase143Exists, $phase143DocExists, $phase143JsonExists, $phase143ValidatorExists) | Where-Object { $_ }).Count -gt 0) {
    $phase143Status = "PARTIAL"
} elseif (-not $phase143Exists -and -not $phase143DocExists -and -not $phase143JsonExists -and -not $phase143ValidatorExists) {
    $phase143Status = "MISSING"
} else {
    $phase143Status = "UNKNOWN"
}

Write-Host "Phase 14.3 checkpoint:"
Write-Host "- folder: $phase143Exists"
Write-Host "- decision engine doc: $phase143DocExists"
Write-Host "- decision result JSON: $phase143JsonExists"
Write-Host "- validator: $phase143ValidatorExists"
Write-Host "- status: $phase143Status"
Write-Host ""

$jsonRoots = @(
    "docs\AI_OS\trading_laboratory\phase_14_3",
    "docs\AI_OS\trading_laboratory\phase_14_4",
    "docs\AI_OS\trading_laboratory\profitability",
    "docs\AI_OS\trading_laboratory\latency"
)

$jsonFiles = @()
foreach ($root in $jsonRoots) {
    if (Test-Path -LiteralPath $root) {
        $jsonFiles += Get-ChildItem -LiteralPath $root -Filter "*.json" -File -Recurse -ErrorAction SilentlyContinue
    }
}

Write-Host "JSON parse and safety scan:"
$forbiddenPatterns = @(
    '"execution_allowed"\s*:\s*true',
    '"approved_for_live_execution"\s*:\s*true',
    '"broker[^"]*"\s*:\s*"(ENABLED|ACTIVE|TRUE|ON)"',
    '"broker[^"]*enabled"\s*:\s*true',
    '"oanda[^"]*"\s*:\s*"(ENABLED|ACTIVE|TRUE|ON)"',
    '"oanda[^"]*enabled"\s*:\s*true',
    '"real_webhook[^"]*"\s*:\s*"(ENABLED|ACTIVE|TRUE|ON)"',
    '"real_webhook[^"]*enabled"\s*:\s*true',
    '"real_order[^"]*"\s*:\s*"(ENABLED|ACTIVE|TRUE|ON)"',
    '"real_order[^"]*enabled"\s*:\s*true',
    '"live_trading[^"]*"\s*:\s*"(ENABLED|ACTIVE|TRUE|ON)"',
    '"live_trading[^"]*enabled"\s*:\s*true',
    '"live_execution[^"]*"\s*:\s*"(ENABLED|ACTIVE|TRUE|ON)"',
    '"live_execution[^"]*enabled"\s*:\s*true'
)

foreach ($file in $jsonFiles | Sort-Object FullName) {
    $relative = Resolve-Path -LiteralPath $file.FullName -Relative
    try {
        $raw = Get-Content -LiteralPath $file.FullName -Raw
        $null = $raw | ConvertFrom-Json
        Write-Host "- PARSE PASS: $relative"
    } catch {
        $failures.Add("JSON parse failed: $relative")
        Write-Host "- PARSE FAIL: $relative"
        continue
    }

    foreach ($pattern in $forbiddenPatterns) {
        if ($raw -match $pattern) {
            $failures.Add("Forbidden live execution pattern found in $relative")
            Write-Host "- SAFETY FAIL: $relative"
            break
        }
    }
}

if ($jsonFiles.Count -eq 0) {
    Write-Host "- No JSON files found in scanned roots."
}
Write-Host ""

Write-Host "Running existing Trading Lab DRY_RUN validators:"
$phase143Validated = $false
foreach ($validator in $validators) {
    Write-Host "- RUN: $($validator.Name)"
    & powershell -ExecutionPolicy Bypass -File $validator.FullName
    if ($LASTEXITCODE -ne 0) {
        $failures.Add("Validator failed: $($validator.Name)")
        Write-Host "- FAIL: $($validator.Name)"
    } else {
        Write-Host "- PASS: $($validator.Name)"
        if ($validator.Name -eq "Test-AiOsTradingLabPhase143DecisionEngine.DRY_RUN.ps1") {
            $phase143Validated = $true
        }
    }
}
Write-Host ""

if ($phase143Status -eq "PRESENT_NOT_VALIDATED" -and $phase143Validated) {
    $phase143Status = "PRESENT_AND_VALIDATED"
}

Write-Host "Final Phase 14.3 status: $phase143Status"

if ($failures.Count -gt 0) {
    Write-Host "CONTROL TOWER RESULT: FAIL"
    foreach ($failure in $failures) {
        Write-Host "- $failure"
    }
    exit 1
}

Write-Host "CONTROL TOWER RESULT: PASS"
Write-Host "Safety blockers confirmed: live execution, broker, OANDA, real webhooks, real orders remain blocked in scanned JSON."
exit 0
