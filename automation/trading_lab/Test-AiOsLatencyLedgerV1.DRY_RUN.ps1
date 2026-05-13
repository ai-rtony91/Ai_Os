$ErrorActionPreference = "Stop"

Write-Host "AI_OS Latency Ledger v1 DRY_RUN"
Write-Host "Mode: read-only validation"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$contractPath = Join-Path $repoRoot "docs/AI_OS/trading_laboratory/latency/LATENCY_LEDGER_V1_CONTRACT.json"
$fixturePath = Join-Path $repoRoot "apps/dashboard/mock-data/latency-ledger-v1.example.json"

foreach ($path in @($contractPath, $fixturePath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing required latency ledger v1 file: $path"
    }
    Get-Content -LiteralPath $path -Raw | ConvertFrom-Json | Out-Null
}

$contract = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json
$fixture = Get-Content -LiteralPath $fixturePath -Raw | ConvertFrom-Json

foreach ($field in $contract.required_fields) {
    if (-not ($fixture.PSObject.Properties.Name -contains $field)) {
        throw "Latency ledger fixture missing required field: $field"
    }
}

foreach ($field in $contract.required_latency_fields) {
    if (-not ($fixture.PSObject.Properties.Name -contains $field)) {
        throw "Latency ledger fixture missing required latency field: $field"
    }
}

foreach ($field in $contract.required_values.PSObject.Properties.Name) {
    $expected = $contract.required_values.$field
    $actual = $fixture.$field
    if ($actual -ne $expected) {
        throw "Latency ledger fixture $field must be $expected. Found: $actual"
    }
}

foreach ($field in $contract.prohibited_fields) {
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

if ($contract.allowed_latency_statuses -notcontains $fixture.latency_status) {
    throw "Latency status is not allowed: $($fixture.latency_status)"
}

if ($contract.delay_reason_codes -notcontains $fixture.delay_reason_code) {
    throw "Delay reason code is not allowed: $($fixture.delay_reason_code)"
}

$timestamps = @{}
foreach ($field in $contract.timestamp_order) {
    $value = $fixture.$field
    if ($null -eq $value -or $value -eq "" -or $value -eq "Pending validation" -or $value -eq "Not measured") {
        continue
    }
    $timestamps[$field] = [DateTimeOffset]::Parse($value)
}

$computedTotal = 0
$hasMissingTimestamp = $false
$hasClockSkew = $false

foreach ($delayField in $contract.step_delay_map.PSObject.Properties.Name) {
    $startField = $contract.step_delay_map.$delayField[0]
    $endField = $contract.step_delay_map.$delayField[1]

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
    if ($fixture.latency_status -ne $contract.stale_signal_rules.negative_delay_status) {
        throw "Negative delay requires CLOCK_SKEW_BLOCKED."
    }
    if ([string]::IsNullOrWhiteSpace($fixture.blocked_reason)) {
        throw "Clock skew requires blocked_reason."
    }
} elseif ($hasMissingTimestamp) {
    if ($fixture.latency_status -ne $contract.stale_signal_rules.missing_timestamp_status) {
        throw "Missing timestamp requires PENDING_VALIDATION."
    }
} elseif ($fixture.total_delay_seconds -ge $contract.stale_signal_rules.stale_from_seconds) {
    if ($fixture.latency_status -ne $contract.stale_signal_rules.stale_status -or $fixture.stale_signal -ne $true) {
        throw "High latency requires STALE_BLOCKED and stale_signal true."
    }
    if ([string]::IsNullOrWhiteSpace($fixture.blocked_reason)) {
        throw "High latency requires blocked_reason."
    }
} elseif ($fixture.total_delay_seconds -ge $contract.stale_signal_rules.delayed_from_seconds) {
    if ($fixture.latency_status -ne $contract.stale_signal_rules.delayed_status) {
        throw "Delayed latency requires DELAYED_REVIEW."
    }
    if ([string]::IsNullOrWhiteSpace($fixture.delay_reason)) {
        throw "Delayed latency requires delay_reason."
    }
} else {
    if ($fixture.latency_status -ne $contract.stale_signal_rules.fresh_status -or $fixture.stale_signal -ne $false) {
        throw "Fresh latency requires FRESH and stale_signal false."
    }
}

if ($fixture.blocked_reason -notmatch "Live execution remains BLOCKED") {
    throw "blocked_reason must explicitly keep live execution blocked."
}

Write-Host "PASS: AI_OS Latency Ledger v1 contract and fixture are valid, JSON parses, latency fields are complete, stale rules are enforced, and live execution is blocked."
