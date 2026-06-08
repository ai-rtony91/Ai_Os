<#
.SYNOPSIS
    AI_OS Codex <-> dual-reviewer bridge launcher.

.DESCRIPTION
    Native entry point for aios.ps1. Validates that the two reviewer API keys are
    present (presence only -- never prints values), then hands the goal to the
    Python bridge, which runs the Codex -> ChatGPT+Claude review loop and STOPS
    every round for your approval (firing the existing ADB SOS wake).

    Boundaries: Anthony remains approval authority. No commit/push/merge, no
    protected-path writes, no Telegram. SOS is ADB-only (the path that works now).

.EXAMPLE
    .\tools\bridge\Invoke-DualReviewBridge.ps1 -Goal "Fix the failing forex backtest adapter tests"
#>
param(
    [Parameter(Mandatory = $true)][string]$Goal,
    [string]$Repo = "C:\Dev\Ai.Os",
    [int]$MaxRounds = 10,
    [string]$CodexCmd = "codex exec",
    [string]$OpenAiModel = "gpt-5.1",
    [string]$AnthropicModel = "claude-sonnet-4-6",
    [switch]$NoSos
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$LogDir  = Join-Path $Repo "logs\bridge"
$LogFile = Join-Path $LogDir "dual_review_bridge.log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-AiosLog {
    param([string]$Text)
    $Stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Stamp`t$Text" | Tee-Object -FilePath $LogFile -Append | Out-Null
}

# --- key presence check (presence ONLY, values never read/printed) ---
$missing = @()
if (-not $env:OPENAI_API_KEY)    { $missing += "OPENAI_API_KEY" }
if (-not $env:ANTHROPIC_API_KEY) { $missing += "ANTHROPIC_API_KEY" }
if ($missing.Count -gt 0) {
    Write-AiosLog ("FAIL missing keys: " + ($missing -join ", "))
    Write-Host "Missing required API key(s): $($missing -join ', ')" -ForegroundColor Red
    Write-Host "Set them in this session (values are never logged), e.g.:"
    Write-Host '  $env:OPENAI_API_KEY = "sk-..."'
    Write-Host '  $env:ANTHROPIC_API_KEY = "sk-ant-..."'
    exit 10
}

Write-AiosLog "START dual-review bridge | goal=$Goal | repo=$Repo | rounds=$MaxRounds"
Write-Host "AI_OS dual-review bridge -- stops every round for your approval (ADB SOS on)." -ForegroundColor Cyan

$pyArgs = @(
    (Join-Path $Repo "automation\operator_relief\dual_review_bridge.py"),
    "--goal", $Goal,
    "--repo", $Repo,
    "--max-rounds", $MaxRounds,
    "--codex-cmd", $CodexCmd,
    "--openai-model", $OpenAiModel,
    "--anthropic-model", $AnthropicModel
)
if ($NoSos) { $pyArgs += "--no-sos" }

Push-Location $Repo
try {
    python @pyArgs
    $code = $LASTEXITCODE
}
finally {
    Pop-Location
}

Write-AiosLog "END dual-review bridge | exit=$code"
exit $code
