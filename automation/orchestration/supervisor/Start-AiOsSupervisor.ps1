Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$statusScript = Join-Path $scriptRoot "Show-AiOsSupervisorStatus.ps1"

if (-not (Test-Path -LiteralPath $statusScript -PathType Leaf)) {
    throw "Supervisor status script not found: $statusScript"
}

& $statusScript
