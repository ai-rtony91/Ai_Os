param(
  [string]$RepoRoot = "."
)

$ErrorActionPreference = "Stop"
$ResolvedRepoRoot = (Resolve-Path $RepoRoot).Path
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
  param([string]$Message)
  $script:failures.Add($Message) | Out-Null
  Write-Host "FAIL: $Message" -ForegroundColor Red
}

function Read-JsonFile {
  param([string]$RelativePath)
  $fullPath = Join-Path $ResolvedRepoRoot $RelativePath
  if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
    Add-Failure "Missing JSON file: $RelativePath"
    return $null
  }
  try {
    return Get-Content -LiteralPath $fullPath -Raw | ConvertFrom-Json
  } catch {
    Add-Failure "JSON parse failed: $RelativePath :: $($_.Exception.Message)"
    return $null
  }
}

function Test-ArrayField {
  param(
    [object]$Packet,
    [string]$Path,
    [string]$FieldName
  )
  if (-not ($Packet.PSObject.Properties.Name -contains $FieldName)) {
    Add-Failure "$Path missing required field: $FieldName"
    return
  }
  $items = @($Packet.$FieldName)
  if ($items.Count -eq 0) {
    Add-Failure "$Path field must contain at least one item: $FieldName"
  }
}

function Test-ScalarField {
  param(
    [object]$Packet,
    [string]$Path,
    [string]$FieldName
  )
  if (-not ($Packet.PSObject.Properties.Name -contains $FieldName)) {
    Add-Failure "$Path missing required field: $FieldName"
    return
  }
  if ([string]::IsNullOrWhiteSpace([string]$Packet.$FieldName)) {
    Add-Failure "$Path field must not be empty: $FieldName"
  }
}

function Test-BlockedToken {
  param(
    [object]$Packet,
    [string]$Path,
    [string]$Token
  )
  $blockedText = (@($Packet.blocked_actions) -join " ").ToLowerInvariant()
  if (-not $blockedText.Contains($Token.ToLowerInvariant())) {
    Add-Failure "$Path blocked_actions must include: $Token"
  }
}

Write-Host "AI_OS Mission JSON DRY_RUN Validator" -ForegroundColor Cyan
Write-Host "Repo: $ResolvedRepoRoot"
Write-Host "Safety: read-only validator. No files are created, edited, moved, deleted, staged, committed, pushed, launched, broker-routed, webhook-fired, credential-accessed, or traded."

$schemaPath = "work_packets/schema.json"
$schema = Read-JsonFile -RelativePath $schemaPath
if ($schema) {
  if ($schema.'$id' -ne "AIOS_WORK_PACKET.v1") {
    Add-Failure "$schemaPath must declare `$id AIOS_WORK_PACKET.v1."
  }
  foreach ($field in @("id", "version", "title", "lane", "mode", "status", "objective", "allowed_actions", "blocked_actions", "files_in_scope", "validators", "risks", "stop_condition", "approval_required", "created_by", "notes")) {
    if (@($schema.required) -notcontains $field) {
      Add-Failure "$schemaPath required list missing: $field"
    }
  }
}

$packetPaths = @(
  "work_packets/examples/trading_lab_latency.json",
  "work_packets/examples/dashboard_orchestration_cleanup.json",
  "work_packets/examples/validator_chain_hardening.json",
  "work_packets/examples/worker_registry_consolidation.json"
)

$ids = @{}
foreach ($path in $packetPaths) {
  $packet = Read-JsonFile -RelativePath $path
  if (-not $packet) {
    continue
  }

  foreach ($field in @("id", "version", "title", "lane", "mode", "status", "objective", "stop_condition", "created_by")) {
    Test-ScalarField -Packet $packet -Path $path -FieldName $field
  }
  foreach ($field in @("allowed_actions", "blocked_actions", "files_in_scope", "validators", "risks", "notes")) {
    Test-ArrayField -Packet $packet -Path $path -FieldName $field
  }
  if (-not ($packet.PSObject.Properties.Name -contains "approval_required")) {
    Add-Failure "$path missing required field: approval_required"
  } elseif ($packet.approval_required -ne $true) {
    Add-Failure "$path approval_required must be true."
  }
  if (@("DRY_RUN", "APPLY") -notcontains $packet.mode) {
    Add-Failure "$path mode must be DRY_RUN or APPLY."
  }
  if (@("READY_FOR_DRY_RUN", "READY_FOR_APPLY", "BLOCKED", "REVIEW") -notcontains $packet.status) {
    Add-Failure "$path status is not an allowed packet status."
  }
  if ($ids.ContainsKey($packet.id)) {
    Add-Failure "$path duplicates packet id $($packet.id)."
  } else {
    $ids[$packet.id] = $path
  }

  foreach ($token in @("broker", "OANDA", "API key", "webhook", "real order", "live trading", "commit", "push", "new branch", "scheduled task", "startup task", "extra window", "Codex auto-launch")) {
    Test-BlockedToken -Packet $packet -Path $path -Token $token
  }
}

if ($failures.Count -gt 0) {
  Write-Host ""
  Write-Host "AI_OS MISSION JSON VALIDATION: FAIL" -ForegroundColor Red
  exit 1
}

Write-Host ""
Write-Host "AI_OS MISSION JSON VALIDATION: PASS" -ForegroundColor Green
Write-Host "Packets validated: $($packetPaths.Count)"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
exit 0
