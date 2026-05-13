$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$jsonFiles = Get-ChildItem -Path (Join-Path $root "contracts") -Filter "*.json"
$requiredBlockedStates = @("LIVE_ORDER_BLOCKED", "BROKER_API_BLOCKED", "AUTONOMOUS_EXECUTION_BLOCKED", "WEBHOOK_EXECUTION_BLOCKED", "REAL_FUNDS_BLOCKED")
$requiredPermissions = @("PAPER_ALLOWED", "LIVE_BLOCKED", "SIMULATION_ALLOWED", "BROKER_DISCONNECTED")
$requiredFields = @("signal_id", "market", "pair_or_asset", "confidence_score", "recommendation", "paper_only_status", "execution_permission", "live_execution_status", "blocked_reason")

foreach ($file in $jsonFiles) {
  $json = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
  if ($json.paper_only_status -ne "PAPER_ONLY") {
    Write-Host "FAIL: paper_only_status must be PAPER_ONLY: $($file.FullName)"
    exit 1
  }
  if ($json.live_execution_status -ne "BLOCKED") {
    Write-Host "FAIL: live_execution_status must remain BLOCKED: $($file.FullName)"
    exit 1
  }
  foreach ($state in $requiredBlockedStates) {
    if ($json.blocked_execution_states -notcontains $state) {
      Write-Host "FAIL: Missing blocked execution state $state in $($file.FullName)"
      exit 1
    }
  }
  foreach ($permission in $requiredPermissions) {
    if ($json.execution_permissions -notcontains $permission) {
      Write-Host "FAIL: Missing execution permission $permission in $($file.FullName)"
      exit 1
    }
  }
  $payload = $json.signal
  if (-not $payload) { $payload = $json.permission_contract }
  if (-not $payload) { $payload = $json.paper_route }
  foreach ($field in $requiredFields) {
    if (-not ($payload.PSObject.Properties.Name -contains $field)) {
      Write-Host "FAIL: Missing contract field $field in $($file.FullName)"
      exit 1
    }
  }
}

Write-Host "PASS: AI_OS execution boundary DRY_RUN validation passed."
Write-Host "Blocked execution states, permissions, and contract fields confirmed."
