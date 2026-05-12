$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

$RequiredFiles = @(
    "apps/trading_lab/trading_lab/tv_tp_bridge/paper_route_replay.py",
    "apps/trading_lab/mock-data/tv_tp_bridge/paper_route_replay_result.example.json",
    "automation/trading_lab/Test-AiOsTradingLabPhase1411PaperRouteReplay.DRY_RUN.ps1",
    "docs/AI_OS/trading_laboratory/phase_14_11/PHASE_14_11_PAPER_ROUTE_REPLAY_CONNECTOR.md",
    "Reports/checkpoints/CHECKPOINT_PHASE_14_11_PAPER_ROUTE_REPLAY.md"
)

foreach ($File in $RequiredFiles) {
    if (-not (Test-Path $File)) {
        throw "Missing Phase 14.11 file: $File"
    }
}

$ReplayJsonPath = "apps/trading_lab/mock-data/tv_tp_bridge/paper_route_replay_result.example.json"
$ReplayJson = Get-Content -Raw $ReplayJsonPath | ConvertFrom-Json

$PythonScript = @'
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path.cwd()))

from apps.trading_lab.trading_lab.tv_tp_bridge.paper_route_replay import (
    build_paper_route_replay_result,
    write_example_result,
)

result = build_paper_route_replay_result()
written = write_example_result()

assert result == written

required = {
    "replay_id",
    "mode",
    "source",
    "pair",
    "timeframe",
    "direction",
    "paper_validation_status",
    "traderspost_handoff_status",
    "broker_status",
    "live_execution_status",
    "expected_fill_price",
    "actual_fill_price",
    "spread_estimate",
    "slippage_estimate",
    "fill_latency_ms",
    "paper_result_status",
    "execution_quality_score",
    "scorecard_ready",
    "blocked_reason",
}
missing = required.difference(result)
assert not missing, f"Missing replay fields: {sorted(missing)}"
assert isinstance(result["scorecard_ready"], bool)
assert isinstance(result["execution_quality_score"], (int, float))
assert result["mode"] == "paper_only"
assert result["live_execution_status"] == "BLOCKED"
assert result["broker_status"] == "NOT_CONNECTED"
assert result["traderspost_handoff_status"] == "NOT_SENT"
assert "spread_estimate" in result
assert "slippage_estimate" in result
assert isinstance(result["spread_estimate"], (int, float))
assert isinstance(result["slippage_estimate"], (int, float))

print(json.dumps(result, indent=2))
'@

$TempScript = New-TemporaryFile
try {
    Set-Content -Path $TempScript -Value $PythonScript -Encoding UTF8
    $Output = python $TempScript
    if ($LASTEXITCODE -ne 0) {
        throw "Phase 14.11 connector execution failed."
    }
}
finally {
    Remove-Item -Path $TempScript -Force
}

$ReplayJson = Get-Content -Raw $ReplayJsonPath | ConvertFrom-Json
$RequiredFields = @(
    "replay_id",
    "mode",
    "source",
    "pair",
    "timeframe",
    "direction",
    "paper_validation_status",
    "traderspost_handoff_status",
    "broker_status",
    "live_execution_status",
    "expected_fill_price",
    "actual_fill_price",
    "spread_estimate",
    "slippage_estimate",
    "fill_latency_ms",
    "paper_result_status",
    "execution_quality_score",
    "scorecard_ready",
    "blocked_reason"
)

foreach ($Field in $RequiredFields) {
    if (-not $ReplayJson.PSObject.Properties.Name.Contains($Field)) {
        throw "Missing required replay field: $Field"
    }
}

if ($ReplayJson.scorecard_ready -isnot [bool]) {
    throw "scorecard_ready must be boolean."
}
$ExecutionQualityScore = 0.0
if (-not [double]::TryParse([string]$ReplayJson.execution_quality_score, [ref]$ExecutionQualityScore)) {
    throw "execution_quality_score must be numeric."
}
$SpreadEstimate = 0.0
if (-not [double]::TryParse([string]$ReplayJson.spread_estimate, [ref]$SpreadEstimate)) {
    throw "spread_estimate must be numeric."
}
$SlippageEstimate = 0.0
if (-not [double]::TryParse([string]$ReplayJson.slippage_estimate, [ref]$SlippageEstimate)) {
    throw "slippage_estimate must be numeric."
}
if ($ReplayJson.mode -ne "paper_only") {
    throw "mode must be paper_only."
}
if ($ReplayJson.live_execution_status -ne "BLOCKED") {
    throw "live_execution_status must be BLOCKED."
}
if ($ReplayJson.broker_status -ne "NOT_CONNECTED") {
    throw "broker_status must be NOT_CONNECTED."
}
if ($ReplayJson.traderspost_handoff_status -ne "NOT_SENT") {
    throw "traderspost_handoff_status must be NOT_SENT."
}
if ($ReplayJson.oanda_status -eq "CONNECTED") {
    throw "OANDA must not be connected."
}
if ($ReplayJson.real_order_status -eq "SENT") {
    throw "Real order must not be sent."
}
if ($ReplayJson.api_key_present -eq $true) {
    throw "API key must not be present."
}
if ($ReplayJson.secret_present -eq $true) {
    throw "Secret must not be present."
}

$ForbiddenTerms = @(
    "live execution allowed",
    "broker connected",
    "webhook sent",
    "OANDA connected",
    "real order sent",
    "API key present",
    "secret present"
)

$OutputContent = Get-Content -Raw $ReplayJsonPath

foreach ($Term in $ForbiddenTerms) {
    if ($OutputContent -match [regex]::Escape($Term)) {
        throw "Forbidden unsafe output found: $Term"
    }
}

Write-Output "PASS: AI_OS Phase 14.11 paper route replay validation passed."
Write-Output "Paper-only replay route is operational."
Write-Output "Live execution, broker routing, webhooks, OANDA, API keys, and real orders remain BLOCKED."
