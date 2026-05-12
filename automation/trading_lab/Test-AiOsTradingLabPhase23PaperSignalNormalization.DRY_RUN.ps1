$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$fixturePath = Join-Path $repoRoot "apps/dashboard/mock-data/phase-23-paper-signal-normalization.example.json"
$contractPath = Join-Path $repoRoot "docs/AI_OS/trading_laboratory/phase_23/PAPER_SIGNAL_NORMALIZATION_CONTRACT.json"

foreach ($path in @($fixturePath, $contractPath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing required Phase 23 file: $path"
    }
    Get-Content -LiteralPath $path -Raw | ConvertFrom-Json | Out-Null
}

$fixture = Get-Content -LiteralPath $fixturePath -Raw | ConvertFrom-Json
$contract = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json

foreach ($field in $contract.required_fields) {
    if (-not ($fixture.PSObject.Properties.Name -contains $field)) {
        throw "Phase 23 fixture missing required field: $field"
    }
}

foreach ($field in $contract.required_values.PSObject.Properties.Name) {
    $expected = $contract.required_values.$field
    $actual = $fixture.$field
    if ($actual -ne $expected) {
        throw "Phase 23 fixture $field must be $expected. Found: $actual"
    }
}

if ($contract.allowed_directions -notcontains $fixture.direction) {
    throw "Phase 23 fixture direction is not allowed: $($fixture.direction)"
}

if ($contract.allowed_normalization_statuses -notcontains $fixture.normalization_status) {
    throw "Phase 23 fixture normalization_status is not allowed: $($fixture.normalization_status)"
}

if ($fixture.symbol -notmatch "^[A-Z]{3}/[A-Z]{3}$") {
    throw "Phase 23 fixture symbol must use BASE/QUOTE format."
}

if (-not ($fixture.missing_fields -is [array])) {
    throw "Phase 23 fixture missing_fields must be an array."
}

foreach ($field in $contract.prohibited_fields) {
    if ($fixture.PSObject.Properties.Name -contains $field) {
        throw "Prohibited field found in Phase 23 fixture: $field"
    }
}

foreach ($field in @("live_execution", "broker", "real_order")) {
    if ($fixture.$field -ne "BLOCKED") {
        throw "Phase 23 fixture $field must remain BLOCKED."
    }
}

if ($fixture.api_key_required -ne $false) {
    throw "Phase 23 fixture api_key_required must remain false."
}

Write-Host "PASS: Phase 23 paper signal normalization fixture and contract are valid, paper-only, and safety blocked."
