$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $repoRoot

Write-Host "Trading Bot V0.1 Partial Integration Release Gate"
Write-Host "Mode: DRY_RUN"
Write-Host "No commit. No push."
Write-Host ""

# Archive Trading Lab docs referenced below are historical/reference-only evidence, not current authority.
# This release gate does not approve live trading, broker execution, real webhooks, real orders, credentials, APPLY, commit, push, merge, or deployment.
$failures = New-Object System.Collections.Generic.List[string]

$lane1Files = @(
    "archive/docs_aios_trading_laboratory_legacy/phase_14_4/PHASE_14_4_SUPERTREND_MVP_SIGNAL_PREVIEW.md",
    "archive/docs_aios_trading_laboratory_legacy/phase_14_4/PHASE_14_4_SUPERTREND_SIGNAL_PREVIEW_001.json",
    "automation/trading_lab/Test-AiOsTradingLabPhase144SuperTrendPreview.DRY_RUN.ps1"
)

$lane2Files = @(
    "archive/docs_aios_trading_laboratory_legacy/phase_14_5/PHASE_14_5_TRADINGVIEW_ALERT_PAYLOAD_MOCK.md",
    "archive/docs_aios_trading_laboratory_legacy/phase_14_5/PHASE_14_5_TRADINGVIEW_ALERT_PAYLOAD_001.json",
    "archive/docs_aios_trading_laboratory_legacy/phase_14_6/PHASE_14_6_TRADERSPOST_ROUTE_PREVIEW_MOCK.md",
    "archive/docs_aios_trading_laboratory_legacy/phase_14_6/PHASE_14_6_TRADERSPOST_ROUTE_PREVIEW_001.json",
    "automation/trading_lab/Test-AiOsTradingLabPhase145TradingViewPayloadMock.DRY_RUN.ps1",
    "automation/trading_lab/Test-AiOsTradingLabPhase146TradersPostRoutePreview.DRY_RUN.ps1"
)

$lane3Files = @(
    "archive/docs_aios_trading_laboratory_legacy/phase_14_7/PHASE_14_7_PAPER_TRADE_OUTCOME_LOOP.md",
    "archive/docs_aios_trading_laboratory_legacy/phase_14_7/PHASE_14_7_PAPER_TRADE_OUTCOME_001.json",
    "automation/trading_lab/Test-AiOsTradingLabPhase147PaperTradeOutcomeLoop.DRY_RUN.ps1"
)

function Test-FilesPresent {
    param([string[]]$Paths, [string]$LaneName)
    $missing = @()
    foreach ($path in $Paths) {
        if (-not (Test-Path -LiteralPath $path)) {
            $missing += $path
        }
    }
    if ($missing.Count -gt 0) {
        foreach ($path in $missing) {
            $script:failures.Add("$LaneName missing required file: $path")
        }
        return $false
    }
    return $true
}

function Invoke-LaneValidator {
    param([string]$Path, [string]$LaneName)
    if (-not (Test-Path -LiteralPath $Path)) {
        $script:failures.Add("$LaneName validator missing: $Path")
        return [bool]$false
    }
    $validatorOutput = & powershell -ExecutionPolicy Bypass -File $Path 2>&1
    foreach ($line in $validatorOutput) {
        Write-Host $line
    }
    if ($LASTEXITCODE -ne 0) {
        $script:failures.Add("$LaneName validator failed: $Path")
        return [bool]$false
    }
    return [bool]$true
}

function Get-ChangedFiles {
    $files = New-Object System.Collections.Generic.List[string]
    foreach ($line in (git status --porcelain)) {
        if ($line.Length -lt 4) { continue }
        $path = $line.Substring(3).Trim()
        if (Test-Path -LiteralPath $path -PathType Container) {
            Get-ChildItem -LiteralPath $path -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
                $files.Add($_.FullName)
            }
        } elseif (Test-Path -LiteralPath $path -PathType Leaf) {
            $files.Add((Resolve-Path -LiteralPath $path).Path)
        }
    }
    return $files | Sort-Object -Unique
}

function Test-TrueEnablementSafety {
    param([string[]]$Files)

    $hits = New-Object System.Collections.Generic.List[string]
    $patterns = @(
        '"execution_allowed"\s*:\s*true',
        '"approved_for_live_execution"\s*:\s*true',
        '"live_trading"\s*:\s*"ENABLED"',
        '"live_execution"\s*:\s*"ENABLED"',
        '"live_execution_status"\s*:\s*"ENABLED"',
        '"broker_execution"\s*:\s*"ENABLED"',
        '"broker_status"\s*:\s*"ENABLED"',
        '"oanda_execution"\s*:\s*"ENABLED"',
        '"oanda_status"\s*:\s*"ENABLED"',
        '"webull_execution"\s*:\s*"ENABLED"',
        '"webull_status"\s*:\s*"ENABLED"',
        '"real_webhook"\s*:\s*"ENABLED"',
        '"real_webhook_status"\s*:\s*"ENABLED"',
        '"real_order"\s*:\s*"ENABLED"',
        '"real_order_status"\s*:\s*"ENABLED"',
        '"webhook_url"\s*:\s*"https?://[^"]+"',
        '"api_key"\s*:\s*"(?!\s*(?:BLOCKED|NOT_APPROVED|DISABLED)\s*")[^"]+"',
        '"secret"\s*:\s*"(?!\s*(?:BLOCKED|NOT_APPROVED|DISABLED)\s*")[^"]+"',
        '"token"\s*:\s*"(?!\s*(?:BLOCKED|NOT_APPROVED|DISABLED)\s*")[^"]+"',
        '"password"\s*:\s*"(?!\s*(?:BLOCKED|NOT_APPROVED|DISABLED)\s*")[^"]+"',
        '"private_key"\s*:\s*"(?!\s*(?:BLOCKED|NOT_APPROVED|DISABLED)\s*")[^"]+"'
    )

    foreach ($file in $Files) {
        if ($file -match '\.pyc$') { continue }
        try {
            $raw = Get-Content -LiteralPath $file -Raw -ErrorAction Stop
        } catch {
            continue
        }
        foreach ($pattern in $patterns) {
            if ($raw -match $pattern) {
                $relative = Resolve-Path -LiteralPath $file -Relative
                $hits.Add("$relative matched $pattern")
            }
        }
    }
    return $hits
}

$lane1Present = Test-FilesPresent -Paths $lane1Files -LaneName "Codex #1"
$lane2Present = Test-FilesPresent -Paths $lane2Files -LaneName "Codex #2"
$lane3Present = Test-FilesPresent -Paths $lane3Files -LaneName "Codex #3"

$lane1Validator = Invoke-LaneValidator -Path "automation/trading_lab/Test-AiOsTradingLabPhase144SuperTrendPreview.DRY_RUN.ps1" -LaneName "Codex #1"
$lane2ValidatorA = Invoke-LaneValidator -Path "automation/trading_lab/Test-AiOsTradingLabPhase145TradingViewPayloadMock.DRY_RUN.ps1" -LaneName "Codex #2"
$lane2ValidatorB = Invoke-LaneValidator -Path "automation/trading_lab/Test-AiOsTradingLabPhase146TradersPostRoutePreview.DRY_RUN.ps1" -LaneName "Codex #2"
$lane3Validator = Invoke-LaneValidator -Path "automation/trading_lab/Test-AiOsTradingLabPhase147PaperTradeOutcomeLoop.DRY_RUN.ps1" -LaneName "Codex #3"
$loopValidator = Invoke-LaneValidator -Path "automation/trading_lab/Test-AiOsTradingLabPhase144To147BotLoop.DRY_RUN.ps1" -LaneName "Codex #4 cross-lane"

$changedFiles = @(Get-ChangedFiles)
$safetyHits = @(Test-TrueEnablementSafety -Files $changedFiles)

if ($safetyHits.Count -gt 0) {
    foreach ($hit in $safetyHits) {
        $failures.Add("Safety true enablement hit: $hit")
    }
}

$dirtyStatus = @(git status --porcelain)
$repoDirty = $dirtyStatus.Count -gt 0

Write-Host ""
Write-Host "Lane results:"
Write-Host "- Codex #1: $($lane1Present -and $lane1Validator)"
Write-Host "- Codex #2: $($lane2Present -and $lane2ValidatorA -and $lane2ValidatorB)"
Write-Host "- Codex #3: $($lane3Present -and $lane3Validator)"
Write-Host "- Cross-lane loop: $loopValidator"
Write-Host ""

if ($safetyHits.Count -eq 0) {
    Write-Host "Refined safety scan: PASS_FALSE_POSITIVE"
} else {
    Write-Host "Refined safety scan: FAIL_TRUE_ENABLEMENT"
    foreach ($hit in $safetyHits) {
        Write-Host "- $hit"
    }
}

if ($repoDirty) {
    Write-Host "Repo cleanliness: DIRTY"
} else {
    Write-Host "Repo cleanliness: CLEAN"
}

if ($failures.Count -gt 0) {
    Write-Host "Final release gate decision: BLOCK_INTEGRATION"
    foreach ($failure in $failures) {
        Write-Host "- $failure"
    }
    exit 1
}

if ($repoDirty) {
    Write-Host "Final release gate decision: HOLD_FOR_CLEANUP"
    exit 0
}

Write-Host "Final release gate decision: APPROVE_INTEGRATION"
exit 0
