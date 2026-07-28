param(
    [string]$ReportDirectory = "",
    [string]$ArtifactJson = "",
    [string]$Today = ""
)

$ErrorActionPreference = "Stop"

function Resolve-AiOsRepoRoot {
    if ($env:AIOS_REPO_ROOT -and (Test-Path -LiteralPath $env:AIOS_REPO_ROOT)) {
        return (Resolve-Path -LiteralPath $env:AIOS_REPO_ROOT).Path
    }
    if ($PSScriptRoot) {
        $candidate = Join-Path $PSScriptRoot "../.."
        if (Test-Path -LiteralPath $candidate) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }
    $gitRoot = (& git rev-parse --show-toplevel 2>$null)
    if ($LASTEXITCODE -eq 0 -and $gitRoot) {
        return (Resolve-Path -LiteralPath $gitRoot.Trim()).Path
    }
    throw "AIOS_REPO_ROOT_UNRESOLVED"
}

function Get-GitStatusShort {
    return @(& git status --short --untracked-files=all)
}

try {
    $repoRoot = Resolve-AiOsRepoRoot
    Set-Location -LiteralPath $repoRoot

    $dirty = @(Get-GitStatusShort)
    if ($dirty.Count -gt 0) {
        throw "DIRTY_WORKTREE_BLOCKED:$($dirty -join '; ')"
    }

    if (-not $ReportDirectory) {
        if ($env:RUNNER_TEMP) {
            $ReportDirectory = Join-Path $env:RUNNER_TEMP "aios_daily_forex_continuation_router"
        }
        else {
            $ReportDirectory = Join-Path ([System.IO.Path]::GetTempPath()) "aios_daily_forex_continuation_router"
        }
    }

    $arguments = @("-m", "automation.forex_engine.daily_forex_continuation_router_v1", "--repo-root", $repoRoot, "--output-dir", $ReportDirectory)
    if ($ArtifactJson) { $arguments += @("--artifact-json", $ArtifactJson) }
    if ($Today) { $arguments += @("--today", $Today) }

    $output = @(& python @arguments 2>&1)
    if ($output) { $output | ForEach-Object { Write-Output $_ } }
    if ($LASTEXITCODE -ne 0) { throw "ROUTER_FAILED:$($output -join "`n")" }

    Write-Output "ROUTER_REPORT_JSON=$(Join-Path $ReportDirectory 'AIOS_DAILY_FOREX_CONTINUATION_ROUTER_V1.json')"
    Write-Output "ROUTER_REPORT_MD=$(Join-Path $ReportDirectory 'AIOS_DAILY_FOREX_CONTINUATION_ROUTER_V1_REPORT.md')"
    Write-Output "ROUTER_TICKET_JSON=$(Join-Path $ReportDirectory 'AIOS_DAILY_FOREX_NEXT_PACKET_TICKET_V1.json')"
    exit 0
}
catch {
    Write-Output "CONTINUATION_ROUTER_FAILED=$($_.Exception.Message)"
    exit 1
}
