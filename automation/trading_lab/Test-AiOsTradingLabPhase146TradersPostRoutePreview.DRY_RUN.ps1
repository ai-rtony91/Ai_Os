Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$routePath = Join-Path $repoRoot "docs\AI_OS\trading_laboratory\phase_14_6\PHASE_14_6_TRADERSPOST_ROUTE_PREVIEW_001.json"

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

$route = Read-JsonFile -Path $routePath
Assert-NoProhibitedFields -Object $route

foreach ($field in @("route_preview_id", "phase", "mode", "paper_only", "execution_allowed", "live_execution_status", "source_payload_ref", "destination", "symbol", "timeframe", "direction_intent", "route_action", "quantity_mode", "order_type", "supertrend", "phase_14_3_decision_ref", "scorecard_ref", "latency_ref", "outcome_ref", "route_status")) {
    Assert-Property -Object $route -Name $field
}

if ($route.mode -ne "DRY_RUN") { throw "Phase 14.6 mode must be DRY_RUN." }
if ($route.paper_only -ne $true) { throw "Phase 14.6 route must be paper_only." }
if ($route.live_execution_status -ne "BLOCKED") { throw "live_execution_status must be BLOCKED." }
if ($route.execution_allowed -eq $true) { throw "execution_allowed must not be true." }
if ($route.route_action -ne "paper_preview_only") { throw "Route action must stay paper_preview_only." }

if ($route.supertrend.output -notin @("bullish", "bearish", "neutral", "blocked")) {
    throw "SuperTrend output must be bullish, bearish, neutral, or blocked."
}
if ($route.supertrend.role -ne "permission_filter_only" -or $route.supertrend.not_a_trigger -ne $true) {
    throw "SuperTrend must be permission/filter only and not a trigger."
}

foreach ($field in @("format_prepared", "external_delivery_status", "external_connection_status", "order_delivery_status", "paper_route_preview_status")) {
    Assert-Property -Object $route.route_status -Name $field
}
if ($route.route_status.external_delivery_status -ne "NOT_SENT") { throw "TradersPost-style route preview must not be sent." }
if ($route.route_status.external_connection_status -ne "BLOCKED") { throw "External connection must be BLOCKED." }
if ($route.route_status.order_delivery_status -ne "BLOCKED") { throw "Order delivery must be BLOCKED." }

Write-Output "PASS: Phase 14.6 TradersPost-style route preview DRY_RUN validation passed."
Write-Output "Route preview is format-only and does not execute."
