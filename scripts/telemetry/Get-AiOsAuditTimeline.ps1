param(
  [string]$LedgerPath = "telemetry/work_ledger.jsonl",

  [ValidateSet("Table", "Json")]
  [string]$Format = "Table",

  [int]$Recent = 0
)

function Get-AuditCategory {
  param([string]$EventType)

  switch ($EventType) {
    "policy_decision" { return "policy_decision" }
    "approval_requested" { return "approval" }
    "approval_decided" { return "approval" }
    "packet_blocked" { return "failure" }
    "packet_applied" { return "execution" }
    "clean_state_checked" { return "recovery" }
    "packet_dispatched" { return "packet_lifecycle" }
    default { return "telemetry" }
  }
}

function Get-RecoveryAction {
  param(
    [string]$EventType,
    [string]$Status
  )

  if ($EventType -ne "packet_blocked") {
    return $null
  }

  if ($Status -eq "failed") {
    return "Review failure reason, retry budget, and rollback metadata before reassignment."
  }

  return "Keep packet blocked until human review clears approval, policy, and rollback evidence."
}

if (-not (Test-Path -LiteralPath $LedgerPath)) {
  $empty = [ordered]@{
    schema = "aios.audit_timeline.v1"
    generatedAt = (Get-Date).ToUniversalTime().ToString("o")
    ledgerPath = $LedgerPath
    sourceEventCount = 0
    invalidLineCount = 0
    timeline = @()
    nextSafeAction = "No telemetry ledger found. Generate telemetry before replay."
  }

  $empty | ConvertTo-Json -Depth 8
  exit 0
}

$events = New-Object System.Collections.Generic.List[object]
$invalidLineCount = 0

foreach ($line in Get-Content -LiteralPath $LedgerPath) {
  $trimmed = $line.Trim()

  if (-not $trimmed) {
    continue
  }

  try {
    $events.Add(($trimmed | ConvertFrom-Json))
  } catch {
    $invalidLineCount += 1
  }
}

$timeline = foreach ($event in $events) {
  $eventType = [string]$event.eventType
  $status = [string]$event.status
  $packetId = [string]$event.packetId
  $approvalId = [string]$event.approvalId

  $whatChanged = if ($packetId -and $status) {
    "Packet $packetId status became $status"
  } elseif ($approvalId -and $status) {
    "Approval $approvalId status became $status"
  } elseif ($packetId) {
    "Packet $packetId recorded $eventType"
  } else {
    "Recorded $eventType"
  }

  [pscustomobject]@{
    ts = $event.ts
    category = Get-AuditCategory -EventType $eventType
    eventType = $eventType
    source = $event.source
    packetId = $event.packetId
    approvalId = $event.approvalId
    status = $event.status
    risk = $event.risk
    why = $event.summary
    whatChanged = $whatChanged
    recoveryAction = Get-RecoveryAction -EventType $eventType -Status $status
    eventId = $event.eventId
  }
}

$timeline = @($timeline | Sort-Object ts)

if ($Recent -gt 0) {
  $timeline = @($timeline | Select-Object -Last $Recent)
}

if ($Format -eq "Json") {
  [ordered]@{
    schema = "aios.audit_timeline.v1"
    generatedAt = (Get-Date).ToUniversalTime().ToString("o")
    ledgerPath = $LedgerPath
    sourceEventCount = $events.Count
    invalidLineCount = $invalidLineCount
    timeline = $timeline
    nextSafeAction = "Review blocked, failed, or pending approval events before APPLY, commit, or push."
  } | ConvertTo-Json -Depth 10
  exit 0
}

$timeline |
  Select-Object ts, category, eventType, packetId, approvalId, status, risk, why |
  Format-Table -AutoSize

if ($invalidLineCount -gt 0) {
  Write-Warning "$invalidLineCount invalid telemetry ledger line(s) were skipped."
}
