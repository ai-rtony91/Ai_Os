$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Validators = @(
    "automation\progress\Test-AiOsProgressLedgerReadiness.DRY_RUN.ps1",
    "automation\signal_intelligence\Test-AiOsSignalIntelligenceReadiness.DRY_RUN.ps1",
    "automation\signal_intelligence\Test-AiOsSignalPipelineReadiness.DRY_RUN.ps1",
    "automation\signal_intelligence\Test-AiOsStrategyRegistryExpansionReadiness.DRY_RUN.ps1",
    "automation\backtesting\Test-AiOsBacktestIngestionReadiness.DRY_RUN.ps1",
    "automation\backtesting\Test-AiOsBacktestEvidenceLayerReadiness.DRY_RUN.ps1",
    "automation\execution_safety\Test-AiOsExecutionSafetyBoundaryReadiness.DRY_RUN.ps1",
    "automation\execution_safety\Test-AiOsRiskControlDesignReadiness.DRY_RUN.ps1",
    "automation\agents\Test-AiOsMultiAgentRoleMatrixReadiness.DRY_RUN.ps1",
    "automation\agents\Test-AiOsAgentAuditLogReadiness.DRY_RUN.ps1",
    "automation\azure\Test-AiOsAzureProductionBoundaryReadiness.DRY_RUN.ps1",
    "automation\production\Test-AiOsObservabilityReadiness.DRY_RUN.ps1",
    "automation\bootstrap_engine\Test-AiOsBootstrapEngineReadiness.DRY_RUN.ps1",
    "automation\autonomous\Test-AiOsSelfAuditEngineReadiness.DRY_RUN.ps1",
    "automation\autonomous\Test-AiOsSelfHealingBoundaryReadiness.DRY_RUN.ps1",
    "automation\autonomous\Test-AiOsAutonomousOperatingLoopReadiness.DRY_RUN.ps1"
)

Write-Host "AI_OS Stage 7-11 Master Validation DRY_RUN"
$Failures = @()

foreach ($RelativePath in $Validators) {
    $FullPath = Join-Path $RepoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $FullPath -PathType Leaf)) {
        Write-Host "MISSING: $RelativePath"
        $Failures += $RelativePath
        continue
    }

    Write-Host "RUNNING: $RelativePath"
    & powershell -ExecutionPolicy Bypass -File $FullPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAILED: $RelativePath"
        $Failures += $RelativePath
    }
}

if ($Failures.Count -gt 0) {
    Write-Host "Result: FAIL"
    $Failures | ForEach-Object { Write-Host "Failure: $_" }
    exit 1
}

Write-Host "Result: PASS"
exit 0
