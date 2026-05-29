[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$GoalText,

    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsAutoLoopFullPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $Path))
}

function Test-AiOsAutoLoopReportPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $allowedRoot = [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path "telemetry\auto_loop\reports"))
    $fullPath = Get-AiOsAutoLoopFullPath -Path $Path
    return $fullPath.StartsWith($allowedRoot, [System.StringComparison]::OrdinalIgnoreCase)
}

$timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$packetId = "AUTO_LOOP_PACKET_CANDIDATE_{0}" -f (Get-Date -Format "yyyyMMddHHmmss")
$branch = (& git branch --show-current 2>$null)
if (-not $branch) {
    $branch = "UNKNOWN"
}

$record = [ordered]@{
    packet_id = $packetId
    created_at = $timestamp
    goal_text = $GoalText
    mode = "DRY_RUN"
    lane = "Auto-Loop Closure Lane"
    worker_identity = "Codex Finish-Line Auto-Loop Worker"
    branch = $branch
    worktree = (Get-Location).Path
    allowed_paths = @(
        "automation/orchestration/auto_loop/",
        "telemetry/auto_loop/"
    )
    forbidden_paths = @(
        "automation/orchestration/work_packets/",
        "automation/orchestration/approval_inbox/",
        "automation/orchestration/command_queue/",
        "automation/orchestration/workers/",
        "runtime/",
        "services/runtime/",
        "services/supervisor/",
        "services/orchestrator/",
        "apps/trading_lab/trading_lab/execution/",
        "aios/modules/trader/",
        "secrets/",
        "credentials/",
        "broker/",
        "OANDA/"
    )
    protected_paths = @(
        "AGENTS.md",
        "README.md",
        "WHITEPAPER.md",
        "docs/governance/",
        "docs/workflows/",
        "docs/security/",
        "docs/architecture/",
        "docs/audits/"
    )
    required_reads = @(
        "AGENTS.md",
        "README.md",
        "WHITEPAPER.md",
        "docs/governance/source-of-truth-map.md",
        "docs/audits/active-system-map.md",
        "automation/orchestration/README.md"
    )
    validator_chain = @(
        "automation/orchestration/auto_loop/scripts/Test-AiOsAutoLoopPreflight.DRY_RUN.ps1",
        "automation/orchestration/auto_loop/scripts/Get-AiOsAutoLoopValidatorRoute.DRY_RUN.ps1"
    )
    approval_required = $true
    risk_tier = "low"
    stop_condition = "Stop after DRY_RUN report and operator next action. Do not mutate active state."
    final_report_required = $true
    live_trading_blocked = $true
    commit_allowed = $false
    push_allowed = $false
    did = @(
        "Created a DRY_RUN packet candidate object from the provided goal.",
        "Kept safety defaults locked to human approval and no commit or push."
    )
    did_not = @(
        "Did not write active queue state.",
        "Did not mutate approval inbox state.",
        "Did not dispatch workers.",
        "Did not touch trading, broker, secrets, commit, push, or merge."
    )
}

$json = $record | ConvertTo-Json -Depth 10

if ($OutputPath) {
    if (-not (Test-AiOsAutoLoopReportPath -Path $OutputPath)) {
        throw "OutputPath must be under telemetry/auto_loop/reports."
    }

    $fullOutputPath = Get-AiOsAutoLoopFullPath -Path $OutputPath
    $parent = Split-Path -Parent $fullOutputPath
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    Set-Content -LiteralPath $fullOutputPath -Value ($json + [Environment]::NewLine) -Encoding UTF8
}

Write-Output $json
