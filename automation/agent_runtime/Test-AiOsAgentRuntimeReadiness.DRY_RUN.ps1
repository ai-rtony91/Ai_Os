$ErrorActionPreference = "Stop"

Write-Host "AI_OS Agent Runtime Readiness DRY_RUN"
Write-Host "Mode: read-only"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$runtimeDir = Join-Path $repoRoot "docs\AI_OS\agent_runtime"
$dashboardFixture = Join-Path $repoRoot "apps\dashboard\mock-data\agent-runtime-status.example.json"

$requiredFiles = @(
  "docs\AI_OS\agent_runtime\README.md",
  "docs\AI_OS\agent_runtime\PHASE_15_1_AGENT_ORCHESTRATION_RUNTIME_CORE.md",
  "docs\AI_OS\agent_runtime\AGENT_RUNTIME_CONTROL_MODEL.md",
  "docs\AI_OS\agent_runtime\AGENT_RUNTIME_TASK_SCHEMA.json",
  "docs\AI_OS\agent_runtime\AGENT_RUNTIME_QUEUE.json",
  "docs\AI_OS\agent_runtime\AGENT_RUNTIME_STATUS.json",
  "docs\AI_OS\agent_runtime\AGENT_RUNTIME_GAP_LOG.json",
  "docs\AI_OS\agent_runtime\AGENT_RUNTIME_OWNERSHIP_RULES.json",
  "docs\AI_OS\agent_runtime\AGENT_RUNTIME_VALIDATION_REPORT.json",
  "docs\AI_OS\agent_runtime\AGENT_RUNTIME_NEXT_ACTION.md",
  "docs\AI_OS\agent_runtime\AGENT_RUNTIME_CODEX_SUMMARY.md",
  "docs\AI_OS\agent_runtime\AGENT_RUNTIME_TIME_OF_NO_RETURN_RULES.md",
  "docs\AI_OS\agent_runtime\TRADING_LAB_AGENT_RUNTIME_BRIDGE.md",
  "docs\AI_OS\agent_runtime\LLM_WORKER_CONNECTION_BOUNDARY.md",
  "docs\AI_OS\agent_runtime\README_FOR_NON_TECHNICAL_OPERATOR.md",
  "automation\agent_runtime\Test-AiOsAgentRuntimeReadiness.DRY_RUN.ps1",
  "automation\agent_runtime\Get-AiOsAgentRuntimeSnapshot.DRY_RUN.ps1",
  "automation\agent_runtime\README_FOLDER_PURPOSE.txt",
  "apps\dashboard\mock-data\agent-runtime-status.example.json"
)

$failures = New-Object System.Collections.Generic.List[string]

foreach ($relativePath in $requiredFiles) {
  $fullPath = Join-Path $repoRoot $relativePath
  if (-not (Test-Path -LiteralPath $fullPath)) {
    $failures.Add("Missing required file: $relativePath")
  }
}

$jsonFiles = @()
if (Test-Path -LiteralPath $runtimeDir) {
  $jsonFiles += Get-ChildItem -LiteralPath $runtimeDir -Filter "*.json" -File
}
if (Test-Path -LiteralPath $dashboardFixture) {
  $jsonFiles += Get-Item -LiteralPath $dashboardFixture
}

foreach ($jsonFile in $jsonFiles) {
  try {
    Get-Content -LiteralPath $jsonFile.FullName -Raw | ConvertFrom-Json | Out-Null
  } catch {
    $failures.Add("JSON parse failed: $($jsonFile.FullName)")
  }
}

$allTextFiles = @()
if (Test-Path -LiteralPath $runtimeDir) {
  $allTextFiles += Get-ChildItem -LiteralPath $runtimeDir -File
}
if (Test-Path -LiteralPath $dashboardFixture) {
  $allTextFiles += Get-Item -LiteralPath $dashboardFixture
}

$combinedText = ""
foreach ($file in $allTextFiles) {
  $combinedText += "`n"
  $combinedText += Get-Content -LiteralPath $file.FullName -Raw
}

$requiredSafetyText = @(
  '"live_execution_status": "BLOCKED"',
  '"external_llm_install_status": "NOT_ENABLED"',
  '"broker_status": "BLOCKED"',
  '"oanda_status": "BLOCKED"',
  '"api_key_status": "BLOCKED"',
  '"secrets_status": "BLOCKED"',
  '"live_execution": "BLOCKED"',
  '"broker": "BLOCKED"',
  '"oanda": "BLOCKED"',
  '"api_keys": "BLOCKED"',
  '"secrets": "BLOCKED"',
  '"external_llm_install": "NOT_ENABLED"'
)

foreach ($text in $requiredSafetyText) {
  if ($combinedText -notlike "*$text*") {
    $failures.Add("Missing safety text: $text")
  }
}

$enabledPatterns = @(
  '"live_execution_status"\s*:\s*"ENABLED"',
  '"broker_status"\s*:\s*"ENABLED"',
  '"oanda_status"\s*:\s*"ENABLED"',
  '"api_key_status"\s*:\s*"ENABLED"',
  '"secrets_status"\s*:\s*"ENABLED"'
)

foreach ($pattern in $enabledPatterns) {
  if ($combinedText -match $pattern) {
    $failures.Add("Unsafe ENABLED status found for pattern: $pattern")
  }
}

if ($failures.Count -eq 0) {
  Write-Host "PASS: Agent runtime scaffold is present, JSON parses, and risky statuses remain blocked."
  exit 0
}

Write-Host "FAIL: Agent runtime readiness check found issues."
foreach ($failure in $failures) {
  Write-Host "- $failure"
}
exit 1

