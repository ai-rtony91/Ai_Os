$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$fixturePath = Join-Path $repoRoot "apps/dashboard/mock-data/phase-25-latency-measurement-core.example.json"
$specPath = Join-Path $repoRoot "docs/specs/trading-lab-latency-contract.md"

foreach ($path in @($fixturePath, $specPath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing required Phase 25 file: $path"
    }
}

$fixture = Get-Content -LiteralPath $fixturePath -Raw | ConvertFrom-Json
$specText = Get-Content -LiteralPath $specPath -Raw

$requiredSpecMarkers = @(
    "does not authorize live trading",
    "Generated Trading Lab latency results are evidence only",
    "Dashboard mock latency files are fixture-only",
    "Archive files are historical reference only",
    "Future timestamps, negative delays, and clock skew must not be treated as PASS"
)

foreach ($marker in $requiredSpecMarkers) {
    if ($specText -notmatch [regex]::Escape($marker)) {
        throw "Canonical latency spec missing required boundary marker: $marker"
    }
}

$requiredFields = @(
    "schema_version",
    "phase",
    "title",
    "mode",
    "summary",
    "measurement_status",
    "signal_id",
    "alert_created_time",
    "alert_received_time",
    "validation_start_time",
    "validation_end_time",
    "route_preview_time",
    "paper_execution_time",
    "journal_write_time",
    "scorecard_update_time",
    "total_delay_seconds",
    "stale_status",
    "delayed_reason",
    "clock_skew_status",
    "step_delays",
    "measurement_rules",
    "live_execution",
    "broker",
    "real_order",
    "api_key_required",
    "blocked_fields",
    "next_safe_action"
)

$requiredStepDelays = @(
    "alert_to_receive_seconds",
    "receive_to_validation_start_seconds",
    "validation_duration_seconds",
    "validation_to_route_preview_seconds",
    "route_preview_to_paper_execution_seconds",
    "paper_execution_to_journal_seconds",
    "journal_to_scorecard_seconds"
)

$requiredValues = @{
    mode = "paper_only"
    live_execution = "BLOCKED"
    broker = "BLOCKED"
    real_order = "BLOCKED"
    api_key_required = $false
}

$allowedStaleStatuses = @(
    "Pending validation",
    "FRESH",
    "DELAYED_REVIEW",
    "STALE_BLOCKED",
    "CLOCK_SKEW_DETECTED",
    "BLOCKED_FOR_REVIEW",
    "Fresh",
    "Delayed",
    "Stale"
)

$allowedClockSkewStatuses = @(
    "Pending validation",
    "PASS",
    "CLOCK_SKEW_DETECTED",
    "CLOCK_SKEW_BLOCKED",
    "BLOCKED_FOR_REVIEW"
)

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

$timestampOrder = @(
    "alert_created_time",
    "alert_received_time",
    "validation_start_time",
    "validation_end_time",
    "route_preview_time",
    "paper_execution_time",
    "journal_write_time",
    "scorecard_update_time"
)

foreach ($field in $requiredFields) {
    if (-not ($fixture.PSObject.Properties.Name -contains $field)) {
        throw "Phase 25 fixture missing required field: $field"
    }
}

foreach ($field in $requiredStepDelays) {
    if (-not ($fixture.step_delays.PSObject.Properties.Name -contains $field)) {
        throw "Phase 25 fixture step_delays missing field: $field"
    }
}

foreach ($field in $requiredValues.Keys) {
    $expected = $requiredValues[$field]
    $actual = $fixture.$field
    if ($actual -ne $expected) {
        throw "Phase 25 fixture $field must be $expected. Found: $actual"
    }
}

if ($allowedStaleStatuses -notcontains $fixture.stale_status) {
    throw "Phase 25 fixture stale_status is not allowed: $($fixture.stale_status)"
}

if ($allowedClockSkewStatuses -notcontains $fixture.clock_skew_status) {
    throw "Phase 25 fixture clock_skew_status is not allowed: $($fixture.clock_skew_status)"
}

foreach ($field in $prohibitedFields) {
    if ($fixture.PSObject.Properties.Name -contains $field) {
        throw "Prohibited field found in Phase 25 fixture: $field"
    }
}

foreach ($field in @("live_execution", "broker", "real_order")) {
    if ($fixture.$field -ne "BLOCKED") {
        throw "Phase 25 fixture $field must remain BLOCKED."
    }
}

if ($fixture.api_key_required -ne $false) {
    throw "Phase 25 fixture api_key_required must remain false."
}

$previousTimestamp = $null
foreach ($field in $timestampOrder) {
    $value = $fixture.$field
    if ($null -eq $value -or $value -eq "" -or $value -eq "Pending validation" -or $value -eq "Not measured") {
        continue
    }

    $currentTimestamp = [DateTimeOffset]::Parse($value)
    if ($null -ne $previousTimestamp -and $currentTimestamp -lt $previousTimestamp) {
        if ($fixture.clock_skew_status -ne "CLOCK_SKEW_DETECTED") {
            throw "Timestamp order is negative at $field but clock_skew_status is not CLOCK_SKEW_DETECTED."
        }
    }
    $previousTimestamp = $currentTimestamp
}

foreach ($field in $requiredStepDelays) {
    $value = $fixture.step_delays.$field
    if ($null -ne $value -and $value -lt 0 -and $fixture.clock_skew_status -ne "CLOCK_SKEW_DETECTED") {
        throw "Negative step delay $field requires CLOCK_SKEW_DETECTED."
    }
}

Write-Host "PASS: Phase 25 latency measurement core fixture and contract are valid, paper-only, and safety blocked."
