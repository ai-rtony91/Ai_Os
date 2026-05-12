$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$serverFile = Join-Path $repoRoot "apps\trading_lab\trading_lab\server\run_local_server.py"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python was not found. Install Python or add it to PATH, then rerun this launcher."
}

if (-not (Test-Path -LiteralPath $serverFile)) {
    throw "Server file missing: $serverFile"
}

Set-Location $repoRoot
$env:PYTHONPATH = Join-Path $repoRoot "apps\trading_lab"

Write-Host "AI_OS Trading Lab Local Paper Runtime"
Write-Host "Paper Only: YES"
Write-Host "Live Trading: BLOCKED"
Write-Host "URL: http://127.0.0.1:8765"
Write-Host "Press Ctrl+C to stop"

python $serverFile
if ($LASTEXITCODE -ne 0) {
    throw "AI_OS local paper server stopped with exit code $LASTEXITCODE."
}
