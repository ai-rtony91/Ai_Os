Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
# Archive Trading Lab docs referenced below are historical/reference-only evidence, not current authority.
# This validator does not approve live trading, broker execution, real webhooks, real orders, credentials, APPLY, commit, push, merge, or deployment.
$payloadPath = Join-Path $repoRoot "archive\docs_aios_trading_laboratory_legacy\phase_14_5\PHASE_14_5_TRADINGVIEW_ALERT_PAYLOAD_001.json"

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

$payload = Read-JsonFile -Path $payloadPath
Assert-NoProhibitedFields -Object $payload

foreach ($field in @("payload_id", "phase", "mode", "paper_only", "execution_allowed", "live_execution_status", "source", "symbol", "timeframe", "direction_intent", "alert_timestamp", "strategy_name", "strategy_metadata", "supertrend", "latency_ref", "phase_14_3_decision_ref", "scorecard_ref", "outcome_ref", "safety")) {
    Assert-Property -Object $payload -Name $field
}

if ($payload.mode -ne "DRY_RUN") { throw "Phase 14.5 mode must be DRY_RUN." }
if ($payload.paper_only -ne $true) { throw "Phase 14.5 payload must be paper_only." }
if ($payload.live_execution_status -ne "BLOCKED") { throw "live_execution_status must be BLOCKED." }
if ($payload.execution_allowed -eq $true) { throw "execution_allowed must not be true." }
if ($payload.source -ne "TradingView-style local mock") { throw "Payload must remain a TradingView-style local mock." }

foreach ($field in @("preview_ref", "output", "role", "not_a_trigger")) {
    Assert-Property -Object $payload.supertrend -Name $field
}

if ($payload.supertrend.output -notin @("bullish", "bearish", "neutral", "blocked")) {
    throw "SuperTrend output must be bullish, bearish, neutral, or blocked."
}
if ($payload.supertrend.role -ne "permission_filter_only" -or $payload.supertrend.not_a_trigger -ne $true) {
    throw "SuperTrend must be permission/filter only and not a trigger."
}

foreach ($field in @("external_delivery_status", "credential_status", "order_delivery_status")) {
    Assert-Property -Object $payload.safety -Name $field
}
if ($payload.safety.external_delivery_status -ne "NOT_SENT") { throw "Mock TradingView payload must not be delivered." }
if ($payload.safety.credential_status -ne "BLOCKED") { throw "Credential status must be BLOCKED." }
if ($payload.safety.order_delivery_status -ne "BLOCKED") { throw "Order delivery must be BLOCKED." }

Write-Output "PASS: Phase 14.5 TradingView-style payload mock DRY_RUN validation passed."
Write-Output "Mock payload parsed symbol, timeframe, direction intent, timestamp, and strategy metadata."
Write-Output "No real webhook URL or live execution field is present."
