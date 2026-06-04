[CmdletBinding()]
param(
    [ValidateSet("DRY_RUN")]
    [string]$Mode = "DRY_RUN",

    [string]$RepoRoot,

    [switch]$OutputJson
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRootResolved = if (-not [string]::IsNullOrWhiteSpace($RepoRoot)) {
    (Resolve-Path -LiteralPath $RepoRoot).Path
} else {
    (Resolve-Path -LiteralPath (Join-Path $scriptRoot "../../..")).Path
}

$readinessScript = Join-Path $repoRootResolved "automation/onboarding/Test-AiOsOpenAiCodexNightSupervisorOnboarding.ps1"

if (-not (Test-Path -LiteralPath $readinessScript -PathType Leaf)) {
    Write-Error "Onboarding readiness script not found: $readinessScript"
    exit 1
}

$arguments = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", $readinessScript,
    "-Mode", $Mode,
    "-RepoRoot", $repoRootResolved
)

if ($OutputJson) {
    $arguments += "-OutputJson"
}

& powershell @arguments
exit $LASTEXITCODE
