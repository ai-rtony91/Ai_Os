param(
    [switch]$Apply,
    [switch]$AllowNonMain
)

$ErrorActionPreference = "Stop"

function Write-AiosLine {
    param([string]$Status, [string]$Message)
    Write-Host "$Status`t$Message"
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$forbiddenOutputTerms = @(".env", "secrets", "credentials", "broker", "OANDA", "live webhook", "real order")
$pythonModule = Join-Path $repoRoot "services\python_supervisor\autonomy_bridge.py"

Set-Location $repoRoot
$branch = (& git branch --show-current).Trim()
$gitStatus = (& git status --short --branch) -join "`n"

Write-AiosLine "INFO" "repo_path=$repoRoot"
Write-AiosLine "INFO" "branch=$branch"
Write-AiosLine "INFO" "mode=$(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"

if ($branch -ne "main" -and -not $AllowNonMain) {
    Write-AiosLine "BLOCKED" "Autonomy Bridge only runs on main unless -AllowNonMain is explicitly passed."
    exit 2
}

if (-not (Test-Path $pythonModule)) {
    Write-AiosLine "BLOCKED" "Missing Python bridge module: $pythonModule"
    exit 2
}

$plannedOutputs = @(
    "telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json",
    "telemetry/morning_digest/MORNING_DIGEST_STATE.json",
    "telemetry/morning_digest/MORNING_DIGEST_LATEST.md"
)

foreach ($output in $plannedOutputs) {
    foreach ($term in $forbiddenOutputTerms) {
        if ($output.ToLowerInvariant().Contains($term.ToLowerInvariant())) {
            Write-AiosLine "BLOCKED" "Forbidden output path term detected: $term in $output"
            exit 2
        }
    }
}

Write-AiosLine "INFO" "planned_outputs=$($plannedOutputs -join ', ')"

$argsList = @(
    $pythonModule,
    "--repo-root", $repoRoot,
    "--repo-branch", $branch,
    "--git-status", $gitStatus,
    "--pretty"
)

if ($Apply) {
    $argsList += "--apply"
}

$outputJson = & python @argsList
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    Write-AiosLine "BLOCKED" "Python bridge returned exit code $exitCode"
    Write-Output $outputJson
    exit $exitCode
}

$receipt = $outputJson | ConvertFrom-Json
if (-not $receipt.bridge_state.dashboard_cards -or $receipt.bridge_state.dashboard_cards.Count -lt 1) {
    Write-AiosLine "BLOCKED" "Bridge output did not include dashboard_cards."
    exit 2
}

Write-AiosLine "PASS" "autonomy_bridge_status=$($receipt.status)"
Write-AiosLine "PASS" "planned_output_paths=$($receipt.planned_output_paths -join ', ')"
if ($Apply) {
    Write-AiosLine "PASS" "written_output_paths=$($receipt.written_output_paths -join ', ')"
} else {
    Write-AiosLine "PASS" "DRY_RUN only; no files written."
}

$outputJson
