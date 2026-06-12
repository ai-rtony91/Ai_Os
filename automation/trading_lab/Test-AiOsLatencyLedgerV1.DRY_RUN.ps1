$ErrorActionPreference = "Stop"

Write-Host "AI_OS Latency Ledger v1 DRY_RUN"
Write-Host "Mode: read-only validation"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$specPath = Join-Path $repoRoot "docs/specs/trading-lab-latency-contract.md"
$fixturePath = Join-Path $repoRoot "apps/dashboard/mock-data/latency-ledger-v1.example.json"

foreach ($path in @($specPath, $fixturePath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing required latency ledger v1 file: $path"
    }
}

$specText = Get-Content -LiteralPath $specPath -Raw
$requiredSpecMarkers = @(
    "does not authorize live trading",
    "Generated Trading Lab latency results are evidence only",
    "Dashboard mock latency files are fixture-only",
    "Archive files are historical reference only",
    "Missing timestamps must not be treated as PASS",
    "Future timestamps, negative delays, and clock skew must not be treated as PASS"
)

foreach ($marker in $requiredSpecMarkers) {
    if ($specText -notmatch [regex]::Escape($marker)) {
        throw "Canonical latency spec missing required boundary marker: $marker"
    }
}

$fixture = Get-Content -LiteralPath $fixturePath -Raw | ConvertFrom-Json

$requiredFields = @(
    "schema_version",
    "ledger_id",
    "mode",
    "source",
    "symbol",
    "timeframe",
    "direction_intent",
    "strategy_name",
    "alert_created_at",
    "alert_received_at",
    "validation_started_at",
    "validation_completed_at",
    "route_preview_at",
    "paper_trade_simulated_at",
    "journal_recorded_at",
    "scorecard_updated_at",
    "total_delay_seconds",
    "latency_status",
    "stale_signal",
    "stale_signal_status",
    "delay_reason",
    "delay_reason_code",
    "blocked_reason",
    "paper_only_validation_gate",
    "risk_gate_status",
    "future_traderspost_handoff_status",
    "traderspost_route_preview_status",
    "live_execution_status",
    "broker_status",
    "oanda_status",
    "real_webhook_status",
    "real_order_status",
    "api_key_required",
    "safety_gates",
    "stale_signal_rules",
    "next_safe_action"
)

$requiredLatencyFields = @(
    "alert_to_receive_seconds",
    "receive_to_validation_start_seconds",
    "validation_duration_seconds",
    "validation_to_route_preview_seconds",
    "route_preview_to_paper_simulation_seconds",
    "paper_simulation_to_journal_seconds",
    "journal_to_scorecard_seconds"
)

$requiredValues = @{
    mode = "paper_only"
    paper_only_validation_gate = "REQUIRED"
    live_execution_status = "BLOCKED"
    broker_status = "BLOCKED"
    oanda_status = "BLOCKED"
    real_webhook_status = "BLOCKED"
    real_order_status = "BLOCKED"
    api_key_required = $false
}

$prohibitedFields = @(
    "api_key",
    "secret",
    "token",
    "broker_account",
    "account_id",
    "webhook_url",
    "order_id",
    "live_order"
)

$allowedLatencyStatuses = @(
    "FRESH",
    "DELAYED_REVIEW",
    "STALE_BLOCKED",
    "CLOCK_SKEW_BLOCKED",
    "CLOCK_SKEW_DETECTED",
    "PENDING_VALIDATION",
    "BLOCKED_FOR_REVIEW",
    "UNKNOWN"
)

$delayReasonCodes = @(
    "NONE",
    "MISSING_TIMESTAMP",
    "DELAYED",
    "STALE",
    "CLOCK_SKEW",
    "REVIEW_REQUIRED"
)

$timestampOrder = @(
    "alert_created_at",
    "alert_received_at",
    "validation_started_at",
    "validation_completed_at",
    "route_preview_at",
    "paper_trade_simulated_at",
    "journal_recorded_at",
    "scorecard_updated_at"
)

$stepDelayMap = [ordered]@{
    alert_to_receive_seconds = @("alert_created_at", "alert_received_at")
    receive_to_validation_start_seconds = @("alert_received_at", "validation_started_at")
    validation_duration_seconds = @("validation_started_at", "validation_completed_at")
    validation_to_route_preview_seconds = @("validation_completed_at", "route_preview_at")
    route_preview_to_paper_simulation_seconds = @("route_preview_at", "paper_trade_simulated_at")
    paper_simulation_to_journal_seconds = @("paper_trade_simulated_at", "journal_recorded_at")
    journal_to_scorecard_seconds = @("journal_recorded_at", "scorecard_updated_at")
}

$staleSignalRules = @{
    delayed_from_seconds = 300
    stale_from_seconds = 900
    fresh_status = "FRESH"
    delayed_status = "DELAYED_REVIEW"
    stale_status = "STALE_BLOCKED"
    negative_delay_status = "CLOCK_SKEW_BLOCKED"
    missing_timestamp_status = "PENDING_VALIDATION"
}

foreach ($field in $requiredFields) {
    if (-not ($fixture.PSObject.Properties.Name -contains $field)) {
        throw "Latency ledger fixture missing required field: $field"
    }
}

foreach ($field in $requiredLatencyFields) {
    if (-not ($fixture.PSObject.Properties.Name -contains $field)) {
        throw "Latency ledger fixture missing required latency field: $field"
    }
}

foreach ($field in $requiredValues.Keys) {
    $expected = $requiredValues[$field]
    $actual = $fixture.$field
    if ($actual -ne $expected) {
        throw "Latency ledger fixture $field must be $expected. Found: $actual"
    }
}

foreach ($field in $prohibitedFields) {
    if ($fixture.PSObject.Properties.Name -contains $field) {
        throw "Prohibited field found in latency ledger fixture: $field"
    }
}

foreach ($field in @("live_execution_status", "broker_status", "oanda_status", "real_webhook_status", "real_order_status")) {
    if ($fixture.$field -ne "BLOCKED") {
        throw "Latency ledger fixture $field must remain BLOCKED."
    }
    if ($fixture.safety_gates.$field -ne "BLOCKED") {
        throw "Latency ledger fixture safety_gates.$field must remain BLOCKED."
    }
}

if ($fixture.api_key_required -ne $false -or $fixture.safety_gates.api_key_required -ne $false) {
    throw "api_key_required must remain false."
}

if ($allowedLatencyStatuses -notcontains $fixture.latency_status) {
    throw "Latency status is not allowed: $($fixture.latency_status)"
}

if ($delayReasonCodes -notcontains $fixture.delay_reason_code) {
    throw "Delay reason code is not allowed: $($fixture.delay_reason_code)"
}

$timestamps = @{}
foreach ($field in $timestampOrder) {
    $value = $fixture.$field
    if ($null -eq $value -or $value -eq "" -or $value -eq "Pending validation" -or $value -eq "Not measured") {
        continue
    }
    $timestamps[$field] = [DateTimeOffset]::Parse($value)
}

$computedTotal = 0
$hasMissingTimestamp = $false
$hasClockSkew = $false

foreach ($delayField in $stepDelayMap.Keys) {
    $startField = $stepDelayMap[$delayField][0]
    $endField = $stepDelayMap[$delayField][1]

    if (-not $timestamps.ContainsKey($startField) -or -not $timestamps.ContainsKey($endField)) {
        $hasMissingTimestamp = $true
        continue
    }

    $expectedSeconds = [int][Math]::Round(($timestamps[$endField] - $timestamps[$startField]).TotalSeconds)
    if ($expectedSeconds -lt 0) {
        $hasClockSkew = $true
    }

    if ($fixture.$delayField -ne $expectedSeconds) {
        throw "Delay field $delayField expected $expectedSeconds but found $($fixture.$delayField)."
    }

    $computedTotal += $expectedSeconds
}

if (-not $hasMissingTimestamp -and $fixture.total_delay_seconds -ne $computedTotal) {
    throw "total_delay_seconds expected $computedTotal but found $($fixture.total_delay_seconds)."
}

if ($hasClockSkew) {
    if ($fixture.latency_status -ne $staleSignalRules.negative_delay_status) {
        throw "Negative delay requires CLOCK_SKEW_BLOCKED."
    }
    if ([string]::IsNullOrWhiteSpace($fixture.blocked_reason)) {
        throw "Clock skew requires blocked_reason."
    }
} elseif ($hasMissingTimestamp) {
    if ($fixture.latency_status -ne $staleSignalRules.missing_timestamp_status) {
        throw "Missing timestamp requires PENDING_VALIDATION."
    }
} elseif ($fixture.total_delay_seconds -ge $staleSignalRules.stale_from_seconds) {
    if ($fixture.latency_status -ne $staleSignalRules.stale_status -or $fixture.stale_signal -ne $true) {
        throw "High latency requires STALE_BLOCKED and stale_signal true."
    }
    if ([string]::IsNullOrWhiteSpace($fixture.blocked_reason)) {
        throw "High latency requires blocked_reason."
    }
} elseif ($fixture.total_delay_seconds -ge $staleSignalRules.delayed_from_seconds) {
    if ($fixture.latency_status -ne $staleSignalRules.delayed_status) {
        throw "Delayed latency requires DELAYED_REVIEW."
    }
    if ([string]::IsNullOrWhiteSpace($fixture.delay_reason)) {
        throw "Delayed latency requires delay_reason."
    }
} else {
    if ($fixture.latency_status -ne $staleSignalRules.fresh_status -or $fixture.stale_signal -ne $false) {
        throw "Fresh latency requires FRESH and stale_signal false."
    }
}

if ($fixture.blocked_reason -notmatch "Live execution remains BLOCKED") {
    throw "blocked_reason must explicitly keep live execution blocked."
}

Write-Host "PASS: AI_OS Latency Ledger v1 contract and fixture are valid, JSON parses, latency fields are complete, stale rules are enforced, and live execution is blocked."
