$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$scorecardScript = Join-Path $repoRoot "apps\trading_lab\trading_lab\reports\paper_signal_scorecard.py"
$scorecardPath = Join-Path $repoRoot "Reports\trading_lab\PAPER_SIGNAL_SCORECARD.md"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python was not found. Install Python or add it to PATH, then rerun this scorecard."
}

if (-not (Test-Path -LiteralPath $scorecardScript)) {
    throw "Paper signal scorecard script missing: $scorecardScript"
}

Set-Location $repoRoot
$env:PYTHONPATH = Join-Path $repoRoot "apps\trading_lab"

python $scorecardScript --output $scorecardPath
if ($LASTEXITCODE -ne 0) {
    throw "AI_OS paper signal scorecard failed."
}

Write-Host "Saved: Reports\trading_lab\PAPER_SIGNAL_SCORECARD.md"
