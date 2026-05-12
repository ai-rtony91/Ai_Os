$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$senderFile = Join-Path $repoRoot "apps\trading_lab\trading_lab\server\send_fake_signal.py"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python was not found. Install Python or add it to PATH, then rerun this launcher."
}

if (-not (Test-Path -LiteralPath $senderFile)) {
    throw "Fake signal sender missing: $senderFile"
}

Set-Location $repoRoot
$env:PYTHONPATH = Join-Path $repoRoot "apps\trading_lab"

python $senderFile
if ($LASTEXITCODE -ne 0) {
    throw "Fake paper signal failed."
}
