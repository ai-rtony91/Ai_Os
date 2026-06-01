[CmdletBinding()]
param(
    [string[]]$Tools = @("codex", "claude", "gh", "git"),
    [int]$VersionTimeoutSec = 10
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$logPath = Join-Path $repoRoot "relay\logs\preflight.log"
$timeoutHelper = Join-Path $PSScriptRoot "..\timeout\Invoke-AiOsCliWithTimeout.ps1"
$missing = New-Object System.Collections.Generic.List[string]
$unauth = New-Object System.Collections.Generic.List[string]

foreach ($tool in $Tools) {
    $cmd = Get-Command $tool -ErrorAction SilentlyContinue
    if ($null -eq $cmd) {
        $missing.Add($tool)
        continue
    }

    $result = & $timeoutHelper -FilePath $cmd.Source -ArgumentList @("--version") -TimeoutSec $VersionTimeoutSec -WorkingDirectory $repoRoot
    if ([string]$result.exit_code -ne "0") {
        $unauth.Add($tool)
    }
}

$payload = [ordered]@{
    ok = ($missing.Count -eq 0 -and $unauth.Count -eq 0)
    missing = @($missing)
    unauth = @($unauth)
    checked_at_utc = (Get-Date).ToUniversalTime()
}

$logDir = Split-Path -Parent $logPath
if (-not (Test-Path -LiteralPath $logDir -PathType Container)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}
Add-Content -LiteralPath $logPath -Value (($payload | ConvertTo-Json -Compress -Depth 5))

return [pscustomobject]$payload
