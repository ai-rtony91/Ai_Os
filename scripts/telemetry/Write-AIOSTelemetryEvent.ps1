<#
Canonical telemetry event writer for AI_OS.
Appends one event to the durable ledger as an append-only JSONL record.
Field names align with docs/governance/telemetry-contract.md target canonical schema.
This script captures evidence only. It does not approve APPLY, commit, push, or any governed action.
#>

param(
  [Parameter(Mandatory = $true)]
  [string]$EventType,

  [Parameter(Mandatory = $true)]
  [string]$Source,

  [Parameter(Mandatory = $true)]
  [string]$Result,

  [string]$Actor = "UNKNOWN",

  [string]$Lane = "UNKNOWN",

  [string]$RepoPath = "",

  [string]$Branch = "UNKNOWN",

  [string]$Mode = "DRY_RUN",

  [object]$AuthorityToken = $null,

  [string]$InputReference = "",

  [string]$OutputReference = "",

  [string]$RiskLevel = "LOW",

  [string]$NextSafeAction = "",

  [string]$ValidationStatus = "NOT_RUN",

  [string]$LedgerPath = "telemetry/work_ledger.jsonl"
)

$ResolvedRepoPath = if ($RepoPath) {
  $RepoPath
} else {
  (Resolve-Path -LiteralPath ".").Path
}

$Event = [ordered]@{
  event_id          = "evt_$([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds())"
  timestamp_utc     = (Get-Date).ToUniversalTime().ToString("o")
  event_type        = $EventType
  source            = $Source
  actor             = $Actor
  lane              = $Lane
  repo_path         = $ResolvedRepoPath
  branch            = $Branch
  mode              = $Mode
  authority_token   = $AuthorityToken
  authority_note    = "Telemetry is evidence, not approval authority."
  input_reference   = $InputReference
  output_reference  = $OutputReference
  result            = $Result
  risk_level        = $RiskLevel
  next_safe_action  = $NextSafeAction
  validation_status = $ValidationStatus
}

$Directory = Split-Path -Parent $LedgerPath
if ($Directory -and -not (Test-Path -LiteralPath $Directory)) {
  New-Item -ItemType Directory -Force $Directory | Out-Null
}

($Event | ConvertTo-Json -Compress -Depth 8) | Add-Content -Path $LedgerPath

$Event | ConvertTo-Json -Depth 8
