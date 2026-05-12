param(
  [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
  param([string]$Message)
  $script:failures.Add($Message) | Out-Null
}

Push-Location $RepoRoot
try {
  $fixturePath = "apps/dashboard/mock-data/trading-lab-window-system.example.json"
  $docPath = "docs/AI_OS/trading_laboratory/paper_bot_core/TRADING_LAB_MODULAR_WINDOW_SYSTEM.md"

  foreach ($file in @($fixturePath, $docPath)) {
    if (-not (Test-Path -LiteralPath $file)) {
      Add-Failure "Missing required file: $file"
    }
  }

  $data = $null
  if (Test-Path -LiteralPath $fixturePath) {
    try {
      $data = Get-Content -Raw -LiteralPath $fixturePath | ConvertFrom-Json
    } catch {
      Add-Failure "trading-lab-window-system.example.json parse failed."
    }
  }

  if ($null -ne $data) {
    foreach ($windowName in @("tradingview_chart", "paper_trade_engine", "traderspost_route_preview", "status_telemetry", "next_action")) {
      if (-not ($data.windows.PSObject.Properties.Name -contains $windowName)) {
        Add-Failure "Missing required window: $windowName"
      }
    }

    foreach ($field in @("live_execution_status", "broker_status", "oanda_status", "api_key_status", "credential_status", "real_webhook_status", "real_order_status")) {
      if ($data.safety.$field -ne "BLOCKED") {
        Add-Failure "Safety field is not BLOCKED: $field"
      }
    }

    if ($data.external_platforms.main_screen_buttons_allowed -ne $false) {
      Add-Failure "External platforms are not blocked from main-screen buttons."
    }

    $platformText = ($data.external_platforms | ConvertTo-Json -Depth 10)
    foreach ($unsafePattern in @("login_allowed.*true", "credentials_requested.*true", "api_key_requested.*true", "webhook_enabled.*true", "broker_connection_allowed.*true", "real_route_enabled.*true", "real_execution_enabled.*true")) {
      if ($platformText -match $unsafePattern) {
        Add-Failure "Unsafe external platform enablement found: $unsafePattern"
      }
    }
  }

  $dashboardText = ""
  foreach ($file in @("apps/dashboard/AIOS_STATIC_PREVIEW.html", "apps/dashboard/js/aios-static-preview.js", "apps/dashboard/mock-data/dashboard-navigation-model.example.json", "apps/dashboard/mock-data/dashboard-ui-registry.example.json")) {
    if (Test-Path -LiteralPath $file) {
      $dashboardText += "`n" + (Get-Content -Raw -LiteralPath $file)
    }
  }
  foreach ($platform in @("MetaTrader 5", "TradingView", "TradersPost")) {
    if ($dashboardText -match "main-screen button.*$platform") {
      Add-Failure "$platform appears as a main-screen button."
    }
  }

  $nodeResult = & node --check "apps/dashboard/js/aios-static-preview.js" 2>&1
  if ($LASTEXITCODE -ne 0) {
    Add-Failure "node --check failed: $nodeResult"
  }

  & powershell -NoProfile -ExecutionPolicy Bypass -File "automation/trading_lab/Test-AiOsPaperBotCoreReadiness.DRY_RUN.ps1" | Out-Null
  if ($LASTEXITCODE -ne 0) {
    Add-Failure "Paper Bot Core validator failed."
  }

  & powershell -NoProfile -ExecutionPolicy Bypass -File "automation/trading_lab/Test-AiOsPaperBotRuntimeSimulation.DRY_RUN.ps1" | Out-Null
  if ($LASTEXITCODE -ne 0) {
    Add-Failure "Paper Runtime validator failed."
  }

  if ($failures.Count -gt 0) {
    Write-Output "AI_OS Trading Lab Window System: FAIL"
    $failures | ForEach-Object { Write-Output "FAIL: $_" }
    exit 1
  }

  Write-Output "AI_OS Trading Lab Window System: PASS"
  Write-Output "Window fixture JSON parse: PASS"
  Write-Output "Required windows: PASS"
  Write-Output "Safety boundary: PASS"
  Write-Output "External platform placement: PASS"
  Write-Output "Dashboard JS syntax: PASS"
  Write-Output "Paper Bot Core validator: PASS"
  Write-Output "Paper Runtime validator: PASS"
} finally {
  Pop-Location
}
