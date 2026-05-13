$ErrorActionPreference = "Stop"

Write-Host "AI_OS TradingView Paper Signal Handoff v1 DRY_RUN"
Write-Host "Mode: read-only validation"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$contractPath = Join-Path $repoRoot "docs/AI_OS/trading_laboratory/external_handoff/TRADINGVIEW_PAPER_SIGNAL_HANDOFF_V1_CONTRACT.json"
$fixturePath = Join-Path $repoRoot "apps/dashboard/mock-data/tradingview-paper-signal-handoff-v1.example.json"

foreach ($path in @($contractPath, $fixturePath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing required TradingView paper handoff v1 file: $path"
    }
    Get-Content -LiteralPath $path -Raw | ConvertFrom-Json | Out-Null
}

$contract = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json
$fixture = Get-Content -LiteralPath $fixturePath -Raw | ConvertFrom-Json

foreach ($field in $contract.required_fields) {
    if (-not ($fixture.PSObject.Properties.Name -contains $field)) {
        throw "Fixture missing required field: $field"
    }
}

foreach ($field in $contract.required_latency_fields) {
    if (-not ($fixture.PSObject.Properties.Name -contains $field)) {
        throw "Fixture missing required latency field: $field"
    }
}

foreach ($field in $contract.required_values.PSObject.Properties.Name) {
    $expected = $contract.required_values.$field
    $actual = $fixture.$field
    if ($actual -ne $expected) {
        throw "Fixture $field must be $expected. Found: $actual"
    }
}

foreach ($step in $contract.required_workflow) {
    if ($fixture.workflow -notcontains $step) {
        throw "Fixture missing workflow step: $step"
    }
}

foreach ($field in $contract.prohibited_fields) {
    if ($fixture.PSObject.Properties.Name -contains $field) {
        throw "Prohibited field found in fixture: $field"
    }
}

foreach ($field in @("live_execution", "broker", "oanda", "real_webhook", "real_order")) {
    if ($fixture.$field -ne "BLOCKED") {
        throw "Fixture $field must remain BLOCKED."
    }
    if ($fixture.safety_gates.$field -ne "BLOCKED") {
        throw "Fixture safety_gates.$field must remain BLOCKED."
    }
}

if ($fixture.api_key_required -ne $false -or $fixture.safety_gates.api_key_required -ne $false) {
    throw "api_key_required must remain false."
}

if ($contract.allowed_latency_statuses -notcontains $fixture.latency_status) {
    throw "Fixture latency_status is not allowed: $($fixture.latency_status)"
}

$timestamps = @{}
foreach ($field in $contract.timestamp_order) {
    $value = $fixture.$field
    if ($null -eq $value -or $value -eq "" -or $value -eq "Pending validation" -or $value -eq "Not measured") {
        continue
    }
    $timestamps[$field] = [DateTimeOffset]::Parse($value)
}

$expectedDelays = @{
    alert_to_receive_ms = @("alert_created_at", "alert_received_at")
    receive_to_validation_ms = @("alert_received_at", "validation_started_at")
    validation_duration_ms = @("validation_started_at", "validation_completed_at")
    validation_to_route_ms = @("validation_completed_at", "route_preview_at")
    route_to_paper_sim_ms = @("route_preview_at", "paper_trade_simulated_at")
}

$computedTotal = 0
$hasMissingTimestamp = $false
$hasClockSkew = $false

foreach ($delayField in $expectedDelays.Keys) {
    $startField = $expectedDelays[$delayField][0]
    $endField = $expectedDelays[$delayField][1]

    if (-not $timestamps.ContainsKey($startField) -or -not $timestamps.ContainsKey($endField)) {
        $hasMissingTimestamp = $true
        continue
    }

    $expectedMs = [int][Math]::Round(($timestamps[$endField] - $timestamps[$startField]).TotalMilliseconds)
    if ($expectedMs -lt 0) {
        $hasClockSkew = $true
    }
    if ($fixture.$delayField -ne $expectedMs) {
        throw "Delay field $delayField expected $expectedMs but found $($fixture.$delayField)."
    }
    $computedTotal += $expectedMs
}

if (-not $hasMissingTimestamp -and $fixture.total_delay_ms -ne $computedTotal) {
    throw "total_delay_ms expected $computedTotal but found $($fixture.total_delay_ms)."
}

if ($hasClockSkew -and $fixture.latency_status -ne $contract.stale_signal_rules.negative_delay_status) {
    throw "Negative delay requires CLOCK_SKEW_DETECTED."
}

if ($hasMissingTimestamp -and $fixture.latency_status -ne $contract.stale_signal_rules.missing_timestamp_status) {
    throw "Missing timestamp requires PENDING_VALIDATION."
}

if (-not $hasMissingTimestamp -and -not $hasClockSkew) {
    if ($fixture.total_delay_ms -ge $contract.stale_signal_rules.stale_from_ms) {
        if ($fixture.latency_status -ne "STALE" -or $fixture.stale_signal -ne $true) {
            throw "Stale latency requires latency_status STALE and stale_signal true."
        }
        if ([string]::IsNullOrWhiteSpace($fixture.blocked_reason)) {
            throw "Stale latency requires blocked_reason."
        }
    } elseif ($fixture.total_delay_ms -ge $contract.stale_signal_rules.delayed_from_ms) {
        if ($fixture.latency_status -ne "DELAYED") {
            throw "Delayed latency requires latency_status DELAYED."
        }
        if ([string]::IsNullOrWhiteSpace($fixture.delay_reason)) {
            throw "Delayed latency requires delay_reason."
        }
    } elseif ($fixture.latency_status -ne "PASS") {
        throw "Fresh latency requires latency_status PASS."
    }
}

Write-Host "PASS: TradingView paper signal handoff v1 fixture and contract are valid, latency-first, and paper-only with live execution blocked."
