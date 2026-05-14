param(
  [Parameter(Mandatory = $true)]
  [string]$EventType,

  [Parameter(Mandatory = $true)]
  [string]$Source,

  [Parameter(Mandatory = $true)]
  [string]$Summary,

  [string]$PacketId = "",

  [string]$ApprovalId = "",

  [string]$Status = "",

  [string]$Risk = "",

  [string]$LedgerPath = "telemetry/work_ledger.jsonl"
)

$Event = [ordered]@{
  eventId = "evt_$([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds())"
  eventType = $EventType
  system = "AI_OS"
  source = $Source
  summary = $Summary
  packetId = $PacketId
  approvalId = $ApprovalId
  status = $Status
  risk = $Risk
  ts = (Get-Date).ToUniversalTime().ToString("o")
}

$Directory = Split-Path -Parent $LedgerPath
if ($Directory -and -not (Test-Path -LiteralPath $Directory)) {
  New-Item -ItemType Directory -Force $Directory | Out-Null
}

($Event | ConvertTo-Json -Compress -Depth 8) | Add-Content -Path $LedgerPath

$Event | ConvertTo-Json -Depth 8
