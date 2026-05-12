param(
  [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"

$requiredFiles = @(
  "docs/AI_OS/trading_laboratory/paper_bot_core/README.md",
  "docs/AI_OS/trading_laboratory/paper_bot_core/PAPER_BOT_CORE_SPEC.md",
  "docs/AI_OS/trading_laboratory/paper_bot_core/PAPER_BOT_DECISION_FLOW.md",
  "docs/AI_OS/trading_laboratory/paper_bot_core/PAPER_BOT_SAFETY_BOUNDARY.md",
  "docs/AI_OS/trading_laboratory/paper_bot_core/PAPER_BOT_NEXT_ACTION.md",
  "docs/AI_OS/trading_laboratory/paper_bot_core/PAPER_BOT_SIGNAL_CONTRACT.json",
  "docs/AI_OS/trading_laboratory/paper_bot_core/PAPER_BOT_DECISION_CONTRACT.json",
  "docs/AI_OS/trading_laboratory/paper_bot_core/PAPER_BOT_RISK_GATE_CONTRACT.json",
  "docs/AI_OS/trading_laboratory/paper_bot_core/PAPER_BOT_SCORECARD_CONTRACT.json",
  "docs/AI_OS/trading_laboratory/paper_bot_core/PAPER_BOT_STATUS.json",
  "docs/AI_OS/trading_laboratory/paper_bot_core/MOCK_SIGNAL_001.json",
  "docs/AI_OS/trading_laboratory/paper_bot_core/MOCK_DECISION_001.json",
  "docs/AI_OS/trading_laboratory/paper_bot_core/MOCK_RISK_GATE_001.json",
  "docs/AI_OS/trading_laboratory/paper_bot_core/MOCK_SCORECARD_001.json",
  "docs/AI_OS/trading_laboratory/paper_bot_core/MOCK_PAPER_TRADE_001.json",
  "apps/dashboard/mock-data/paper-bot-core.example.json"
)

$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
  param([string]$Message)
  $script:failures.Add($Message) | Out-Null
}

Push-Location $RepoRoot
try {
  foreach ($file in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $file)) {
      Add-Failure "Missing required file: $file"
    }
  }

  $jsonFiles = Get-ChildItem -LiteralPath "docs/AI_OS/trading_laboratory/paper_bot_core" -Filter "*.json" -File
  $jsonFiles += Get-Item -LiteralPath "apps/dashboard/mock-data/paper-bot-core.example.json"
  foreach ($jsonFile in $jsonFiles) {
    try {
      Get-Content -Raw -LiteralPath $jsonFile.FullName | ConvertFrom-Json | Out-Null
    } catch {
      Add-Failure "JSON parse failed: $($jsonFile.FullName)"
    }
  }

  $newFiles = @($requiredFiles, "apps/dashboard/js/aios-static-preview.js", "apps/dashboard/mock-data/trading-lab-workspace.example.json")
  $combinedText = foreach ($file in $newFiles) {
    if (Test-Path -LiteralPath $file) {
      Get-Content -Raw -LiteralPath $file
    }
  }
  $text = ($combinedText -join "`n")

  foreach ($requiredMarker in @("BLOCKED", "No broker", "No OANDA", "No API keys", "No credentials", "No real webhooks", "No real orders", "No live execution")) {
    if ($text -notmatch [regex]::Escape($requiredMarker)) {
      Add-Failure "Missing safety marker: $requiredMarker"
    }
  }

  foreach ($unsafePattern in @("live_execution_status.*allowed", "broker_status.*connected", "oanda_status.*connected", "real_order_status.*enabled", "real_webhook_status.*enabled", "api_key_status.*enabled", "credential_status.*enabled")) {
    if ($text -match $unsafePattern) {
      Add-Failure "Unsafe enabled pattern found: $unsafePattern"
    }
  }

  $secretPattern = "(?i)(api[_-]?key\s*[:=]\s*[A-Za-z0-9_\-]{12,}|secret\s*[:=]\s*[A-Za-z0-9_\-]{12,}|token\s*[:=]\s*[A-Za-z0-9_\-]{12,}|password\s*[:=]\s*\S+)"
  if ($text -match $secretPattern) {
    Add-Failure "Possible secret-like value found in new Paper Bot Core files."
  }

  $nodeResult = & node --check "apps/dashboard/js/aios-static-preview.js" 2>&1
  if ($LASTEXITCODE -ne 0) {
    Add-Failure "node --check failed: $nodeResult"
  }

  $gitStatus = & git status --short --branch

  if ($failures.Count -gt 0) {
    Write-Output "AI_OS Paper Bot Core Readiness: FAIL"
    $failures | ForEach-Object { Write-Output "FAIL: $_" }
    Write-Output "Git status:"
    $gitStatus | ForEach-Object { Write-Output $_ }
    exit 1
  }

  Write-Output "AI_OS Paper Bot Core Readiness: PASS"
  Write-Output "JSON parse: PASS"
  Write-Output "Safety boundary: PASS"
  Write-Output "Dashboard JS syntax: PASS"
  Write-Output "Git status:"
  $gitStatus | ForEach-Object { Write-Output $_ }
} finally {
  Pop-Location
}
