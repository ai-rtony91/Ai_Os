$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$summaryScript = Join-Path $repoRoot "apps\trading_lab\trading_lab\reports\paper_runtime_summary.py"
$summaryPath = Join-Path $repoRoot "Reports\trading_lab\PAPER_RUNTIME_OPERATOR_SUMMARY.md"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python was not found. Install Python or add it to PATH, then rerun this status check."
}

if (-not (Test-Path -LiteralPath $summaryScript)) {
    throw "Paper runtime summary script missing: $summaryScript"
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $summaryPath) | Out-Null

Set-Location $repoRoot
$env:PYTHONPATH = Join-Path $repoRoot "apps\trading_lab"

Write-Host "AI_OS Trading Lab Paper Runtime Status"
Write-Host "Paper Only: YES"
Write-Host "Local Only: YES"
Write-Host "Live Trading: BLOCKED"
Write-Host ""

python $summaryScript --output $summaryPath
if ($LASTEXITCODE -ne 0) {
    throw "AI_OS paper runtime status summary failed."
}

Write-Host ""
Write-Host "Summary file: Reports\trading_lab\PAPER_RUNTIME_OPERATOR_SUMMARY.md"
