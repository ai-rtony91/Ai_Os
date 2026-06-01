[CmdletBinding()]
param(
    [switch]$Apply,
    [switch]$Pretty
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsRepoRoot {
    $root = & git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($root)) {
        throw "Unable to find git repository root."
    }
    return $root.Trim()
}

$repoRoot = Get-AiOsRepoRoot
$python = (Get-Command python -ErrorAction Stop).Source
$script = Join-Path $repoRoot "services/python_supervisor/runtime_state_exporter.py"
$argsList = @($script, "--repo-root", $repoRoot)
if ($Apply) { $argsList += "--apply" }
if ($Pretty) { $argsList += "--pretty" }

$output = @(& $python @argsList 2>&1)
$exitCode = $LASTEXITCODE
$text = ($output | Out-String).Trim()
if ($exitCode -ne 0) {
    throw "runtime_state_exporter.py failed with exit code $exitCode`: $text"
}

$receipt = $text | ConvertFrom-Json
Write-Host "AI_OS Runtime State Export"
Write-Host "Mode: $($receipt.mode)"
Write-Host "Written: $($receipt.written)"
Write-Host "Supervisor status: $($receipt.runtime_state_preview.supervisor_status)"
Write-Host "Write paths: $(@($receipt.write_paths) -join ', ')"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
