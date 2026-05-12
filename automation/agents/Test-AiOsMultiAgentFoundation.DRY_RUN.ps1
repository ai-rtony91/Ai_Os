$ErrorActionPreference = "Stop"

Write-Host "AI_OS Multi-Agent Foundation DRY_RUN"
Write-Host "Mode: read-only"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")

$RequiredFiles = @(
  "docs\AI_OS\multi_agent\AIOS_MULTI_AGENT_FOUNDATION_PLAN.md",
  "docs\AI_OS\multi_agent\AIOS_AGENT_ROUTING_MODEL.md",
  "docs\AI_OS\multi_agent\AIOS_AGENT_ROLE_MATRIX.json",
  "docs\AI_OS\secrets\AIOS_LOCAL_ONLY_KEY_STORAGE_PLAN.md",
  "apps\dashboard\mock-data\multi-agent-foundation.example.json",
  "automation\agents\Test-AiOsMultiAgentFoundation.DRY_RUN.ps1",
  "Reports\health\MULTI_AGENT_FOUNDATION_DRY_RUN.md",
  "Reports\checkpoints\CHECKPOINT_MULTI_AGENT_FOUNDATION_DRY_RUN.md"
)

$JsonFiles = @(
  "docs\AI_OS\multi_agent\AIOS_AGENT_ROLE_MATRIX.json",
  "apps\dashboard\mock-data\multi-agent-foundation.example.json"
)

$Failures = New-Object System.Collections.Generic.List[string]

foreach ($RelativePath in $RequiredFiles) {
  $FullPath = Join-Path $RepoRoot $RelativePath
  if (-not (Test-Path -LiteralPath $FullPath -PathType Leaf)) {
    $Failures.Add("Missing required file: $RelativePath")
  }
}

foreach ($RelativePath in $JsonFiles) {
  $FullPath = Join-Path $RepoRoot $RelativePath
  if (Test-Path -LiteralPath $FullPath -PathType Leaf) {
    try {
      Get-Content -LiteralPath $FullPath -Raw | ConvertFrom-Json | Out-Null
    } catch {
      $Failures.Add("JSON parse failed: $RelativePath")
    }
  }
}

$RoleMatrixPath = Join-Path $RepoRoot "docs\AI_OS\multi_agent\AIOS_AGENT_ROLE_MATRIX.json"
if (Test-Path -LiteralPath $RoleMatrixPath -PathType Leaf) {
  $RoleMatrix = Get-Content -LiteralPath $RoleMatrixPath -Raw | ConvertFrom-Json
  $RequiredRoles = @(
    "human_operator",
    "chatgpt_orchestrator",
    "codex_implementation_agent",
    "claude_review_agent",
    "risk_gate_agent",
    "validator_agent"
  )
  $RoleIds = @($RoleMatrix.roles | ForEach-Object { $_.id })
  foreach ($Role in $RequiredRoles) {
    if ($RoleIds -notcontains $Role) {
      $Failures.Add("Missing role: $Role")
    }
  }
  if ($RoleMatrix.integration_status.api_keys -ne "BLOCKED") { $Failures.Add("API keys status is not BLOCKED.") }
  if ($RoleMatrix.integration_status.secrets -ne "BLOCKED") { $Failures.Add("Secrets status is not BLOCKED.") }
  if ($RoleMatrix.integration_status.anthropic_integration -ne "NOT_ENABLED") { $Failures.Add("Anthropic integration is not NOT_ENABLED.") }
  if ($RoleMatrix.integration_status.openai_integration_changes -ne "NOT_CHANGED") { $Failures.Add("OpenAI integration changes status is not NOT_CHANGED.") }
  if ($RoleMatrix.trading_safety.live_trading -ne "BLOCKED") { $Failures.Add("Live trading status is not BLOCKED.") }
  if ($RoleMatrix.trading_safety.broker -ne "BLOCKED") { $Failures.Add("Broker status is not BLOCKED.") }
  if ($RoleMatrix.trading_safety.oanda -ne "BLOCKED") { $Failures.Add("OANDA status is not BLOCKED.") }
  if ($RoleMatrix.trading_safety.real_webhooks -ne "BLOCKED") { $Failures.Add("Real webhooks status is not BLOCKED.") }
  if ($RoleMatrix.trading_safety.real_orders -ne "BLOCKED") { $Failures.Add("Real orders status is not BLOCKED.") }
}

$DashboardFixturePath = Join-Path $RepoRoot "apps\dashboard\mock-data\multi-agent-foundation.example.json"
if (Test-Path -LiteralPath $DashboardFixturePath -PathType Leaf) {
  $DashboardFixture = Get-Content -LiteralPath $DashboardFixturePath -Raw | ConvertFrom-Json
  if ($DashboardFixture.integration_status.api_keys -ne "BLOCKED") { $Failures.Add("Dashboard API keys status is not BLOCKED.") }
  if ($DashboardFixture.integration_status.secrets -ne "BLOCKED") { $Failures.Add("Dashboard secrets status is not BLOCKED.") }
  if ($DashboardFixture.integration_status.anthropic_integration -ne "NOT_ENABLED") { $Failures.Add("Dashboard Anthropic integration is not NOT_ENABLED.") }
  if ($DashboardFixture.trading_safety.live_trading -ne "BLOCKED") { $Failures.Add("Dashboard live trading status is not BLOCKED.") }
  if ($DashboardFixture.trading_safety.broker -ne "BLOCKED") { $Failures.Add("Dashboard broker status is not BLOCKED.") }
  if ($DashboardFixture.trading_safety.oanda -ne "BLOCKED") { $Failures.Add("Dashboard OANDA status is not BLOCKED.") }
  if ($DashboardFixture.trading_safety.real_webhooks -ne "BLOCKED") { $Failures.Add("Dashboard real webhooks status is not BLOCKED.") }
  if ($DashboardFixture.trading_safety.real_orders -ne "BLOCKED") { $Failures.Add("Dashboard real orders status is not BLOCKED.") }
}

$ScanText = ""
foreach ($RelativePath in $RequiredFiles) {
  $FullPath = Join-Path $RepoRoot $RelativePath
  if (Test-Path -LiteralPath $FullPath -PathType Leaf) {
    $ScanText += "`n"
    $ScanText += Get-Content -LiteralPath $FullPath -Raw
  }
}

$UnsafePatterns = @(
  '"api_keys"\s*:\s*"ENABLED"',
  '"secrets"\s*:\s*"ENABLED"',
  '"anthropic_integration"\s*:\s*"ENABLED"',
  '"live_trading"\s*:\s*"ENABLED"',
  '"broker"\s*:\s*"ENABLED"',
  '"oanda"\s*:\s*"ENABLED"',
  '"real_webhooks"\s*:\s*"ENABLED"',
  '"real_orders"\s*:\s*"ENABLED"'
)

foreach ($Pattern in $UnsafePatterns) {
  if ($ScanText -match $Pattern) {
    $Failures.Add("Unsafe enabled status found: $Pattern")
  }
}

Write-Host "Git status:"
git status --short --branch

if ($Failures.Count -eq 0) {
  Write-Host "PASS: Multi-agent foundation files are present, JSON parses, roles exist, and safety locks remain blocked."
  exit 0
}

Write-Host "FAIL: Multi-agent foundation readiness check found issues."
foreach ($Failure in $Failures) {
  Write-Host "- $Failure"
}
exit 1
