$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    $root = (& git rev-parse --show-toplevel 2>$null)
    if ([string]::IsNullOrWhiteSpace($root)) {
        return (Resolve-Path ".").Path
    }
    return $root.Trim()
}

function Add-Failure {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    $script:Failures.Add($Message) | Out-Null
}

function Test-RequiredPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [string]$Description
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        Add-Failure "FAIL: Missing $Description at $Path"
    }
}

$repoRoot = Get-RepoRoot
Set-Location -LiteralPath $repoRoot
$Failures = [System.Collections.Generic.List[string]]::new()

$requiredFiles = @(
    "automation\telemetry\Invoke-AiOsProductionSnapshot.ps1",
    "automation\telemetry\Update-AiOsProgressLedger.ps1",
    "Reports\telemetry\AIOS_PRODUCTION_DAILY_LEDGER.csv",
    "Reports\telemetry\AIOS_STAGE_PROGRESS_LEDGER.csv",
    "Reports\telemetry\AIOS_WORKER_ACTIVITY_LEDGER.csv",
    "Reports\telemetry\AIOS_VALIDATOR_HISTORY_LEDGER.csv",
    "Reports\telemetry\AIOS_AI_VS_HUMAN_OUTPUT_LEDGER.csv",
    "docs\AI_OS\telemetry\PHASE_15_1_PRODUCTION_TELEMETRY_ENGINE.md",
    "apps\dashboard\mock-data\production-heatmap-v1.example.json",
    "apps\dashboard\mock-data\stage-progress-v1.example.json",
    "apps\dashboard\mock-data\ai-vs-human-output-v1.example.json"
)

foreach ($file in $requiredFiles) {
    Test-RequiredPath -Path (Join-Path $repoRoot $file) -Description "required telemetry file"
}

Test-RequiredPath -Path (Join-Path $repoRoot "Reports\telemetry") -Description "Reports telemetry folder"
Test-RequiredPath -Path (Join-Path $repoRoot "docs\AI_OS\telemetry") -Description "docs telemetry folder"

$scriptsToScan = @(
    "automation\telemetry\Invoke-AiOsProductionSnapshot.ps1",
    "automation\telemetry\Update-AiOsProgressLedger.ps1"
)

$blockedPatternParts = @(
    ("OA" + "NDA"),
    'api[_ -]?key',
    'secret[_ -]?key',
    'broker\s+order',
    'place[-_\s]*order',
    'send[-_\s]*order',
    'submit[-_\s]*order',
    'live[-_\s]*execution\s*=\s*\$?true',
    'enable[-_\s]*live[-_\s]*trading',
    'New[-_\s]*ScheduledTask',
    'Register[-_\s]*ScheduledTask',
    'schtasks'
)

foreach ($relativeScript in $scriptsToScan) {
    $scriptPath = Join-Path $repoRoot $relativeScript
    if (-not (Test-Path -LiteralPath $scriptPath)) {
        continue
    }

    $content = Get-Content -LiteralPath $scriptPath -Raw
    foreach ($pattern in $blockedPatternParts) {
        if ($content -match $pattern) {
            Add-Failure "FAIL: Blocked production safety pattern detected in $relativeScript"
            break
        }
    }
}

$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$diffCheckOutput = & git diff --check 2>&1
$diffCheckExitCode = $LASTEXITCODE
$ErrorActionPreference = $previousErrorActionPreference

if ($diffCheckOutput) {
    $diffCheckOutput | ForEach-Object { Write-Host $_ }
}

if ($diffCheckExitCode -ne 0) {
    Add-Failure "FAIL: git diff --check reported whitespace or conflict-marker problems."
}

if ($Failures.Count -gt 0) {
    foreach ($failure in $Failures) {
        Write-Host $failure
    }
    exit 1
}

Write-Host "PASS: AI_OS Production Telemetry validation passed."
