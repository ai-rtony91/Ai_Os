param(
    [string]$RepoRoot = "",
    [string]$CandidateJsonPath = "",
    [string[]]$SecurityJsonPath = @(),
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-AiOsRepoRoot {
    param([string]$CandidateRoot)

    if (-not [string]::IsNullOrWhiteSpace($CandidateRoot)) {
        return (Resolve-Path -LiteralPath $CandidateRoot -ErrorAction Stop).Path
    }

    return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
}

function New-WatchtowerFailure {
    param([string]$RepoRootPath, [string]$Reason)

    return [ordered]@{
        schema = "AIOS_TRADING_WATCHTOWER_RESULT.v1"
        generated_at_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        component = "trading_watchtower"
        mode = "PAPER_ONLY_READ_ONLY"
        paper_only = $true
        read_only = $true
        execution_allowed = $false
        broker_allowed = $false
        order_submission_allowed = $false
        live_trading_allowed = $false
        candidate_count = 0
        valid_candidate_count = 0
        rejected_candidate_count = 0
        rejected_candidates = @()
        market_radar = @()
        candidate_targets = @()
        priority_targets = @()
        market_regime = "UNKNOWN"
        watchtower_status = "REVIEW_REQUIRED"
        next_best_setup = $null
        security_integration = [ordered]@{
            evidence_present = $false
            review_required = $true
            triggers = @("watchtower_wrapper_failure")
            next_safe_action = "Stop and inspect the Watchtower wrapper failure before using ranking output."
        }
        ranking = [ordered]@{
            ranking_method = "confidence/evidence/regime/stop/volatility/risk weighted paper-only score"
            highest_total_score_first = $true
            high_priority_threshold = 75
            candidate_threshold = 45
            penalizes_stale_missing_unknown_evidence = $true
        }
        safety = [ordered]@{
            paper_only = $true
            read_only = $true
            execution_allowed = $false
            broker_allowed = $false
            order_submission_allowed = $false
            live_trading_allowed = $false
            writes_outputs_by_default = $false
            requires_api_keys = $false
            broker_modules_called = $false
            paper_orders_submitted = $false
            live_orders_submitted = $false
            network_access = $false
            external_webhooks = $false
            dashboard_mutation = $false
            scheduler_activation = $false
            daemon_activation = $false
            worker_launch = $false
        }
        next_safe_action = "Stop and inspect the Watchtower wrapper failure before continuing."
        failure_reason = $Reason
        repo_root = $RepoRootPath
    }
}

try {
    $resolvedRoot = Resolve-AiOsRepoRoot -CandidateRoot $RepoRoot
    $watchtowerPath = Join-Path $resolvedRoot "apps\trading_lab\trading_lab\watchtower.py"
    if (-not (Test-Path -LiteralPath $watchtowerPath -PathType Leaf)) {
        throw "Missing Watchtower module: $watchtowerPath"
    }

    $arguments = @($watchtowerPath)
    if (-not [string]::IsNullOrWhiteSpace($CandidateJsonPath)) {
        $arguments += @("--candidate-json", (Resolve-Path -LiteralPath $CandidateJsonPath -ErrorAction Stop).Path)
    }
    foreach ($path in $SecurityJsonPath) {
        if (-not [string]::IsNullOrWhiteSpace($path)) {
            $arguments += @("--security-json", (Resolve-Path -LiteralPath $path -ErrorAction Stop).Path)
        }
    }

    $json = & python @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Watchtower Python module exited with code $LASTEXITCODE"
    }

    if ($OutputJson) {
        $json
    }
    else {
        $result = ($json | Out-String) | ConvertFrom-Json
        [ordered]@{
            schema = $result.schema
            mode = $result.mode
            paper_only = $result.paper_only
            execution_allowed = $result.execution_allowed
            broker_allowed = $result.broker_allowed
            order_submission_allowed = $result.order_submission_allowed
            live_trading_allowed = $result.live_trading_allowed
            watchtower_status = $result.watchtower_status
            market_regime = $result.market_regime
            candidate_count = $result.candidate_count
            valid_candidate_count = $result.valid_candidate_count
            top_symbol = if ($null -ne $result.next_best_setup) { $result.next_best_setup.symbol } else { $null }
            next_safe_action = $result.next_safe_action
        } | ConvertTo-Json -Depth 8
    }
    exit 0
}
catch {
    $failure = New-WatchtowerFailure -RepoRootPath $RepoRoot -Reason $_.Exception.Message
    $failure | ConvertTo-Json -Depth 20
    exit 1
}
