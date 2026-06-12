$ErrorActionPreference = "Stop"

# Archive docs referenced below are historical/reference-only evidence, not current authority.
# This DRY_RUN validator does not approve live trading, broker execution, real webhooks, real orders, credentials, APPLY, commit, push, merge, or deployment.

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$fixturePath = Join-Path $repoRoot "apps\dashboard\mock-data\trading-lab-workstation.example.json"
$contractPath = Join-Path $repoRoot "archive\docs_aios_trading_laboratory_legacy\phase_24\TRADING_LAB_WORKSTATION_CONTRACT.json"
$docPath = Join-Path $repoRoot "archive\docs_aios_trading_laboratory_legacy\phase_24\PHASE_24_TRADING_LAB_WORKSTATION_LAYOUT_SYSTEM.md"
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
  param([string]$Message)
  $script:failures.Add($Message) | Out-Null
}

foreach ($path in @($fixturePath, $contractPath, $docPath)) {
  if (-not (Test-Path -LiteralPath $path)) {
    Add-Failure "Missing required file: $path"
  }
}

if ($failures.Count -eq 0) {
  try {
    $fixture = Get-Content -LiteralPath $fixturePath -Raw | ConvertFrom-Json
    $contract = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json
  } catch {
    Add-Failure "JSON parse failed for fixture or contract."
  }
}

if ($failures.Count -eq 0) {
  foreach ($section in $contract.required_sections) {
    if (-not $fixture.PSObject.Properties.Name.Contains($section)) {
      Add-Failure "Fixture missing section: $section"
    }
  }

  foreach ($field in $contract.required_top_bar_fields) {
    if (-not $fixture.top_bar.PSObject.Properties.Name.Contains($field)) {
      Add-Failure "Fixture top_bar missing field: $field"
    }
  }

  foreach ($field in $contract.required_latency_fields) {
    if (-not $fixture.latency.PSObject.Properties.Name.Contains($field)) {
      Add-Failure "Fixture latency missing field: $field"
    }
  }

  foreach ($field in $contract.required_center_fields) {
    if (-not $fixture.center_panel.PSObject.Properties.Name.Contains($field)) {
      Add-Failure "Fixture center_panel missing field: $field"
    }
  }

  foreach ($field in $contract.required_risk_gate_fields) {
    if (-not $fixture.right_panel.risk_gate.PSObject.Properties.Name.Contains($field)) {
      Add-Failure "Fixture right_panel.risk_gate missing field: $field"
    }
  }

  foreach ($property in $contract.required_blocked_safety_fields.PSObject.Properties) {
    $name = $property.Name
    $expected = $property.Value
    if ($fixture.safety.$name -ne $expected) {
      Add-Failure "Safety field $name must be $expected."
    }
  }

  foreach ($profile in $contract.required_workspace_profiles) {
    if ($fixture.left_panel.workspace_profiles -notcontains $profile) {
      Add-Failure "Missing workspace profile: $profile"
    }
  }

  foreach ($step in $contract.required_workflow) {
    if ($fixture.center_panel.active_workflow -notmatch [regex]::Escape($step)) {
      Add-Failure "Active workflow missing step: $step"
    }
  }

  if ($fixture.center_panel.workflow_rail.step -notcontains $fixture.center_panel.current_workflow_step) {
    Add-Failure "Current workflow step is not present in workflow_rail."
  }

  $combined = (Get-Content -LiteralPath $fixturePath -Raw) + "`n" + (Get-Content -LiteralPath $contractPath -Raw)
  foreach ($unsafePattern in @(
    '"live_trading"\s*:\s*"ENABLED"',
    '"broker"\s*:\s*"ENABLED"',
    '"oanda"\s*:\s*"ENABLED"',
    '"api_keys"\s*:\s*"ENABLED"',
    '"real_webhooks"\s*:\s*"ENABLED"',
    '"real_orders"\s*:\s*"ENABLED"',
    '"ai_assisted_execution"\s*:\s*"ENABLED"',
    'window\.open',
    'place_order'
  )) {
    if ($combined -match $unsafePattern) {
      Add-Failure "Unsafe pattern found: $unsafePattern"
    }
  }
}

if ($failures.Count -eq 0) {
  Write-Host "PASS: Phase 24 Trading Lab workstation fixture and contract are valid, latency fields are nested, and safety remains BLOCKED."
  exit 0
}

Write-Host "FAIL: Phase 24 Trading Lab workstation validation found issues."
foreach ($failure in $failures) {
  Write-Host "- $failure"
}
exit 1
