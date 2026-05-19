<# 
AI_OS Stage 7-12 Master Validation DRY_RUN
Read-only validator runner. Does not create, modify, delete, move, rename, deploy, connect brokers, or place trades.
#>

[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path -LiteralPath ".").Path
)

$ErrorActionPreference = "Stop"

function New-Result {
    param(
        [string]$Name,
        [string]$Scope,
        [string]$Status,
        [string]$Evidence,
        [string]$NextAction
    )

    [PSCustomObject]@{
        Validator = $Name
        Scope = $Scope
        Status = $Status
        Evidence = $Evidence
        NextAction = $NextAction
    }
}

$requiredPaths = @(
    "docs/AI_OS/signal_intelligence",
    "docs/AI_OS/execution",
    "docs/AI_OS/agents",
    "docs/AI_OS/production",
    "docs/concepts/aios-autonomous-safety-concepts.md",
    "docs/roadmap/aios-product-roadmap.md",
    "docs/concepts/aios-dashboard-and-interface-concepts.md",
    "docs/AI_OS/validators",
    "Reports/daily",
    "Reports/checkpoints",
    "Reports/progress",
    "Reports/health"
)

$results = New-Object System.Collections.Generic.List[object]

foreach ($path in $requiredPaths) {
    $fullPath = Join-Path -Path $RepoRoot -ChildPath $path
    if (Test-Path -LiteralPath $fullPath) {
        $results.Add((New-Result -Name "RequiredPathExists" -Scope $path -Status "PASS" -Evidence $path -NextAction "None"))
    } else {
        $results.Add((New-Result -Name "RequiredPathExists" -Scope $path -Status "FAIL" -Evidence $path -NextAction "Create a DRY_RUN gap plan before APPLY"))
    }
}

$validatorFiles = Get-ChildItem -LiteralPath (Join-Path -Path $RepoRoot -ChildPath "automation") -Recurse -File -Filter "*.DRY_RUN.ps1" -ErrorAction SilentlyContinue
if ($validatorFiles.Count -gt 0) {
    $results.Add((New-Result -Name "ValidatorInventory" -Scope "automation" -Status "PASS" -Evidence "$($validatorFiles.Count) DRY_RUN validators discovered" -NextAction "Review inventory before master runner expansion"))
} else {
    $results.Add((New-Result -Name "ValidatorInventory" -Scope "automation" -Status "WARN" -Evidence "No DRY_RUN validators discovered" -NextAction "Create validator inventory gap report"))
}

$protectedRootFiles = @(
    "README.md",
    "AGENTS.md",
    "RISK_POLICY.md",
    "SOURCE_LOG.md",
    "ERROR_LOG.md",
    "HALLUCINATION_LOG.md",
    "AAR.md",
    "DAILY_REPORT.md",
    "WHITEPAPER.md"
)

foreach ($file in $protectedRootFiles) {
    $fullPath = Join-Path -Path $RepoRoot -ChildPath $file
    if (Test-Path -LiteralPath $fullPath) {
        $results.Add((New-Result -Name "ProtectedRootFilePresent" -Scope $file -Status "PASS" -Evidence $file -NextAction "Do not modify without explicit approval"))
    } else {
        $results.Add((New-Result -Name "ProtectedRootFilePresent" -Scope $file -Status "WARN" -Evidence $file -NextAction "Mark UNKNOWN unless verified elsewhere"))
    }
}

$results | Format-Table -AutoSize

if ($results.Status -contains "FAIL") {
    exit 1
}

exit 0
