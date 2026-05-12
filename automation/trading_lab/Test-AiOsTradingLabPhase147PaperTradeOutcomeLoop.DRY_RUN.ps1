Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$outcomePath = Join-Path $repoRoot "docs\AI_OS\trading_laboratory\phase_14_7\PHASE_14_7_PAPER_TRADE_OUTCOME_001.json"

function Read-JsonFile {
    param([Parameter(Mandatory = $true)][string] $Path)
    if (-not (Test-Path -LiteralPath $Path)) { throw "Missing JSON file: $Path" }
    return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Assert-Property {
    param([Parameter(Mandatory = $true)][object] $Object, [Parameter(Mandatory = $true)][string] $Name)
    if (-not ($Object.PSObject.Properties.Name -contains $Name)) { throw "Missing required field: $Name" }
}

function Assert-NoProhibitedFields {
    param([Parameter(Mandatory = $true)][AllowNull()][object] $Object, [string[]] $Path = @())
    $prohibited = @("broker", "OANDA", "api_key", "webhook_url", "live_order", "order_id", "account_id", "real_execution")
    if ($null -eq $Object) { return }
    if ($Object -is [System.Array]) {
        for ($index = 0; $index -lt $Object.Count; $index++) {
            Assert-NoProhibitedFields -Object $Object[$index] -Path ($Path + "[$index]")
        }
        return
    }
    if ($Object.PSObject.Properties) {
        foreach ($property in $Object.PSObject.Properties) {
            if ($prohibited -contains $property.Name) {
                throw "Prohibited field found: $(($Path + $property.Name) -join '.')"
            }
            Assert-NoProhibitedFields -Object $property.Value -Path ($Path + $property.Name)
        }
    }
}

$outcome = Read-JsonFile -Path $outcomePath
Assert-NoProhibitedFields -Object $outcome

foreach ($field in @("outcome_id", "phase", "mode", "paper_only", "execution_allowed", "live_execution_status", "source_payload_ref", "route_preview_ref", "phase_14_3_decision_ref", "symbol", "timeframe", "direction_intent", "supertrend", "paper_outcome", "latency_update", "scorecard_update", "outcome_ledger_ref", "safety")) {
    Assert-Property -Object $outcome -Name $field
}

if ($outcome.mode -ne "PAPER_ONLY") { throw "Phase 14.7 mode must be PAPER_ONLY." }
if ($outcome.paper_only -ne $true) { throw "Phase 14.7 outcome must be paper_only." }
if ($outcome.live_execution_status -ne "BLOCKED") { throw "live_execution_status must be BLOCKED." }
if ($outcome.execution_allowed -eq $true) { throw "execution_allowed must not be true." }

if ($outcome.supertrend.output -notin @("bullish", "bearish", "neutral", "blocked")) {
    throw "SuperTrend output must be bullish, bearish, neutral, or blocked."
}
if ($outcome.supertrend.role -ne "permission_filter_only" -or $outcome.supertrend.not_a_trigger -ne $true) {
    throw "SuperTrend must be permission/filter only and not a trigger."
}

foreach ($field in @("outcome_status", "fill_status", "entry_price", "exit_price", "result_r", "review_note")) {
    Assert-Property -Object $outcome.paper_outcome -Name $field
}
if ($outcome.paper_outcome.fill_status -ne "mock_only") { throw "Paper outcome loop must write only mock status." }

foreach ($field in @("latency_ref", "latency_seconds", "stale_status", "clock_skew_status")) {
    Assert-Property -Object $outcome.latency_update -Name $field
}
foreach ($field in @("scorecard_ref", "scorecard_status", "paper_sample_count", "latest_outcome_ref")) {
    Assert-Property -Object $outcome.scorecard_update -Name $field
}
if (-not $outcome.outcome_ledger_ref) { throw "Outcome ledger reference is required." }

foreach ($field in @("paper_write_only", "external_connection_status", "external_delivery_status", "credential_status", "order_delivery_status")) {
    Assert-Property -Object $outcome.safety -Name $field
}
if ($outcome.safety.paper_write_only -ne $true) { throw "Outcome loop must be paper_write_only." }
if ($outcome.safety.external_connection_status -ne "BLOCKED") { throw "External connection must be BLOCKED." }
if ($outcome.safety.external_delivery_status -ne "NOT_SENT") { throw "External delivery must be NOT_SENT." }
if ($outcome.safety.credential_status -ne "BLOCKED") { throw "Credential status must be BLOCKED." }
if ($outcome.safety.order_delivery_status -ne "BLOCKED") { throw "Order delivery must be BLOCKED." }

Write-Output "PASS: Phase 14.7 paper trade outcome loop DRY_RUN validation passed."
Write-Output "Paper outcome loop writes only paper/mock status and keeps scorecard, latency, and outcome references."
