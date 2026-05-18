param(
    [switch]$Apply
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$WindowLayoutScript = Join-Path $RepoRoot "automation\window_identity\Open-AiOsWorkerWindowLayout.ps1"

if (-not (Test-Path -LiteralPath $WindowLayoutScript -PathType Leaf)) {
    throw "Window layout launcher not found: $WindowLayoutScript"
}

Write-Host "AI_OS Morning Workspace Launcher"
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host "Delegating to canonical window identity launcher."
Write-Host ""

$launcherArgs = @(
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $WindowLayoutScript,
    "-Preset",
    "compact"
)

if ($Apply) {
    $launcherArgs += "-Apply"
}

powershell @launcherArgs
