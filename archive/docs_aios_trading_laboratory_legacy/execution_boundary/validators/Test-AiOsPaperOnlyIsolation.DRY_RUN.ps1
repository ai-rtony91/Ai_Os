$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$files = Get-ChildItem -Path $root -Recurse -File
$jsonFiles = Get-ChildItem -Path $root -Recurse -Filter "*.json"

foreach ($file in $jsonFiles) {
  $json = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
  if (-not ($json.PSObject.Properties.Name -contains "paper_only_status")) {
    Write-Host "FAIL: Missing paper_only_status: $($file.FullName)"
    exit 1
  }
  if ($json.paper_only_status -ne "PAPER_ONLY") {
    Write-Host "FAIL: paper_only_status must be PAPER_ONLY: $($file.FullName)"
    exit 1
  }
  if ($json.live_execution_status -ne "BLOCKED") {
    Write-Host "FAIL: live_execution_status must be BLOCKED: $($file.FullName)"
    exit 1
  }
}

foreach ($file in $files) {
  $text = Get-Content -LiteralPath $file.FullName -Raw
  $unsafePattern = "live_execution_status`"\s*:\s*`"ALLOWED|" +
    "broker_api_status`"\s*:\s*`"CONNECTED|" +
    "webhook_execution_status`"\s*:\s*`"ENABLED|" +
    "autonomous_execution_status`"\s*:\s*`"ENABLED|" +
    "real_funds_status`"\s*:\s*`"ENABLED"
  if ($text -match $unsafePattern) {
    Write-Host "FAIL: Unsafe execution state found: $($file.FullName)"
    exit 1
  }
}

Write-Host "PASS: AI_OS paper-only isolation DRY_RUN validation passed."
Write-Host "Execution layer remains blocked, disconnected, and paper-only."
