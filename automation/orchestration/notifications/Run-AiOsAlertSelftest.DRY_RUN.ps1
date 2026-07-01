[CmdletBinding()]
param(
    [ValidateSet("", "tip", "jackpot", "reply")]
    [string]$Only = "",
    [switch]$Compact
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$scriptPath = Join-Path $PSScriptRoot "aios_alert_selftest_v1.py"
$configPath = Join-Path $repoRoot "control\secrets\alert_channels.example.json"

if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
    throw "Missing AIOS alert self-test script: $scriptPath"
}
if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) {
    throw "Missing AIOS alert self-test example config: $configPath"
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
}
if ($null -eq $python) {
    throw "Python was not found on PATH."
}

$pythonArgs = @($scriptPath, "--repo-root", $repoRoot, "--config", $configPath)
if ($Only) {
    $pythonArgs += @("--only", $Only)
}
if (-not $Compact) {
    $pythonArgs += "--pretty"
}

& $python.Source @pythonArgs
exit $LASTEXITCODE
