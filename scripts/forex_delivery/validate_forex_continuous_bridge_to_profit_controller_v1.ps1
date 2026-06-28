Set-Location -LiteralPath "C:/Dev/Ai.Os"
$ErrorActionPreference = "Stop"

$AllowedPaths = @(
    "docs/governance/programs/AIOS_FOREX_CONTINUOUS_BRIDGE_TO_PROFIT_CONTROLLER_V1.md",
    "docs/governance/programs/epics/EPC-FOREX-CONTINUOUS-PROFIT-EXECUTION-BRIDGE-V1.md",
    "docs/governance/programs/buckets/BKT-FOREX-CONTINUOUS-BRIDGE-COMPRESSED-FLOWS-V1.md",
    "automation/forex_engine/forex_continuous_bridge_to_profit_controller_v1.py",
    "scripts/forex_delivery/run_forex_continuous_bridge_to_profit_controller_v1.py",
    "scripts/forex_delivery/validate_forex_continuous_bridge_to_profit_controller_v1.ps1",
    "scripts/forex_delivery/publish_forex_continuous_bridge_to_profit_controller_v1.ps1",
    "Reports/forex_delivery/AIOS_FOREX_CONTINUOUS_BRIDGE_TO_PROFIT_CONTROLLER_V1.json",
    "Reports/forex_delivery/AIOS_FOREX_CONTINUOUS_BRIDGE_TO_PROFIT_CONTROLLER_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_CONTINUOUS_BRIDGE_TO_PROFIT_CONTROLLER_NEXT_ACTION_QUEUE_V1.md",
    "tests/forex_engine/test_forex_continuous_bridge_to_profit_controller_v1.py"
)

function Get-DirtyArtifacts {
    $status = git status --short
    if (-not $status) {
        return @()
    }
    $paths = @()
    foreach ($line in $status) {
        $parts = $line.ToString().Trim()
        if ($parts.Length -lt 4) {
            continue
        }
        $path = $parts.Substring(3).Trim()
        if ([string]::IsNullOrWhiteSpace($path)) {
            continue
        }
        if ($path.EndsWith("/")) {
            continue
        }
        $paths += $path
    }
    return $paths
}

function Assert-AllowedDirtyScope {
    param([string[]]$dirtyPaths, [string[]]$allowed)
    $invalid = @()
    foreach ($path in $dirtyPaths) {
        if (-not ($allowed -contains $path)) {
            $invalid += $path
        }
    }
    if ($invalid.Count -gt 0) {
        throw "Dirty scope contains unallowed paths: $($invalid -join ', ')"
    }
}

$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    throw "Validation requires branch main. Current branch: $currentBranch"
}

$dirtyPaths = Get-DirtyArtifacts
Assert-AllowedDirtyScope -dirtyPaths $dirtyPaths -allowed $AllowedPaths

python scripts/forex_delivery/run_forex_continuous_bridge_to_profit_controller_v1.py
if ($LASTEXITCODE -ne 0) { throw "CONTROLLER_RUNNER_FAILED" }

python -m pytest tests/forex_engine/test_forex_continuous_bridge_to_profit_controller_v1.py -q
if ($LASTEXITCODE -ne 0) { throw "CONTROLLER_PYTEST_FAILED" }

git diff --check -- $AllowedPaths
if ($LASTEXITCODE -ne 0) { throw "CONTROLLER_DIFF_CHECK_FAILED" }

$JsonPath = "Reports/forex_delivery/AIOS_FOREX_CONTINUOUS_BRIDGE_TO_PROFIT_CONTROLLER_V1.json"
$requiredJsonFields = @(
    "controller_status",
    "controller_mode",
    "owner_live_capital_intent_usd",
    "target_return_band",
    "profit_return_rate_status",
    "runtime_status",
    "vacation_mode_status",
    "next_required_flow"
)

$report = Get-Content -Raw $JsonPath | ConvertFrom-Json
foreach ($field in $requiredJsonFields) {
    if (-not ($report.PSObject.Properties.Name -contains $field)) {
        throw "Validation failed: missing JSON field $field"
    }
}

Write-Output "VALIDATION_PASSED"
