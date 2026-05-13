$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$jsonFiles = Get-ChildItem -Path $root -Recurse -Filter "*.json"
$requiredStates = @("ALLOW", "REJECT", "WAIT", "LOW_CONFIDENCE", "SESSION_BLOCK", "RISK_BLOCK")

foreach ($file in $jsonFiles) {
  try {
    $content = Get-Content -LiteralPath $file.FullName -Raw
    $json = $content | ConvertFrom-Json
  } catch {
    Write-Host "FAIL: JSON parse failed: $($file.FullName)"
    exit 1
  }

  if ($json.PSObject.Properties.Name -contains "paper_only_status") {
    if ($json.paper_only_status -ne "PAPER_ONLY") {
      Write-Host "FAIL: paper_only_status must be PAPER_ONLY: $($file.FullName)"
      exit 1
    }
  } else {
    Write-Host "FAIL: Missing paper_only_status: $($file.FullName)"
    exit 1
  }

  if ($json.live_execution_status -ne "BLOCKED") {
    Write-Host "FAIL: live_execution_status must remain BLOCKED: $($file.FullName)"
    exit 1
  }
}

$decisionTreePath = Join-Path $root "signals\FOREX_SIGNAL_DECISION_TREE_001.json"
$decisionTree = Get-Content -LiteralPath $decisionTreePath -Raw | ConvertFrom-Json
foreach ($state in $requiredStates) {
  if ($decisionTree.decision_states -notcontains $state) {
    Write-Host "FAIL: Missing decision state: $state"
    exit 1
  }
}

$files = Get-ChildItem -Path $root -Recurse -File
foreach ($file in $files) {
  $text = Get-Content -LiteralPath $file.FullName -Raw
  if ($text -notmatch "paper-only|paper_only|PAPER_ONLY") {
    Write-Host "FAIL: File must contain paper-only language: $($file.FullName)"
    exit 1
  }
  $unsafePattern = "api" + "_key\s*[:=]\s*[^`"']|" +
    "webhook" + "_url|" +
    "broker" + "_execute|" +
    "live" + "_order|" +
    "external request " + "allowed|" +
    "live_execution" + "_status`"\s*:\s*`"" + "ALLOWED"
  if ($text -match $unsafePattern) {
    Write-Host "FAIL: Unsafe execution pattern found: $($file.FullName)"
    exit 1
  }
}

Write-Host "PASS: Forex Money Bot decision engine DRY_RUN validation passed."
Write-Host "Paper-only decision states and blocked live execution confirmed."
