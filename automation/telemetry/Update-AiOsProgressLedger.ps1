$ErrorActionPreference = "Stop"

function Invoke-GitLines {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & git @Arguments 2>$null
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    if ($exitCode -ne 0) {
        return @()
    }

    return @($output)
}

function Get-RepoRoot {
    $root = @(Invoke-GitLines -Arguments @("rev-parse", "--show-toplevel"))
    if ($root.Count -eq 0 -or [string]::IsNullOrWhiteSpace([string]$root[0])) {
        return (Resolve-Path ".").Path
    }
    return ([string]$root[0]).Trim()
}

$repoRoot = Get-RepoRoot
Set-Location -LiteralPath $repoRoot

$telemetryDir = Join-Path $repoRoot "Reports\telemetry"
New-Item -ItemType Directory -Force -Path $telemetryDir | Out-Null

$ledgerPath = Join-Path $telemetryDir "AIOS_STAGE_PROGRESS_LEDGER.csv"
$ledgerHeader = "date,timestamp,phase,stage,stage_name,status,percent_complete,evidence_path,notes"

if (-not (Test-Path -LiteralPath $ledgerPath)) {
    Set-Content -LiteralPath $ledgerPath -Value $ledgerHeader -Encoding utf8
}

$now = Get-Date
$row = [pscustomobject]@{
    date             = $now.ToString("yyyy-MM-dd")
    timestamp        = $now.ToString("o")
    phase            = "Phase 15"
    stage            = "Stage 15.1"
    stage_name       = "Production Telemetry Engine"
    status           = "STARTED"
    percent_complete = 10
    evidence_path    = "Reports/telemetry/AIOS_PRODUCTION_DAILY_LEDGER.csv"
    notes            = "Initial production telemetry engine created. No live trading. No broker. No secrets."
}

$row | Export-Csv -LiteralPath $ledgerPath -NoTypeInformation -Append -Encoding utf8

Write-Host "PASS: AI_OS stage progress ledger appended to $ledgerPath"
