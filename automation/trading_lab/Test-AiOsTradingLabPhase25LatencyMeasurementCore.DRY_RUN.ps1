$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$fixturePath = Join-Path $repoRoot "apps/dashboard/mock-data/phase-25-latency-measurement-core.example.json"
$contractPath = Join-Path $repoRoot "docs/AI_OS/trading_laboratory/phase_25/LATENCY_MEASUREMENT_CORE_CONTRACT.json"

foreach ($path in @($fixturePath, $contractPath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing required Phase 25 file: $path"
    }
    Get-Content -LiteralPath $path -Raw | ConvertFrom-Json | Out-Null
}

$fixture = Get-Content -LiteralPath $fixturePath -Raw | ConvertFrom-Json
$contract = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json

foreach ($field in $contract.required_fields) {
    if (-not ($fixture.PSObject.Properties.Name -contains $field)) {
        throw "Phase 25 fixture missing required field: $field"
    }
}

foreach ($field in $contract.required_step_delays) {
    if (-not ($fixture.step_delays.PSObject.Properties.Name -contains $field)) {
        throw "Phase 25 fixture step_delays missing field: $field"
    }
}

foreach ($field in $contract.required_values.PSObject.Properties.Name) {
    $expected = $contract.required_values.$field
    $actual = $fixture.$field
    if ($actual -ne $expected) {
        throw "Phase 25 fixture $field must be $expected. Found: $actual"
    }
}

if ($contract.allowed_statuses.stale_status -notcontains $fixture.stale_status) {
    throw "Phase 25 fixture stale_status is not allowed: $($fixture.stale_status)"
}

if ($contract.allowed_statuses.clock_skew_status -notcontains $fixture.clock_skew_status) {
    throw "Phase 25 fixture clock_skew_status is not allowed: $($fixture.clock_skew_status)"
}

foreach ($field in $contract.prohibited_fields) {
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
foreach ($field in $contract.timestamp_order) {
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

foreach ($field in $contract.required_step_delays) {
    $value = $fixture.step_delays.$field
    if ($null -ne $value -and $value -lt 0 -and $fixture.clock_skew_status -ne "CLOCK_SKEW_DETECTED") {
        throw "Negative step delay $field requires CLOCK_SKEW_DETECTED."
    }
}

Write-Host "PASS: Phase 25 latency measurement core fixture and contract are valid, paper-only, and safety blocked."
