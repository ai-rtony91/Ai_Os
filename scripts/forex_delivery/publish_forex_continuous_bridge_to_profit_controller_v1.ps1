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
$BranchName = "lane/forex-continuous-bridge-to-profit-controller-v1"
$CommitMessage = "feat(forex): add continuous bridge to profit controller"

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
        throw "Publish scope is dirty with unallowed files: $($invalid -join ', ')"
    }
}

function Assert-StagedScope {
    param([string[]]$stagedPaths, [string[]]$allowed)
    $invalid = @()
    foreach ($path in $stagedPaths) {
        if (-not ($allowed -contains $path)) {
            $invalid += $path
        }
    }
    if ($invalid.Count -gt 0) {
        throw "Staged scope contains unallowed files: $($invalid -join ', ')"
    }
}

$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    throw "Publish requires branch main. Current branch: $currentBranch"
}

$dirtyPaths = Get-DirtyArtifacts
Assert-AllowedDirtyScope -dirtyPaths $dirtyPaths -allowed $AllowedPaths

pwsh -File scripts/forex_delivery/validate_forex_continuous_bridge_to_profit_controller_v1.ps1
if ($LASTEXITCODE -ne 0) { throw "HOST_VALIDATION_FAILED" }

git fetch origin
git checkout -B $BranchName
git add -- $AllowedPaths
$staged = git diff --cached --name-only
Assert-StagedScope -stagedPaths $staged -allowed $AllowedPaths

if ($staged.Count -eq 0) {
    throw "No files staged for publish."
}

git commit -m $CommitMessage
git push -u origin $BranchName

$prUrl = gh pr create --title "feat: add continuous bridge to profit controller" --body "Adds the compressed Forex continuous bridge-to-profit controller and host validator/publish artifacts." --fill
if ([string]::IsNullOrWhiteSpace($prUrl)) {
    throw "PR creation did not return a PR URL."
}

gh pr checks --watch $prUrl
$checkState = gh pr view --json checksState --jq ".checksState"
if ($checkState -ne "SUCCESS") {
    throw "PR checks did not pass. State: $checkState"
}

gh pr merge --squash $prUrl
git checkout main
git fetch origin
git reset --hard origin/main
git status --short --branch | Write-Output

Write-Output "PUBLISH_COMPLETE_CLEAN"
